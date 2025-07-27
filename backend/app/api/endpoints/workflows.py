from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Workflow
from app.schemas import WorkflowCreate, WorkflowUpdate, WorkflowResponse
from app.services.workflow_engine import WorkflowEngine
import structlog

logger = structlog.get_logger()
router = APIRouter()


@router.post("/", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    workflow: WorkflowCreate,
    db: Session = Depends(get_db)
):
    """Create a new workflow"""
    try:
        db_workflow = Workflow(
            name=workflow.name,
            description=workflow.description,
            nodes=workflow.nodes,
            edges=workflow.edges
        )
        db.add(db_workflow)
        db.commit()
        db.refresh(db_workflow)
        
        logger.info("Workflow created", workflow_id=db_workflow.id, name=workflow.name)
        return db_workflow
        
    except Exception as e:
        logger.error("Failed to create workflow", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create workflow"
        )


@router.get("/", response_model=List[WorkflowResponse])
async def get_workflows(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all workflows"""
    try:
        workflows = db.query(Workflow).offset(skip).limit(limit).all()
        return workflows
        
    except Exception as e:
        logger.error("Failed to get workflows", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get workflows"
        )


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific workflow"""
    try:
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )
        return workflow
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get workflow", error=str(e), workflow_id=workflow_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get workflow"
        )


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: int,
    workflow_update: WorkflowUpdate,
    db: Session = Depends(get_db)
):
    """Update a workflow"""
    try:
        db_workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not db_workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )
        
        # Update fields
        update_data = workflow_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_workflow, field, value)
        
        db.commit()
        db.refresh(db_workflow)
        
        logger.info("Workflow updated", workflow_id=workflow_id)
        return db_workflow
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update workflow", error=str(e), workflow_id=workflow_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update workflow"
        )


@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workflow(
    workflow_id: int,
    db: Session = Depends(get_db)
):
    """Delete a workflow"""
    try:
        db_workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not db_workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )
        
        db.delete(db_workflow)
        db.commit()
        
        logger.info("Workflow deleted", workflow_id=workflow_id)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete workflow", error=str(e), workflow_id=workflow_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete workflow"
        )


@router.post("/{workflow_id}/validate")
async def validate_workflow(
    workflow_id: int,
    db: Session = Depends(get_db)
):
    """Validate a workflow structure"""
    try:
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )
        
        workflow_engine = WorkflowEngine()
        validation_result = workflow_engine._validate_workflow(
            workflow.nodes, workflow.edges
        )
        
        return {
            "workflow_id": workflow_id,
            "valid": validation_result["valid"],
            "error": validation_result.get("error")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to validate workflow", error=str(e), workflow_id=workflow_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate workflow"
        )


@router.post("/execute")
async def execute_workflow(
    workflow_data: dict,
    db: Session = Depends(get_db)
):
    """Execute a workflow with a query"""
    try:
        workflow_id = workflow_data.get("workflowId")
        query = workflow_data.get("query")
        nodes = workflow_data.get("nodes", [])
        edges = workflow_data.get("edges", [])
        
        if not query:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query is required"
            )
        
        workflow_engine = WorkflowEngine()
        result = await workflow_engine.execute_workflow(
            query=query,
            nodes=nodes,
            edges=edges,
            db=db
        )
        
        return {
            "workflow_id": workflow_id,
            "query": query,
            "response": result.get("response"),
            "context": result.get("context"),
            "logs": result.get("logs"),
            "execution_time": result.get("execution_time")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to execute workflow", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to execute workflow"
        ) 