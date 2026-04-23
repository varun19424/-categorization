from django.test import SimpleTestCase
from rest_framework.test import APIClient

from categorization.sample_data import SAMPLE_COMPANIES
from categorization.services.evaluation import evaluate_samples


class CategorizationApiTests(SimpleTestCase):
    def setUp(self):
        self.client = APIClient()

    def test_health_check(self):
        response = self.client.get("/api/v1/health/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_mock_categorization_returns_expected_shape(self):
        payload = {
            "transaction": {
                "description": "AWS monthly cloud hosting invoice",
                "vendor": "Amazon Web Services",
            },
            "company_context": SAMPLE_COMPANIES["acme-saas"],
        }

        response = self.client.post("/api/v1/categorizations/suggest/", payload, format="json")
        body = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(body["category"], "Cloud Infrastructure")
        self.assertIn(body["category"], SAMPLE_COMPANIES["acme-saas"]["chart_of_accounts"])
        self.assertGreaterEqual(body["confidence"], 0.0)
        self.assertLessEqual(body["confidence"], 1.0)
        self.assertIn("reasoning", body)

    def test_meals_and_entertainment_alias_matches_chart_label(self):
        payload = {
            "transaction": {
                "description": "Dinner with client at restaurant",
            },
            "company_context": {
                "company_id": "comp_102",
                "industry": "Consulting",
                "chart_of_accounts": [
                    "Meals & Entertainment",
                    "Travel Expense",
                ],
                "historical_transactions": [],
            },
        }

        response = self.client.post("/api/v1/categorize/", payload, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["category"], "Meals & Entertainment")

    def test_invalid_input_matches_expected_error_contract(self):
        payload = {
            "transaction": {},
            "company_context": {},
        }

        response = self.client.post("/api/v1/categorize/", payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {"error": "Invalid input: description and chart_of_accounts are required"},
        )

    def test_empty_chart_of_accounts_returns_expected_error(self):
        payload = {
            "transaction": {
                "description": "Taxi ride",
            },
            "company_context": {
                "company_id": "comp_108",
                "industry": "General",
                "chart_of_accounts": [],
                "historical_transactions": [],
            },
        }

        response = self.client.post("/api/v1/categorize/", payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Chart of accounts cannot be empty"})

    def test_evaluation_samples_score_perfectly_with_mock_provider(self):
        report = evaluate_samples()
        self.assertEqual(report["total_samples"], 5)
        self.assertEqual(report["top_1_accuracy"], 1.0)

# Create your tests here.
