"""
Mock X402 Server for demonstration purposes.
Simulates a premium resource that requires micropayments.
"""

import json
import uuid
import time
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="X402 Demo Server", version="1.0.0")

# Configuration
DEMO_CONFIG = {
    "usdc_address": "0x036CbD53842c5426634e7929541eC2318f3dCF7e",  # Base Sepolia USDC
    "payment_address": "0x742d35Cc6634C0532925a3b8D1b9c1369e3cA89b",  # Demo payment wallet
    "network": "base-sepolia",
    "premium_resource_cost": "0.10"  # 10 cents in USDC
}

# In-memory storage for demo
payment_records = {}
valid_signatures = set()


def verify_payment_signature(payment_data: Dict[str, Any]) -> bool:
    """
    Mock payment verification.
    In production, this would verify the EIP-712 signature on-chain.
    """
    signature = payment_data.get("signature", "")
    payment_id = payment_data.get("paymentId", "")

    # For demo: accept mock signatures and store them
    if signature.startswith("0xmocksig") or len(signature) > 60:
        valid_signatures.add(signature)
        payment_records[payment_id] = {
            "signature": signature,
            "verified_at": time.time(),
            "status": "verified"
        }
        logger.info(
            f"✅ Payment verified: {payment_id} with signature {signature[:20]}...")
        return True

    logger.warning(f"❌ Invalid payment signature for {payment_id}")
    return False


@app.get("/api/premium-data")
async def get_premium_data(request: Request):
    """
    Premium data endpoint that requires x402 payment.
    """
    # Check for X-PAYMENT header
    x_payment = request.headers.get("X-PAYMENT")

    if not x_payment:
        # Return 402 Payment Required with payment details
        payment_id = str(uuid.uuid4())

        response_data = {
            "status": "payment_required",
            "maxAmountRequired": DEMO_CONFIG["premium_resource_cost"],
            "assetAddress": DEMO_CONFIG["usdc_address"],
            "paymentAddress": DEMO_CONFIG["payment_address"],
            "network": DEMO_CONFIG["network"],
            "paymentId": payment_id,
            "timestamp": time.time(),
            "message": "Payment required to access premium data"
        }

        logger.info(f"💰 Returning 402 Payment Required: {payment_id}")
        return JSONResponse(
            status_code=402,
            content=response_data,
            headers={"Content-Type": "application/json"}
        )

    # Parse and verify payment
    try:
        payment_data = json.loads(x_payment)

        if verify_payment_signature(payment_data):
            # Payment verified - return premium data
            premium_data = {
                "data": {
                    "premium_insights": [
                        "Market volatility prediction: 15% increase expected",
                        "Optimal trading window: 14:30-16:00 UTC",
                        "Risk assessment: Medium-Low for current portfolio"
                    ],
                    "ai_recommendations": [
                        "Consider diversifying into DeFi protocols",
                        "Monitor Bitcoin correlation indicators",
                        "Reduce exposure to high-beta assets"
                    ],
                    "exclusive_metrics": {
                        "sentiment_score": 0.73,
                        "volatility_index": 0.42,
                        "momentum_indicator": 0.61
                    }
                },
                "payment_confirmed": {
                    "payment_id": payment_data.get("paymentId"),
                    "amount": payment_data.get("amount"),
                    "verified_at": time.time()
                },
                "status": "success"
            }

            logger.info(
                f"✅ Premium data delivered for payment {payment_data.get('paymentId')}")
            return JSONResponse(content=premium_data)
        else:
            raise HTTPException(
                status_code=403, detail="Invalid payment signature")

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400, detail="Invalid X-PAYMENT header format")
    except Exception as e:
        logger.error(f"Payment verification error: {e}")
        raise HTTPException(
            status_code=500, detail="Payment verification failed")


@app.get("/api/free-data")
async def get_free_data():
    """
    Free data endpoint for comparison.
    """
    return {
        "data": {
            "basic_info": [
                "Current market status: Active",
                "Basic price movements available",
                "General market sentiment: Neutral"
            ]
        },
        "status": "success",
        "message": "Free tier data"
    }


@app.get("/api/payment-status/{payment_id}")
async def get_payment_status(payment_id: str):
    """
    Check payment status.
    """
    if payment_id in payment_records:
        return {
            "payment_id": payment_id,
            "status": payment_records[payment_id]["status"],
            "verified_at": payment_records[payment_id]["verified_at"]
        }
    else:
        raise HTTPException(status_code=404, detail="Payment not found")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "x402-demo-server",
        "timestamp": time.time(),
        "payments_processed": len(payment_records)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
