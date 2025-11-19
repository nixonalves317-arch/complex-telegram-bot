import os
import requests
import logging

logger = logging.getLogger(__name__)

class AIProvider:
    def ask(self, prompt: str) -> str:
        raise NotImplementedError

class OpenRouterProvider(AIProvider):
    def __init__(self, api_key=None, model='mistral/mistral-tiny'):
        self.key = api_key or os.getenv('OPENROUTER_KEY')
        self.model = model

    def ask(self, prompt: str) -> str:
        if not self.key:
            raise RuntimeError('OpenRouter key not set')
        url = 'https://openrouter.ai/api/v1/chat/completions'
        headers = {'Authorization': f'Bearer {self.key}', 'Content-Type': 'application/json'}
        payload = {'model': self.model, 'messages':[{'role':'user','content':prompt}]}
        r = requests.post(url, json=payload, headers=headers, timeout=30)
        r.raise_for_status()
        j = r.json()
        try:
            return j['choices'][0]['message']['content']
        except Exception:
            logger.exception('OpenRouter parse error')
            return str(j)

class HuggingFaceProvider(AIProvider):
    def __init__(self, token=None, model=None):
        self.token = token or os.getenv('HF_TOKEN')
        self.model = model or os.getenv('HF_MODEL')
    def ask(self, prompt: str) -> str:
        if not self.token or not self.model:
            raise RuntimeError('HF token or model not set')
        url = f'https://api-inference.huggingface.co/models/{self.model}'
        headers = {'Authorization': f'Bearer {self.token}'}
        payload = {'inputs': prompt}
        r = requests.post(url, headers=headers, json=payload, timeout=60)
        r.raise_for_status()
        j = r.json()
        if isinstance(j, list) and 'generated_text' in j[0]:
            return j[0]['generated_text']
        if isinstance(j, dict) and 'generated_text' in j:
            return j['generated_text']
        return str(j)

class GeminiProvider(AIProvider):
    def __init__(self, api_key=None):
        self.key = api_key or os.getenv('GEMINI_KEY')
    def ask(self, prompt: str) -> str:
        if not self.key:
            raise RuntimeError('Gemini key not set')
        url = f'https://generativelanguage.googleapis.com/v1beta/models/text-bison-001:generate?key={self.key}'
        payload = {'prompt': {'text': prompt}, 'temperature': 0.2}
        r = requests.post(url, json=payload, timeout=60)
        r.raise_for_status()
        j = r.json()
        try:
            return j['candidates'][0]['content'][0]['text']
        except Exception:
            return str(j)
