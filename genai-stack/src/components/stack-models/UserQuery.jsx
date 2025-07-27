import React from "react";
import { Handle, Position } from "reactflow";
import { FileInput, Settings } from "lucide-react";
import { useStackData } from "../../context/stackAiContext";

export default function UserQueryNode({ selected }) {
  const { stackData, updateStack } = useStackData();

  return (
    <div
      className={` shadow-lg rounded-lg bg-white border-1   ${
        selected ? "border-blue-500" : "border-gray-200"
      } min-w-[200px]`}
    >
      <div className="flex items-center gap-2 mb-2 justify-between w-full pt-4 px-4">
        <div className="flex items-center gap-2 mb-2">
          <FileInput className="w-4 h-4 text-gray-600" />
          <div className="font-medium text-sm">User Query</div>
        </div>
        <Settings className="w-4 h-4 text-gray-600" />
      </div>
      <div className="text-xs bg-[#d6effbad] px-4 py-2">
        Entry point for user queries
      </div>
      <div className="mt-2 px-4 pb-4 ">
        <label
          htmlFor="user-query-input"
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          User Query
        </label>
        <textarea
          id="user-query-input"
          placeholder="Enter placeholder text..."
          className="w-full px-2 py-1 text-xs border rounded focus:outline-none focus:ring-0 "
          defaultValue={stackData.user_query || ""}
          onChange={(e) =>
            updateStack({ ...stackData, user_query: e.target.value })
          }
          rows={4}
        />
        <p className="w-full text-right text-gray-800 text-[11px]">Query</p>

        <div className="absolute bottom-6 right-0 text-gray-500 cursor-pointer">
          {/* <span>Query</span> */}
          <Handle
            type="source"
            position={Position.Bottom}
            id="query"
            className="w-2 h-2 bg-blue-500 absolute bottom-10 right-10"
          />
        </div>
      </div>
    </div>
  );
}
