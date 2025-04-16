import os
from pathlib import Path
import logging
from dotenv import load_dotenv
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))
from document_manager import DocumentManager

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
UPLOAD_DIR = "/Users/joshzheng/Downloads/test-uploads"

def main():
    # Check if upload directory exists
    if not os.path.exists(UPLOAD_DIR):
        logger.error(f"Upload directory does not exist: {UPLOAD_DIR}")
        return
    
    # Get OpenAI API key
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        logger.error("OPENAI_API_KEY environment variable is not set")
        return
    
    # Initialize DocumentManager
    doc_manager = DocumentManager()
    
    # Ingest documents
    success = doc_manager.ingest_documents(UPLOAD_DIR)
    
    if success:
        logger.info("Document ingestion completed successfully")
    else:
        logger.error("Document ingestion failed")

if __name__ == "__main__":
    main() 