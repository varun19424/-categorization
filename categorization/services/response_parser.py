import json

from categorization.exceptions import StructuredOutputError


class ResponseParser:
    required_keys = {"category", "confidence", "reasoning"}

    def parse(self, raw_text, valid_categories):
        try:
            payload = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            raise StructuredOutputError(detail=f"Provider returned invalid JSON: {exc.msg}") from exc

        missing = self.required_keys.difference(payload.keys())
        if missing:
            raise StructuredOutputError(detail=f"Provider response is missing keys: {sorted(missing)}")

        if payload["category"] not in valid_categories:
            raise StructuredOutputError(detail="Provider returned a category outside the chart of accounts.")

        try:
            confidence_score = float(payload["confidence"])
        except (TypeError, ValueError) as exc:
            raise StructuredOutputError(detail="Confidence score must be numeric.") from exc

        payload["confidence"] = max(0.0, min(1.0, round(confidence_score, 2)))
        payload["reasoning"] = str(payload["reasoning"]).strip()
        return payload
