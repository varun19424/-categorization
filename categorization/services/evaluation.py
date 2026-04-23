from categorization.sample_data import EVALUATION_SAMPLES
from categorization.services.categorization_service import CategorizationService


def evaluate_samples():
    service = CategorizationService()
    results = []
    matches = 0

    for sample in EVALUATION_SAMPLES:
        suggestion = service.suggest(
            {
                "transaction": sample["transaction"],
                "company_context": sample["company_context"],
            }
        )
        is_match = suggestion["category"] == sample["expected_category"]
        matches += int(is_match)
        results.append(
            {
                "company_id": sample["company_context"]["company_id"],
                "description": sample["transaction"]["description"],
                "predicted_category": suggestion["category"],
                "expected_category": sample["expected_category"],
                "confidence_score": suggestion["confidence"],
                "is_match": is_match,
            }
        )

    total = len(EVALUATION_SAMPLES)
    average_confidence = round(sum(item["confidence_score"] for item in results) / total, 2)
    return {
        "total_samples": total,
        "top_1_accuracy": round(matches / total, 2),
        "average_confidence": average_confidence,
        "results": results,
    }
