import React, { useState, useEffect } from "react";
import { X } from "lucide-react";
import { useStackData } from "../context/stackAiContext";
import { useNavigate } from "react-router-dom";
import axios from "axios";

export default function CreateStack({ isOpen, onClose, onCreate }) {
  const [isValid, setIsValid] = useState(false);

  const { stackData, updateStack, stacks, setStacks } = useStackData();
  const [stackName, setStackName] = useState("");
  const [stackDescription, setStackDescription] = useState("");
  const [path, setPath] = useState();
  const navigate = useNavigate();

  const handleSubmit = async () => {
    if (!stackName.trim()) return;

    const mockStackId = null;
    const updatedStack = {
      ...stackData,
      stackId: mockStackId,
      name: stackName,
      description: stackDescription,
    };

    try {
      const res = await axios.post("http://localhost:8000/api/v1/workflows/", {
        name: stackName,
        description: stackDescription,
        nodes: [],
        edges: [],
      });

      const newWorkflowId = res.data.id;

      // Update local state
      setStacks((prevStacks) => [...prevStacks, updatedStack]);

      // Optional: Call onCreate for parent handling
      onCreate({ title: stackName, description: stackDescription });

      // Navigate to new workflow page using actual ID
      navigate(`/builder/${newWorkflowId}`);

      console.log("✅ New stack created:", updatedStack);
      onClose();
    } catch (error) {
      console.error("❌ Failed to create workflow via API:", error);
    }
  };

  useEffect(() => {
    if (stackName.length > 0 && stackDescription.length > 0) {
      setIsValid(true);
    } else {
      setIsValid(false);
    }
  }, [stackName, stackDescription]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-[#00000038] bg-opacity-40 backdrop-blur-sm flex justify-center items-center z-50 ">
      <div className="bg-white w-[400px] rounded-lg shadow-lg p-6 relative">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-black"
        >
          <X size={18} />
        </button>

        <h2 className="text-md font-semibold mb-4">Create New Stack</h2>

        {/* Name Input */}
        <div className="mb-4">
          <label className="text-sm font-medium text-gray-700 block mb-1">
            Name
          </label>
          <input
            type="text"
            value={stackName}
            onChange={(e) => setStackName(e.target.value)}
            className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
            placeholder="Enter stack name"
          />
        </div>

        {/* Description */}
        <div className="mb-6">
          <label className="text-sm font-medium text-gray-700 block mb-1">
            Description
          </label>
          <textarea
            value={stackDescription}
            onChange={(e) => setStackDescription(e.target.value)}
            className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
            rows={4}
            placeholder="Enter description"
          />
        </div>

        {/* Action Buttons */}
        <div className="flex justify-end gap-4">
          <button
            onClick={onClose}
            className="text-sm px-4 py-2 rounded border border-gray-300 text-gray-700"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={!stackName.trim() || !isValid}
            className={`text-sm px-4 py-2 rounded ${
              stackName.trim() && isValid
                ? "bg-green-600 text-white hover:bg-green-700"
                : "bg-gray-200 text-gray-400 cursor-not-allowed"
            }`}
          >
            Create
          </button>
        </div>
      </div>
    </div>
  );
}
