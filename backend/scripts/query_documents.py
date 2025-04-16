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
    
    # Initial prompt
    query = "What are these documents about?"
    
    # Generate answer using DocumentManager
    answer = doc_manager.generate_answer(query)
    
    print("\nQuestion:", query)
    print("\nAnswer:", answer)
    
    # Get and print the context used
    context = doc_manager.get_relevant_documents(query)
    print("\nContext used:")
    for i, doc in enumerate(context, 1):
        print(f"\nDocument {i}:")
        print(doc)

if __name__ == "__main__":
    main() 