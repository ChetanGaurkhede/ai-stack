import { MessageCircle, SendHorizontal, X } from "lucide-react";
import { useState } from "react";
import React from "react";

export default function ChatInterface({ isOpen, onClose, workflowId }) {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = {
      type: "user",
      content: inputMessage,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInputMessage("");
    setIsLoading(true);

    try {
      // Simulate API call
      setTimeout(() => {
        const aiResponse = {
          type: "ai",
          content: `This is a simulated response to: "${inputMessage}". In the real implementation, this would be processed through your workflow components.`,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, aiResponse]);
        setIsLoading(false);
      }, 3000);
    } catch (error) {
      setIsLoading(false);
      console.error("Error sending message:", error);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-[#00000038] bg-opacity-40 backdrop-blur-sm flex justify-center items-center z-50 ">
      <div className="bg-white rounded-lg w-full max-w-2xl h-[500px] flex flex-col ">
        {/* Header */}
        <div className="flex items-center justify-between p-3 shadow-sm px-5 py-5">
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
            <div className="text-center text-gray-500 mt-8">
              <div className="flex items-center w-fit mx-auto mb-3 gap-2">
                <MessageCircle className="w-5 h-5 mx-auto  text-blue-500" />
                <span>GenAi stack chat</span>
              </div>
              <p>Start a conversation to test your stack</p>
            </div>
          )}

          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${
                message.type === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  message.type === "user"
                    ? "bg-blue-600 text-white"
                    : "bg-gray-200 text-gray-800"
                }`}
              >
                <p className="text-sm">{message.content}</p>
                <p className="text-xs opacity-70 mt-1">
                  {message.timestamp.toLocaleTimeString()}
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
        <div className="p-4 px-5 ">
          <div className="flex gap-2 relative">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && sendMessage()}
              placeholder="Send a message..."
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isLoading}
            />

            <button
              onClick={sendMessage}
              disabled={isLoading || !inputMessage.trim()}
              className="absolute right-2 top-1/2 cursor-pointer transform -translate-y-1/2 rounded-full p-2 bg-white hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <SendHorizontal className="w-5 h-5 text-gray-800 " />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
