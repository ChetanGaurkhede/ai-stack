import { useState } from "react";
import run from "../lib/gemini";// ✅ correct file

const useGeminiChat = () => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const sendPrompt = async (inputMessage) => {
    if (!inputMessage.trim()) return;

    const userMsg = {
      type: "user",
      content: inputMessage,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const geminiResponse = await run(inputMessage);
      const aiMsg = {
        type: "ai",
        content: geminiResponse,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiMsg]);
    } catch (error) {
      console.error("Gemini Chat Error:", error);
      setMessages((prev) => [
        ...prev,
        {
          type: "ai",
          content: "⚠️ Gemini failed to respond.",
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return { messages, isLoading, sendPrompt };
};

export default useGeminiChat;
