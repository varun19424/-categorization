from django.conf import settings

from categorization.services.llm.providers import MockLLMProvider, OpenAICompatibleProvider


def build_provider():
    provider = settings.LLM_PROVIDER.lower()
    if provider == "mock":
        return MockLLMProvider()
    if provider in {"openai", "openai_compatible"}:
        return OpenAICompatibleProvider(
            base_url=settings.LLM_BASE_URL,
            api_key=settings.LLM_API_KEY,
            model=settings.LLM_MODEL,
        )
    return MockLLMProvider()
