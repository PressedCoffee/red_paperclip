# Genesis Pad Hackathon Sprint Plan

## Overview

This sprint prepares Genesis Pad for the Coinbase CDP AgentKit Hackathon by implementing a focused proof-of-concept demonstrating:

- On-chain autonomous agent trading with CDP wallets
- x402 pay flow for micro-transactions and resource unlocking
- NFT metadata storage via Pinata (IPFS)
- Simple AWS backend API/dashboard showcasing live simulation data
- A scripted multi-agent scenario highlighting the core loop: mint, trade, coalition, chaos, pay flow

---

## Module Breakdown

### 1. x402 Pay Flow Integration

- Extend WalletManager or AgentKit wrapper to perform x402-compliant payments using agent wallets
- Implement mock "resource unlock" deducting USDC and toggling feature flags
- Log all pay events: payer, payee/endpoint, amount, unlock type

### 2. Pinata NFT Metadata Storage

- Integrate Pinata HTTP API to pin JSON metadata for each agent's NFT
- Store IPFS hash in the agent's Capsule Registry entry
- Provide fallback mock for development mode

### 3. AWS Backend API / Dashboard

- Create lightweight REST API (Flask/FastAPI or Lambda + API Gateway)
- Endpoints: `/agents` (status, XP, badges), `/trades` (logs), `/coalitions` (logs), `/payments` (x402 logs)
- JSON response structure matches Snapshot data
- Optional basic auth or token guard
- Document JSON structure in README

### 4. Demo Scenario & Automation

- Script scenario with 5–10 agents: mint NFT, run trade loops, form coalitions, trigger chaos event, perform x402 payment to unlock resource
- CLI script: `python run_hackathon_demo.py`
- Store session log as JSON for submission

### 5. Documentation & Deliverables

- Update root README.md with hackathon setup and environment variables (`CDP_API_KEY_NAME`, `PINATA_API_KEY`, etc.)
- Add usage examples for API endpoints
- Include demo screenshots or Mermaid flowchart for judges

---

## Dependencies

- x402 Pay Flow depends on WalletManager and AgentKit integration
- Pinata integration requires Capsule Registry access
- AWS API depends on simulation logs and data structures
- Demo scenario integrates all above modules plus chaos and coalition features
- Documentation depends on all module implementations

---

## Proposed Folder Layout

```
/payments/x402_payment_handler.py
/api/premium_data.py
/demos/run_hackathon_demo.py
/tests/test_x402_payment.py
/tests/test_pinata_integration.py
/tests/test_aws_api.py
```

---

## Implementation Sequence

1. Implement x402 Payment Handler and mock resource unlock
2. Integrate Pinata NFT metadata storage with fallback
3. Develop AWS backend API and dashboard endpoints
4. Script demo scenario and CLI automation
5. Update documentation with setup, usage, and flowcharts
6. Conduct unit and integration testing throughout

---

## Testing Strategy

- Unit tests for x402 payment parsing, signing, and retry logic
- Unit tests for Pinata API calls and fallback behavior
- Integration tests for full payment flow and API responses
- Demo scenario test for expected event generation and log consistency
- Manual verification of dashboard and API endpoints

---

## Rough Timeline

| Phase | Tasks                         | Duration |
| ----- | ----------------------------- | -------- |
| 1     | x402 Payment Handler          | 2 days   |
| 2     | Pinata NFT Metadata Storage   | 1.5 days |
| 3     | AWS Backend API / Dashboard   | 2 days   |
| 4     | Demo Scenario & Automation    | 1.5 days |
| 5     | Documentation & Final Testing | 1 day    |

---
