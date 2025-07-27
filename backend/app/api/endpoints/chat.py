import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import ChatSession, Workflow, Document
from app.schemas import ChatRequest, ChatResponse, ChatSessionResponse
from app.services.workflow_engine import WorkflowEngine
import structlog

logger = structlog.get_logger()
router = APIRouter()


@router.post("/execute", response_model=ChatResponse)
async def execute_workflow(
    chat_request: ChatRequest,
    db: Session = Depends(get_db)
):
    """Execute a workflow with a query"""
    try:
        # Get workflow
        workflow = db.query(Workflow).filter(Workflow.id == chat_request.workflow_id).first()
        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )
        
        if not workflow.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Workflow is not active"
            )
        
        # Get document if specified
        document = None
        if chat_request.document_id:
            document = db.query(Document).filter(Document.id == chat_request.document_id).first()
            if not document:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Document not found"
                )
        
        # Execute workflow
        workflow_engine = WorkflowEngine()
        execution_result = await workflow_engine.execute_workflow(
            {
                "nodes": workflow.nodes,
                "edges": workflow.edges
            },
            chat_request.query,
            chat_request.document_id
        )
        
        if not execution_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Workflow execution failed: {execution_result.get('error', 'Unknown error')}"
            )
        
        # Create chat session
        session_id = str(uuid.uuid4())
        chat_session = ChatSession(
            session_id=session_id,
            workflow_id=chat_request.workflow_id,
            document_id=chat_request.document_id,
            user_query=chat_request.query,
            system_response=execution_result["response"],
            context_used=execution_result.get("context_used"),
            execution_logs=execution_result.get("logs")
        )
        db.add(chat_session)
        db.commit()
        
        logger.info("Workflow executed successfully", 
                   session_id=session_id, workflow_id=chat_request.workflow_id)
        
        return ChatResponse(
            session_id=session_id,
            response=execution_result["response"],
            context_used=execution_result.get("context_used"),
            execution_logs=execution_result.get("logs"),
            created_at=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Workflow execution failed", error=str(e), workflow_id=chat_request.workflow_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to execute workflow"
        )


@router.get("/sessions", response_model=List[ChatSessionResponse])
async def get_chat_sessions(
    workflow_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get chat sessions with optional workflow filter"""
    try:
        query = db.query(ChatSession)
        
        if workflow_id:
            query = query.filter(ChatSession.workflow_id == workflow_id)
        
        sessions = query.order_by(ChatSession.created_at.desc()).offset(skip).limit(limit).all()
        return sessions
        
    except Exception as e:
        logger.error("Failed to get chat sessions", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get chat sessions"
        )


@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_chat_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific chat session"""
    try:
        session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        return session
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get chat session", error=str(e), session_id=session_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get chat session"
        )


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Delete a chat session"""
    try:
        session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        db.delete(session)
        db.commit()
        
        logger.info("Chat session deleted", session_id=session_id)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete chat session", error=str(e), session_id=session_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete chat session"
        )


@router.get("/workflows/{workflow_id}/sessions", response_model=List[ChatSessionResponse])
async def get_workflow_chat_sessions(
    workflow_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all chat sessions for a specific workflow"""
    try:
        # Verify workflow exists
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )
        
        sessions = db.query(ChatSession).filter(
            ChatSession.workflow_id == workflow_id
        ).order_by(ChatSession.created_at.desc()).offset(skip).limit(limit).all()
        
        return sessions
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get workflow chat sessions", error=str(e), workflow_id=workflow_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get workflow chat sessions"
        )


@router.post("/test")
async def test_workflow(
    workflow_data: dict,
    query: str,
    document_id: int = None,
    db: Session = Depends(get_db)
):
    """Test a workflow without saving the session"""
    try:
        # Validate workflow data
        if "nodes" not in workflow_data or "edges" not in workflow_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid workflow data: missing nodes or edges"
            )
        
        # Verify document exists if specified
        if document_id:
            document = db.query(Document).filter(Document.id == document_id).first()
            if not document:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Document not found"
                )
        
        # Execute workflow
        workflow_engine = WorkflowEngine()
        execution_result = await workflow_engine.execute_workflow(
            workflow_data,
            query,
            document_id
        )
        
        return {
            "success": execution_result["success"],
            "response": execution_result.get("response"),
            "error": execution_result.get("error"),
            "execution_time": execution_result.get("execution_time"),
            "logs": execution_result.get("logs", [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Workflow test failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to test workflow"
        )


@router.post("/send")
async def send_message(
    message_data: dict,
    db: Session = Depends(get_db)
):
    """Send a message to a workflow and get response"""
    try:
        message = message_data.get("message")
        workflow_id = message_data.get("workflowId")
        session_id = message_data.get("sessionId")
        
        if not message or not workflow_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message and workflowId are required"
            )
        
        # Get workflow
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )
        
        # Execute workflow
        workflow_engine = WorkflowEngine()
        execution_result = await workflow_engine.execute_workflow(
            query=message,
            nodes=workflow.nodes,
            edges=workflow.edges,
            db=db
        )
        
        # Create or update session
        if session_id:
            chat_session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
            if chat_session:
                chat_session.user_query = message
                chat_session.system_response = execution_result.get("response", "")
                chat_session.context_used = execution_result.get("context")
                chat_session.execution_logs = execution_result.get("logs")
                db.commit()
        else:
            session_id = str(uuid.uuid4())
            chat_session = ChatSession(
                session_id=session_id,
                workflow_id=workflow_id,
                user_query=message,
                system_response=execution_result.get("response", ""),
                context_used=execution_result.get("context"),
                execution_logs=execution_result.get("logs")
            )
            db.add(chat_session)
            db.commit()
        
        return {
            "sessionId": session_id,
            "response": execution_result.get("response", ""),
            "context": execution_result.get("context"),
            "logs": execution_result.get("logs"),
            "execution_time": execution_result.get("execution_time")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to send message", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message"
        ) 