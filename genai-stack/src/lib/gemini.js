import { GoogleGenerativeAI } from "@google/generative-ai";

const apiKey = import.meta.env.VITE_API_KEY;
const genAI = new GoogleGenerativeAI(apiKey);

const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

const generationConfig = {
  temperature: 0.7,
  topP: 1,
  topK: 40,
  maxOutputTokens: 2048,
  responseMimeType: "text/plain",
};

export default async function run(prompt) {
  const chatSession = model.startChat({ generationConfig });

  const result = await chatSession.sendMessage(prompt);
  const response = result.response;
  return response.text();
}
