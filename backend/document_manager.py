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
        logger.info(f"Split documents into {len(split_docs)} chunks")
        
        # Convert documents to embeddings
        texts = [doc.page_content for doc in split_docs]        
        embeddings = self.embedding_model.embed_documents(texts)
        
        # Combine embeddings with original documents
        for i, doc in enumerate(split_docs):
            doc.metadata['embedding'] = embeddings[i]
            
        logger.info("Successfully combined embeddings with documents")
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
            logger.info(f"Found {len(file_paths)} files to process")
            for file_path in file_paths:
                logger.info(f"Processing file: {file_path}")
            
            documents = self.load_documents([str(p) for p in file_paths])
            logger.info(f"Loaded {len(documents)} documents")
            
            # Split documents into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
            )
            split_docs = text_splitter.split_documents(documents)
            logger.info(f"Split into {len(split_docs)} chunks")
            
            # Convert documents to embeddings
            texts = [doc.page_content for doc in split_docs]
            logger.info(f"Generating embeddings for {len(texts)} text chunks")
            logger.info(f"Sample text chunk: {texts[0][:200]}")
            
            # Generate embeddings directly with OpenAI API for more control
            embeddings = []
            for text in texts:
                response = self.openai_client.embeddings.create(
                    model="text-embedding-3-small",
                    input=text
                )
                embeddings.append(response.data[0].embedding)
                
            logger.info(f"Generated {len(embeddings)} embeddings")
            logger.info(f"First embedding size: {len(embeddings[0])}")
            logger.info(f"First embedding sample: {embeddings[0][:5]}")
            
            # Prepare points for Qdrant
            points = []
            for i, (doc, embedding) in enumerate(zip(split_docs, embeddings)):
                points.append(
                    models.PointStruct(
                        id=i,
                        vector=embedding,  # Use the embedding directly
                        payload={
                            "text": doc.page_content,
                            "metadata": doc.metadata
                        }
                    )
                )
            
            # Log sample points
            logger.info(f"Created {len(points)} points for Qdrant")
            if points:
                logger.info(f"Sample point:")
                logger.info(f"ID: {points[0].id}")
                logger.info(f"Vector size: {len(points[0].vector)}")
                logger.info(f"Payload preview: {str(points[0].payload)[:200]}...")
            
            # Upload points to Qdrant
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            logger.info(f"Successfully stored {len(points)} document chunks in Qdrant")
            
            # Verify ingestion with a test search
            test_query = "What is this document about?"
            test_embedding = self.get_embedding(test_query)
            test_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=test_embedding,
                limit=1,
                score_threshold=0.0  # No threshold for testing
            )
            
            if test_results:
                logger.info("Test search successful")
                logger.info(f"Found {len(test_results)} results")
                logger.info(f"Top result score: {test_results[0].score}")
            else:
                logger.error("Test search failed - no results found")
            
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
    
    def get_relevant_documents(self, query: str, limit: int = 5, score_threshold: float = 0.1) -> List[str]:
        """
        Retrieve relevant documents from Qdrant based on the query.
        
        Args:
            query: The search query
            limit: Maximum number of documents to return
            score_threshold: Minimum similarity score to consider a document relevant
            
        Returns:
            List of relevant document texts
        """
        logger.info(f"Searching for documents with query: {query}")
        query_embedding = self.get_embedding(query)
        
        # Get all points first to check what's available
        all_points = self.qdrant_client.scroll(
            collection_name=self.collection_name,
            limit=10
        )
        logger.info(f"Total available points: {len(all_points[0])}")
        if all_points[0]:
            logger.info("Sample point content:")
            logger.info(all_points[0][0].payload["text"][:200])
        
        # Use exact search with lower score threshold
        search_results = self.qdrant_client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=limit,
            score_threshold=score_threshold,
            search_params=models.SearchParams(
                exact=True,  # Use exact search
                hnsw_ef=128  # Increase search accuracy
            )
        )

        # Log search results for debugging
        logger.info(f"Found {len(search_results)} results")
        for i, hit in enumerate(search_results):
            logger.info(f"Result {i+1}: Score={hit.score:.4f}")
            logger.info(f"Content preview: {hit.payload['text'][:200]}...")
        
        # Return all results without additional filtering
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