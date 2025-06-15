import os
import json
import logging
from typing import Optional, Dict
import uuid

import requests
import boto3
from botocore.exceptions import BotoCoreError, ClientError

# Feature flag dictionary - can be imported or configured elsewhere
EXPERIMENTAL_FEATURES = {
    "pinata_nft_storage": True
}


class PinataNFTStorage:
    """
    Handles pinning JSON metadata to Pinata IPFS and fallback to AWS S3 storage.
    """

    PINATA_API_URL = "https://api.pinata.cloud/pinning/pinJSONToIPFS"

    def __init__(self):
        self.pinata_api_key = os.getenv("PINATA_API_KEY")
        self.pinata_api_secret = os.getenv("PINATA_API_SECRET")
        self.s3_bucket_name = os.getenv("AWS_S3_BUCKET_NAME")
        self.s3_client = boto3.client("s3") if self.s3_bucket_name else None

        if not self.pinata_api_key or not self.pinata_api_secret:
            logging.warning(
                "Pinata API credentials are not set. Pinata pinning will fail.")
        if not self.s3_bucket_name:
            logging.warning(
                "AWS S3 bucket name is not set. S3 fallback will be unavailable.")

    def pin_json_metadata(self, metadata: Dict) -> Optional[str]:
        """
        Pin JSON metadata to Pinata IPFS.

        Args:
            metadata (Dict): JSON metadata to pin.

        Returns:
            Optional[str]: IPFS hash if successful, None otherwise.
        """
        if not EXPERIMENTAL_FEATURES.get("pinata_nft_storage", False):
            logging.info(
                "Pinata NFT storage feature is disabled by feature flag.")
            return None

        if not self.pinata_api_key or not self.pinata_api_secret:
            logging.error("Pinata API credentials missing.")
            return None

        headers = {
            "pinata_api_key": self.pinata_api_key,
            "pinata_secret_api_key": self.pinata_api_secret,
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(
                self.PINATA_API_URL,
                headers=headers,
                data=json.dumps({"pinataContent": metadata}),
                timeout=10
            )
            response.raise_for_status()
            ipfs_hash = response.json().get("IpfsHash")
            if ipfs_hash:
                logging.info(
                    f"Successfully pinned metadata to Pinata: {ipfs_hash}")
                return ipfs_hash
            else:
                logging.error(
                    f"Pinata response missing IpfsHash: {response.text}")
                return None
        except requests.RequestException as e:
            logging.error(f"Error pinning JSON metadata to Pinata: {e}")
            return None

    def store_json_metadata_s3(self, metadata: Dict) -> Optional[str]:
        """
        Store JSON metadata in AWS S3 as fallback.

        Args:
            metadata (Dict): JSON metadata to store.

        Returns:
            Optional[str]: S3 object key if successful, None otherwise.
        """
        if not self.s3_client:
            logging.error(
                "AWS S3 client not initialized or bucket name missing.")
            return None

        object_key = f"nft_metadata/{uuid.uuid4()}.json"
        try:
            self.s3_client.put_object(
                Bucket=self.s3_bucket_name,
                Key=object_key,
                Body=json.dumps(metadata),
                ContentType="application/json"
            )
            logging.info(f"Successfully stored metadata in S3: {object_key}")
            return object_key
        except (BotoCoreError, ClientError) as e:
            logging.error(f"Error storing JSON metadata in S3: {e}")
            return None

    def store_metadata(self, metadata: Dict) -> Optional[str]:
        """
        Store metadata using Pinata with fallback to AWS S3.

        Args:
            metadata (Dict): JSON metadata to store.

        Returns:
            Optional[str]: IPFS hash or S3 object key if successful, None otherwise.
        """
        ipfs_hash = self.pin_json_metadata(metadata)
        if ipfs_hash:
            return ipfs_hash

        logging.warning(
            "Pinata pinning failed, attempting fallback to AWS S3.")
        s3_key = self.store_json_metadata_s3(metadata)
        if s3_key:
            return s3_key

        logging.error("Failed to store metadata in both Pinata and AWS S3.")
        return None
