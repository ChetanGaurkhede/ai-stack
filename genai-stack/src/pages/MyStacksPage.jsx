import React, { useState, useCallback, useRef, useEffect } from "react";
import ReactFlow, {
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  ConnectionLineType,
  Panel,
} from "reactflow";
import "reactflow/dist/style.css";
import {
  Play,
  MessageCircle,
  Plus,
  SquareDashedMousePointer,
} from "lucide-react";
import ComponentLibrary from "../components/ComponentLibrary";
import ChatInterface from "../components/chatbox/ChatInterface";
import UserQueryNode from "../components/stack-models/UserQuery";
import LLMEngineNode from "../components/stack-models/LLMEngine";
import KnowledgeBaseNode from "../components/stack-models/KnowledgeBase";
import OutputNode from "../components/stack-models/Output";
import { useStackData } from "../context/stackAiContext";
import { useLocation } from "react-router-dom";
import axios from "axios";
import toast from "react-hot-toast";

// Node types
const nodeTypes = {
  userQuery: UserQueryNode,
  knowledgeBase: KnowledgeBaseNode,
  llmEngine: LLMEngineNode,
  outPut: OutputNode,
};

// Main App Component
export default function WorkflowBuilders() {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedNode, setSelectedNode] = useState(null);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [workflowName, setWorkflowName] = useState("My Workflow");
  const reactFlowWrapper = useRef(null);
  const [reactFlowInstance, setReactFlowInstance] = useState(null);
  const [isDataLoaded, setIsDataLoaded] = useState(false);

  const location = useLocation();

  const { stackData, updateStack } = useStackData();
  const [allStack, setAllStacks] = useState([]);
  const [urlId, setUrlId] = useState("");
  const [isExistingWorkflow, setIsExistingWorkflow] = useState(false);

  useEffect(() => {
    // Reset data loaded flag when pathname changes
    setIsDataLoaded(false);

    const fetchData = async () => {
      // Prevent multiple loads
      if (isDataLoaded) return;

      try {
        const response = await axios.get(
          "http://localhost:8000/api/v1/workflows/"
        );
        const data = response.data;
        setAllStacks(data);

        // Get builderId from URL
        const path = location.pathname;
        const segments = path.split("/");
        const isBuilderRoute = segments[1] === "builder";
        const builderId = isBuilderRoute ? segments[2] : null;
        setUrlId(builderId);

        if (builderId) {
          const matched = data.find(
            (stack) => String(stack.id) === String(builderId)
          );
          if (matched) {
            setIsExistingWorkflow(true); // 🔧 This is an existing workflow
            updateStack(matched);

            // 🔧 FIX: Properly reconstruct nodes with all required properties
            const reconstructedNodes = matched.nodes.map((node) => ({
              id: node.id,
              type: node.type,
              position: {
                x: parseFloat(node.position.x) || 0,
                y: parseFloat(node.position.y) || 0,
              },
              data: node.data || { label: node.type },
              dragging: false,
              selected: false,
            }));

            // 🔧 FIX: Properly reconstruct edges with all required properties
            const reconstructedEdges = matched.edges.map((edge) => ({
              id: edge.id,
              source: edge.source,
              target: edge.target,
              sourceHandle: edge.sourceHandle || null,
              targetHandle: edge.targetHandle || null,
              type: edge.type || "default",
            }));

            console.log("🔄 Loading existing workflow:", matched.name);
            console.log("🔄 Loading nodes:", reconstructedNodes);
            console.log("🔄 Loading edges:", reconstructedEdges);

            setNodes(reconstructedNodes);
            setEdges(reconstructedEdges);
            setWorkflowName(matched.name || "My Workflow");
            setIsDataLoaded(true);
          } else {
            console.warn("⚠️ Stack not found for ID:", builderId);
            setIsExistingWorkflow(false); // New workflow
            setIsDataLoaded(true);
          }
        } else {
          setIsExistingWorkflow(false); // New workflow
          setIsDataLoaded(true);
        }
      } catch (error) {
        console.error("❌ Failed to fetch workflows:", error);
        setIsExistingWorkflow(false);
        setIsDataLoaded(true);
      }
    };

    fetchData();
  }, [location.pathname]);

  const onInit = (rfi) => {
    setReactFlowInstance(rfi);
  };

  const onAddNode = useCallback(
    (type) => {
      const newNode = {
        id: `${type}-${Date.now()}`,
        type,
        position: { x: Math.random() * 400, y: Math.random() * 400 },
        data: { label: type },
      };
      setNodes((nds) => nds.concat(newNode));
    },
    [setNodes]
  );

  const onUpdateNode = useCallback(
    (nodeId, newData) => {
      setNodes((nds) =>
        nds.map((node) =>
          node.id === nodeId
            ? { ...node, data: { ...node.data, ...newData } }
            : node
        )
      );
    },
    [setNodes]
  );

  const onNodeClick = useCallback((event, node) => {
    setSelectedNode(node);
  }, []);

  const validateWorkflow = () => {
    // Basic validation logic
    const hasUserQuery = nodes.some((node) => node.type === "userQuery");
    const hasOutput = nodes.some((node) => node.type === "outPut");

    if (!hasUserQuery || !hasOutput) {
      toast.error(
        "Workflow must have at least a User Query and Output component"
      );
      return false;
    }

    if (edges.length === 0) {
      toast.success("Components must be connected");
      return false;
    }

    return true;
  };

  const buildStack = async () => {
    if (!validateWorkflow()) return;

    const payload = {
      name: stackData.name || workflowName || "Untitled Workflow",
      description: stackData.description || "",
      nodes: nodes.map((node) => ({
        id: node.id,
        type: node.type,
        position: node.position,
        data: node.data,
      })),
      edges: edges.map((edge) => ({
        id: edge.id,
        source: edge.source,
        target: edge.target,
        sourceHandle: edge.sourceHandle,
        targetHandle: edge.targetHandle,
        type: edge.type,
      })),
      is_active: true,
    };

    try {
      let response;

      if (isExistingWorkflow && urlId) {
        // 🔧 UPDATE existing workflow using PUT
        console.log("🔄 Updating existing workflow with ID:", urlId);
        response = await axios.put(
          `http://localhost:8000/api/v1/workflows/${urlId}`,
          payload
        );
        console.log("✅ Workflow updated successfully:", response.data);
        toast.success("Workflow updated successfully!");
      } else {
        // 🔧 CREATE new workflow using POST
        console.log("🔄 Creating new workflow");
        response = await axios.post(
          "http://localhost:8000/api/v1/workflows/",
          payload
        );
        console.log("✅ New workflow created:", response.data);
        toast.success("New workflow created successfully!");

        // Update the URL and state to reflect the new workflow
        const newWorkflowId = response.data.id;
        setUrlId(newWorkflowId);
        setIsExistingWorkflow(true);

        // Optionally update the URL without causing a page reload
        window.history.replaceState(null, null, `/builder/${newWorkflowId}`);
      }
    } catch (error) {
      console.error("❌ Failed to save workflow:", error);

      if (error.response) {
        const errorMsg =
          error.response.data?.detail || error.response.statusText;
        console.error("Response data:", error.response.data);
        toast.error(`Failed to save workflow: ${errorMsg}`);
      } else if (error.request) {
        console.error("No response received:", error.request);
        toast.error("Failed to save workflow: No response from server");
      } else {
        console.error("Error:", error.message);
        toast.error(`Failed to save workflow: ${error.message}`);
      }
    }
  };

  const clearWorkflow = () => {
    setNodes([]);
    setEdges([]);
    setSelectedNode(null);
  };

  const onDragOver = useCallback((event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
  }, []);

  const onDrop = useCallback(
    (event) => {
      event.preventDefault();

      const type = event.dataTransfer.getData("application/reactflow");
      if (!type) return;

      const bounds = reactFlowWrapper.current.getBoundingClientRect();
      const position = reactFlowInstance.project({
        x: event.clientX - bounds.left,
        y: event.clientY - bounds.top,
      });

      const newNode = {
        id: `${type}-${Date.now()}`,
        type,
        position,
        data: { label: `${type}` },
      };

      setNodes((nds) => nds.concat(newNode));
    },
    [reactFlowInstance, setNodes]
  );

  const onConnect = useCallback(
    (params) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  // 🔧 FIX: Separate effect to handle fitting view when nodes are loaded
  useEffect(() => {
    if (reactFlowInstance && nodes.length > 0 && isDataLoaded) {
      // Small delay to ensure nodes are rendered, then fit view once
      const timeoutId = setTimeout(() => {
        reactFlowInstance.fitView({ padding: 0.1 });
      }, 100);

      return () => clearTimeout(timeoutId);
    }
  }, [reactFlowInstance, isDataLoaded]);

  return (
    <div className="flex h-screen bg-gray-50">
      <div className="flex flex-1 mt-16">
        {/* Component Library */}
        <ComponentLibrary
          onAddNode={onAddNode}
          workflowName={workflowName}
          setWorkflowName={setWorkflowName}
        />

        {/* Main Workspace */}
        <div className="flex-1 flex flex-col">
          {/* Status Indicator */}
          {/* <div className="px-4 py-2 bg-gray-100 border-b">
            <span className="text-sm text-gray-600">
              {isExistingWorkflow ? (
                <span className="flex items-center gap-2">
                  <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                  Editing: {workflowName} (ID: {urlId})
                </span>
              ) : (
                <span className="flex items-center gap-2">
                  <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                  New Workflow
                </span>
              )}
            </span>
          </div> */}

          {/* ReactFlow Canvas */}
          <div className="flex-1" ref={reactFlowWrapper}>
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onDrop={onDrop}
              onDragOver={onDragOver}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onConnect={onConnect}
              onInit={onInit}
              onNodeClick={onNodeClick}
              nodeTypes={nodeTypes}
              connectionLineType={ConnectionLineType.SmoothStep}
              fitView
            >
              <Controls
                showZoom={true}
                showFitView={true}
                showInteractive={true}
                style={{
                  position: "absolute",
                  bottom: 10,
                  left: "50%",
                  transform: "translateX(-50%)",
                  display: "flex",
                  flexDirection: "row",
                  gap: "8px",
                  background: "white",
                  padding: "2px 10px",
                  borderRadius: "8px",
                  boxShadow: "0 2px 6px rgba(0, 0, 0, 0.1)",
                }}
              />

              <Background variant="dots" gap={12} size={1} />

              {nodes.length === 0 && (
                <Panel position="center">
                  <div className="text-center p-4 rounded-lg mt-30">
                    <div className="mb-4">
                      <div className="w-fit bg-gray-200 rounded-full flex items-center justify-center mx-auto mb-4 p-3 shadow-2xl">
                        <SquareDashedMousePointer className="w-5 h-5 text-green-400" />
                      </div>
                      <h3 className="text-md font-medium text-gray-800 mb-2">
                        Drag & drop to get started
                      </h3>
                    </div>
                  </div>
                </Panel>
              )}
            </ReactFlow>
          </div>
        </div>
      </div>

      {/* Chat Modal */}
      <ChatInterface
        isOpen={isChatOpen}
        onClose={() => setIsChatOpen(false)}
        workflowId="current-workflow"
      />

      <div className="flex flex-col items-center justify-center fixed bottom-10 right-5 p-4 space-y-4 z-50">
        {/* Build Stack Button with Tooltip */}
        <div className="relative">
          <div
            className="absolute right-14 top-1/2 transform -translate-y-1/2 
        bg-white text-gray-900 text-sm rounded-md px-3 py-1 shadow 
        whitespace-nowrap min-w-[110px] text-center
        opacity-0 pointer-events-none transition-opacity duration-200
        group-hover:opacity-100"
          >
            {isExistingWorkflow ? "Update Workflow" : "Create Workflow"}
          </div>
          <div
            onClick={buildStack}
            className="group rounded-full bg-green-400 p-3 shadow-md flex items-center gap-2 hover:bg-green-800 
        transition duration-200 ease-in-out transform hover:scale-110 cursor-pointer"
          >
            <Play className="w-4 h-4 text-white" />
          </div>
        </div>

        {/* Chat with Stack Button with Tooltip */}
        <div className="relative">
          <div
            className="absolute right-14 top-1/2 transform -translate-y-1/2 
        bg-white text-gray-900 text-sm rounded-md px-3 py-1 shadow 
        whitespace-nowrap min-w-[120px] text-center
        opacity-0 pointer-events-none transition-opacity duration-200
        group-hover:opacity-100"
          >
            Chat with Stack
          </div>
          <div
            onClick={() => setIsChatOpen(true)}
            className="group rounded-full bg-blue-400 p-3 shadow-md flex items-center gap-2 hover:bg-blue-800 
        transition duration-200 ease-in-out transform hover:scale-110 cursor-pointer"
          >
            <MessageCircle className="w-4 h-4 text-white" />
          </div>
        </div>
      </div>
    </div>
  );
}
