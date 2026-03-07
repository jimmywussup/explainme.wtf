import os
import base64
from google import genai
from google.genai import types
from openai import OpenAI
from anthropic import Anthropic

class LLMAdapter:
    def send_message(self, prompt: str, image_bytes: bytes = None, force_simple: bool = False, force_thinking: bool = False, system_instruction: str = None) -> tuple[str, str]:
        raise NotImplementedError

class GeminiAdapter(LLMAdapter):
    def __init__(self, api_key: str, fast_model_id: str, thinking_model_id: str):
        self.client = genai.Client(api_key=api_key)
        self.fast_model_id = fast_model_id
        self.thinking_model_id = thinking_model_id
        self.history = []
        
    def send_message(self, prompt: str, image_bytes: bytes = None, force_simple: bool = False, force_thinking: bool = False, system_instruction: str = None) -> tuple[str, str]:
        parts = []
        if image_bytes:
            parts.append(types.Part.from_bytes(data=image_bytes, mime_type="image/png"))
        parts.append(types.Part.from_text(text=prompt))
        
        if force_thinking:
            is_complex = True
        elif force_simple:
            is_complex = False
        else:
            classify_prompt = (
                "You are the routing brain for 'explainme.wtf', an app whose main goal is to simply explain text the user highlights on their screen, or briefly analyze screenshots. "
                "Evaluate the following query based on this context.\n\n"
                "If the user explicitly asks to 'google', 'search', or look something up online, or asks to use a 'complex', 'thinking', 'pro', 'advanced', or 'reasoning' model, reply exactly and only with 'THINKING'.\n"
                "If the user explicitly asks or commands to use a 'simple', 'fast', 'basic', or 'lite' model, reply exactly and only with 'FAST'.\n"
                "If the query asks about current events, real-time news, live data, or anything that requires up-to-date information from the internet, reply with 'THINKING'.\n"
                "Otherwise, evaluate the core task: if it is a standard app request like a simple factual question, text explanation, dictionary lookup, OCR, or translation, reply with 'FAST'.\n"
                "Only if it requires deep reasoning, advanced math, complex coding architectures, or heavy multi-step logic, reply with 'THINKING'.\n"
                "Reply exactly and only with 'FAST' or 'THINKING'."
            )
            classify_parts = parts + [types.Part.from_text(text=classify_prompt)]
            classify_contents = self.history + [types.Content(role="user", parts=classify_parts)]
            
            try:
                classify_resp = self.client.models.generate_content(
                    model=self.fast_model_id,
                    contents=classify_contents
                )
                is_complex = "THINKING" in (classify_resp.text or "").upper()
            except Exception:
                is_complex = False
            
        active_model = self.thinking_model_id if is_complex else self.fast_model_id
        
        config = types.GenerateContentConfig()
        if "pro" in active_model.lower():
            config.tools = [types.Tool(google_search=types.GoogleSearch())]
            
        if system_instruction:
            config.system_instruction = system_instruction
            
        new_content = types.Content(role="user", parts=parts)
        self.history.append(new_content)
        
        response = self.client.models.generate_content(
            model=active_model,
            contents=self.history,
            config=config
        )
        
        self.history.append(types.Content(role="model", parts=[types.Part.from_text(text=response.text)]))
        return response.text, "Thinking" if is_complex else "Fast"

