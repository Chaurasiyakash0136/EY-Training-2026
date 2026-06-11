# Document Summarisation API Assignment
=== SECTION A — ARCHITECTURE BRIEF ===

This service is an AI-powered Document Summarisation API implemented using FastAPI and designed with production-oriented software engineering practices. A client sends a POST request containing document text and a requested summarisation style (`brief` or `detailed`) to the `/summarize` endpoint. The request first passes through middleware that generates a unique request ID, records latency, and updates Prometheus metrics for observability. The request payload is validated using Pydantic models before business logic is executed. Based on the selected style, the service constructs a targeted prompt and sends it to an OpenAI language model. The generated summary is returned as structured JSON. Configuration is externalised into a YAML file and validated at startup. One design trade-off is choosing synchronous LLM calls instead of asynchronous background processing. This simplifies implementation and debugging, although high-throughput systems may benefit from queue-based processing and caching strategies.

=== SECTION B — CONFIG FILE AND LOADER ===

## B1. config.yaml

```yaml
service_name: document-summarization-api
port: 8000
log_level: INFO

llm:
  provider: openai
  model: gpt-4o-mini
  max_tokens: 300
```

## B2. Pydantic v2 Configuration Models and Loader

```python
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field


class LLMConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider: Literal["openai", "azure_openai", "anthropic"]
    model: str
    max_tokens: int = Field(gt=0, le=4000)


class AppConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    service_name: str
    port: int = Field(gt=0, le=65535)
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"]
    llm: LLMConfig


def load_config(path: str) -> AppConfig:
    with open(path, "r", encoding="utf-8") as file:
        raw_config = yaml.safe_load(file)

    return AppConfig.model_validate(raw_config)
```

=== SECTION C — REQUEST / RESPONSE SCHEMAS ===

```python
from typing import Literal

from pydantic import BaseModel, Field


class SummariseRequest(BaseModel):
    text: str = Field(
        min_length=20,
        description="Text content that will be summarized"
    )
    style: Literal["brief", "detailed"]


class SummariseResponse(BaseModel):
    summary: str
    model: str
    input_chars: int
```

=== SECTION D — FASTAPI APP WITH /summarize ENDPOINT ===

```python
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from openai import OpenAI

client = OpenAI()


@asynccontextmanager
async def lifespan(app: FastAPI):

    config = load_config("config.yaml")

    logging.basicConfig(
        level=getattr(logging, config.log_level),
        format="%(asctime)s %(levelname)s %(message)s"
    )

    app.state.config = config
    app.state.ready = True

    yield

    app.state.ready = False


app = FastAPI(
    title="Document Summarisation API",
    version="1.0.0",
    lifespan=lifespan
)


@app.post(
    "/summarize",
    response_model=SummariseResponse
)
async def summarize(payload: SummariseRequest):

    config = app.state.config

    if payload.style == "brief":
        prompt = f"""
        You are a professional document summarization assistant.

        Requirements:
        - Preserve key facts
        - Avoid hallucinations
        - Use exactly 2 bullet points
        - Maximum 20 words per bullet

        Document:
        {payload.text}
        """
    else:
        prompt = f"""
        You are a professional document summarization assistant.

        Requirements:
        - Preserve key facts
        - Avoid hallucinations
        - Write a detailed summary
        - Use exactly 3 paragraphs

        Document:
        {payload.text}
        """

    try:
        response = client.chat.completions.create(
            model=config.llm.model,
            max_tokens=config.llm.max_tokens,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        summary_text = (
            response.choices[0]
            .message
            .content
            .strip()
        )

    except Exception as exc:
        logging.exception("LLM request failed")

        raise HTTPException(
            status_code=500,
            detail="Failed to generate summary"
        ) from exc

    return SummariseResponse(
        summary=summary_text,
        model=config.llm.model,
        input_chars=len(payload.text)
    )
```

=== SECTION E — MIDDLEWARE + METRICS + HEALTH/READY ===

## E1. Request Logging Middleware and Metrics

```python
import logging
import time
import uuid

from prometheus_client import Counter

REQUEST_COUNT = Counter(
    "request_count_total",
    "Total number of API requests",
    ["method", "path"]
)


@app.middleware("http")
async def logging_middleware(request, call_next):

    request_id = str(uuid.uuid4())
    start_time = time.perf_counter()

    response = await call_next(request)

    duration_ms = (
        time.perf_counter() - start_time
    ) * 1000

    REQUEST_COUNT.labels(
        method=request.method,
        path=request.url.path
    ).inc()

    logging.info(
        "request_completed | "
        f"request_id={request_id} "
        f"method={request.method} "
        f"path={request.url.path} "
        f"status_code={response.status_code} "
        f"duration_ms={duration_ms:.2f}"
    )

    response.headers["X-Request-ID"] = request_id

    return response
```

## E2. Health, Readiness and Metrics Endpoints

```python
from fastapi import Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    generate_latest
)


@app.get("/healthz")
async def healthz():
    return {"status": "alive"}


@app.get("/readyz")
async def readyz():

    if app.state.ready:
        return {"status": "ready"}

    return Response(
        content='{"status":"not_ready"}',
        status_code=503,
        media_type="application/json"
    )


@app.get("/metrics")
async def metrics():

    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
```
=== SECTION F — PYTEST TESTS ===

```python
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


@patch("app.client.chat.completions.create")
def test_summarize_happy_path_with_mocked_llm(mock_create):

    mock_response = MagicMock()

    mock_response.choices = [
        MagicMock(
            message=MagicMock(
                content="Mocked summary"
            )
        )
    ]

    mock_create.return_value = mock_response

    payload = {
        "text": (
            "This is a sample document used to validate "
            "the summarization endpoint during testing."
        ),
        "style": "brief"
    }

    response = client.post(
        "/summarize",
        json=payload
    )

    assert response.status_code == 200
    assert response.json()["summary"] == "Mocked summary"
    assert response.json()["model"] == "gpt-4o-mini"
    assert response.json()["input_chars"] > 0


def test_summarize_invalid_style_returns_422():

    payload = {
        "text": (
            "This text satisfies the minimum length "
            "requirement for request validation."
        ),
        "style": "unknown"
    }

    response = client.post(
        "/summarize",
        json=payload
    )

    assert response.status_code == 422


def test_healthz_returns_200_alive():

    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {
        "status": "alive"
    }
```

=== SECTION G — REFLECTION ===

Combining FastAPI, Pydantic, Prometheus, OpenAI integration, and pytest worked well because each component has a clearly defined responsibility and integrates cleanly with the others. Configuration validation, request validation, observability, and API routing could be developed independently and then assembled into a cohesive service. The most challenging aspect was designing the LLM integration in a way that remained fully testable without depending on an external provider during test execution. Mocking the OpenAI client solved this challenge and improved test reliability. If this application were deployed to production, the MLOps practice I would most strongly recommend retaining is observability through structured logging, metrics, and health/readiness probes. These capabilities provide visibility into service behaviour, simplify troubleshooting, support automated monitoring, and improve overall operational reliability in production environments.
