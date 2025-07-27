import React from "react";
import { Handle, Position } from "reactflow";
import { FileInput, Settings } from "lucide-react";
import { useStackData } from "../../context/stackAiContext";


export default function OutputNode ({ data, selected }) {
  const { stackData, updateStack } = useStackData();
  const outputText =
    data.outputText || "Output will be generated based on query";

  return (
    <div
      className={`min-w-[260px] max-w-[300px] rounded-lg shadow-lg border relative ${
        selected ? "border-orange-500" : "border-gray-200"
      } bg-white`}
    >
      <div className="p-4">
        {/* Header */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <FileInput className="w-4 h-4 text-gray-600" />
            <h3 className="text-sm font-semibold text-gray-800">Output</h3>
          </div>
          <Settings className="w-4 h-4 text-gray-600 cursor-pointer" />
        </div>

        {/* Description */}
        <div className="text-xs bg-blue-100 text-gray-800 px-3 py-2 rounded mb-3">
          Output of the result nodes as text
        </div>

        {/* Output Label */}
        <label className="block text-xs font-semibold text-gray-700 mb-1">
          Output Text
        </label>

        {/* Output Box */}
        <textarea
          onChange={(e) =>
            updateStack({ ...stackData, output_text: e.target.value })
          }
          value={stackData.output_text }
          placeholder="Outeput will be generated based on query"
          rows={5}
          className="text-[11px] w-full px-3 py-2 bg-gray-100 text-gray-500 border border-gray-300 rounded-md min-h-[50px] focus:outline-none focus:ring-0 resize-none"
        >
          {outputText}
        </textarea>
        <p className="text-[11px] text-gray-800">Output</p>

        {/* Footer (optional) */}
        <Handle
          type="target"
          position={Position.Left}
          id="query"
          className="w-2 h-2 bg-purple-500 z-10"
          style={{
            position: "absolute",
            right: " -20px",
            top: "175px",
            backgroundColor: "green",
          }}
        />
      </div>
    </div>
  );
};
