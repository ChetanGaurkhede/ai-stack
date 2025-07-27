import os
import uuid
import aiofiles
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Document
from app.schemas import DocumentResponse
from app.services.knowledge_base_service import KnowledgeBaseService
from app.config import settings
import structlog

logger = structlog.get_logger()
router = APIRouter()


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process a document"""
    try:
        # Validate file type
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in settings.allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file_extension} not allowed. Allowed types: {settings.allowed_extensions}"
            )
        
        # Validate file size
        if file.size and file.size > settings.max_file_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size {file.size} exceeds maximum allowed size {settings.max_file_size}"
            )
        
        # Create upload directory if it doesn't exist
        os.makedirs(settings.upload_dir, exist_ok=True)
        
        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(settings.upload_dir, unique_filename)
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Create document record
        db_document = Document(
            filename=unique_filename,
            original_filename=file.filename,
            file_path=file_path,
            file_size=len(content),
            file_type=file_extension
        )
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        
        # Process document for embeddings
        try:
            kb_service = KnowledgeBaseService()
            process_result = await kb_service.process_document(file_path, db_document.id)
            
            # Update document with content
            db_document.content = process_result.get("text_content", "")
            db_document.embeddings_created = True
            db.commit()
            db.refresh(db_document)
            
            logger.info("Document uploaded and processed successfully", 
                       document_id=db_document.id, filename=file.filename)
            
        except Exception as e:
            logger.error("Document processing failed", error=str(e), document_id=db_document.id)
            # Don't fail the upload, just log the error
            # The document is still saved but embeddings are not created
        
        return db_document
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Document upload failed", error=str(e), filename=file.filename)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload document"
        )


@router.get("/", response_model=List[DocumentResponse])
async def get_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all documents"""
    try:
        documents = db.query(Document).offset(skip).limit(limit).all()
        return documents
        
    except Exception as e:
        logger.error("Failed to get documents", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get documents"
        )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific document"""
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        return document
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get document", error=str(e), document_id=document_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get document"
        )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Delete a document"""
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Delete file from filesystem
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
        
        # Delete embeddings from ChromaDB
        try:
            kb_service = KnowledgeBaseService()
            await kb_service.delete_document_embeddings(document_id)
        except Exception as e:
            logger.warning("Failed to delete embeddings", error=str(e), document_id=document_id)
        
        # Delete from database
        db.delete(document)
        db.commit()
        
        logger.info("Document deleted", document_id=document_id)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete document", error=str(e), document_id=document_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document"
        )


@router.post("/{document_id}/reprocess")
async def reprocess_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Reprocess a document for embeddings"""
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        if not os.path.exists(document.file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document file not found on filesystem"
            )
        
        # Delete existing embeddings
        kb_service = KnowledgeBaseService()
        await kb_service.delete_document_embeddings(document_id)
        
        # Reprocess document
        process_result = await kb_service.process_document(document.file_path, document_id)
        
        # Update document
        document.content = process_result.get("text_content", "")
        document.embeddings_created = True
        db.commit()
        
        logger.info("Document reprocessed", document_id=document_id)
        
        return {
            "document_id": document_id,
            "success": True,
            "chunks_processed": process_result.get("chunks_processed", 0)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to reprocess document", error=str(e), document_id=document_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reprocess document"
        )


@router.get("/{document_id}/chunks")
async def get_document_chunks(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Get all chunks for a specific document"""
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        kb_service = KnowledgeBaseService()
        chunks = await kb_service.get_document_chunks(document_id)
        
        return {
            "document_id": document_id,
            "chunks": chunks,
            "total_chunks": len(chunks)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get document chunks", error=str(e), document_id=document_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get document chunks"
        ) 