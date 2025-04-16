from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import parser_classes
from qdrant_client import QdrantClient
import os
from document_manager import DocumentManager
from rest_framework import status
import json

# Create a single instance of DocumentManager to be reused
document_manager = DocumentManager()

# Create your views here.

@api_view(['GET'])
def hello_world(request):
    return Response("helloooo josh")

@api_view(['GET'])
def list_files(request):
    upload_dir = '/Users/joshzheng/Downloads/test-uploads'
    try:
        # Create directory if it doesn't exist
        os.makedirs(upload_dir, exist_ok=True)
        
        # List all files in the directory
        files = []
        for filename in os.listdir(upload_dir):
            # Skip .DS_Store files
            if filename == '.DS_Store':
                continue
                
            file_path = os.path.join(upload_dir, filename)
            if os.path.isfile(file_path):
                files.append({
                    'name': filename,
                    'size': os.path.getsize(file_path)
                })
        
        return Response(files)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_file(request):
    if 'file' not in request.FILES:
        return Response({'error': 'No file provided'}, status=400)
    
    file = request.FILES['file']
    upload_dir = '/Users/joshzheng/Downloads/test-uploads'
    
    # Create directory if it doesn't exist
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save the file
    file_path = os.path.join(upload_dir, file.name)
    with open(file_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    
    return Response({'message': 'File uploaded successfully', 'filename': file.name})

@api_view(['POST'])
def process_documents(request):
    """
    Process all documents in the upload directory and store them in Qdrant.
    """
    upload_dir = '/Users/joshzheng/Downloads/test-uploads'
    
    try:
        success = document_manager.ingest_documents(upload_dir)
        if success:
            return Response({'message': 'Documents processed and stored successfully'})
        return Response({'error': 'Failed to process documents'}, status=500)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def query_documents(request):
    """
    Query documents and get an answer based on the provided query.
    """
    query = request.GET.get('query', '')
    if not query:
        return Response({'error': 'No query provided'}, status=400)
    
    try:
        answer = document_manager.generate_answer(query)
        return Response({'answer': answer})
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def search_documents(request):
    """
    Search for relevant documents based on the query.
    """
    query = request.GET.get('query', '')
    limit = int(request.GET.get('limit', 3))
    
    if not query:
        return Response({'error': 'No query provided'}, status=400)
    
    try:
        documents = document_manager.get_relevant_documents(query, limit=limit)
        return Response({'documents': documents})
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
def chat(request):
    try:
        message = request.data.get('message')
        if not message:
            return Response(
                {"error": "Message is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get relevant documents and generate answer
        answer = document_manager.generate_answer(message)
        return Response({"response": answer})
    
    except Exception as e:
        return Response(
            {"error": str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
def clear_documents(request):
    """
    Clear all documents from the Qdrant collection and delete all files in the upload directory.
    """
    upload_dir = '/Users/joshzheng/Downloads/test-uploads'
    
    try:
        # Delete all files in the upload directory
        for filename in os.listdir(upload_dir):
            file_path = os.path.join(upload_dir, filename)
            try:
                if os.path.isfile(file_path) and filename != '.DS_Store':
                    os.unlink(file_path)
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")
        
        # Delete the collection and recreate it
        document_manager.qdrant_client.delete_collection(document_manager.collection_name)
        document_manager._setup_collection()
        
        return Response({
            'message': 'Documents collection cleared and files deleted successfully'
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
def ingest_documents(request):
    """
    Ingest all documents from the upload directory into Qdrant.
    """
    upload_dir = '/Users/joshzheng/Downloads/test-uploads'
    
    try:
        success = document_manager.ingest_documents(upload_dir)
        if success:
            return Response({'message': 'Documents ingested successfully'})
        return Response({'error': 'Failed to ingest documents'}, status=500)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
