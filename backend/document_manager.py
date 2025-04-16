import os
from typing import List, Optional
from pathlib import Path
import logging
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.http import models
from openai import OpenAI

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentManager:
    def __init__(self, qdrant_url: str = "http://localhost:6333", collection_name: str = "documents"):
        """
        Initialize the DocumentManager with Qdrant and OpenAI clients.
        
        Args:
            qdrant_url: URL of the Qdrant server
            collection_name: Name of the collection to use in Qdrant
        """
        self.qdrant_url = qdrant_url
        self.collection_name = collection_name
        
        # Initialize clients
        self.qdrant_client = QdrantClient(url=qdrant_url)
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.embedding_model = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
        
        # Setup Qdrant collection
        self._setup_collection()
    
    def _setup_collection(self):
        """Initialize Qdrant collection if it doesn't exist."""
        try:
            self.qdrant_client.get_collection(self.collection_name)
        except Exception:
            self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=1536,  # OpenAI embedding dimension
                    distance=models.Distance.COSINE
                )
            )
            logger.info(f"Created new collection: {self.collection_name}")
    
    def load_documents(self, file_paths: List[str]) -> List[dict]:
        """Load documents from various file types."""
        documents = []
        for file_path in file_paths:
            try:
                if file_path.endswith('.pdf'):
                    loader = PyPDFLoader(file_path)
                elif file_path.endswith('.txt'):
                    loader = TextLoader(file_path)
                else:
                    logger.warning(f"Unsupported file type: {file_path}")
                    continue
                
                docs = loader.load()
                documents.extend(docs)
                logger.info(f"Successfully loaded {file_path}")
            except Exception as e:
                logger.error(f"Error loading {file_path}: {str(e)}")
        
        return documents
    
    def process_documents(self, documents: List[dict]) -> List[dict]:
        """Split documents into chunks and convert to embeddings."""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        split_docs = text_splitter.split_documents(documents)
        
        # Convert documents to embeddings
        texts = [doc.page_content for doc in split_docs]
        embeddings = self.embedding_model.embed_documents(texts)
        
        # Combine embeddings with original documents
        for i, doc in enumerate(split_docs):
            doc.metadata['embedding'] = embeddings[i]
        
        return split_docs
    
    def ingest_documents(self, upload_dir: str) -> bool:
        """
        Ingest documents from a directory into Qdrant.
        
        Args:
            upload_dir: Directory containing documents to ingest
            
        Returns:
            bool: True if ingestion was successful, False otherwise
        """
        if not os.path.exists(upload_dir):
            logger.error(f"Upload directory does not exist: {upload_dir}")
            return False
        
        # Get list of files to process
        file_paths = []
        for ext in ['*.txt', '*.pdf']:
            file_paths.extend(Path(upload_dir).glob(ext))
        
        if not file_paths:
            logger.warning(f"No .txt or .pdf files found in {upload_dir}")
            return False
        
        try:
            # Load and process documents
            documents = self.load_documents([str(p) for p in file_paths])
            processed_docs = self.process_documents(documents)
            
            # Prepare points for Qdrant
            points = []
            for i, doc in enumerate(processed_docs):
                points.append(
                    models.PointStruct(
                        id=i,
                        vector=doc.metadata['embedding'],
                        payload={
                            "text": doc.page_content,
                            "metadata": doc.metadata
                        }
                    )
                )
            
            # Upload points to Qdrant
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            logger.info(f"Successfully stored {len(points)} document chunks in Qdrant")
            return True
            
        except Exception as e:
            logger.error(f"Error during document ingestion: {str(e)}")
            return False
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for a text using OpenAI's API."""
        response = self.openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    
    def get_relevant_documents(self, query: str, limit: int = 3) -> List[str]:
        """
        Retrieve relevant documents from Qdrant based on the query.
        
        Args:
            query: The search query
            limit: Maximum number of documents to return
            
        Returns:
            List of relevant document texts
        """
        query_embedding = self.get_embedding(query)
        
        search_results = self.qdrant_client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=limit
        )
        
        return [hit.payload["text"] for hit in search_results]
    
    def generate_answer(self, query: str, context: Optional[List[str]] = None) -> str:
        """
        Generate an answer using OpenAI's API with the provided context.
        
        Args:
            query: The question to answer
            context: Optional list of context documents. If None, will search for relevant documents.
            
        Returns:
            Generated answer
        """
        if context is None:
            context = self.get_relevant_documents(query)
        
        context_str = "\n".join(context)
        
        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided context. If the context doesn't contain relevant information, say so."},
                {"role": "user", "content": f"Context:\n{context_str}\n\nQuestion: {query}"}
            ],
            temperature=0.7
        )
        
        return response.choices[0].message.content 