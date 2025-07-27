import React, { useEffect, useState } from "react";
import { useStackData } from "../context/stackAiContext";
import {
  FileInput,
  Sparkles,
  BookOpen,
  FileOutput,
  FolderPen,
  AlignJustify,
} from "lucide-react";

export default function ComponentLibrary({
  onAddNode,
  workflowName,
  setWorkflowName,
}) {
  const [isEditing, setIsEditing] = useState(false);
  const { stackData, updateStack } = useStackData();

  const handleBlur = () => {
    if (!stackData.name.trim()) {
      updateStack({ ...stackData, name: "Untitled Workflow" });
    }
    setIsEditing(false);
  };
  const components = [
    {
      type: "userQuery",
      label: "User Query",
      icon: FileInput,
      color: "bg-blue-50 border-blue-200",
    },
    {
      type: "llmEngine",
      label: "LLM (OpenAI)",
      icon: Sparkles,
      color: "bg-green-50 border-green-200",
    },
    {
      type: "knowledgeBase",
      label: "Knowledge Base",
      icon: BookOpen,
      color: "bg-purple-50 border-purple-200",
    },
    {
      type: "outPut",
      label: "Output",
      icon: FileOutput,
      color: "bg-orange-50 border-orange-200",
    },
  ];

  return (
    <div className="w-64 bg-white border-r border-gray-200 p-4">
      <div className="relative w-full max-w-xs bg-gray-100 rounded-sm px-1 mb-4 mt-3">
        {isEditing ? (
          <input
            type="text"
            value={stackData.name}
            onChange={(e) =>
              updateStack({ ...stackData, name: e.target.value })
            }
            onBlur={handleBlur}
            autoFocus
            className="text-lg font-semibold bg-transparent border border-gray-300 focus:outline-none focus:ring-1 focus:ring-blue-400 px-2 py-1 rounded w-full pr-8"
          />
        ) : (
          <div className="flex items-center gap-2 text-lg font-semibold text-gray-800 bg-transparent px-2 py-2 rounded cursor-pointer">
            <span className="truncate text-sm">{stackData.name}</span>
            <FolderPen
              className="w-4 h-4 text-gray-500 ml-auto absolute right-3 top-1/2 transform -translate-y-1/2 cursor-pointer"
              onClick={() => setIsEditing(true)}
            />
          </div>
        )}
      </div>
      <h3 className="font-semibold text-gray-800 mb-4 text-xs">Components</h3>
      <div className="space-y-2">
        {components.map((component) => {
          const IconComponent = component.icon;
          return (
            <div
              key={component.type}
              className={`p-3 rounded-lg border-2 ${component.color} cursor-move hover:shadow-md transition-shadow`}
              draggable
              onDragStart={(event) => {
                event.dataTransfer.setData(
                  "application/reactflow",
                  component.type
                );
                event.dataTransfer.effectAllowed = "move";
              }}
            >
              <div className="flex items-center gap-2">
                <IconComponent className="w-4 h-4" />
                <span className="text-sm font-medium">{component.label}</span>
                <AlignJustify className="w-4 h-4 text-gray-500 ml-auto" />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
