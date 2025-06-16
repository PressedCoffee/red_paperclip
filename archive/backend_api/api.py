"""
Backend API module for AWS / Dashboard.

Provides modular routes for:
- /agents
- /trades
- /coalitions
- /payments
- /capsules

Features:
- Basic API token guard with hardcoded secret for hackathon.
- Feature flag control to enable/disable API.
- Logging with correlation IDs for traceability.

JSON Response Examples:
- GET /agents
  {
    "timestamp": "2025-06-14T18:00:00Z",
    "agent_id": "agent_123",
    "correlation_id": "corr_abc123",
    "data": {...}
  }

- GET /trades
  {
    "timestamp": "2025-06-14T18:00:00Z",
    "trade_id": "trade_456",
    "correlation_id": "corr_def456",
    "data": {...}
  }

- GET /coalitions
  {
    "timestamp": "2025-06-14T18:00:00Z",
    "coalition_id": "coal_789",
    "correlation_id": "corr_ghi789",
    "data": {...}
  }

- GET /payments
  {
    "timestamp": "2025-06-14T18:00:00Z",
    "payment_id": "pay_101",
    "correlation_id": "corr_jkl101",
    "data": {...}
  }

- GET /capsules
  {
    "timestamp": "2025-06-14T18:00:00Z",
    "capsule_id": "cap_202",
    "correlation_id": "corr_mno202",
    "data": {...}
  }
"""

from datetime import datetime, timezone
from fastapi import FastAPI, Depends, HTTPException, Security, Request
from fastapi.security.api_key import APIKeyHeader
from fastapi.routing import APIRouter
from starlette.status import HTTP_403_FORBIDDEN
import logging
import uuid
import os

# Feature flag to enable/disable API
API_ENABLED = os.getenv("API_ENABLED", "true").lower() == "true"

# Feature flag to enable/disable Genesis Pad integration
ENABLE_GENESIS_PAD = os.getenv("ENABLE_GENESIS_PAD", "true").lower() == "true"

# Hardcoded API token for hackathon
API_TOKEN = "hackathon-secret-token"

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

app = FastAPI(title="AWS Backend API / Dashboard")

# Setup logger
logger = logging.getLogger("backend_api")
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")


def get_correlation_id(request: Request):
    # Extract correlation ID from headers or generate new
    corr_id = request.headers.get("X-Correlation-ID")
    if not corr_id:
        corr_id = str(uuid.uuid4())
    return corr_id


async def api_key_auth(api_key: str = Security(api_key_header)):
    if not API_ENABLED:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN,
                            detail="API is disabled by feature flag")
    if api_key != API_TOKEN:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN,
                            detail="Invalid API token")
    return api_key

# Define routers for each module
agents_router = APIRouter(prefix="/agents", tags=["agents"])
trades_router = APIRouter(prefix="/trades", tags=["trades"])
coalitions_router = APIRouter(prefix="/coalitions", tags=["coalitions"])
payments_router = APIRouter(prefix="/payments", tags=["payments"])
capsules_router = APIRouter(prefix="/capsules", tags=["capsules"])

# Sample data placeholders (to be replaced with real data sources)
sample_agents = [
    {"agent_id": "agent_123", "name": "Agent Smith", "status": "active"},
    {"agent_id": "agent_456", "name": "Agent Doe", "status": "inactive"},
]

sample_trades = [
    {"trade_id": "trade_001", "agent_id": "agent_123",
        "amount": 1000, "status": "completed"},
    {"trade_id": "trade_002", "agent_id": "agent_456",
        "amount": 500, "status": "pending"},
]

sample_coalitions = [
    {"coalition_id": "coal_001", "members": [
        "agent_123", "agent_456"], "status": "active"},
]

sample_payments = [
    {"payment_id": "pay_001", "agent_id": "agent_123",
        "amount": 100, "status": "processed"},
]

sample_capsules = [
    {"capsule_id": "cap_001", "agent_id": "agent_123",
        "content": "Capsule data here",
        "public_snippet": "This is the public snippet from Genesis Pad capsule."},
]


def build_response(data_key: str, data_id_key: str, data_item: dict, correlation_id: str):
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        data_id_key: data_item.get(data_id_key),
        "correlation_id": correlation_id,
        "data": data_item,
    }

# Agents endpoint


@agents_router.get("/", dependencies=[Depends(api_key_auth)])
async def get_agents(request: Request):
    correlation_id = get_correlation_id(request)
    logger.info(f"GET /agents called - correlation_id={correlation_id}")

    agents_with_snippet = []
    for agent in sample_agents:
        agent_copy = agent.copy()
        if ENABLE_GENESIS_PAD:
            # Find capsule for this agent
            capsule = next(
                (c for c in sample_capsules if c.get("agent_id") == agent.get("agent_id")), None)
            if capsule and "public_snippet" in capsule:
                agent_copy["public_snippet"] = capsule["public_snippet"]
            else:
                agent_copy["public_snippet"] = None
        agents_with_snippet.append(agent_copy)

    responses = [build_response(
        "agent_id", "agent_id", agent, correlation_id) for agent in agents_with_snippet]
    return responses

# Trades endpoint


@trades_router.get("/", dependencies=[Depends(api_key_auth)])
async def get_trades(request: Request):
    correlation_id = get_correlation_id(request)
    logger.info(f"GET /trades called - correlation_id={correlation_id}")
    responses = [build_response(
        "trade_id", "trade_id", trade, correlation_id) for trade in sample_trades]
    return responses

# Coalitions endpoint


@coalitions_router.get("/", dependencies=[Depends(api_key_auth)])
async def get_coalitions(request: Request):
    correlation_id = get_correlation_id(request)
    logger.info(f"GET /coalitions called - correlation_id={correlation_id}")
    responses = [build_response("coalition_id", "coalition_id",
                                coalition, correlation_id) for coalition in sample_coalitions]
    return responses

# Payments endpoint


@payments_router.get("/", dependencies=[Depends(api_key_auth)])
async def get_payments(request: Request):
    correlation_id = get_correlation_id(request)
    logger.info(f"GET /payments called - correlation_id={correlation_id}")
    responses = [build_response(
        "payment_id", "payment_id", payment, correlation_id) for payment in sample_payments]
    return responses

# Capsules endpoint


@capsules_router.get("/", dependencies=[Depends(api_key_auth)])
async def get_capsules(request: Request):
    correlation_id = get_correlation_id(request)
    logger.info(f"GET /capsules called - correlation_id={correlation_id}")
    responses = [build_response(
        "capsule_id", "capsule_id", capsule, correlation_id) for capsule in sample_capsules]
    return responses

# Include routers in app
app.include_router(agents_router)
app.include_router(trades_router)
app.include_router(coalitions_router)
app.include_router(payments_router)
app.include_router(capsules_router)
