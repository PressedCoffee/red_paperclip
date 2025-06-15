import json
import logging
import pytest
from unittest.mock import MagicMock, patch
from requests.models import Response

from agents.x402_payment_handler import X402PaymentHandler
from agents.agent import AgentLifecycleManager


class DummyWalletManager:
    def __init__(self):
        self.get_wallet_address = MagicMock(return_value="0xWalletAddress")
        self.sign_typed_data = MagicMock(return_value="0xSignature")


@pytest.fixture
def wallet_manager():
    return DummyWalletManager()


@pytest.fixture
def payment_handler(wallet_manager):
    return X402PaymentHandler(wallet_manager)


def test_parse_402_response_valid(payment_handler):
    payload = json.dumps({
        "payment_params": {
            "domain": {"name": "Test"},
            "types": {"TestType": []},
            "primaryType": "TestType",
            "message": {"foo": "bar"}
        }
    })
    result = payment_handler.parse_402_response(payload)
    assert result is not None
    assert result["domain"]["name"] == "Test"


def test_parse_402_response_missing_params(payment_handler):
    payload = json.dumps({"some_other_key": {}})
    result = payment_handler.parse_402_response(payload)
    assert result is None


def test_parse_402_response_invalid_json(payment_handler):
    payload = "{invalid json"
    result = payment_handler.parse_402_response(payload)
    assert result is None


def test_sign_payment_authorization_success(wallet_manager, payment_handler):
    payment_params = {
        "domain": {"name": "Test"},
        "types": {"TestType": []},
        "primaryType": "TestType",
        "message": {"foo": "bar"}
    }
    signature = payment_handler.sign_payment_authorization(payment_params)
    assert signature == "0xSignature"
    wallet_manager.sign_typed_data.assert_called_once()


def test_sign_payment_authorization_no_wallet_address(wallet_manager, payment_handler):
    wallet_manager.get_wallet_address.return_value = None
    payment_params = {
        "domain": {"name": "Test"},
        "types": {"TestType": []},
        "primaryType": "TestType",
        "message": {"foo": "bar"}
    }
    signature = payment_handler.sign_payment_authorization(payment_params)
    assert signature is None


def test_sign_payment_authorization_incomplete_params(wallet_manager, payment_handler):
    payment_params = {
        "domain": {"name": "Test"},
        "types": None,
        "primaryType": "TestType",
        "message": {"foo": "bar"}
    }
    signature = payment_handler.sign_payment_authorization(payment_params)
    assert signature is None


def test_sign_payment_authorization_exception(wallet_manager, payment_handler):
    wallet_manager.sign_typed_data.side_effect = Exception("Signing error")
    payment_params = {
        "domain": {"name": "Test"},
        "types": {"TestType": []},
        "primaryType": "TestType",
        "message": {"foo": "bar"}
    }
    signature = payment_handler.sign_payment_authorization(payment_params)
    assert signature is None


def test_construct_payment_header(payment_handler):
    signature = "0xSignature"
    payment_params = {"domain": {"name": "Test"}}
    header = payment_handler.construct_payment_header(
        signature, payment_params)
    assert "X-PAYMENT" in header
    header_value = json.loads(header["X-PAYMENT"])
    assert header_value["signature"] == signature
    assert header_value["paymentDetails"] == payment_params


@patch("agents.agent.requests.get")
@patch("agents.agent.logging")
def test_get_resource_with_x402_retry_feature_flag_disabled(mock_logging, mock_get):
    # Setup mock to simulate normal GET
    mock_get.return_value = MagicMock(status_code=200, text="OK")

    agent_lifecycle = AgentLifecycleManager(agent=None)
    # Disable feature flag by patching the dict inside method
    with patch.dict("agents.agent.AgentLifecycleManager.__dict__", {"EXPERIMENTAL_FEATURES": {"x402": False}}):
        response = agent_lifecycle.get_resource_with_x402_retry(
            "http://example.com")
        assert response.status_code == 200
        mock_get.assert_called_once_with("http://example.com")


@patch("agents.agent.requests.get")
@patch("agents.agent.logging")
def test_get_resource_with_x402_retry_successful_payment_flow(mock_logging, mock_get):
    # Setup 402 response with valid payment params
    payment_params = {
        "domain": {"name": "Test"},
        "types": {"TestType": []},
        "primaryType": "TestType",
        "message": {"foo": "bar"}
    }
    response_402 = MagicMock(status_code=402, text=json.dumps(
        {"payment_params": payment_params}))
    response_200 = MagicMock(status_code=200, text="Success")

    # Setup mock get to return 402 first, then 200 on retry
    mock_get.side_effect = [response_402, response_200]

    # Patch X402PaymentHandler methods
    with patch.object(AgentLifecycleManager, "x402_payment_handler", create=True) as mock_handler:
        mock_handler.parse_402_response.return_value = payment_params
        mock_handler.sign_payment_authorization.return_value = "0xSignature"
        mock_handler.construct_payment_header.return_value = {
            "X-PAYMENT": "header_value"}

        agent_lifecycle = AgentLifecycleManager(agent=None)
        # Patch feature flag to True
        with patch.dict("agents.agent.AgentLifecycleManager.__dict__", {"EXPERIMENTAL_FEATURES": {"x402": True}}):
            # Inject the mock handler
            agent_lifecycle.x402_payment_handler = mock_handler
            response = agent_lifecycle.get_resource_with_x402_retry(
                "http://example.com", max_retries=1)

    assert response.status_code == 200
    assert mock_get.call_count == 2
    mock_handler.parse_402_response.assert_called_once()
    mock_handler.sign_payment_authorization.assert_called_once()
    mock_handler.construct_payment_header.assert_called_once()
    mock_logging.info.assert_any_call(
        "Payment successful for URL http://example.com with correlation_id " +
        mock_logging.info.call_args[0][0].split()[-1]
    )


