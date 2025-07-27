import { MessageCircle, SendHorizontal, X } from "lucide-react";
import React, { useState } from "react";
import useGeminiChat from "../../hooks/useGeminiChat";
import { useStackData } from "../../context/stackAiContext";

export default function ChatInterface({ isOpen, onClose }) {
  // const { messages, isLoading, sendPrompt } = useGeminiChat();
  const [inputMessage, setInputMessage] = useState("");
  const { input, setInput, messages, isLoading, sendPrompt } = useStackData();

  const handleSend = () => {
    if (!inputMessage.trim()) return;
    sendPrompt(inputMessage);
    setInputMessage("");
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/20 backdrop-blur-md flex justify-center items-center z-50">
      <div className="bg-white rounded-lg w-full max-w-2xl h-[500px] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 shadow-sm border-b">
          <div className="flex items-center gap-2">
            <MessageCircle className="w-5 h-5 text-green-600" />
            <h3 className="font-semibold">GenAI Stack Chat</h3>
          </div>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && (
            <div className="text-center text-gray-500 mt-10">
              <p>Start a conversation with your stack</p>
            </div>
          )}
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex ${
                msg.type === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  msg.type === "user"
                    ? "bg-blue-600 text-white"
                    : "bg-gray-200 text-gray-800"
                }`}
              >
                <p
                  className="text-sm whitespace-pre-wrap"
                  dangerouslySetInnerHTML={{ __html: msg.content }}
                />
                <p className="text-xs mt-1 opacity-60">
                  {msg.timestamp.toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-200 px-4 py-2 rounded-lg">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div
                    className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                    style={{ animationDelay: "0.1s" }}
                  ></div>
                  <div
                    className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                    style={{ animationDelay: "0.2s" }}
                  ></div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Input */}
        <div className="p-4 border-t">
          <div className="flex gap-2 relative">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
              placeholder="Type a message..."
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isLoading}
            />
            <button
              onClick={handleSend}
              disabled={!inputMessage.trim() || isLoading}
              className="absolute right-2 top-1/2 transform -translate-y-1/2 p-2 rounded-full bg-white hover:bg-gray-100 disabled:opacity-50"
            >
              <SendHorizontal className="w-5 h-5 text-gray-800" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
