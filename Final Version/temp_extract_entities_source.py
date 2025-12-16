async def extract_entities(
    chunks: dict[str, TextChunkSchema],
    global_config: dict[str, str],
    pipeline_status: dict = None,
    pipeline_status_lock=None,
    llm_response_cache: BaseKVStorage | None = None,
    text_chunks_storage: BaseKVStorage | None = None,
) -> list:
    # Check for cancellation at the start of entity extraction
    if pipeline_status is not None and pipeline_status_lock is not None:
        async with pipeline_status_lock:
            if pipeline_status.get("cancellation_requested", False):
                raise PipelineCancelledException(
                    "User cancelled during entity extraction"
                )

    use_llm_func: callable = global_config["llm_model_func"]
    entity_extract_max_gleaning = global_config["entity_extract_max_gleaning"]

    ordered_chunks = list(chunks.items())
    # add language and example number params to prompt
    language = global_config["addon_params"].get("language", DEFAULT_SUMMARY_LANGUAGE)
    entity_types = global_config["addon_params"].get(
        "entity_types", DEFAULT_ENTITY_TYPES
    )

    examples = "\n".join(PROMPTS["entity_extraction_examples"])

    example_context_base = dict(
        tuple_delimiter=PROMPTS["DEFAULT_TUPLE_DELIMITER"],
        completion_delimiter=PROMPTS["DEFAULT_COMPLETION_DELIMITER"],
        entity_types=", ".join(entity_types),
        language=language,
    )
    # add example's format
    examples = examples.format(**example_context_base)

    context_base = dict(
        tuple_delimiter=PROMPTS["DEFAULT_TUPLE_DELIMITER"],
        completion_delimiter=PROMPTS["DEFAULT_COMPLETION_DELIMITER"],
        entity_types=",".join(entity_types),
        examples=examples,
        language=language,
    )

    processed_chunks = 0
    total_chunks = len(ordered_chunks)

    async def _process_single_content(chunk_key_dp: tuple[str, TextChunkSchema]):
        """Process a single chunk
        Args:
            chunk_key_dp (tuple[str, TextChunkSchema]):
                ("chunk-xxxxxx", {"tokens": int, "content": str, "full_doc_id": str, "chunk_order_index": int})
        Returns:
            tuple: (maybe_nodes, maybe_edges) containing extracted entities and relationships
        """
        nonlocal processed_chunks
        chunk_key = chunk_key_dp[0]
        chunk_dp = chunk_key_dp[1]
        content = chunk_dp["content"]
        # Get file path from chunk data or use default
        file_path = chunk_dp.get("file_path", "unknown_source")

        # Create cache keys collector for batch processing
        cache_keys_collector = []

        # Get initial extraction
        entity_extraction_system_prompt = PROMPTS[
            "entity_extraction_system_prompt"
        ].format(**{**context_base, "input_text": content})
        entity_extraction_user_prompt = PROMPTS["entity_extraction_user_prompt"].format(
            **{**context_base, "input_text": content}
        )
        entity_continue_extraction_user_prompt = PROMPTS[
            "entity_continue_extraction_user_prompt"
        ].format(**{**context_base, "input_text": content})

        final_result, timestamp = await use_llm_func_with_cache(
            entity_extraction_user_prompt,
            use_llm_func,
            system_prompt=entity_extraction_system_prompt,
            llm_response_cache=llm_response_cache,
            cache_type="extract",
            chunk_id=chunk_key,
            cache_keys_collector=cache_keys_collector,
        )

        history = pack_user_ass_to_openai_messages(
            entity_extraction_user_prompt, final_result
        )

        # Process initial extraction with file path
        maybe_nodes, maybe_edges = await _process_extraction_result(
            final_result,
            chunk_key,
            timestamp,
            file_path,
            tuple_delimiter=context_base["tuple_delimiter"],
            completion_delimiter=context_base["completion_delimiter"],
        )

        # Process additional gleaning results only 1 time when entity_extract_max_gleaning is greater than zero.
        if entity_extract_max_gleaning > 0:
            glean_result, timestamp = await use_llm_func_with_cache(
                entity_continue_extraction_user_prompt,
                use_llm_func,
                system_prompt=entity_extraction_system_prompt,
                llm_response_cache=llm_response_cache,
                history_messages=history,
                cache_type="extract",
                chunk_id=chunk_key,
                cache_keys_collector=cache_keys_collector,
            )

            # Process gleaning result separately with file path
            glean_nodes, glean_edges = await _process_extraction_result(
                glean_result,
                chunk_key,
                timestamp,
                file_path,
                tuple_delimiter=context_base["tuple_delimiter"],
                completion_delimiter=context_base["completion_delimiter"],
            )

            # Merge results - compare description lengths to choose better version
            for entity_name, glean_entities in glean_nodes.items():
                if entity_name in maybe_nodes:
                    # Compare description lengths and keep the better one
                    original_desc_len = len(
                        maybe_nodes[entity_name][0].get("description", "") or ""
                    )
                    glean_desc_len = len(glean_entities[0].get("description", "") or "")

                    if glean_desc_len > original_desc_len:
                        maybe_nodes[entity_name] = list(glean_entities)
                    # Otherwise keep original version
                else:
                    # New entity from gleaning stage
                    maybe_nodes[entity_name] = list(glean_entities)

            for edge_key, glean_edges in glean_edges.items():
                if edge_key in maybe_edges:
                    # Compare description lengths and keep the better one
                    original_desc_len = len(
                        maybe_edges[edge_key][0].get("description", "") or ""
                    )
                    glean_desc_len = len(glean_edges[0].get("description", "") or "")

                    if glean_desc_len > original_desc_len:
                        maybe_edges[edge_key] = list(glean_edges)
                    # Otherwise keep original version
                else:
                    # New edge from gleaning stage
                    maybe_edges[edge_key] = list(glean_edges)

        # Batch update chunk's llm_cache_list with all collected cache keys
        if cache_keys_collector and text_chunks_storage:
            await update_chunk_cache_list(
                chunk_key,
                text_chunks_storage,
                cache_keys_collector,
                "entity_extraction",
            )

        processed_chunks += 1
        entities_count = len(maybe_nodes)
        relations_count = len(maybe_edges)
        log_message = f"Chunk {processed_chunks} of {total_chunks} extracted {entities_count} Ent + {relations_count} Rel {chunk_key}"
        logger.info(log_message)
        if pipeline_status is not None:
            async with pipeline_status_lock:
                pipeline_status["latest_message"] = log_message
                pipeline_status["history_messages"].append(log_message)

        # Return the extracted nodes and edges for centralized processing
        return maybe_nodes, maybe_edges

    # Get max async tasks limit from global_config
    chunk_max_async = global_config.get("llm_model_max_async", 4)
    semaphore = asyncio.Semaphore(chunk_max_async)

    async def _process_with_semaphore(chunk):
        async with semaphore:
            # Check for cancellation before processing chunk
            if pipeline_status is not None and pipeline_status_lock is not None:
                async with pipeline_status_lock:
                    if pipeline_status.get("cancellation_requested", False):
                        raise PipelineCancelledException(
                            "User cancelled during chunk processing"
                        )

            try:
                return await _process_single_content(chunk)
            except Exception as e:
                chunk_id = chunk[0]  # Extract chunk_id from chunk[0]
                prefixed_exception = create_prefixed_exception(e, chunk_id)
                raise prefixed_exception from e

    tasks = []
    for c in ordered_chunks:
        task = asyncio.create_task(_process_with_semaphore(c))
        tasks.append(task)

    # Wait for tasks to complete or for the first exception to occur
    # This allows us to cancel remaining tasks if any task fails
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)

    # Check if any task raised an exception and ensure all exceptions are retrieved
    first_exception = None
    chunk_results = []

    for task in done:
        try:
            exception = task.exception()
            if exception is not None:
                if first_exception is None:
                    first_exception = exception
            else:
                chunk_results.append(task.result())
        except Exception as e:
            if first_exception is None:
                first_exception = e

    # If any task failed, cancel all pending tasks and raise the first exception
    if first_exception is not None:
        # Cancel all pending tasks
        for pending_task in pending:
            pending_task.cancel()

        # Wait for cancellation to complete
        if pending:
            await asyncio.wait(pending)

        # Add progress prefix to the exception message
        progress_prefix = f"C[{processed_chunks + 1}/{total_chunks}]"

        # Re-raise the original exception with a prefix
        prefixed_exception = create_prefixed_exception(first_exception, progress_prefix)
        raise prefixed_exception from first_exception

    # If all tasks completed successfully, chunk_results already contains the results
    # Return the chunk_results for later processing in merge_nodes_and_edges
    return chunk_results
