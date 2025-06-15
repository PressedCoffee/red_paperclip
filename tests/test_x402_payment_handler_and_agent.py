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


def test_fallback_wallet_used_when_no_real_wallet(monkeypatch):
    from agents.x402_payment_handler import X402PaymentHandler, FallbackWallet

    class NoWalletManager:
        def get_wallet_address(self):
            return None

        def sign_typed_data(self, **kwargs):
            return "0xfallbacksignature"

    no_wallet_manager = NoWalletManager()
    handler = X402PaymentHandler(no_wallet_manager)
    # The wallet_manager should be replaced with FallbackWallet instance
    assert isinstance(handler.wallet_manager, FallbackWallet)

    payment_params = {
        "domain": {"name": "Test"},
        "types": {"TestType": []},
        "primaryType": "TestType",
        "message": {"foo": "bar"}
    }
    signature = handler.sign_payment_authorization(payment_params)
    assert signature == "0xfallbacksignature"


def test_sign_payment_authorization_logs_error_and_returns_none(monkeypatch, caplog):
    from agents.x402_payment_handler import X402PaymentHandler

    class BadWalletManager:
        def get_wallet_address(self):
            return "0xWalletAddress"

        def sign_typed_data(self, **kwargs):
            raise Exception("Signing failure")

    bad_wallet_manager = BadWalletManager()
    handler = X402PaymentHandler(bad_wallet_manager)

    payment_params = {
        "domain": {"name": "Test"},
        "types": {"TestType": []},
        "primaryType": "TestType",
        "message": {"foo": "bar"}
    }

    with caplog.at_level("ERROR"):
        signature = handler.sign_payment_authorization(payment_params)
        assert signature is None
        # Check that error was logged
        assert any(
            "Exception during signing payment authorization" in msg for msg in caplog.messages)
