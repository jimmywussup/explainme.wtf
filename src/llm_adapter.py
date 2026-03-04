import os
import google.generativeai as genai
from openai import OpenAI
from anthropic import Anthropic

class LLMAdapter:
    def send_message(self, prompt: str) -> str:
        raise NotImplementedError

class GeminiAdapter(LLMAdapter):
    def __init__(self, api_key: str, model_id: str = "gemini-2.5-flash"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_id)
        self.chat = self.model.start_chat(history=[])
        
    def send_message(self, prompt: str) -> str:
        response = self.chat.send_message(prompt)
        return response.text

class OpenAIAdapter(LLMAdapter):
    def __init__(self, api_key: str, model_id: str = "gpt-4o"):
        self.client = OpenAI(api_key=api_key)
        self.model_id = model_id
        self.messages = []
        
    def send_message(self, prompt: str) -> str:
        self.messages.append({"role": "user", "content": prompt})
        response = self.client.chat.completions.create(
            model=self.model_id,
            messages=self.messages
        )
        msg_text = response.choices[0].message.content
        self.messages.append({"role": "assistant", "content": msg_text})
        return msg_text

class AnthropicAdapter(LLMAdapter):
    def __init__(self, api_key: str, model_id: str = "claude-3-5-sonnet-20241022"):
        self.client = Anthropic(api_key=api_key)
        self.model_id = model_id
        self.messages = []
        
    def send_message(self, prompt: str) -> str:
        self.messages.append({"role": "user", "content": prompt})
        response = self.client.messages.create(
            model=self.model_id,
            max_tokens=1024,
            messages=self.messages
        )
        msg_text = response.content[0].text
        self.messages.append({"role": "assistant", "content": msg_text})
        return msg_text

class DeepSeekAdapter(LLMAdapter):
    def __init__(self, api_key: str, model_id: str = "deepseek-chat"):
        self.client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        self.model_id = model_id
        self.messages = []
        
    def send_message(self, prompt: str) -> str:
        self.messages.append({"role": "user", "content": prompt})
        response = self.client.chat.completions.create(
            model=self.model_id,
            messages=self.messages
        )
        msg_text = response.choices[0].message.content
        self.messages.append({"role": "assistant", "content": msg_text})
        return msg_text

def get_llm_adapter(provider: str, api_key: str, model_id: str) -> LLMAdapter:
    """Factory to get the correct LLM adapter based on settings."""
    if not api_key:
        raise ValueError(f"API Key for {provider} is not set.")
        
    if provider.lower() == "gemini":
        return GeminiAdapter(api_key, model_id or "gemini-2.5-flash")
    elif provider.lower() == "openai":
        return OpenAIAdapter(api_key, model_id or "gpt-4o")
    elif provider.lower() == "anthropic":
        return AnthropicAdapter(api_key, model_id or "claude-3-5-sonnet-20241022")
    elif provider.lower() == "deepseek":
        return DeepSeekAdapter(api_key, model_id or "deepseek-chat")
    else:
        raise ValueError(f"Unsupported provider: {provider}")
