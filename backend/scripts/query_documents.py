import os
from dotenv import load_dotenv
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))
from document_manager import DocumentManager

# Load environment variables
load_dotenv()

def main():
    # Get OpenAI API key
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("OPENAI_API_KEY environment variable is not set")
        return
    
    # Initialize DocumentManager
    doc_manager = DocumentManager()
    
    # Test queries
    queries = [
        "What is this document about?",
        "What are the main topics covered?",
        "Tell me about the FAQ content"
    ]
    
    for query in queries:
        print(f"\n{'='*50}")
        print(f"Query: {query}")
        print(f"{'='*50}")
        
        # Get relevant documents
        context = doc_manager.get_relevant_documents(query)
        print(f"\nFound {len(context)} relevant documents:")
        
        for i, doc in enumerate(context, 1):
            print(f"\nDocument {i}:")
            print(doc[:200] + "...")
        
        # Generate answer
        answer = doc_manager.generate_answer(query)
        print(f"\nAnswer: {answer}")

if __name__ == "__main__":
    main() 