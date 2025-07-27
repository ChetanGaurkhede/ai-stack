import React, { useEffect, useState } from "react";
import { Handle, Position } from "reactflow";
import { Sparkles, Settings, Eye, EyeOff } from "lucide-react";
import { useStackData } from "../../context/stackAiContext";

export default function LLMEngineNode({ data, selected }) {
  const [showOpenAIKey, setShowOpenAIKey] = useState(false);
  const [showSerpKey, setShowSerpKey] = useState(false);
  const [webSearch, setWebSearch] = useState(true);

  const { stackData, updateStack } = useStackData();
  useEffect(() => {
    console.log(stackData);
  }, [stackData]);

  return (
    <div
      className={`px-4 py-3 shadow-lg rounded-lg bg-white border-1 ${
        selected ? "border-green-500" : "border-gray-200"
      } min-w-[260px] max-w-[300px]`}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-gray-600" />
          <div className="font-medium text-sm">LLM (OpenAI)</div>
        </div>
        <Settings className="w-4 h-4 text-gray-600 cursor-pointer" />
      </div>

      <div className="text-xs bg-[#d6effbad] px-4 py-2">
        Run a query with OpenAI LLM
      </div>

      {/* Model Selector */}
      <div className="mb-3 text-xs mt-2">
        <label className="block mb-1 text-gray-700">Model</label>
        <select
          value={stackData.ai_model}
          onChange={(e) =>
            updateStack({ ...stackData, ai_model: e.target.value })
          }
          className="w-full border rounded px-2 py-1 text-xs focus:outline-none focus:ring-0"
        >
          <option value="gpt-4o-mini">GPT 4o- Mini</option>
          <option value="gpt-4">GPT-4</option>
          <option value="gpt-3.5">GPT-3.5</option>
        </select>
      </div>

      {/* OpenAI API Key */}
      <div className="mb-3 text-xs relative">
        <label className="block mb-1 text-gray-700">API Key</label>
        <input
          type={showOpenAIKey ? "text" : "password"}
          value={stackData.llm_api_key || ""}
          onChange={(e) =>
            updateStack({ ...stackData, llm_api_key: e.target.value })
          }
          className="w-full border rounded px-2 py-1 pr-7 focus:outline-none focus:ring-0"
        />
        <span
          className="absolute top-7 right-2 cursor-pointer text-gray-500"
          onClick={() => setShowOpenAIKey((prev) => !prev)}
        >
          {showOpenAIKey ? <Eye size={14} /> : <EyeOff size={14} />}
        </span>
      </div>

      {/* Prompt Field */}
      <div className="mb-3 text-xs">
        <label className="block mb-1 text-gray-700">Prompt</label>
        <textarea
          rows={4}
          value={stackData.api_prompt || ""}
          onChange={(e) =>
            updateStack({ ...stackData, api_prompt: e.target.value })
          }
          className="w-full border rounded px-2 py-1 text-xs focus:outline-none focus:ring-0  "
          defaultValue={`You are a helpful PDF assistant. Use web search if the PDF lacks context
          CONTEXT: {context}
          User Query: {query}`}
        />
      </div>

      {/* Temperature */}
      <div className="mb-3 text-xs">
        <label className="block mb-1 text-gray-700">Temperature</label>
        <input
          type="number"
          min={0}
          max={1}
          step={0.01}
          value={stackData.temp ?? 0.75}
          className="w-full border rounded px-2 py-1 text-xs focus:outline-none focus:ring-0"
          onChange={(e) => {
            const value = parseFloat(e.target.value);
            if (!isNaN(value)) {
              const clampedValue = Math.min(1, Math.max(0, value));
              updateStack({ ...stackData, temp: clampedValue });
            }
          }}
        />
      </div>

      {/* WebSearch Toggle */}

      {/* WebSearch Toggle */}
      <div className="mb-3 flex items-center justify-between text-xs">
        <span className="text-gray-700">WebSearch Tool</span>
        <label className="inline-flex relative items-center cursor-pointer">
          <input
            type="checkbox"
            checked={stackData.web_search || false}
            onChange={() =>
              updateStack({ ...stackData, web_search: !stackData.web_search })
            }
            className="sr-only peer"
          />
          <div className="w-9 h-5 bg-gray-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-green-400 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-green-500 relative" />
        </label>
      </div>

      {/* SERP API */}
      <div className="mb-1 text-xs relative">
        <label className="block mb-1 text-gray-700">SERF API</label>
        <input
          type={showSerpKey ? "text" : "password"}
          className="w-full border rounded px-2 py-1 pr-7"
          value={stackData.serp_api_key || ""}
          onChange={(e) =>
            updateStack({ ...stackData, serp_api_key: e.target.value })
          }
        />
        <span
          className="absolute top-7 right-2 cursor-pointer text-gray-500"
          onClick={() => setShowSerpKey((prev) => !prev)}
        >
          {showSerpKey ? <Eye size={14} /> : <EyeOff size={14} />}
        </span>
      </div>
      <p className="w-full text-right text-[11px] text-gray-800 mt-3">Output</p>

      {/* Incoming handle */}

      <Handle
        type="target"
        position={Position.Left}
        id="query"
        className="w-2 h-2 bg-purple-500 z-10"
        style={{
          position: "absolute",
          right: " 2px",
          top: "250px",
          backgroundColor: "black",
        }}
      />
      <Handle
        type="target"
        position={Position.Left}
        id="query"
        className="w-2 h-2 bg-purple-500 z-10"
        style={{
          position: "absolute",
          right: " 2px",
          top: "300px",
          backgroundColor: "black",
        }}
      />
      <Handle
        type="source"
        position={Position.Right}
        id="query"
        className="w-2 h-2 bg-purple-500 z-10"
        style={{
          position: "absolute",
          right: " 3px",
          top: "462px",
          backgroundColor: "black",
        }}
      />
    </div>
  );
}