@patch("agents.agent.requests.get")
@patch("agents.agent.logging")
def test_get_resource_with_x402_retry_parse_failure(mock_logging, mock_get):
    response_402 = MagicMock(status_code=402, text="invalid json")
    mock_get.return_value = response_402

    with patch.object(AgentLifecycleManager, "x402_payment_handler", create=True) as mock_handler:
        mock_handler.parse_402_response.return_value = None

        agent_lifecycle = AgentLifecycleManager(agent=None)
        with patch.dict("agents.agent.AgentLifecycleManager.__dict__", {"EXPERIMENTAL_FEATURES": {"x402": True}}):
            agent_lifecycle.x402_payment_handler = mock_handler
            response = agent_lifecycle.get_resource_with_x402_retry(
                "http://example.com")

    assert response.status_code == 402
    mock_logging.error.assert_called_with(
        "Failed to parse payment parameters from 402 response for URL http://example.com"
    )


@patch("agents.agent.requests.get")
@patch("agents.agent.logging")
def test_get_resource_with_x402_retry_signing_failure(mock_logging, mock_get):
    payment_params = {
        "domain": {"name": "Test"},
        "types": {"TestType": []},
        "primaryType": "TestType",
        "message": {"foo": "bar"}
    }
    response_402 = MagicMock(status_code=402, text=json.dumps(
        {"payment_params": payment_params}))
    mock_get.return_value = response_402

    with patch.object(AgentLifecycleManager, "x402_payment_handler", create=True) as mock_handler:
        mock_handler.parse_402_response.return_value = payment_params
        mock_handler.sign_payment_authorization.return_value = None

        agent_lifecycle = AgentLifecycleManager(agent=None)
        with patch.dict("agents.agent.AgentLifecycleManager.__dict__", {"EXPERIMENTAL_FEATURES": {"x402": True}}):
            agent_lifecycle.x402_payment_handler = mock_handler
            response = agent_lifecycle.get_resource_with_x402_retry(
                "http://example.com")

    assert response.status_code == 402
    mock_logging.error.assert_called_with(
        "Failed to sign payment authorization for URL http://example.com"
    )


@patch("agents.agent.requests.get")
@patch("agents.agent.logging")
def test_get_resource_with_x402_retry_retry_failure(mock_logging, mock_get):
    payment_params = {
        "domain": {"name": "Test"},
        "types": {"TestType": []},
        "primaryType": "TestType",
        "message": {"foo": "bar"}
    }
    response_402 = MagicMock(status_code=402, text=json.dumps(
        {"payment_params": payment_params}))
    response_403 = MagicMock(status_code=403, text="Forbidden")

    mock_get.side_effect = [response_402, response_403]

    with patch.object(AgentLifecycleManager, "x402_payment_handler", create=True) as mock_handler:
        mock_handler.parse_402_response.return_value = payment_params
        mock_handler.sign_payment_authorization.return_value = "0xSignature"
        mock_handler.construct_payment_header.return_value = {
            "X-PAYMENT": "header_value"}

        agent_lifecycle = AgentLifecycleManager(agent=None)
        with patch.dict("agents.agent.AgentLifecycleManager.__dict__", {"EXPERIMENTAL_FEATURES": {"x402": True}}):
            agent_lifecycle.x402_payment_handler = mock_handler
            response = agent_lifecycle.get_resource_with_x402_retry(
                "http://example.com", max_retries=1)

    assert response.status_code == 403
    mock_logging.warning.assert_called()
    mock_logging.error.assert_called_with(
        "Exceeded max retries for payment on URL http://example.com"
    )


@patch("agents.agent.requests.get")
@patch("agents.agent.logging")
def test_get_resource_with_x402_retry_request_exception(mock_logging, mock_get):
    mock_get.side_effect = Exception("Network error")

    agent_lifecycle = AgentLifecycleManager(agent=None)
    with patch.dict("agents.agent.AgentLifecycleManager.__dict__", {"EXPERIMENTAL_FEATURES": {"x402": True}}):
        response = agent_lifecycle.get_resource_with_x402_retry(
            "http://example.com")

    assert response is None
    mock_logging.error.assert_called()


@patch("agents.agent.requests.get")
@patch("agents.agent.logging")
def test_get_resource_with_x402_retry_retry_request_exception(mock_logging, mock_get):
    payment_params = {
        "domain": {"name": "Test"},
        "types": {"TestType": []},
        "primaryType": "TestType",
        "message": {"foo": "bar"}
    }
    response_402 = MagicMock(status_code=402, text=json.dumps(
        {"payment_params": payment_params}))

    mock_get.side_effect = [response_402, Exception("Network error")]

    with patch.object(AgentLifecycleManager, "x402_payment_handler", create=True) as mock_handler:
        mock_handler.parse_402_response.return_value = payment_params
        mock_handler.sign_payment_authorization.return_value = "0xSignature"
        mock_handler.construct_payment_header.return_value = {
            "X-PAYMENT": "header_value"}

        agent_lifecycle = AgentLifecycleManager(agent=None)
        with patch.dict("agents.agent.AgentLifecycleManager.__dict__", {"EXPERIMENTAL_FEATURES": {"x402": True}}):
            agent_lifecycle.x402_payment_handler = mock_handler
            response = agent_lifecycle.get_resource_with_x402_retry(
                "http://example.com")

    assert response is None
    mock_logging.error.assert_called()
