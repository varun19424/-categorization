import logging

from categorization.services.context_builder import ContextBuilder
from categorization.services.llm.factory import build_provider
from categorization.services.response_parser import ResponseParser

logger = logging.getLogger(__name__)


class CategorizationService:
    def __init__(self):
        self.context_builder = ContextBuilder()
        self.provider = build_provider()
        self.parser = ResponseParser()

    def suggest(self, payload):
        company_context = payload["company_context"]
        company_id = company_context["company_id"]

        context = self.context_builder.build(
            company_id=company_id,
            company_context=company_context,
            transaction=payload["transaction"],
        )
        logger.info(
            "categorization_request company_id=%s provider=%s history_count=%s",
            company_id,
            self.provider.provider_name,
            len(context["historical_examples"]),
        )

        raw_response = self.provider.categorize(context)
        parsed = self.parser.parse(raw_response, valid_categories=context["chart_of_accounts"])
        return parsed
