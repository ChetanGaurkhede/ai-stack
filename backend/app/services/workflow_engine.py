import asyncio
import time
import uuid
from typing import Dict, Any, List, Optional
from app.services.llm_service import LLMService
from app.services.knowledge_base_service import KnowledgeBaseService
from app.services.web_search_service import WebSearchService
import structlog

logger = structlog.get_logger()


class WorkflowEngine:
    def __init__(self):
        self.llm_service = LLMService()
        self.kb_service = KnowledgeBaseService()
        self.web_search_service = WebSearchService()
    
    async def execute_workflow(
        self,
        workflow_data: Dict[str, Any],
        query: str,
        document_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute a workflow based on the provided nodes and edges
        """
        start_time = time.time()
        execution_logs = []
        
        try:
            # Parse workflow
            nodes = workflow_data.get("nodes", [])
            edges = workflow_data.get("edges", [])
            
            # Validate workflow
            validation_result = self._validate_workflow(nodes, edges)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": validation_result["error"],
                    "execution_time": time.time() - start_time,
                    "logs": execution_logs
                }
            
            # Build execution graph
            execution_graph = self._build_execution_graph(nodes, edges)
            
            # Execute workflow
            result = await self._execute_graph(
                execution_graph, query, document_id, execution_logs
            )
            
            execution_time = time.time() - start_time
            
            return {
                "success": True,
                "response": result["response"],
                "context_used": result.get("context_used"),
                "execution_time": execution_time,
                "logs": execution_logs
            }
            
        except Exception as e:
            logger.error("Workflow execution failed", error=str(e))
            execution_time = time.time() - start_time
            
            return {
                "success": False,
                "error": str(e),
                "execution_time": execution_time,
                "logs": execution_logs
            }
    
    def _validate_workflow(self, nodes: List[Dict], edges: List[Dict]) -> Dict[str, Any]:
        """Validate workflow structure"""
        if not nodes:
            return {"valid": False, "error": "No nodes found in workflow"}
        
        if not edges:
            return {"valid": False, "error": "No edges found in workflow"}
        
        # Check for required node types
        node_types = [node.get("type") for node in nodes]
        required_types = ["userQuery", "output"]
        
        for required_type in required_types:
            if required_type not in node_types:
                return {
                    "valid": False,
                    "error": f"Required node type '{required_type}' not found"
                }
        
        # Check for cycles (simple check)
        if len(edges) >= len(nodes):
            return {"valid": False, "error": "Workflow may contain cycles"}
        
        return {"valid": True}
    
    def _build_execution_graph(self, nodes: List[Dict], edges: List[Dict]) -> Dict[str, Any]:
        """Build execution graph from nodes and edges"""
        graph = {}
        
        # Initialize graph
        for node in nodes:
            node_id = node["id"]
            graph[node_id] = {
                "node": node,
                "dependencies": [],
                "dependents": []
            }
        
        # Build connections
        for edge in edges:
            source_id = edge["source"]
            target_id = edge["target"]
            
            if source_id in graph and target_id in graph:
                graph[source_id]["dependents"].append(target_id)
                graph[target_id]["dependencies"].append(source_id)
        
        return graph
    
    async def _execute_graph(
        self,
        graph: Dict[str, Any],
        query: str,
        document_id: Optional[int],
        logs: List[Dict]
    ) -> Dict[str, Any]:
        """Execute the workflow graph"""
        # Find execution order (topological sort)
        execution_order = self._topological_sort(graph)
        
        # Store intermediate results
        node_results = {}
        
        # Execute nodes in order
        for node_id in execution_order:
            node_data = graph[node_id]
            node = node_data["node"]
            
            log_entry = {
                "timestamp": time.time(),
                "node_id": node_id,
                "node_type": node.get("type"),
                "action": "executing"
            }
            logs.append(log_entry)
            
            try:
                result = await self._execute_node(
                    node, query, document_id, node_results
                )
                node_results[node_id] = result
                
                log_entry["action"] = "completed"
                log_entry["result"] = "success"
                
            except Exception as e:
                log_entry["action"] = "failed"
                log_entry["result"] = "error"
                log_entry["error"] = str(e)
                raise
        
        # Find output node result
        output_node_id = None
        for node_id, node_data in graph.items():
            if node_data["node"].get("type") == "output":
                output_node_id = node_id
                break
        
        if output_node_id and output_node_id in node_results:
            return node_results[output_node_id]
        else:
            raise ValueError("No output node found or output node failed")
    
    def _topological_sort(self, graph: Dict[str, Any]) -> List[str]:
        """Perform topological sort to determine execution order"""
        in_degree = {}
        queue = []
        result = []
        
        # Initialize in-degree
        for node_id in graph:
            in_degree[node_id] = len(graph[node_id]["dependencies"])
            if in_degree[node_id] == 0:
                queue.append(node_id)
        
        # Process queue
        while queue:
            node_id = queue.pop(0)
            result.append(node_id)
            
            for dependent_id in graph[node_id]["dependents"]:
                in_degree[dependent_id] -= 1
                if in_degree[dependent_id] == 0:
                    queue.append(dependent_id)
        
        if len(result) != len(graph):
            raise ValueError("Workflow contains cycles")
        
        return result
    
    async def _execute_node(
        self,
        node: Dict[str, Any],
        query: str,
        document_id: Optional[int],
        node_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a single node"""
        node_type = node.get("type")
        node_data = node.get("data", {})
        
        if node_type == "userQuery":
            return await self._execute_user_query_node(query, node_data)
        
        elif node_type == "knowledgeBase":
            return await self._execute_knowledge_base_node(
                query, document_id, node_data, node_results
            )
        
        elif node_type == "llmEngine":
            return await self._execute_llm_engine_node(
                query, node_data, node_results
            )
        
        elif node_type == "output":
            return await self._execute_output_node(node_data, node_results)
        
        else:
            raise ValueError(f"Unknown node type: {node_type}")
    
    async def _execute_user_query_node(self, query: str, node_data: Dict) -> Dict[str, Any]:
        """Execute user query node"""
        return {
            "type": "userQuery",
            "query": query,
            "response": query  # Pass through the query
        }
    
    async def _execute_knowledge_base_node(
        self,
        query: str,
        document_id: Optional[int],
        node_data: Dict,
        node_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute knowledge base node"""
        try:
            # Get configuration
            similarity_threshold = node_data.get("similarityThreshold", 0.7)
            top_k = node_data.get("topK", 5)
            
            # Search for similar content
            similar_chunks = await self.kb_service.search_similar(
                query, document_id, top_k, similarity_threshold
            )
            
            # Format context
            context_parts = []
            for chunk in similar_chunks:
                context_parts.append(f"Document chunk (similarity: {chunk['similarity']:.2f}):\n{chunk['text']}")
            
            context = "\n\n".join(context_parts) if context_parts else ""
            
            return {
                "type": "knowledgeBase",
                "query": query,
                "context": context,
                "chunks_found": len(similar_chunks),
                "similarity_threshold": similarity_threshold
            }
            
        except Exception as e:
            logger.error("Knowledge base node execution failed", error=str(e))
            return {
                "type": "knowledgeBase",
                "query": query,
                "context": "",
                "chunks_found": 0,
                "error": str(e)
            }
    
    async def _execute_llm_engine_node(
        self,
        query: str,
        node_data: Dict,
        node_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute LLM engine node"""
        try:
            # Get configuration
            provider = node_data.get("provider", "openai")
            model = node_data.get("model", "")
            temperature = node_data.get("temperature", 0.7)
            max_tokens = node_data.get("maxTokens", 1000)
            custom_prompt = node_data.get("customPrompt", "")
            use_web_search = node_data.get("useWebSearch", False)
            
            # Build context from previous nodes
            context_parts = []
            
            # Add knowledge base context if available
            for node_id, result in node_results.items():
                if result.get("type") == "knowledgeBase" and result.get("context"):
                    context_parts.append(f"Document Context:\n{result['context']}")
            
            # Add web search context if enabled
            if use_web_search:
                web_context = await self.web_search_service.get_relevant_context(query)
                if web_context:
                    context_parts.append(f"Web Search Results:\n{web_context}")
            
            context = "\n\n".join(context_parts) if context_parts else None
            
            # Generate response
            llm_result = await self.llm_service.generate_response(
                query=query,
                context=context,
                provider=provider,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                custom_prompt=custom_prompt
            )
            
            return {
                "type": "llmEngine",
                "query": query,
                "response": llm_result["response"],
                "model": llm_result["model"],
                "provider": llm_result["provider"],
                "context_used": context is not None,
                "web_search_used": use_web_search
            }
            
        except Exception as e:
            logger.error("LLM engine node execution failed", error=str(e))
            return {
                "type": "llmEngine",
                "query": query,
                "response": f"Error generating response: {str(e)}",
                "error": str(e)
            }
    
    async def _execute_output_node(
        self,
        node_data: Dict,
        node_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute output node"""
        # Find the LLM engine result
        llm_result = None
        for result in node_results.values():
            if result.get("type") == "llmEngine":
                llm_result = result
                break
        
        if llm_result:
            return {
                "type": "output",
                "response": llm_result["response"],
                "context_used": llm_result.get("context_used", False),
                "model": llm_result.get("model"),
                "provider": llm_result.get("provider")
            }
        else:
            return {
                "type": "output",
                "response": "No LLM response available",
                "error": "LLM engine not found in workflow"
            } 