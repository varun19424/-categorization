# AI Transaction Categorization Service

A Django REST API that suggests the best accounting category for a single business transaction using:

- the transaction description and vendor
- the company's chart of accounts
- the company's recent historical transactions

The project ships with a deterministic mock provider for local development and an OpenAI-compatible provider for live LLM-backed categorization.

## Features

- Django 6 + Django REST Framework API
- JSON-only request and response handling
- Deterministic `mock` provider for offline/local testing
- OpenAI-compatible `/chat/completions` provider support
- Structured output parsing and validation
- Consistent error contract
- Built-in sample evaluation command
- Test coverage for core API behavior

## Project Structure

```text
.
|-- categorization/
|   |-- services/
|   |   |-- llm/
|   |   |-- categorization_service.py
|   |   |-- context_builder.py
|   |   `-- response_parser.py
|   |-- management/commands/evaluate_samples.py
|   |-- exception_handler.py
|   |-- sample_data.py
|   |-- serializers.py
|   |-- tests.py
|   |-- urls.py
|   `-- views.py
|-- config/
|   |-- settings.py
|   `-- urls.py
|-- manage.py
|-- requirements.txt
`-- .env.example
```

## Requirements

- Python 3.12 recommended
- pip

Python dependencies:

- `django==6.0.4`
- `djangorestframework==3.17.1`
- `pypdf==6.10.2`

## Quick Start

### 1. Create and activate a virtual environment

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 2. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 3. Configure environment variables

Copy `.env.example` to `.env` and update the values you want to use.

Example:

```env
LLM_PROVIDER=mock
LLM_API_KEY=
LLM_MODEL=gpt-4.1-mini
LLM_BASE_URL=https://api.openai.com/v1
ALLOWED_HOSTS=127.0.0.1,localhost
```

### 4. Run database migrations

```powershell
python manage.py migrate
```

### 5. Start the development server

```powershell
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/api/v1/`.

## Configuration

The application reads environment variables from a root-level `.env` file.

### Supported variables

- `LLM_PROVIDER`
  - `mock` for deterministic local behavior
  - `openai` or `openai_compatible` for a live provider
- `LLM_API_KEY`
  - Required when `LLM_PROVIDER=openai`
- `LLM_MODEL`
  - Default: `gpt-4.1-mini`
- `LLM_BASE_URL`
  - Default: `https://api.openai.com/v1`
- `ALLOWED_HOSTS`
  - Comma-separated list
  - Default: `127.0.0.1,localhost`

### Notes

- If `LLM_PROVIDER` is unrecognized, the app falls back to the mock provider.
- If `LLM_PROVIDER=openai` and `LLM_API_KEY` is missing, the API returns an error.
- `DEBUG` is currently enabled in `config/settings.py` and should be reviewed before production use.

## API Endpoints

Base prefix: `/api/v1/`

### Health Check

`GET /api/v1/health/`

Response:

```json
{
  "status": "ok"
}
```

### Categorization Suggestion

Primary endpoint:

`POST /api/v1/categorize/`

Compatible alias:

`POST /api/v1/categorizations/suggest/`

Request body:

```json
{
  "transaction": {
    "description": "AWS monthly cloud hosting invoice",
    "vendor": "Amazon Web Services"
  },
  "company_context": {
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
      "Bank Fees"
    ],
    "historical_transactions": [
      {
        "description": "AWS EC2 usage for production environment",
        "vendor": "Amazon Web Services",
        "category": "Cloud Infrastructure"
      }
    ]
  }
}
```

Successful response:

```json
{
  "category": "Cloud Infrastructure",
  "confidence": 0.96,
  "reasoning": "Matched keyword 'aws' against the configured chart of accounts."
}
```

## Validation Rules

### Required request fields

- `transaction.description`
- `company_context.company_id`
- `company_context.industry`
- `company_context.chart_of_accounts`
- `company_context.historical_transactions`

### Important validation behavior

- `transaction.vendor` is optional
- `historical_transactions` may be empty
- `chart_of_accounts` must not be empty
- The selected category must be one of the categories from `chart_of_accounts`

## Error Contract

Errors are returned in a simplified JSON shape:

```json
{
  "error": "message"
}
```

Examples:

Missing required fields:

```json
{
  "error": "Invalid input: description and chart_of_accounts are required"
}
```

Empty chart of accounts:

```json
{
  "error": "Chart of accounts cannot be empty"
}
```

