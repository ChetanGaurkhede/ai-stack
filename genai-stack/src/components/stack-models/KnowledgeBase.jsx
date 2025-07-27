import React, { useEffect, useState } from "react";
import { Handle, Position } from "reactflow";
import { FileInput, Settings, Upload, Eye, EyeOff } from "lucide-react";
import { useStackData } from "../../context/stackAiContext";

export default function KnowledgeBaseNode({ data, selected }) {
  const [showApiKey, setShowApiKey] = useState(false);
  const { stackData, updateStack } = useStackData();

  const handleApiKeyChange = (e) => {
    updateStack({ ...stackData, llm_api_key: e.target.value });
  };


  return (
    <div
      className={`shadow-lg rounded-lg bg-white border-2 relative ${
        selected ? "border-purple-500" : "border-gray-200"
      } min-w-[250px] max-w-[300px]`}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 pt-4">
        <div className="flex items-center gap-2">
          <FileInput className="w-4 h-4 text-gray-600" />
          <h3 className="font-medium text-sm">Knowledge Base</h3>
        </div>
        <Settings className="w-4 h-4 text-gray-600 cursor-pointer" />
      </div>

      {/* Subtitle */}
      <div className="text-[11px] bg-[#d6effbad] px-4 py-2 mt-2">
        Let LLM search info in your file
      </div>

      {/* Upload File */}
      <div className="px-4 pt-3">
        <p className="text-xs mb-1">File for Knowledge Base</p>

        {/* Upload Trigger Box */}
        <label
          htmlFor="image-upload"
          className="w-full block border border-dashed border-green-00 bg-green-50 text-green-600 rounded text-xs py-5 text-center cursor-pointer hover:bg-green-100"
        >
          {stackData.llm_file ? "" + stackData.llm_file_name : "Upload File"}
          <Upload className="inline-block ml-1 w-3 h-3" />
        </label>

        {/* Hidden File Input */}
        <input
          id="image-upload"
          type="file"
          accept="application/pdf"
          onChange={(e) => {
            const file = e.target.files[0];
            if (file) {
              const reader = new FileReader();
              reader.onloadend = () => {
                updateStack({
                  ...stackData,
                  llm_file: reader.result,
                  llm_file_name: file.name,
                }); 
              };
              reader.readAsDataURL(file);
            }
          }}
          className="hidden"
        />

        {/* Image Preview */}
        {/* {stackData.llm_file && (
          <div className="px-2 mt-2">
            <img
              src={stackData.llm_file}
              alt="Uploaded Preview"
              className="w-full h-auto rounded border"
            />
          </div>
        )} */}
      </div>

      {/* Embedding Model */}
      <div className="px-4 mt-4">
        <label className="text-xs mb-1 block">Embedding Model</label>
        <select
          className="w-full px-2 py-1 text-xs border rounded focus:outline-none focus:ring-0"
          defaultValue={stackData.llm_model || "text-embedding-3-large"}
          onChange={(e) =>
            updateStack({ ...stackData, llm_model: e.target.value })
          }
        >
          <option value="text-embedding-3-large">text-embedding-3-large</option>
          <option value="text-embedding-ada">text-embedding-ada</option>
        </select>
      </div>

      {/* API Key */}
      <div className="px-4 mt-3 relative">
        <label className="text-xs mb-1 block">API Key</label>
        <div className="relative">
          <input
            type={showApiKey ? "text" : "password"}
            value={stackData.llm_api_key || ""}
            onChange={(e) =>
              updateStack({ ...stackData, llm_api_key: e.target.value })
            }
            className="w-full px-2 py-1 text-xs border rounded pr-8"
          />

          <span
            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 cursor-pointer"
            onClick={() => setShowApiKey(!showApiKey)}
          >
            {showApiKey ? (
              <Eye className="w-3 h-3" />
            ) : (
              <EyeOff className="w-3 h-3" />
            )}
          </span>
        </div>
      </div>

      {/* Footer */}
      <div className=" text-[10px] px-4 pt-4 pb-2 text-gray-500">
        <p className="">Query</p>
        <p className="w-full text-right mt-3">Context</p>
      </div>
      <Handle
        type="source"
        position={Position.Right}
        id="query"
        className="w-2 h-2 bg-purple-500 z-10"
        style={{
          position: "absolute",
          right: " 3px",
          top: "337px",
          backgroundColor: "orange",
        }}
      />
      {/* Outgoing handle */}
      {/* <div className="absolute bottom-11 right-31 w-full h-4"> */}
      <Handle
        type="target"
        position={Position.Bottom}
        id="context"
        className="w-2 h-2 bg-purple-500"
        style={{
          position: "absolute",
          left: "5px",
          bottom: "40px",
          backgroundColor: "orange",
        }}
      />
      {/* </div> */}
    </div>
  );
}
