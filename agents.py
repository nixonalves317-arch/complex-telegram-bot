import os
import logging
from ai_providers import OpenRouterProvider, HuggingFaceProvider, GeminiProvider

logger = logging.getLogger(__name__)

class AgentManager:
    def __init__(self):
        self.providers = []
        p = os.getenv('AI_PROVIDER', 'openrouter').lower()
        if p == 'huggingface':
            self.providers.append(HuggingFaceProvider())
            self.providers.append(OpenRouterProvider())
        elif p == 'gemini':
            self.providers.append(GeminiProvider())
            self.providers.append(OpenRouterProvider())
        else:
            self.providers.append(OpenRouterProvider())
            self.providers.append(HuggingFaceProvider())
        self.providers.append(GeminiProvider())

    def ask(self, prompt: str) -> str:
        last_exc = None
        for prov in self.providers:
            try:
                resp = prov.ask(prompt)
                if resp:
                    return resp
            except Exception:
                logger.exception('provider failed: %s', prov.__class__.__name__)
                last_exc = Exception('provider failed')
                continue
        raise RuntimeError('All providers failed') from last_exc
