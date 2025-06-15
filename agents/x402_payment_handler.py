import json
import logging
import time
import uuid
from typing import Dict, Any, Optional

from agents.wallet.wallet_manager import WalletManager
import warnings

logger = logging.getLogger(__name__)


class FallbackWallet:
    """
    Fallback wallet implementation that provides mock wallet functionality
    when the actual wallet is not available.
    """

    def __init__(self):
        pass

    def get_wallet_address(self) -> str:
        warnings.warn("Using fallback wallet with mock wallet address.")
        return "0x0000000000000000000000000000000000000000"

    def sign_typed_data(self, **kwargs) -> str:
        warnings.warn(
            "Using fallback wallet to sign typed data. Returning mock signature.")
        return "0xmocksignature"

    def __getattr__(self, item):
        # Return a no-op function for any other method calls
        def no_op(*args, **kwargs):
            warnings.warn(
                f"Called fallback wallet method '{item}' which is a no-op.")
            return None
        return no_op

    def __repr__(self):
        return "<FallbackWallet>"

    def __str__(self):
        return "<FallbackWallet>"

    def __bool__(self):
        return True

    def __nonzero__(self):
        return True

    def __eq__(self, other):
        return isinstance(other, FallbackWallet)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash("FallbackWallet")

    def __dir__(self):
        return ["get_wallet_address", "sign_typed_data"]

    def __len__(self):
        return 1

    def __call__(self, *args, **kwargs):
        warnings.warn("Called fallback wallet instance as a function.")
        return None

    def __getitem__(self, item):
        warnings.warn("Called fallback wallet instance with __getitem__.")
        return None

    def __setitem__(self, key, value):
        warnings.warn("Called fallback wallet instance with __setitem__.")

    def __delitem__(self, key):
        warnings.warn("Called fallback wallet instance with __delitem__.")

    def __iter__(self):
        warnings.warn("Called fallback wallet instance with __iter__.")
        return iter([])

    def __next__(self):
        warnings.warn("Called fallback wallet instance with __next__.")
        raise StopIteration

    def __contains__(self, item):
        warnings.warn("Called fallback wallet instance with __contains__.")
        return False

    def __enter__(self):
        warnings.warn("Called fallback wallet instance with __enter__.")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        warnings.warn("Called fallback wallet instance with __exit__.")

    def __format__(self, format_spec):
        return "<FallbackWallet>"

    def __sizeof__(self):
        return 1

    def __getstate__(self):
        return {}

    def __setstate__(self, state):
        pass

    def __reduce__(self):
        return (FallbackWallet, ())

    def __reduce_ex__(self, protocol):
        return (FallbackWallet, ())

    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        return self


class X402PaymentHandler:
    """
    Handler for HTTP 402 Payment Required responses.
    Parses payment parameters, signs payment authorization using CDP wallet,
    and constructs X-PAYMENT header for retrying requests.
    """

    def __init__(self, wallet_manager: WalletManager):
        self.wallet_manager = wallet_manager
        # Check if wallet_manager has a wallet address, else use fallback wallet
        wallet_address = None
        try:
            wallet_address = self.wallet_manager.get_wallet_address()
        except Exception as e:
            logger.warning(
                f"Exception getting wallet address from wallet_manager: {e}")
        if not wallet_address:
            logger.warning(
                "No wallet found in WalletManager, using fallback wallet.")
            self.wallet_manager = FallbackWallet()

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
                logger.warning(
                    "No wallet address available for signing payment authorization. Using fallback wallet.")
                # Use fallback wallet explicitly if not already
                if not isinstance(self.wallet_manager, FallbackWallet):
                    self.wallet_manager = FallbackWallet()
                wallet_address = self.wallet_manager.get_wallet_address()

            # The payment_params should contain the EIP-712 typed data fields:
            # domain, types, primaryType, message
            domain = payment_params.get("domain")
            types = payment_params.get("types")
            primary_type = payment_params.get("primaryType")
            message = payment_params.get("message")

            if not all([domain, types, primary_type, message]):
                logger.error("Incomplete payment parameters for signing.")
                return None

            signature = self.wallet_manager.sign_typed_data(
                wallet_address=wallet_address,
                domain=domain,
                types=types,
                primary_type=primary_type,
                message=message
            )
            if not signature:
                logger.error("Failed to obtain signature from wallet.")
                return None
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
