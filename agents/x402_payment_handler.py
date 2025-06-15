import json
import logging
import time
import uuid
from typing import Dict, Any, Optional

from agents.wallet.wallet_manager import WalletManager

logger = logging.getLogger(__name__)


class X402PaymentHandler:
    """
    Handler for HTTP 402 Payment Required responses.
    Parses payment parameters, signs payment authorization using CDP wallet,
    and constructs X-PAYMENT header for retrying requests.
    """

    def __init__(self, wallet_manager: WalletManager):
        self.wallet_manager = wallet_manager

    def parse_402_response(self, response_payload: str) -> Optional[Dict[str, Any]]:
        """
        Parse the HTTP 402 response payload to extract payment parameters.

        Args:
            response_payload (str): The raw response payload from the 402 response.

        Returns:
            dict: Parsed payment parameters including domain, types, message, primaryType, etc.
        """
        try:
            data = json.loads(response_payload)
            payment_params = data.get(
                "payment_params") or data.get("paymentParameters")
            if not payment_params:
                logger.error(
                    "No payment parameters found in 402 response payload.")
                return None
            return payment_params
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode 402 response payload: {e}")
            return None

    def sign_payment_authorization(self, payment_params: Dict[str, Any]) -> Optional[str]:
        """
        Sign the EIP-712 typed data payment authorization using the CDP wallet.

        Args:
            payment_params (dict): The payment parameters extracted from the 402 response.

        Returns:
            str: The signature string if signing is successful, None otherwise.
        """
        try:
            wallet_address = self.wallet_manager.get_wallet_address()
            if not wallet_address:
                logger.error(
                    "No wallet address available for signing payment authorization.")
                return None

            # The payment_params should contain the EIP-712 typed data fields:
            # domain, types, primaryType, message
            domain = payment_params.get("domain")
            types = payment_params.get("types")
            primary_type = payment_params.get("primaryType")
            message = payment_params.get("message")

            if not all([domain, types, primary_type, message]):
                logger.error("Incomplete payment parameters for signing.")
                return None

            # Use wallet_manager or underlying wallet provider to sign typed data
            # Assuming wallet_manager has a method sign_typed_data (to be implemented or mocked)
            signature = self.wallet_manager.sign_typed_data(
                wallet_address=wallet_address,
                domain=domain,
                types=types,
                primary_type=primary_type,
                message=message
            )
            return signature
        except Exception as e:
            logger.error(
                f"Exception during signing payment authorization: {e}")
            return None

    def construct_payment_header(self, signature: str, payment_params: Dict[str, Any]) -> Dict[str, str]:
        """
        Construct the X-PAYMENT header with the signature and payment details.

        Args:
            signature (str): The signature string from signing.
            payment_params (dict): The payment parameters extracted from the 402 response.

        Returns:
            dict: Headers dictionary with 'X-PAYMENT' key.
        """
        payment_header_value = {
            "signature": signature,
            "paymentDetails": payment_params
        }
        header = {
            "X-PAYMENT": json.dumps(payment_header_value)
        }
        return header
