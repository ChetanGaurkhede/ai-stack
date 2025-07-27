import openai
import google.generativeai as genai
from typing import Optional, Dict, Any
from app.config import settings
import structlog

logger = structlog.get_logger()


class LLMService:
    def __init__(self):
        self.openai_client = None
        self.gemini_client = None
        
        if settings.openai_api_key:
            openai.api_key = settings.openai_api_key
            self.openai_client = openai
        
        if settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)
            self.gemini_client = genai
    
    async def generate_response(
        self,
        query: str,
        context: Optional[str] = None,
        provider: str = "openai",
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        custom_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate response using specified LLM provider
        """
        try:
            if provider == "openai":
                return await self._generate_openai_response(
                    query, context, model, temperature, max_tokens, custom_prompt
                )
            elif provider == "gemini":
                return await self._generate_gemini_response(
                    query, context, model, temperature, max_tokens, custom_prompt
                )
            else:
                raise ValueError(f"Unsupported provider: {provider}")
        except Exception as e:
            logger.error("LLM generation failed", error=str(e), provider=provider)
            raise
    
    async def _generate_openai_response(
        self,
        query: str,
        context: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        custom_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate response using OpenAI"""
        if not self.openai_client:
            raise ValueError("OpenAI client not configured")
        
        model = model or settings.openai_model
        
        # Build messages
        messages = []
        
        if custom_prompt:
            messages.append({"role": "system", "content": custom_prompt})
        else:
            messages.append({
                "role": "system",
                "content": "You are a helpful AI assistant. Provide accurate and helpful responses."
            })
        
        if context:
            messages.append({
                "role": "user",
                "content": f"Context: {context}\n\nQuestion: {query}"
            })
        else:
            messages.append({"role": "user", "content": query})
        
        response = await self.openai_client.ChatCompletion.acreate(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return {
            "response": response.choices[0].message.content,
            "model": model,
            "provider": "openai",
            "usage": response.usage.dict() if response.usage else None
        }
    
    async def _generate_gemini_response(
        self,
        query: str,
        context: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        custom_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate response using Google Gemini"""
        if not self.gemini_client:
            raise ValueError("Gemini client not configured")
        
        model = model or settings.gemini_model
        
        # Build prompt
        if custom_prompt:
            prompt = f"{custom_prompt}\n\n"
        else:
            prompt = "You are a helpful AI assistant. Provide accurate and helpful responses.\n\n"
        
        if context:
            prompt += f"Context: {context}\n\nQuestion: {query}"
        else:
            prompt += f"Question: {query}"
        
        model_instance = genai.GenerativeModel(model)
        
        response = await model_instance.generate_content_async(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens
            )
        )
        
        return {
            "response": response.text,
            "model": model,
            "provider": "gemini",
            "usage": None  # Gemini doesn't provide usage info in the same way
        }
    
    async def generate_embeddings(
        self,
        text: str,
        provider: str = "openai"
    ) -> Dict[str, Any]:
        """Generate embeddings using specified provider"""
        try:
            if provider == "openai":
                return await self._generate_openai_embeddings(text)
            elif provider == "gemini":
                return await self._generate_gemini_embeddings(text)
            else:
                raise ValueError(f"Unsupported provider: {provider}")
        except Exception as e:
            logger.error("Embedding generation failed", error=str(e), provider=provider)
            raise
    
    async def _generate_openai_embeddings(self, text: str) -> Dict[str, Any]:
        """Generate embeddings using OpenAI"""
        if not self.openai_client:
            raise ValueError("OpenAI client not configured")
        
        response = await self.openai_client.Embedding.acreate(
            input=text,
            model=settings.openai_embedding_model
        )
        
        return {
            "embeddings": response.data[0].embedding,
            "model": settings.openai_embedding_model,
            "provider": "openai"
        }
    
    async def _generate_gemini_embeddings(self, text: str) -> Dict[str, Any]:
        """Generate embeddings using Google Gemini"""
        if not self.gemini_client:
            raise ValueError("Gemini client not configured")
        
        model = genai.GenerativeModel(settings.gemini_embedding_model)
        response = await model.embed_content_async(text)
        
        return {
            "embeddings": response.embedding,
            "model": settings.gemini_embedding_model,
            "provider": "gemini"
        } 