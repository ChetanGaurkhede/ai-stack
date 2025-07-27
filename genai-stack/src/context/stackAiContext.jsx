// // src/context/FormContext.jsx
// import React, { createContext, useState, useContext } from "react";

// const StackContext = createContext();

// export const useStackData = () => useContext(StackContext);

// export const StackProvider = ({ children }) => {
//   const [stackData, setStackData] = useState({});

//   const updateStack = (newData) => {
//     setStackData((prev) => ({ ...prev, ...newData }));
//   };

//   const [stacks, setStacks] = useState([]);
//   const [loading, setLoading] = useState(false);

//   return (
//     <StackContext.Provider
//       value={{ stackData, updateStack, stacks, setStacks, loading, setLoading }}
//     >
//       {children}
//     </StackContext.Provider>
//   );
// };
import React, { createContext, useState, useContext } from "react";
import run from "../lib/gemini"; // Ensure this function calls Gemini correctly

const StackContext = createContext();

export const useStackData = () => useContext(StackContext);

export const StackProvider = ({ children }) => {
  // Stack data
  const [stackData, setStackData] = useState({});
  const updateStack = (newData) => {
    setStackData((prev) => ({ ...prev, ...newData }));
  };

  const [stacks, setStacks] = useState([]);
  const [loading, setLoading] = useState(false);

  // Gemini Chat data
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  // Append word-by-word with delay
  const delayMessage = (index, word) => {
    setTimeout(() => {
      setMessages((prev) => {
        const lastMsg = prev[prev.length - 1];
        const updated = {
          ...lastMsg,
          content: lastMsg.content + word,
        };
        return [...prev.slice(0, -1), updated];
      });
    }, 40 * index); // adjust speed here
  };

  // Send prompt to Gemini API
  const sendPrompt = async (userInput) => {
    if (!userInput.trim()) return;

    const userMessage = {
      type: "user",
      content: userInput,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setInput("");

    try {
      const rawResponse = await run(userInput);

      // Format response: bold (**text**) & line break (*)
      const withBold = rawResponse.replace(/\*\*(.*?)\*\*/g, "<b>$1</b>");
      const formatted = withBold.replace(/\*/g, "<br/>");

      // Prepare typing animation
      setMessages((prev) => [
        ...prev,
        { type: "ai", content: "", timestamp: new Date() },
      ]);

      const words = formatted.split(/(\s+|<br\/>)/g);
      words.forEach((word, i) => delayMessage(i, word));
    } catch (error) {
      console.error("❌ Gemini error:", error);
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

  return (
    <StackContext.Provider
      value={{
        stackData,
        updateStack,
        stacks,
        setStacks,
        loading,
        setLoading,
        // Gemini
        input,
        setInput,
        messages,
        isLoading,
        sendPrompt,
      }}
    >
      {children}
    </StackContext.Provider>
  );
};
