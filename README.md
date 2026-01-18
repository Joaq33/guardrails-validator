# 🛡️ Guardrails Validator

![CI](https://github.com/Joaq33/guardrails-validator/actions/workflows/ci.yml/badge.svg)
![Python Versions](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)
![License](https://img.shields.io/badge/license-MIT-green)

> Generic LLM validation framework with consensus checking and database logging

**Guardrails Validator** is a powerful, production-ready framework for validating LLM outputs using **consensus mechanisms** across multiple API calls. Built on [Guardrails AI](https://guardrailsai.com/), it supports any Pydantic schema and works with multiple LLM providers (Groq, OpenAI, Gemini).

## ✨ Features

- 🔄 **Consensus Validation**: Run multiple LLM queries and determine consensus (e.g., 10/15 agreement)
- 🎯 **Schema-Agnostic**: Works with any Pydantic model - just define your schema
- 🔌 **Multi-Provider Support**: Groq, OpenAI, Gemini, or custom adapters
- 📊 **SQLite Logging**: Every response logged with session tracking and timestamps
- ⚙️ **Easy Configuration**: Centralized config for quick setup
- 🎨 **SOLID Architecture**: Clean, maintainable, extensible codebase

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/guardrails_validator.git
cd guardrails_validator

# Install dependencies with uv (recommended)
uv sync

# Or with pip
pip install -r requirements.txt
```

### Basic Usage

1. **Set your API key**:
```bash
echo "GROQ_API_KEY=your_api_key_here" >> .env
```

2. **Run with default superhero validation**:
```bash
uv run main.py
```

Or specify a custom domain:
```bash
uv run main.py --domain examples.domains.superhero_config
```

## 📖 Creating Your Own Domain

### 1. Create a Domain Config

Create `examples/domains/your_domain_config.py`:

```python
from pydantic import BaseModel, Field

# Define your schema
class ProductReview(BaseModel):
    is_positive: bool = Field(description="Positive sentiment")
    mentions_price: bool = Field(description="Price mentioned")
    rating: int = Field(description="Star rating 1-5")

# Configure validation
VALIDATION_TASK = "product review analysis"
ITEMS_TO_VALIDATE = ["Great product!", "Too expensive", "Love it!"]
VALIDATION_SCHEMA = ProductReview
```

### 2. Run Your Domain

```bash
uv run main.py --domain examples.domains.your_domain_config
```

## Usage Examples

### Example 1: Superhero Validation (Default)

```python
from pydantic import BaseModel, Field

class ProductReview(BaseModel):
    is_positive: bool = Field(description="Positive sentiment")
    mentions_price: bool = Field(description="Price mentioned")
    rating: int = Field(description="Star rating 1-5")
```

### Update Configuration

```python
# config.py
VALIDATION_TASK = "product review analysis"
ITEMS_TO_VALIDATE = ["Great product!", "Too expensive", "Love it!"]
VALIDATION_SCHEMA = ProductReview
```

### Results

```
Item                 is_positive     mentions_price  rating         
-----------------------------------------------------------------
Checking Great product!...
  [Logs]
    Call 1: is_positive=True, mentions_price=False, rating=5
    Call 2: is_positive=True, mentions_price=False, rating=5
    Call 3: is_positive=True, mentions_price=False, rating=4
  [Consensus]
  Result: is_positive=True, mentions_price=False, rating=5
```

## ⚙️ Configuration

### Framework Settings (`config.py`)

Controls framework behavior - **you typically don't need to modify this**:

```python
# Consensus settings
CONSENSUS_ITERATIONS = 5           # Number of API calls
CONSENSUS_THRESHOLD_RATIO = 0.6    # 60% agreement required

# LLM provider
DEFAULT_ADAPTER_TYPE = "groq"      # or "gpt", "gemini", "mock"

# Database
DATABASE_PATH = "validation_logs.db"
```

### Domain Settings (`examples/domains/your_config.py`)

Define what you're validating:

```python
VALIDATION_TASK = "your task description"
ITEMS_TO_VALIDATE = ["item1", "item2", ...]
VALIDATION_SCHEMA = YourPydanticModel
```

## 🔌 Supported Providers

| Provider | Model Example | API Key Env Var |
|----------|---------------|-----------------|
| **Groq** | `llama-3.3-70b-versatile` | `GROQ_API_KEY` |
| **OpenAI** | `gpt-4o` | `OPENAI_API_KEY` |
| **Gemini** | `gemini-2.5-flash-lite` | `GENAI_API_KEY` |

Add custom adapters by extending `LLMAdapter` in `adapters/`.

## 📊 Database Logging

Every validation response is logged to SQLite:

```sql
-- View session results
SELECT * FROM validation_responses 
WHERE session_id = 'session_20260119_065500_abc123';

-- Analyze consensus patterns
SELECT item_name, field_name, field_value, COUNT(*) as votes
FROM validation_responses 
WHERE session_id = 'your_session' AND is_error = 0
GROUP BY item_name, field_name, field_value
ORDER BY item_name, votes DESC;
```

## 🧪 Testing

The project includes a comprehensive test suite with 13+ tests covering core functionality.

### Run All Tests
```bash
uv run pytest tests/ -v
```

### Run Specific Test Files
```bash
# Test database logging
uv run pytest tests/test_db_logger.py -v

# Test adapters
uv run pytest tests/test_adapters.py -v

# Test models
uv run pytest tests/test_models.py -v

# Integration tests
uv run pytest tests/test_integration.py -v
```

### Test Coverage
```bash
# Install coverage tool
uv add --dev pytest-cov

# Run with coverage report
uv run pytest tests/ --cov=core --cov=adapters --cov=models
```

## 🏗️ Architecture

```
guardrails_validator/
├── core/
│   ├── verifier.py      # Consensus verification logic
│   └── db_logger.py     # SQLite logging
├── adapters/            # LLM provider adapters
│   ├── groq_adapter.py
│   ├── gpt_adapter.py
│   └── gemini_adapter.py
├── models.py            # Pydantic schemas
├── config.py            # Configuration
└── main.py              # Entry point
```

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

Built with [Guardrails AI](https://guardrailsai.com/) and powered by various LLM providers.

---

**⭐ Star this repo if you find it useful!**