class OpenAIAdapter(LLMAdapter):
    def __init__(self, api_key: str, fast_model_id: str, thinking_model_id: str):
        self.client = OpenAI(api_key=api_key)
        self.fast_model_id = fast_model_id
        self.thinking_model_id = thinking_model_id
        self.messages = []
        
    def send_message(self, prompt: str, image_bytes: bytes = None, force_simple: bool = False, force_thinking: bool = False, system_instruction: str = None) -> tuple[str, str]:
        content = []
        if image_bytes:
            b64_image = base64.b64encode(image_bytes).decode("utf-8")
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{b64_image}"}
            })
        content.append({"type": "text", "text": prompt})
        
        if force_thinking:
            is_complex = True
        elif force_simple:
            is_complex = False
        else:
            classify_prompt = (
                "You are the routing brain for 'explainme.wtf', an app whose main goal is to simply explain text the user highlights on their screen, or briefly analyze screenshots. "
                "Evaluate the following query based on this context.\n\n"
                "If the user explicitly asks to 'google', 'search', or look something up online, or asks to use a 'complex', 'thinking', 'pro', 'advanced', or 'reasoning' model, reply exactly and only with 'THINKING'.\n"
                "If the user explicitly asks or commands to use a 'simple', 'fast', 'basic', or 'lite' model, reply exactly and only with 'FAST'.\n"
                "If the query asks about current events, real-time news, live data, or anything that requires up-to-date information from the internet, reply with 'THINKING'.\n"
                "Otherwise, evaluate the core task: if it is a standard app request like a simple factual question, text explanation, dictionary lookup, OCR, or translation, reply with 'FAST'.\n"
                "Only if it requires deep reasoning, advanced math, complex coding architectures, or heavy multi-step logic, reply with 'THINKING'.\n"
                "Reply exactly and only with 'FAST' or 'THINKING'."
            )
            
            classify_messages = self.messages + [{
                "role": "user",
                "content": content + [{"type": "text", "text": classify_prompt}]
            }]
            
            try:
                classify_resp = self.client.chat.completions.create(
                    model=self.fast_model_id,
                    messages=classify_messages,
                    max_tokens=10
                )
                is_complex = "THINKING" in (classify_resp.choices[0].message.content or "").upper()
            except Exception:
                is_complex = False
            
        active_model = self.thinking_model_id if is_complex else self.fast_model_id
        if image_bytes and active_model.startswith("o"):
            active_model = self.fast_model_id # Fallback since o-series doesn't support images
            
        self.messages.append({"role": "user", "content": content})
        
        kwargs = {}
        if not active_model.startswith("o"):
            kwargs["max_tokens"] = 4096
            
        
        messages_to_send = self.messages.copy()
        if system_instruction:
            messages_to_send.insert(0, {"role": "system", "content": system_instruction})
            
        response = self.client.chat.completions.create(
            model=active_model,
            messages=messages_to_send,
            **kwargs
        )
        
        msg_text = response.choices[0].message.content
        self.messages.append({"role": "assistant", "content": msg_text})
        return msg_text, "Thinking" if is_complex else "Fast"

class AnthropicAdapter(LLMAdapter):
    def __init__(self, api_key: str, fast_model_id: str, thinking_model_id: str):
        self.client = Anthropic(api_key=api_key)
        self.fast_model_id = fast_model_id
        self.thinking_model_id = thinking_model_id
        self.messages = []
        
    def send_message(self, prompt: str, image_bytes: bytes = None, force_simple: bool = False, force_thinking: bool = False) -> tuple[str, str]:
        content = []
        if image_bytes:
            b64_image = base64.b64encode(image_bytes).decode("utf-8")
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": b64_image
                }
            })
        content.append({"type": "text", "text": prompt})
        
        if force_thinking:
            is_complex = True
        elif force_simple:
            is_complex = False
        else:
            classify_prompt = (
                "You are the routing brain for 'explainme.wtf', an app whose main goal is to simply explain text the user highlights on their screen, or briefly analyze screenshots. "
                "Evaluate the following query based on this context.\n\n"
                "If the user explicitly asks to 'google', 'search', or look something up online, or asks to use a 'complex', 'thinking', 'pro', 'advanced', or 'reasoning' model, reply exactly and only with 'THINKING'.\n"
                "If the user explicitly asks or commands to use a 'simple', 'fast', 'basic', or 'lite' model, reply exactly and only with 'FAST'.\n"
                "If the query asks about current events, real-time news, live data, or anything that requires up-to-date information from the internet, reply with 'THINKING'.\n"
                "Otherwise, evaluate the core task: if it is a standard app request like a simple factual question, text explanation, dictionary lookup, OCR, or translation, reply with 'FAST'.\n"
                "Only if it requires deep reasoning, advanced math, complex coding architectures, or heavy multi-step logic, reply with 'THINKING'.\n"
                "Reply exactly and only with 'FAST' or 'THINKING'."
            )
            
            classify_messages = self.messages + [{
                "role": "user",
                "content": content + [{"type": "text", "text": classify_prompt}]
            }]
            
            try:
                classify_resp = self.client.messages.create(
                    model=self.fast_model_id,
                    max_tokens=10,
                    messages=classify_messages
                )
                is_complex = "THINKING" in (classify_resp.content[0].text or "").upper()
            except Exception:
                is_complex = False
            
        active_model = self.thinking_model_id if is_complex else self.fast_model_id
        
        self.messages.append({"role": "user", "content": content})
        kwargs = {
            "model": active_model,
            "max_tokens": 4096,
            "messages": self.messages
        }
        if system_instruction:
            kwargs["system"] = system_instruction
            
        response = self.client.messages.create(**kwargs)
        
        msg_text = response.content[0].text
        self.messages.append({"role": "assistant", "content": msg_text})
        return msg_text, "Thinking" if is_complex else "Fast"

