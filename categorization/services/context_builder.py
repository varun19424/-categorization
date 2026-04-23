from difflib import SequenceMatcher


class ContextBuilder:
    def build(self, company_id, company_context, transaction):
        examples = self._top_examples(company_context["historical_transactions"], transaction)
        return {
            "company_id": company_id,
            "industry": company_context["industry"],
            "chart_of_accounts": company_context["chart_of_accounts"],
            "historical_examples": examples,
            "transaction": transaction,
        }

    def _top_examples(self, transactions, transaction, limit=3):
        scored = []
        target = self._join_text(transaction)
        for item in transactions:
            score = SequenceMatcher(None, target.lower(), self._join_text(item).lower()).ratio()
            scored.append((score, item))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [item for _, item in scored[:limit]]

    def _join_text(self, transaction):
        return " ".join(
            filter(
                None,
                [
                    transaction.get("description", ""),
                    transaction.get("vendor", ""),
                ],
            )
        )
