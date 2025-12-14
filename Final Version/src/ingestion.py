"""
Resume ingestion pipeline with batch processing and progress tracking.
"""

import os
import logging
import asyncio
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime

from tqdm import tqdm

from .resume_parser import parse_resume, get_resume_files, extract_candidate_name
from .rag_config import get_rag

logger = logging.getLogger(__name__)


@dataclass
class IngestionResult:
    """Result of ingesting a single resume."""
    file_path: str
    candidate_name: str
    success: bool
    error: Optional[str] = None
    processing_time: float = 0.0


@dataclass
class BatchIngestionResult:
    """Result of batch ingestion."""
    total_files: int
    successful: int
    failed: int
    results: List[IngestionResult] = field(default_factory=list)
    total_time: float = 0.0


class ResumeIngestion:
    """Handles resume ingestion into LightRAG."""
    
    def __init__(self):
        self._rag = None
    
    async def _ensure_rag(self):
        """Ensure RAG is initialized."""
        if self._rag is None:
            self._rag = await get_rag()
        return self._rag
    
    async def ingest_single(
        self,
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> IngestionResult:
        """
        Ingest a single resume file.
        
        Args:
            file_path: Path to resume file
            metadata: Optional metadata to attach
            
        Returns:
            IngestionResult with status
        """
        start_time = datetime.now()
        
        try:
            # Parse resume
            content, file_type = parse_resume(file_path)
            
            if not content.strip():
                return IngestionResult(
                    file_path=file_path,
                    candidate_name="Unknown",
                    success=False,
                    error="Empty content after parsing"
                )
            
            # Extract candidate name
            candidate_name = extract_candidate_name(content, file_path)
            
            # Prepare document with metadata
            doc_content = f"# Resume: {candidate_name}\n\n{content}"
            
            # Get RAG instance
            rag = await self._ensure_rag()
            
            # Ingest into LightRAG (just pass the text content)
            await rag.ainsert(doc_content)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"✅ Ingested: {candidate_name} ({file_type}) in {processing_time:.2f}s")
            
            return IngestionResult(
                file_path=file_path,
                candidate_name=candidate_name,
                success=True,
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ Failed to ingest {file_path}: {e}")
            
            return IngestionResult(
                file_path=file_path,
                candidate_name="Unknown",
                success=False,
                error=str(e),
                processing_time=processing_time
            )
    
    async def ingest_batch(
        self,
        directory: str,
        batch_size: int = 5,
        show_progress: bool = True
    ) -> BatchIngestionResult:
        """
        Ingest all resumes from a directory in batches.
        
        Args:
            directory: Directory containing resume files
            batch_size: Number of files to process concurrently
            show_progress: Show progress bar
            
        Returns:
            BatchIngestionResult with summary
        """
        start_time = datetime.now()
        
        # Get all resume files
        files = get_resume_files(directory)
        
        if not files:
            return BatchIngestionResult(
                total_files=0,
                successful=0,
                failed=0
            )
        
        results = []
        successful = 0
        failed = 0
        
        # Create progress bar
        pbar = tqdm(total=len(files), desc="Ingesting resumes", disable=not show_progress)
        
        # Process in batches
        for i in range(0, len(files), batch_size):
            batch = files[i:i + batch_size]
            
            # Process batch concurrently
            batch_results = await asyncio.gather(
                *[self.ingest_single(f) for f in batch],
                return_exceptions=True
            )
            
            for result in batch_results:
                if isinstance(result, Exception):
                    failed += 1
                    results.append(IngestionResult(
                        file_path="unknown",
                        candidate_name="Unknown",
                        success=False,
                        error=str(result)
                    ))
                elif result.success:
                    successful += 1
                    results.append(result)
                else:
                    failed += 1
                    results.append(result)
                
                pbar.update(1)
        
        pbar.close()
        
        total_time = (datetime.now() - start_time).total_seconds()
        
        # Log summary
        logger.info(
            f"\n📊 Ingestion Summary:\n"
            f"  Total: {len(files)}\n"
            f"  ✅ Successful: {successful}\n"
            f"  ❌ Failed: {failed}\n"
            f"  ⏱️ Time: {total_time:.2f}s\n"
            f"  📈 Rate: {len(files)/total_time:.2f} files/sec"
        )
        
        return BatchIngestionResult(
            total_files=len(files),
            successful=successful,
            failed=failed,
            results=results,
            total_time=total_time
        )


# Convenience functions
async def ingest_resume(file_path: str) -> IngestionResult:
    """Ingest a single resume file."""
    ingestion = ResumeIngestion()
    return await ingestion.ingest_single(file_path)


async def ingest_resumes_from_directory(
    directory: str,
    batch_size: int = 5
) -> BatchIngestionResult:
    """Ingest all resumes from a directory."""
    ingestion = ResumeIngestion()
    return await ingestion.ingest_batch(directory, batch_size)
