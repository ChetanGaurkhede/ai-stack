// src/context/FormContext.jsx
import React, { createContext, useState, useContext } from "react";

const StackContext = createContext();

export const useStackData = () => useContext(StackContext);

export const StackProvider = ({ children }) => {
  const [stackData, setStackData] = useState({});

  const updateStack = (newData) => {
    setStackData((prev) => ({ ...prev, ...newData }));
  };

  const [stacks, setStacks] = useState([]);
  const [loading, setLoading] = useState(false);

  return (
    <StackContext.Provider
      value={{ stackData, updateStack, stacks, setStacks, loading, setLoading }}
    >
      {children}
    </StackContext.Provider>
  );
};

// const stackDataArray = [
//   {
//     stackId: "stack-001",
//     title: "Product Info Extractor",
//     description: "Extracts product details from uploaded PDF specs.",
//     use_query: "Extract product name, price, and description",
//     llm_model: "gpt-4",
//     llm_file_name: "product-specs.pdf",
//     llm_file: "data:application/pdf;base64,JVBERi0xLjQK...", // dummy base64
//     llm_api_key: "sk-123-product",
//     ai_model: "OpenAI",
//     api_key: "api-key-123",
//     api_prompt: "Extract structured product info",
//     temp: "0.7",
//     web_search: false,
//     serf_api_key: "",
//     output_text:
//       "Product: Widget Pro\nPrice: $199\nDescription: High-end widget for professionals.",
//   },
//   {
//     stackId: "stack-002",
//     title: "Resume Analyzer",
//     description:
//       "Analyzes resumes and summarizes key candidate qualifications.",
//     use_query: "Summarize experience and skills",
//     llm_model: "gpt-3.5-turbo",
//     llm_file_name: "resume.pdf",
//     llm_file: "data:application/pdf;base64,JVBERi0xLjQK...", // dummy base64
//     llm_api_key: "sk-123-resume",
//     ai_model: "OpenAI",
//     api_key: "api-key-456",
//     api_prompt: "Summarize candidate background",
//     temp: "0.6",
//     web_search: false,
//     serf_api_key: "",
//     output_text:
//       "Candidate has 5+ years of experience in software development with skills in React and Node.js.",
//   },
//   {
//     stackId: "stack-003",
//     title: "Legal Doc Summarizer",
//     description: "Summarizes legal documents into plain English.",
//     use_query: "Summarize in plain language",
//     llm_model: "claude-2",
//     llm_file_name: "nda-agreement.pdf",
//     llm_file: "data:application/pdf;base64,JVBERi0xLjQK...", // dummy base64
//     llm_api_key: "sk-123-legal",
//     ai_model: "Anthropic",
//     api_key: "api-key-789",
//     api_prompt: "Summarize this NDA in plain English",
//     temp: "0.5",
//     web_search: false,
//     serf_api_key: "",
//     output_text:
//       "This NDA ensures that both parties keep shared information confidential for 2 years.",
//   },
//   {
//     stackId: "stack-004",
//     title: "Market Research Assistant",
//     description:
//       "Combines PDF data and live search to generate market summaries.",
//     use_query: "Analyze market trends from report",
//     llm_model: "gpt-4",
//     llm_file_name: "market-report.pdf",
//     llm_file: "data:application/pdf;base64,JVBERi0xLjQK...", // dummy base64
//     llm_api_key: "sk-123-market",
//     ai_model: "OpenAI",
//     api_key: "api-key-321",
//     api_prompt: "Summarize key market findings and trends",
//     temp: "0.8",
//     web_search: true,
//     serf_api_key: "serper-xyz",
//     output_text:
//       "The report highlights a 12% YoY growth in the AI tools market with increasing adoption across industries.",
//   },
// ];

// const currenStack = {
//     stackId: "",
//     title: "",
//     description: "",
//     use_query: "",
//     llm_model: "",
//     llm_file_name: "",
//     llm_file: "",
//     llm_api_key: "",
//     ai_model: "",
//     api_key: "",
//     api_prompt: "",
//     temp: "",
//     web_search: false,
//     serf_api_key: "",
//     output_text: "",
//   }