class DeepSeekAdapter(LLMAdapter):
    def __init__(self, api_key: str, fast_model_id: str, thinking_model_id: str):
        self.client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        self.fast_model_id = fast_model_id
        self.thinking_model_id = thinking_model_id
        self.messages = []
        
    def send_message(self, prompt: str, image_bytes: bytes = None, force_simple: bool = False, force_thinking: bool = False, system_instruction: str = None) -> tuple[str, str]:
        if image_bytes:
            raise NotImplementedError("DeepSeek does not support image input.")
            
        if force_thinking:
            is_complex = True
        elif force_simple:
            is_complex = False
        else:
            classify_prompt = (
                "You are the routing brain for 'explainme.wtf', an app whose main goal is to simply explain text the user highlights on their screen, or briefly analyze screenshots. "
                "Evaluate the above query based on this context.\n\n"
                "If the user explicitly asks to 'google', 'search', or look something up online, or asks to use a 'complex', 'thinking', 'pro', 'advanced', or 'reasoning' model, reply exactly and only with 'THINKING'.\n"
                "If the user explicitly asks or commands to use a 'simple', 'fast', 'basic', or 'lite' model, reply exactly and only with 'FAST'.\n"
                "If the query asks about current events, real-time news, live data, or anything that requires up-to-date information from the internet, reply with 'THINKING'.\n"
                "Otherwise, evaluate the core task: if it is a standard app request like a simple factual question, text explanation, dictionary lookup, OCR, or translation, reply with 'FAST'.\n"
                "Only if it requires deep reasoning, advanced math, complex coding architectures, or heavy multi-step logic, reply with 'THINKING'.\n"
                "Reply exactly and only with 'FAST' or 'THINKING'."
            )
                
            classify_messages = self.messages + [{
                "role": "user",
                "content": prompt + "\n\n" + classify_prompt
            }]
            
            try:
                classify_resp = self.client.chat.completions.create(
                    model=self.fast_model_id,
                    messages=classify_messages,
                    max_tokens=10
                )
                is_complex = "THINKING" in (classify_resp.choices[0].message.content or "").upper()
            except Exception:
                is_complex = False
            
        active_model = self.thinking_model_id if is_complex else self.fast_model_id
        
        self.messages.append({"role": "user", "content": prompt})
        
        messages_to_send = self.messages.copy()
        if system_instruction:
            messages_to_send.insert(0, {"role": "system", "content": system_instruction})
            
        response = self.client.chat.completions.create(
            model=active_model,
            messages=messages_to_send
        )
        
        msg_text = response.choices[0].message.content
        self.messages.append({"role": "assistant", "content": msg_text})
        return msg_text, "Thinking" if is_complex else "Fast"

def get_llm_adapter(provider: str, api_key: str, fast_model_id: str, thinking_model_id: str) -> LLMAdapter:
    """Factory to get the correct LLM adapter based on settings."""
    if not api_key:
        raise ValueError(f"API Key for {provider} is not set.")
        
    if provider.lower() == "gemini":
        return GeminiAdapter(api_key, fast_model_id or "gemini-2.5-flash-lite", thinking_model_id or "gemini-2.5-pro")
    elif provider.lower() == "openai":
        return OpenAIAdapter(api_key, fast_model_id or "gpt-4o-mini", thinking_model_id or "o1-mini")
    elif provider.lower() == "anthropic":
        return AnthropicAdapter(api_key, fast_model_id or "claude-3-5-haiku-latest", thinking_model_id or "claude-3-7-sonnet-latest")
    elif provider.lower() == "deepseek":
        return DeepSeekAdapter(api_key, fast_model_id or "deepseek-chat", thinking_model_id or "deepseek-reasoner")
    else:
        raise ValueError(f"Unsupported provider: {provider}")
