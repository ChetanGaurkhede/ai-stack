from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# Workflow Schemas
class WorkflowBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class WorkflowCreate(WorkflowBase):
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]


class WorkflowUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    nodes: Optional[List[Dict[str, Any]]] = None
    edges: Optional[List[Dict[str, Any]]] = None
    is_active: Optional[bool] = None


class WorkflowResponse(WorkflowBase):
    id: int
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Document Schemas
class DocumentBase(BaseModel):
    original_filename: str
    file_size: int
    file_type: str


class DocumentCreate(DocumentBase):
    filename: str
    file_path: str


class DocumentResponse(DocumentBase):
    id: int
    filename: str
    file_path: str
    content: Optional[str] = None
    embeddings_created: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Chat Schemas
class ChatRequest(BaseModel):
    workflow_id: int
    query: str = Field(..., min_length=1)
    document_id: Optional[int] = None


class ChatResponse(BaseModel):
    session_id: str
    response: str
    context_used: Optional[Dict[str, Any]] = None
    execution_logs: Optional[Dict[str, Any]] = None
    created_at: datetime


class ChatSessionResponse(BaseModel):
    id: int
    session_id: str
    workflow_id: int
    document_id: Optional[int] = None
    user_query: str
    system_response: str
    context_used: Optional[Dict[str, Any]] = None
    execution_logs: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Component Configuration Schemas
class LLMConfig(BaseModel):
    provider: str = Field(..., pattern="^(openai|gemini)$")
    model: str
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(1000, ge=1, le=4000)
    custom_prompt: Optional[str] = None


class KnowledgeBaseConfig(BaseModel):
    embedding_provider: str = Field(..., pattern="^(openai|gemini)$")
    chunk_size: int = Field(1000, ge=100, le=4000)
    chunk_overlap: int = Field(200, ge=0, le=1000)
    similarity_threshold: float = Field(0.7, ge=0.0, le=1.0)


class WebSearchConfig(BaseModel):
    provider: str = Field(..., pattern="^(serpapi|brave)$")
    max_results: int = Field(5, ge=1, le=20)


# Workflow Execution Schemas
class WorkflowExecutionRequest(BaseModel):
    workflow_id: int
    query: str
    document_id: Optional[int] = None


class WorkflowExecutionResponse(BaseModel):
    success: bool
    response: str
    execution_time: float
    logs: List[Dict[str, Any]]
    context_used: Optional[Dict[str, Any]] = None


# Health Check Schema
class HealthCheck(BaseModel):
    status: str
    timestamp: datetime
    version: str
    database: str
    chromadb: str
    redis: str 