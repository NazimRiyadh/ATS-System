import os
import asyncio
from flask import Flask, request, jsonify
from flask_cors import CORS
from src.rag_engine import initialize_rag
from src.query_processor import extract_keywords
from rank_candidates import get_ranked_candidates
from lightrag.utils import logger
import logging

# Initialize Flask App
app = Flask(__name__)
CORS(app)

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global RAG instance (lazy loaded)
rag_instance = None

async def get_rag():
    global rag_instance
    if rag_instance is None:
        logger.info("Initializing LightRAG...")
        rag_instance = await initialize_rag()
    return rag_instance

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "LightRAG ATS API"}), 200

@app.route('/rank', methods=['POST'])
async def rank_endpoint():
    """
    Endpoint to rank candidates based on a job description.
    Payload: { "query": "Job Description...", "top_k": 5 }
    """
    data = request.get_json()
    query = data.get('query')
    top_k = data.get('top_k', 5)

    if not query:
        return jsonify({"error": "Query is required"}), 400

    try:
        # Optimization: Pass the global rag instance to avoid re-initialization
        rag = await get_rag()
        candidates = await get_ranked_candidates(query, top_k, rag_instance=rag)
        
        return jsonify({
            "query": query,
            "count": len(candidates),
            "results": candidates
        }), 200

    except Exception as e:
        logger.error(f"Error processing rank request: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/ingest', methods=['POST'])
async def ingest_endpoint():
    """
    Endpoint to upload and ingest a resume.
    Expects a file upload with key 'file'.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        filename = file.filename
        save_path = os.path.join(os.environ.get('RESUMES_DIR', './resumes'), filename)
        
        try:
            # Save file
            file.save(save_path)
            
            # Trigger Ingestion (This should ideally be a background task)
            # For MVP, we will do it inline or just save it and let a batch process handle it.
            # Let's just save it for now and return success.
            # Real-time ingestion might be too slow for an API call without a task queue.
            
            return jsonify({
                "message": "File uploaded successfully. It will be processed in the next batch.",
                "filename": filename
            }), 201
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
