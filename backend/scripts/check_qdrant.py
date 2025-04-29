from qdrant_client import QdrantClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    # Initialize Qdrant client
    client = QdrantClient(url="http://localhost:6333")
    collection_name = "documents"
    
    try:
        # Get collection info
        collection_info = client.get_collection(collection_name)
        print(f"Collection info: {collection_info}")
        
        # Count points in collection
        count = client.count(collection_name)
        print(f"Number of documents in collection: {count}")
        
        # Get a sample of points
        points = client.scroll(collection_name, limit=1)
        if points[0]:
            print("\nSample document content:")
            print(points[0][0].payload["text"][:200] + "...")
        else:
            print("\nNo documents found in collection")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 