Provider misconfiguration:

```json
{
  "error": "LLM_API_KEY is required when using the openai provider."
}
```

## How Categorization Works

1. The API validates the incoming payload.
2. The context builder selects up to 3 most similar historical transactions.
3. The configured LLM provider generates a structured categorization response.
4. The response parser validates:
   - JSON format
   - required keys
   - numeric confidence
   - category membership in the provided chart of accounts
5. The API returns normalized JSON to the client.

## Local Testing

Run the test suite:

```powershell
python manage.py test
```

Current tests cover:

- health check endpoint
- successful categorization flow
- alias category matching
- invalid payload handling
- empty chart-of-accounts handling
- sample evaluation behavior

## Evaluation Command

The repository includes a sample evaluation set in `categorization/sample_data.py`.

Run it with:

```powershell
python manage.py evaluate_samples
```

Example output shape:

```json
{
  "total_samples": 5,
  "top_1_accuracy": 1.0,
  "average_confidence": 0.96,
  "results": [
    {
      "company_id": "acme-saas",
      "description": "AWS monthly cloud hosting invoice",
      "predicted_category": "Cloud Infrastructure",
      "expected_category": "Cloud Infrastructure",
      "confidence_score": 0.96,
      "is_match": true
    }
  ]
}
```

## PowerShell Example

```powershell
$body = @{
  transaction = @{
    description = "Dinner with client at restaurant"
  }
  company_context = @{
    company_id = "comp_102"
    industry = "Consulting"
    chart_of_accounts = @(
      "Meals & Entertainment"
      "Travel Expense"
    )
    historical_transactions = @()
  }
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Method POST `
  -Uri "http://127.0.0.1:8000/api/v1/categorize/" `
  -ContentType "application/json" `
  -Body $body
```

## Testing with Postman

### 1. Start the API locally

```powershell
python manage.py runserver
```

Base URL:

```text
http://127.0.0.1:8000
```

### 2. Health check request

Create a new request in Postman:

- Method: `GET`
- URL: `http://127.0.0.1:8000/api/v1/health/`

Click `Send`.

Expected response:

```json
{
  "status": "ok"
}
```

### 3. Categorization request

Create another request in Postman:

- Method: `POST`
- URL: `http://127.0.0.1:8000/api/v1/categorize/`

Headers:

- `Content-Type: application/json`

Body:

- Select `Body`
- Choose `raw`
- Select `JSON`
- Paste the following payload:

```json
{
  "transaction": {
    "description": "AWS monthly cloud hosting invoice",
    "vendor": "Amazon Web Services"
  },
  "company_context": {
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
      "Bank Fees"
    ],
    "historical_transactions": [
      {
        "description": "AWS EC2 usage for production environment",
        "vendor": "Amazon Web Services",
        "category": "Cloud Infrastructure"
      }
    ]
  }
}
```

Click `Send`.

Expected response:

```json
{
  "category": "Cloud Infrastructure",
  "confidence": 0.96,
  "reasoning": "Matched keyword 'aws' against the configured chart of accounts."
}
```

### 4. Optional endpoint alias

You can also test the same request with:

```text
POST http://127.0.0.1:8000/api/v1/categorizations/suggest/
```

### 5. Example invalid request

Use this body to verify validation behavior:

```json
{
  "transaction": {},
  "company_context": {}
}
```

Expected response:

```json
{
  "error": "Invalid input: description and chart_of_accounts are required"
}
```

## Architecture Notes

- `categorization/views.py`: API endpoints
- `categorization/serializers.py`: input and output validation
- `categorization/services/context_builder.py`: ranks relevant historical examples
- `categorization/services/categorization_service.py`: orchestrates the end-to-end flow
- `categorization/services/llm/providers.py`: mock and OpenAI-compatible providers
- `categorization/services/response_parser.py`: validates provider output
- `categorization/exception_handler.py`: normalizes API errors
- `categorization/management/commands/evaluate_samples.py`: evaluation CLI entrypoint

## Current Limitations

- No authentication or authorization
- No persistence layer for categorization requests
- No production deployment configuration
- Provider integration currently targets an OpenAI-compatible chat completions interface
- SQLite is present because this is a Django project, but the categorization workflow itself is request-driven and does not store transactions

## Recommended Development Mode

For local development and predictable results, use:

```env
LLM_PROVIDER=mock
```

This avoids external API calls and keeps tests and manual verification deterministic.
