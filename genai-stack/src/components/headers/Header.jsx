import React from "react";
import { Trash2 } from "lucide-react";

export default function Header() {
  return (
    <div className="bg-white shadow-sm p-3 fixed top-0 left-0 w-full z-50">
      <div className="flex items-center justify-between  px-3">
        <h3 className="font-semibold ">GenAI Stack</h3>
        <div className="flex items-center gap-2">
          <button
            // onClick={clearWorkflow}
            className="h-10 w-10 text-sm bg-blue-400 border border-gray-300 rounded-full text-white flex items-center justify-center gap-2"
          >
            
            <span className="text-xl">S</span>
          </button>
        </div>
      </div>
    </div>
  );
}
