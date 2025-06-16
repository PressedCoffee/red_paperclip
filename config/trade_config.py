"""
Trade Appraisal and Payment Configuration
Configuration for item appraisal, NFT trading, and x402 micropayments
"""

import os
from typing import Dict, Any

# Base-Sepolia Network Configuration
BASE_SEPOLIA_CONFIG = {
    "network_id": "base-sepolia",
    "gas_price_gwei": 0.001,  # Base Sepolia test gas price
    "average_gas_limit": 21000,  # Standard transfer
    "gas_cost_usd": 0.0001,  # Estimated cost in USD
}

# x402 Micropayment Configuration
X402_PAYMENT_CONFIG = {
    "base_fee_usd": 0.001,  # Base micropayment fee
    "gas_multiplier": 1.5,  # Gas cost multiplier for safety
    "coalition_profit_share": 0.05,  # 5% profit share for coalitions
    "pitch_cost_xp": 5,  # XP cost for generating a pitch
    "pitch_cost_usd": 0.01,  # USD cost for premium pitch
    "premium_pitch_threshold": 10,  # XP threshold for free pitches
}

# Archetype Behavior Configuration
ARCHETYPE_CONFIG = {
    "visionary": {
        "risk_multiplier": 1.2,  # Willing to take more risk
        "ugtt_bonus_multiplier": 1.1,  # Gets more from strategy bonuses
        "cost_sensitivity": 0.8,  # Less sensitive to costs
        "drift_weight": 1.3,  # More influenced by drift
    },
    "investor": {
        "risk_multiplier": 0.8,  # More conservative
        "ugtt_bonus_multiplier": 0.9,  # Gets less from strategy bonuses
        "cost_sensitivity": 1.2,  # More sensitive to costs
        "drift_weight": 0.7,  # Less influenced by drift
    },
    "default": {
        "risk_multiplier": 1.0,
        "ugtt_bonus_multiplier": 1.0,
        "cost_sensitivity": 1.0,
        "drift_weight": 1.0,
    }
}

# LLM Configuration
LLM_CONFIG = {
    "enable_llm_reasoning": True,  # Use LLM for value reasoning
    "enable_verbal_exchange": True,  # Use verbal exchange layer
    "fallback_to_hybrid": True,  # Fallback to hybrid if LLM fails
    "max_reasoning_tokens": 150,  # Limit LLM response length
}

# Value Calculation Configuration
VALUE_CONFIG = {
    "base_subjective_multiplier": 1.0,  # Base value multiplier
    "alignment_weight": 0.3,  # Weight of goal alignment in value
    "drift_weight": 0.2,  # Weight of drift in value calculation
    "ugtt_weight": 0.25,  # Weight of UGTT bonus
    "market_context_weight": 0.25,  # Weight of market context
}

# NFT Configuration
NFT_CONFIG = {
    "digital_nft_standard": "ERC-1155",  # Standard for digital items
    "redeemable_contract": "RedPaperclipRedeemable",  # For real-world items
    "provenance_chain_length": 10,  # Max provenance chain to store
    "ownership_verification": True,  # Verify ownership before trade
}


def get_config() -> Dict[str, Any]:
    """Get the complete configuration dictionary."""
    return {
        "base_sepolia": BASE_SEPOLIA_CONFIG,
        "x402_payments": X402_PAYMENT_CONFIG,
        "archetypes": ARCHETYPE_CONFIG,
        "llm": LLM_CONFIG,
        "values": VALUE_CONFIG,
        "nft": NFT_CONFIG,
    }


def get_archetype_config(archetype: str) -> Dict[str, Any]:
    """Get configuration for a specific archetype."""
    return ARCHETYPE_CONFIG.get(archetype, ARCHETYPE_CONFIG["default"])


def calculate_base_costs() -> Dict[str, float]:
    """Calculate base transaction costs."""
    gas_cost = BASE_SEPOLIA_CONFIG["gas_cost_usd"]
    x402_fee = X402_PAYMENT_CONFIG["base_fee_usd"]

    return {
        "gas_cost_usd": gas_cost,
        "x402_fee_usd": x402_fee,
        "total_base_cost_usd": gas_cost + x402_fee,
        "pitch_cost_xp": X402_PAYMENT_CONFIG["pitch_cost_xp"],
        "pitch_cost_usd": X402_PAYMENT_CONFIG["pitch_cost_usd"],
    }
