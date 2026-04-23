SAMPLE_COMPANIES = {
    "acme-saas": {
        "company_id": "acme-saas",
        "industry": "B2B SaaS",
        "chart_of_accounts": [
            "Cloud Infrastructure",
            "Software Subscriptions",
            "Travel",
            "Meals and Entertainment",
            "Office Supplies",
            "Professional Services",
            "Advertising and Marketing",
            "Bank Fees",
        ],
        "historical_transactions": [
            {
                "description": "AWS EC2 usage for production environment",
                "vendor": "Amazon Web Services",
                "category": "Cloud Infrastructure",
            },
            {
                "description": "Notion enterprise plan renewal",
                "vendor": "Notion",
                "category": "Software Subscriptions",
            },
            {
                "description": "Google Ads monthly campaign spend",
                "vendor": "Google",
                "category": "Advertising and Marketing",
            },
            {
                "description": "Airport taxi after customer meeting",
                "vendor": "Uber",
                "category": "Travel",
            },
            {
                "description": "Monthly bank service charge",
                "vendor": "Chase",
                "category": "Bank Fees",
            },
        ],
    },
    "northstar-health": {
        "company_id": "northstar-health",
        "industry": "Healthcare Operations",
        "chart_of_accounts": [
            "Medical Supplies",
            "Clinical Software",
            "Facility Expense",
            "Insurance",
            "Professional Services",
            "Travel",
        ],
        "historical_transactions": [
            {
                "description": "Disposable gloves and masks shipment",
                "vendor": "Medline",
                "category": "Medical Supplies",
            },
            {
                "description": "Electronic medical records platform invoice",
                "vendor": "Athenahealth",
                "category": "Clinical Software",
            },
        ],
    },
}

EVALUATION_SAMPLES = [
    {
        "transaction": {
            "description": "AWS monthly cloud hosting invoice",
            "vendor": "Amazon Web Services",
        },
        "company_context": SAMPLE_COMPANIES["acme-saas"],
        "expected_category": "Cloud Infrastructure",
    },
    {
        "transaction": {
            "description": "Lunch with prospective enterprise customer",
            "vendor": "Sweetgreen",
        },
        "company_context": SAMPLE_COMPANIES["acme-saas"],
        "expected_category": "Meals and Entertainment",
    },
    {
        "transaction": {
            "description": "Figma workspace annual renewal",
            "vendor": "Figma",
        },
        "company_context": SAMPLE_COMPANIES["acme-saas"],
        "expected_category": "Software Subscriptions",
    },
    {
        "transaction": {
            "description": "Legal contract review retainer",
            "vendor": "Wilson Legal",
        },
        "company_context": SAMPLE_COMPANIES["acme-saas"],
        "expected_category": "Professional Services",
    },
    {
        "transaction": {
            "description": "Bulk order of syringes and exam gloves",
            "vendor": "Medline",
        },
        "company_context": SAMPLE_COMPANIES["northstar-health"],
        "expected_category": "Medical Supplies",
    },
]
