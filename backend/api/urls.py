from django.urls import path
from . import views

urlpatterns = [
    path('hello/', views.hello_world, name='hello_world'),
    path('upload/', views.upload_file),
    path('list-files/', views.list_files),
    path('chat/', views.chat, name='chat'),
    path('clear-documents/', views.clear_documents, name='clear_documents'),
    path('ingest-documents/', views.ingest_documents, name='ingest_documents'),
] 