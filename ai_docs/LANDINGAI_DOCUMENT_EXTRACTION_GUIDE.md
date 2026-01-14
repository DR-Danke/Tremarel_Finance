# LandingAI Document Extraction Guide

A comprehensive guide for implementing AI-powered document data extraction using LandingAI's Agentic Document Extraction (ADE) API.

**Version:** 1.0
**Last Updated:** January 2026

---

## Table of Contents

1. [Overview](#overview)
2. [How It Works](#how-it-works)
3. [Getting Started](#getting-started)
4. [API Reference](#api-reference)
5. [Schema Design](#schema-design)
6. [Implementation Patterns](#implementation-patterns)
7. [Error Handling](#error-handling)
8. [Validation Strategies](#validation-strategies)
9. [3-Tier Fallback Architecture](#3-tier-fallback-architecture)
10. [Performance & Cost](#performance--cost)
11. [Complete Code Examples](#complete-code-examples)
12. [Troubleshooting](#troubleshooting)

---

## Overview

LandingAI's **ADE (Agentic Document Extraction)** is an AI-powered service that extracts structured data from documents (PDFs, images) using a two-step process:

1. **Parse**: Convert document to structured markdown (preserving tables, headers, formatting)
2. **Extract**: Use a JSON schema to extract specific fields from the markdown

### Key Benefits

- **Format-agnostic**: Works with PDFs, scanned documents, and images
- **Schema-driven**: Define exactly what data you need using JSON Schema
- **Table-aware**: Accurately extracts data from complex tables
- **Multi-page support**: Handles multi-page documents seamlessly

### Use Cases

- Invoice processing and data capture
- Financial statement extraction
- Contract data extraction
- Form processing (tax forms, applications, etc.)
- Identity document parsing (IDs, certificates)
- Any structured document with predictable fields

---

## How It Works

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   Document      │      │   ADE Parse     │      │   ADE Extract   │
│   (PDF/Image)   │─────▶│   API           │─────▶│   API           │
│                 │      │                 │      │                 │
│                 │      │ Returns:        │      │ Input:          │
│                 │      │ - Markdown      │      │ - Markdown      │
│                 │      │ - Chunks        │      │ - JSON Schema   │
│                 │      │ - Bounding boxes│      │                 │
└─────────────────┘      └─────────────────┘      │ Returns:        │
                                                  │ - Structured    │
                                                  │   JSON data     │
                                                  └─────────────────┘
```

### Step 1: Parse (Document → Markdown)

The Parse API uses AI vision models to:
- Read text from the document (including scanned/handwritten)
- Detect and preserve table structures
- Identify headers, sections, and formatting
- Output clean markdown that represents the document

### Step 2: Extract (Markdown → Structured JSON)

The Extract API uses LLMs to:
- Read the markdown representation
- Match content to your JSON schema fields
- Return structured data with the exact fields you defined

---

## Getting Started

### Prerequisites

1. **LandingAI Account**: Sign up at [landing.ai](https://landing.ai)
2. **API Key**: Generate from the LandingAI dashboard
3. **HTTP Client**: Any language with HTTP support (Python requests, Node.js axios, etc.)

### Environment Setup

```bash
# Required environment variables
LANDINGAI_API_KEY=your_api_key_here

# API Endpoints (these are the current production endpoints)
LANDINGAI_PARSE_ENDPOINT=https://api.va.landing.ai/v1/ade/parse
LANDINGAI_EXTRACT_ENDPOINT=https://api.va.landing.ai/v1/ade/extract
```

### Quick Start (Python)

```python
import os
import json
import requests

API_KEY = os.getenv("LANDINGAI_API_KEY")
PARSE_URL = "https://api.va.landing.ai/v1/ade/parse"
EXTRACT_URL = "https://api.va.landing.ai/v1/ade/extract"

headers = {"Authorization": f"Bearer {API_KEY}"}

# Step 1: Parse document to markdown
with open("document.pdf", "rb") as f:
    files = {"document": ("document.pdf", f, "application/pdf")}
    response = requests.post(PARSE_URL, headers=headers, files=files, timeout=120)

markdown = response.json()["markdown"]

# Step 2: Extract data using schema
schema = {
    "type": "object",
    "properties": {
        "company_name": {"type": "string"},
        "total_amount": {"type": "number"}
    }
}

data = {"schema": json.dumps(schema), "markdown": markdown}
response = requests.post(EXTRACT_URL, headers=headers, data=data, timeout=120)

extracted_data = response.json()["extraction"]
print(extracted_data)
# {"company_name": "Acme Corp", "total_amount": 15000.00}
```

---

## API Reference

### ADE Parse API

**Endpoint:** `POST https://api.va.landing.ai/v1/ade/parse`

**Purpose:** Convert documents (PDF/images) to structured markdown.

#### Request

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `document` | File | Yes | The document file (PDF, PNG, JPEG) |

**Headers:**
```
Authorization: Bearer {API_KEY}
Content-Type: multipart/form-data
```

**Supported Content Types:**
- `application/pdf` - PDF documents
- `image/png` - PNG images
- `image/jpeg` - JPEG images

#### Response (HTTP 200)

```json
{
    "markdown": "# Document Title\n\nContent...\n\n| Column1 | Column2 |\n|---------|---------|...",
    "chunks": [
        {
            "type": "text",
            "markdown": "# Document Title\n\nSome text...",
            "bbox": [0, 0, 100, 50],
            "index": 0
        },
        {
            "type": "table",
            "markdown": "| Header1 | Header2 |\n|---------|---------|...",
            "bbox": [0, 50, 100, 200],
            "index": 1
        }
    ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `markdown` | string | Full document as markdown |
| `chunks` | array | Document sections with type and position |
| `chunks[].type` | string | "text" or "table" |
| `chunks[].bbox` | array | Bounding box coordinates [x1, y1, x2, y2] |

---

### ADE Extract API

**Endpoint:** `POST https://api.va.landing.ai/v1/ade/extract`

**Purpose:** Extract structured data from markdown using a JSON schema.

#### Request

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `markdown` | string | Yes | Markdown from Parse API |
| `schema` | string | Yes | JSON Schema (stringified) defining fields to extract |

**Headers:**
```
Authorization: Bearer {API_KEY}
Content-Type: application/x-www-form-urlencoded
```

**Important:** Send as form data (`data=`), NOT JSON (`json=`).

#### Response (HTTP 200 - Full Success)

```json
{
    "extraction": {
        "company_name": "Acme Corporation",
        "total_amount": 15000.00,
        "invoice_date": "2025-01-15"
    }
}
```

#### Response (HTTP 206 - Partial Success)

```json
{
    "extraction": {
        "company_name": "Acme Corporation",
        "total_amount": 15000.00,
        "invoice_date": null
    },
    "metadata": {
        "schema_violation_error": "Field 'invoice_date' could not be extracted"
    }
}
```

#### HTTP Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Full success - all fields extracted | Use data directly |
| 206 | Partial success - some fields missing | Data is usable, check null fields |
| 400 | Bad request - invalid schema or markdown | Fix request format |
| 401 | Unauthorized - invalid API key | Check API key |
| 429 | Rate limited | Implement backoff/retry |
| 500 | Server error | Retry with exponential backoff |

**Note:** HTTP 206 is common and expected when optional fields cannot be found. The extraction data is still valid.

---

## Schema Design

The extraction schema uses [JSON Schema](https://json-schema.org/) format. Well-designed schemas are critical for accurate extraction.

### Basic Schema Structure

```json
{
    "type": "object",
    "properties": {
        "field_name": {
            "type": "string|number|integer|boolean|array|object",
            "description": "Clear description of what this field contains"
        }
    },
    "required": ["field1", "field2"]
}
```

### Supported Field Types

| Type | JSON Schema | Example Value |
|------|-------------|---------------|
| String | `"type": "string"` | `"Acme Corp"` |
| Number | `"type": "number"` | `15000.50` |
| Integer | `"type": "integer"` | `2025` |
| Boolean | `"type": "boolean"` | `true` |
| Array | `"type": "array"` | `[...]` |
| Object | `"type": "object"` | `{...}` |
| Nullable | `"type": ["string", "null"]` | `"value"` or `null` |

### Best Practices

#### 1. Use Descriptive Field Descriptions

```json
{
    "total_fob_usd": {
        "type": "number",
        "description": "Total FOB (Free On Board) value in US Dollars, found in the summary section"
    }
}
```

The description helps the LLM locate and interpret the correct value.

#### 2. Make Optional Fields Nullable

```json
{
    "secondary_contact": {
        "type": ["string", "null"],
        "description": "Secondary contact name, if present"
    }
}
```

This prevents HTTP 206 errors for truly optional fields.

#### 3. Use Required Sparingly

Only mark fields as `required` if extraction should fail without them:

```json
{
    "properties": {
        "invoice_number": {"type": "string"},
        "total_amount": {"type": "number"},
        "notes": {"type": ["string", "null"]}
    },
    "required": ["invoice_number", "total_amount"]
}
```

#### 4. Handle Arrays for Repeating Data

```json
{
    "line_items": {
        "type": "array",
        "description": "All line items from the invoice",
        "items": {
            "type": "object",
            "properties": {
                "description": {"type": "string"},
                "quantity": {"type": "number"},
                "unit_price": {"type": "number"},
                "total": {"type": "number"}
            }
        }
    }
}
```

#### 5. Handle Multi-Period/Multi-Year Documents

```json
{
    "financial_data_by_year": {
        "type": "array",
        "description": "Extract financial data for ALL available years in the document",
        "items": {
            "type": "object",
            "properties": {
                "year": {"type": "integer"},
                "revenue": {"type": "number"},
                "expenses": {"type": "number"}
            }
        }
    }
}
```

---

## Implementation Patterns

### Pattern 1: Simple Single-Document Extraction

```python
class SimpleExtractor:
    """Basic document extraction for single documents."""

    def __init__(self, api_key: str, schema: dict):
        self.api_key = api_key
        self.schema = schema
        self.headers = {"Authorization": f"Bearer {api_key}"}

    def extract(self, file_path: str) -> dict:
        # Parse
        markdown = self._parse_document(file_path)

        # Extract
        return self._extract_data(markdown)

    def _parse_document(self, file_path: str) -> str:
        content_type = self._get_content_type(file_path)

        with open(file_path, "rb") as f:
            files = {"document": (file_path, f, content_type)}
            response = requests.post(
                "https://api.va.landing.ai/v1/ade/parse",
                headers=self.headers,
                files=files,
                timeout=120
            )

        response.raise_for_status()
        return response.json()["markdown"]

    def _extract_data(self, markdown: str) -> dict:
        data = {
            "schema": json.dumps(self.schema),
            "markdown": markdown
        }

        response = requests.post(
            "https://api.va.landing.ai/v1/ade/extract",
            headers=self.headers,
            data=data,
            timeout=120
        )

        if response.status_code not in [200, 206]:
            response.raise_for_status()

        return response.json()["extraction"]

    def _get_content_type(self, file_path: str) -> str:
        ext = file_path.lower().split(".")[-1]
        return {
            "pdf": "application/pdf",
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg"
        }.get(ext, "application/pdf")
```

### Pattern 2: Batch Processing with Retries

```python
import time
from typing import List, Optional

class BatchExtractor:
    """Process multiple documents with retry logic."""

    def __init__(self, api_key: str, schema: dict, max_retries: int = 3):
        self.extractor = SimpleExtractor(api_key, schema)
        self.max_retries = max_retries

    def extract_batch(self, file_paths: List[str]) -> List[dict]:
        results = []

        for file_path in file_paths:
            result = self._extract_with_retry(file_path)
            results.append({
                "file": file_path,
                "success": result is not None,
                "data": result
            })

        return results

    def _extract_with_retry(self, file_path: str) -> Optional[dict]:
        for attempt in range(self.max_retries):
            try:
                return self.extractor.extract(file_path)
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:  # Rate limited
                    wait_time = 2 ** attempt  # Exponential backoff
                    time.sleep(wait_time)
                elif e.response.status_code >= 500:  # Server error
                    time.sleep(1)
                else:
                    raise  # Client error, don't retry
            except requests.exceptions.Timeout:
                time.sleep(1)

        return None  # All retries failed
```

### Pattern 3: Caching Layer

```python
import hashlib
import json
from pathlib import Path

class CachedExtractor:
    """Cache extraction results to avoid re-processing."""

    def __init__(self, api_key: str, schema: dict, cache_dir: str = ".extraction_cache"):
        self.extractor = SimpleExtractor(api_key, schema)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.schema_hash = self._hash_schema(schema)

    def extract(self, file_path: str, use_cache: bool = True) -> dict:
        cache_key = self._get_cache_key(file_path)
        cache_file = self.cache_dir / f"{cache_key}.json"

        # Check cache
        if use_cache and cache_file.exists():
            with open(cache_file) as f:
                return json.load(f)

        # Extract and cache
        result = self.extractor.extract(file_path)

        with open(cache_file, "w") as f:
            json.dump(result, f)

        return result

    def _get_cache_key(self, file_path: str) -> str:
        with open(file_path, "rb") as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        return f"{file_hash}_{self.schema_hash}"

    def _hash_schema(self, schema: dict) -> str:
        return hashlib.md5(json.dumps(schema, sort_keys=True).encode()).hexdigest()[:8]
```

---

## Error Handling

### Comprehensive Error Handler

```python
class ExtractionError(Exception):
    """Base exception for extraction errors."""
    pass

class ParseError(ExtractionError):
    """Document parsing failed."""
    pass

class ExtractError(ExtractionError):
    """Data extraction failed."""
    pass

class ValidationError(ExtractionError):
    """Extracted data failed validation."""
    pass


def safe_extract(extractor, file_path: str, validator=None) -> dict:
    """
    Safely extract data with comprehensive error handling.

    Returns:
        {
            "success": bool,
            "data": dict or None,
            "error": str or None,
            "error_type": str or None
        }
    """
    try:
        data = extractor.extract(file_path)

        # Optional validation
        if validator and not validator(data):
            return {
                "success": False,
                "data": data,
                "error": "Validation failed",
                "error_type": "validation"
            }

        return {
            "success": True,
            "data": data,
            "error": None,
            "error_type": None
        }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "data": None,
            "error": "Request timed out (120s)",
            "error_type": "timeout"
        }

    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        error_messages = {
            400: "Invalid request - check schema format",
            401: "Invalid API key",
            429: "Rate limit exceeded",
            500: "LandingAI server error"
        }
        return {
            "success": False,
            "data": None,
            "error": error_messages.get(status_code, f"HTTP {status_code}"),
            "error_type": "http_error"
        }

    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": str(e),
            "error_type": "unknown"
        }
```

---

## Validation Strategies

### Strategy 1: Field Completeness Check

```python
def validate_completeness(data: dict, required_fields: List[str], min_coverage: float = 0.8) -> tuple:
    """
    Check if enough fields were extracted.

    Returns:
        (is_valid: bool, coverage: float, missing: List[str])
    """
    missing = [f for f in required_fields if data.get(f) is None]
    coverage = 1 - (len(missing) / len(required_fields))

    return coverage >= min_coverage, coverage, missing
```

### Strategy 2: Financial Validation (Accounting Equation)

```python
def validate_financial_data(data: dict, tolerance: float = 0.05) -> tuple:
    """
    Validate financial data using accounting rules.

    Checks:
    1. Assets = Liabilities + Equity (±tolerance)
    2. Gross Profit = Revenue - COGS (±tolerance)

    Returns:
        (is_valid: bool, errors: List[str])
    """
    errors = []

    # Check accounting equation
    assets = data.get("total_assets", 0)
    liabilities = data.get("total_liabilities", 0)
    equity = data.get("total_equity", 0)

    if assets > 0:
        expected = liabilities + equity
        diff_pct = abs(assets - expected) / assets
        if diff_pct > tolerance:
            errors.append(f"Accounting equation off by {diff_pct:.1%}")

    # Check gross profit calculation
    revenue = data.get("revenue", 0)
    cogs = data.get("cost_of_goods_sold", 0)
    gross_profit = data.get("gross_profit", 0)

    if revenue > 0 and cogs > 0 and gross_profit > 0:
        expected_gross = revenue - cogs
        diff_pct = abs(gross_profit - expected_gross) / revenue
        if diff_pct > tolerance:
            errors.append(f"Gross profit calculation off by {diff_pct:.1%}")

    return len(errors) == 0, errors
```

### Strategy 3: Cross-Document Validation

```python
def validate_cross_document(doc1_data: dict, doc2_data: dict, match_fields: List[str]) -> tuple:
    """
    Validate that matching fields are consistent across documents.

    Use case: Compare company name from invoice vs contract.

    Returns:
        (is_valid: bool, mismatches: List[dict])
    """
    mismatches = []

    for field in match_fields:
        val1 = doc1_data.get(field)
        val2 = doc2_data.get(field)

        if val1 and val2:
            # Normalize strings for comparison
            if isinstance(val1, str) and isinstance(val2, str):
                if val1.lower().strip() != val2.lower().strip():
                    mismatches.append({
                        "field": field,
                        "doc1_value": val1,
                        "doc2_value": val2
                    })
            elif val1 != val2:
                mismatches.append({
                    "field": field,
                    "doc1_value": val1,
                    "doc2_value": val2
                })

    return len(mismatches) == 0, mismatches
```

---

## 3-Tier Fallback Architecture

For production systems, implement a fallback strategy to maximize extraction success:

```
┌─────────────────────────────────────────────────────────────────┐
│  TIER 1: LandingAI ADE (Primary)                                │
│  - Most accurate for structured documents                        │
│  - Schema-validated output                                       │
│  - Cost: $0.30-$4.00 per document                               │
└─────────────────────────┬───────────────────────────────────────┘
                          │ If fails or low confidence
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  TIER 2: GPT-4 Vision (Fallback)                                │
│  - Handles complex/unusual layouts                               │
│  - Good for scanned documents                                    │
│  - Cost: $0.10-$1.00 per document                               │
└─────────────────────────┬───────────────────────────────────────┘
                          │ If fails
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  TIER 3: Pattern Matching (Last Resort)                         │
│  - Regex-based extraction                                        │
│  - Fast and free                                                 │
│  - Limited to well-known formats                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Implementation

```python
import re
import openai
from typing import Optional

class TieredExtractor:
    """
    3-tier extraction system with intelligent fallbacks.
    """

    def __init__(
        self,
        landingai_key: str,
        openai_key: str,
        schema: dict,
        patterns: dict = None
    ):
        self.landingai_extractor = SimpleExtractor(landingai_key, schema)
        self.openai_client = openai.OpenAI(api_key=openai_key)
        self.schema = schema
        self.patterns = patterns or {}  # Regex patterns for Tier 3

    def extract(self, file_path: str) -> dict:
        """
        Extract data using 3-tier approach.

        Returns:
            {
                "data": dict,
                "tier": int,
                "method": str,
                "confidence": float
            }
        """
        # TIER 1: LandingAI ADE
        result = self._try_tier1(file_path)
        if result:
            return result

        # TIER 2: GPT-4 Vision
        result = self._try_tier2(file_path)
        if result:
            return result

        # TIER 3: Pattern Matching
        return self._try_tier3(file_path)

    def _try_tier1(self, file_path: str) -> Optional[dict]:
        """Attempt LandingAI ADE extraction."""
        try:
            data = self.landingai_extractor.extract(file_path)

            # Validate minimum field coverage
            non_null = sum(1 for v in data.values() if v is not None)
            coverage = non_null / len(self.schema["properties"])

            if coverage >= 0.7:  # At least 70% fields extracted
                return {
                    "data": data,
                    "tier": 1,
                    "method": "landingai_ade",
                    "confidence": coverage
                }
        except Exception as e:
            print(f"Tier 1 failed: {e}")

        return None

    def _try_tier2(self, file_path: str) -> Optional[dict]:
        """Attempt GPT-4 Vision extraction."""
        try:
            import base64

            # Convert PDF to images if needed, or read image directly
            with open(file_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode()

            # Build prompt from schema
            fields_desc = "\n".join([
                f"- {k}: {v.get('description', v.get('type', 'unknown'))}"
                for k, v in self.schema["properties"].items()
            ])

            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Extract the following fields from this document:\n{fields_desc}\n\nReturn as JSON."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_data}"
                            }
                        }
                    ]
                }],
                response_format={"type": "json_object"}
            )

            data = json.loads(response.choices[0].message.content)
            return {
                "data": data,
                "tier": 2,
                "method": "gpt4_vision",
                "confidence": 0.8
            }
        except Exception as e:
            print(f"Tier 2 failed: {e}")

        return None

    def _try_tier3(self, file_path: str) -> dict:
        """Fall back to regex pattern matching."""
        import fitz  # PyMuPDF

        # Extract text from PDF
        doc = fitz.open(file_path)
        text = "\n".join(page.get_text() for page in doc)
        doc.close()

        data = {}
        for field, pattern in self.patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                data[field] = match.group(1).strip()

        return {
            "data": data,
            "tier": 3,
            "method": "pattern_matching",
            "confidence": 0.5
        }
```

---

## Performance & Cost

### Performance Characteristics

| Operation | Typical Time | Notes |
|-----------|--------------|-------|
| ADE Parse | 10-30 seconds | Depends on document complexity |
| ADE Extract | 5-15 seconds | Depends on schema complexity |
| Total (Parse + Extract) | 15-45 seconds | Plan for ~120s timeout |

### Cost Estimates

| Method | Cost Range | Best For |
|--------|------------|----------|
| LandingAI ADE | $0.30 - $4.00/doc | Structured documents, tables |
| GPT-4 Vision | $0.10 - $1.00/doc | Complex layouts, scans |
| Pattern Matching | Free | Known formats, simple docs |

### Optimization Tips

1. **Cache results**: Store extraction results keyed by document hash + schema hash
2. **Batch during off-peak**: If not time-sensitive, batch process overnight
3. **Use appropriate tier**: Don't use Tier 1 for simple forms that Tier 3 handles well
4. **Optimize schemas**: Smaller schemas = faster extraction
5. **Pre-filter documents**: Validate file size/type before sending to API

---

## Complete Code Examples

### Example 1: Invoice Extractor

```python
"""
Complete invoice extraction example with validation.
"""

import os
import json
import requests
from datetime import datetime
from typing import Optional

class InvoiceExtractor:
    """
    Extract structured data from invoice documents.
    """

    SCHEMA = {
        "type": "object",
        "properties": {
            "invoice_number": {
                "type": "string",
                "description": "Invoice number or ID"
            },
            "invoice_date": {
                "type": "string",
                "description": "Invoice date in YYYY-MM-DD format"
            },
            "due_date": {
                "type": ["string", "null"],
                "description": "Payment due date in YYYY-MM-DD format"
            },
            "vendor_name": {
                "type": "string",
                "description": "Name of the vendor/supplier"
            },
            "vendor_tax_id": {
                "type": ["string", "null"],
                "description": "Vendor tax ID or registration number"
            },
            "customer_name": {
                "type": ["string", "null"],
                "description": "Name of the customer/buyer"
            },
            "subtotal": {
                "type": ["number", "null"],
                "description": "Subtotal before tax"
            },
            "tax_amount": {
                "type": ["number", "null"],
                "description": "Total tax amount"
            },
            "total_amount": {
                "type": "number",
                "description": "Total invoice amount including tax"
            },
            "currency": {
                "type": "string",
                "description": "Currency code (USD, EUR, MXN, etc.)"
            },
            "line_items": {
                "type": "array",
                "description": "List of line items on the invoice",
                "items": {
                    "type": "object",
                    "properties": {
                        "description": {"type": "string"},
                        "quantity": {"type": ["number", "null"]},
                        "unit_price": {"type": ["number", "null"]},
                        "total": {"type": "number"}
                    }
                }
            }
        },
        "required": ["invoice_number", "vendor_name", "total_amount"]
    }

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {"Authorization": f"Bearer {api_key}"}
        self.parse_url = "https://api.va.landing.ai/v1/ade/parse"
        self.extract_url = "https://api.va.landing.ai/v1/ade/extract"

    def extract(self, file_path: str) -> dict:
        """
        Extract invoice data from a document.

        Args:
            file_path: Path to PDF or image file

        Returns:
            {
                "success": bool,
                "data": dict or None,
                "validation": dict,
                "raw_markdown": str
            }
        """
        # Step 1: Parse
        markdown = self._parse(file_path)

        # Step 2: Extract
        data = self._extract(markdown)

        # Step 3: Validate
        validation = self._validate(data)

        return {
            "success": validation["is_valid"],
            "data": data,
            "validation": validation,
            "raw_markdown": markdown
        }

    def _parse(self, file_path: str) -> str:
        ext = file_path.lower().split(".")[-1]
        content_types = {
            "pdf": "application/pdf",
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg"
        }

        with open(file_path, "rb") as f:
            files = {"document": (file_path, f, content_types.get(ext, "application/pdf"))}
            response = requests.post(
                self.parse_url,
                headers=self.headers,
                files=files,
                timeout=120
            )

        response.raise_for_status()
        return response.json()["markdown"]

    def _extract(self, markdown: str) -> dict:
        data = {
            "schema": json.dumps(self.SCHEMA),
            "markdown": markdown
        }

        response = requests.post(
            self.extract_url,
            headers=self.headers,
            data=data,
            timeout=120
        )

        if response.status_code not in [200, 206]:
            response.raise_for_status()

        return response.json().get("extraction", {})

    def _validate(self, data: dict) -> dict:
        errors = []
        warnings = []

        # Check required fields
        required = ["invoice_number", "vendor_name", "total_amount"]
        for field in required:
            if not data.get(field):
                errors.append(f"Missing required field: {field}")

        # Validate totals math
        subtotal = data.get("subtotal", 0) or 0
        tax = data.get("tax_amount", 0) or 0
        total = data.get("total_amount", 0) or 0

        if subtotal > 0 and tax >= 0:
            expected_total = subtotal + tax
            if abs(total - expected_total) > 0.01:
                warnings.append(f"Total mismatch: {total} != {subtotal} + {tax}")

        # Validate line items
        line_items = data.get("line_items", [])
        if line_items:
            items_total = sum(item.get("total", 0) or 0 for item in line_items)
            if subtotal > 0 and abs(items_total - subtotal) > 1:
                warnings.append(f"Line items sum ({items_total}) doesn't match subtotal ({subtotal})")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "field_coverage": sum(1 for v in data.values() if v is not None) / len(self.SCHEMA["properties"])
        }


# Usage
if __name__ == "__main__":
    extractor = InvoiceExtractor(api_key=os.getenv("LANDINGAI_API_KEY"))

    result = extractor.extract("invoice.pdf")

    if result["success"]:
        print("Extraction successful!")
        print(json.dumps(result["data"], indent=2))
    else:
        print("Extraction failed:")
        for error in result["validation"]["errors"]:
            print(f"  - {error}")
```

### Example 2: Financial Statement Extractor

```python
"""
Extract key metrics from financial statements.
"""

class FinancialStatementExtractor:
    """
    Extract financial metrics from income statements and balance sheets.
    """

    SCHEMA = {
        "type": "object",
        "properties": {
            # Income Statement
            "revenue": {
                "type": "number",
                "description": "Total revenue/sales for the period"
            },
            "cost_of_goods_sold": {
                "type": ["number", "null"],
                "description": "Cost of goods sold (COGS)"
            },
            "gross_profit": {
                "type": ["number", "null"],
                "description": "Gross profit (Revenue - COGS)"
            },
            "operating_expenses": {
                "type": ["number", "null"],
                "description": "Total operating expenses"
            },
            "operating_income": {
                "type": ["number", "null"],
                "description": "Operating income (EBIT)"
            },
            "net_income": {
                "type": "number",
                "description": "Net income/profit for the period"
            },

            # Balance Sheet
            "total_assets": {
                "type": "number",
                "description": "Total assets"
            },
            "current_assets": {
                "type": ["number", "null"],
                "description": "Current assets"
            },
            "total_liabilities": {
                "type": "number",
                "description": "Total liabilities"
            },
            "current_liabilities": {
                "type": ["number", "null"],
                "description": "Current liabilities"
            },
            "total_equity": {
                "type": "number",
                "description": "Total shareholders equity"
            },

            # Metadata
            "period_end_date": {
                "type": "string",
                "description": "End date of the reporting period (YYYY-MM-DD)"
            },
            "currency": {
                "type": "string",
                "description": "Reporting currency (USD, EUR, etc.)"
            },
            "fiscal_year": {
                "type": "integer",
                "description": "Fiscal year"
            }
        },
        "required": ["revenue", "net_income", "total_assets", "total_liabilities", "total_equity"]
    }

    def __init__(self, api_key: str):
        self.extractor = SimpleExtractor(api_key, self.SCHEMA)

    def extract(self, file_path: str) -> dict:
        data = self.extractor.extract(file_path)

        # Calculate derived metrics
        data["metrics"] = self._calculate_metrics(data)

        # Validate
        validation = self._validate(data)

        return {
            "data": data,
            "validation": validation
        }

    def _calculate_metrics(self, data: dict) -> dict:
        """Calculate key financial ratios."""
        metrics = {}

        revenue = data.get("revenue", 0)
        net_income = data.get("net_income", 0)
        total_assets = data.get("total_assets", 0)
        total_equity = data.get("total_equity", 0)
        current_assets = data.get("current_assets", 0)
        current_liabilities = data.get("current_liabilities", 0)

        # Profitability ratios
        if revenue > 0:
            metrics["net_profit_margin"] = round(net_income / revenue * 100, 2)

        if total_assets > 0:
            metrics["return_on_assets"] = round(net_income / total_assets * 100, 2)

        if total_equity > 0:
            metrics["return_on_equity"] = round(net_income / total_equity * 100, 2)

        # Liquidity ratio
        if current_liabilities > 0 and current_assets > 0:
            metrics["current_ratio"] = round(current_assets / current_liabilities, 2)

        return metrics

    def _validate(self, data: dict) -> dict:
        """Validate using accounting equation."""
        errors = []

        assets = data.get("total_assets", 0)
        liabilities = data.get("total_liabilities", 0)
        equity = data.get("total_equity", 0)

        if assets > 0:
            expected = liabilities + equity
            diff_pct = abs(assets - expected) / assets
            if diff_pct > 0.05:  # 5% tolerance
                errors.append(
                    f"Accounting equation violation: Assets ({assets}) != "
                    f"Liabilities ({liabilities}) + Equity ({equity})"
                )

        return {
            "is_valid": len(errors) == 0,
            "errors": errors
        }
```

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| HTTP 401 | Invalid API key | Verify `LANDINGAI_API_KEY` is correct |
| HTTP 206 | Some fields not found | Use nullable types for optional fields |
| HTTP 429 | Rate limited | Implement exponential backoff |
| Timeout | Large/complex document | Increase timeout to 180s+ |
| Empty extraction | Poor schema descriptions | Add detailed `description` fields |
| Wrong values | Ambiguous field names | Make descriptions more specific |

### Debugging Tips

1. **Check the markdown**: Always inspect the Parse API markdown output first. If the document wasn't parsed correctly, extraction will fail.

2. **Test with simple schemas**: Start with a minimal schema (1-2 fields) and expand gradually.

3. **Use descriptive field names**: Field names like `total` are ambiguous. Use `invoice_total_amount` instead.

4. **Log intermediate results**: Log markdown length, chunk count, and extraction response status.

5. **Validate document quality**: Low-resolution scans or rotated documents may parse poorly.

### Debug Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("document_extraction")

def extract_with_logging(file_path: str):
    logger.info(f"Processing: {file_path}")

    # Parse
    logger.debug("Calling ADE Parse API...")
    parse_response = requests.post(...)
    logger.debug(f"Parse status: {parse_response.status_code}")

    markdown = parse_response.json().get("markdown", "")
    logger.info(f"Markdown length: {len(markdown)} chars")
    logger.debug(f"Markdown preview: {markdown[:500]}...")

    # Extract
    logger.debug("Calling ADE Extract API...")
    extract_response = requests.post(...)
    logger.debug(f"Extract status: {extract_response.status_code}")

    if extract_response.status_code == 206:
        logger.warning(f"Partial extraction: {extract_response.json().get('metadata', {})}")

    extraction = extract_response.json().get("extraction", {})
    logger.info(f"Extracted {len(extraction)} fields")

    return extraction
```

---

## Additional Resources

- **LandingAI Documentation**: [docs.landing.ai](https://docs.landing.ai)
- **JSON Schema Reference**: [json-schema.org](https://json-schema.org)
- **OpenAI Vision API** (for Tier 2 fallback): [platform.openai.com/docs](https://platform.openai.com/docs)

---

## Summary

1. **ADE Parse** converts documents to markdown (preserves structure)
2. **ADE Extract** uses JSON schemas to pull specific fields
3. **HTTP 206** is acceptable - partial data is still valid
4. **Design schemas carefully** - descriptions matter
5. **Implement fallbacks** for production reliability
6. **Cache results** to avoid re-processing costs
7. **Validate extracted data** using domain-specific rules

For questions or feedback, refer to the LandingAI documentation or open an issue in your project repository.
