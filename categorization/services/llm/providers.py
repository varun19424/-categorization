import json
from difflib import SequenceMatcher
from urllib import error, request

from categorization.exceptions import ProviderConfigurationError, StructuredOutputError
from categorization.services.llm.base import BaseLLMProvider


class MockLLMProvider(BaseLLMProvider):
    provider_name = "mock"

    keyword_map = {
        "aws": "Cloud Infrastructure",
        "hosting": "Cloud Infrastructure",
        "cloud": "Cloud Infrastructure",
        "figma": "Software Subscriptions",
        "notion": "Software Subscriptions",
        "software": "Software Subscriptions",
        "lunch": "Meals and Entertainment",
        "dinner": "Meals and Entertainment",
        "meal": "Meals and Entertainment",
        "taxi": "Travel",
        "flight": "Travel",
        "hotel": "Travel",
        "google ads": "Advertising and Marketing",
        "ads": "Advertising and Marketing",
        "legal": "Professional Services",
        "retainer": "Professional Services",
        "bank": "Bank Fees",
        "gloves": "Medical Supplies",
        "syringes": "Medical Supplies",
        "masks": "Medical Supplies",
        "athenahealth": "Clinical Software",
    }

    def categorize(self, context):
        transaction_text = " ".join(
            filter(
                None,
                [
                    context["transaction"].get("description", ""),
                    context["transaction"].get("vendor", ""),
                ],
            )
        ).lower()

        for keyword, category in self.keyword_map.items():
            resolved_category = self._resolve_chart_category(category, context["chart_of_accounts"])
            if keyword in transaction_text and resolved_category:
                return json.dumps(
                    {
                        "category": resolved_category,
                        "confidence": 0.96,
                        "reasoning": f"Matched keyword '{keyword}' against the configured chart of accounts.",
                    }
                )

        best_match = None
        best_score = 0.0
        for example in context["historical_examples"]:
            example_text = " ".join(
                filter(None, [example.get("description", ""), example.get("vendor", "")])
            ).lower()
            score = SequenceMatcher(None, transaction_text, example_text).ratio()
            if score > best_score:
                best_match = example
                best_score = score

        category = best_match["category"] if best_match else context["chart_of_accounts"][0]
        confidence = 0.55 if best_match is None else min(0.92, round(0.55 + best_score, 2))
        return json.dumps(
            {
                "category": category,
                "confidence": confidence,
                "reasoning": "Selected the closest historical match when no direct keyword signal was found.",
            }
        )

    def _resolve_chart_category(self, target_category, chart_of_accounts):
        normalized_target = self._normalize(target_category)
        for category in chart_of_accounts:
            if self._normalize(category) == normalized_target:
                return category
        return None

    def _normalize(self, value):
        return (
            value.lower()
            .replace("&", "and")
            .replace("expense", "")
            .replace("  ", " ")
            .strip()
        )


class OpenAICompatibleProvider(BaseLLMProvider):
    provider_name = "openai_compatible"

    def __init__(self, base_url, api_key, model):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model

    def categorize(self, context):
        if not self.api_key:
            raise ProviderConfigurationError(detail="LLM_API_KEY is required when using the openai provider.")

        prompt = self._build_prompt(context)
        payload = {
            "model": self.model,
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You categorize business transactions. "
                        "Return only JSON with keys category, confidence, reasoning."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        }
        req = request.Request(
            url=f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=30) as response:
                body = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            raise StructuredOutputError(detail=f"Provider request failed with HTTP {exc.code}.") from exc
        except error.URLError as exc:
            raise StructuredOutputError(detail="Provider request could not be completed.") from exc

        try:
            return body["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise StructuredOutputError(detail="Provider response did not include a message payload.") from exc

    def _build_prompt(self, context):
        return json.dumps(
            {
                "task": "Select the best category for the transaction.",
                "company_id": context["company_id"],
                "industry": context["industry"],
                "chart_of_accounts": context["chart_of_accounts"],
                "historical_examples": context["historical_examples"],
                "transaction": context["transaction"],
                    "output_rules": {
                        "must_choose_from_chart_of_accounts": True,
                        "confidence_range": [0, 1],
                    },
                }
        )
