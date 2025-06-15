import unittest
from unittest.mock import patch, MagicMock
import json
from agents.nft.pinata_nft_storage import PinataNFTStorage


class TestPinataNFTStorage(unittest.TestCase):
    def setUp(self):
        self.storage = PinataNFTStorage()
        self.sample_metadata = {
            "name": "Test NFT",
            "description": "Test description",
            "attributes": {"key": "value"}
        }

    @patch("agents.nft.pinata_nft_storage.requests.post")
    def test_pin_json_metadata_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"IpfsHash": "QmTestHash"}
        mock_post.return_value = mock_response

        ipfs_hash = self.storage.pin_json_metadata(self.sample_metadata)
        self.assertEqual(ipfs_hash, "QmTestHash")
        mock_post.assert_called_once()

    @patch("agents.nft.pinata_nft_storage.requests.post")
    def test_pin_json_metadata_failure(self, mock_post):
        mock_post.side_effect = Exception("Network error")
        ipfs_hash = self.storage.pin_json_metadata(self.sample_metadata)
        self.assertIsNone(ipfs_hash)

    @patch("agents.nft.pinata_nft_storage.boto3.client")
    def test_store_json_metadata_s3_success(self, mock_boto_client):
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        self.storage.s3_bucket_name = "test-bucket"
        self.storage.s3_client = mock_s3

        mock_s3.put_object.return_value = {}

        s3_key = self.storage.store_json_metadata_s3(self.sample_metadata)
        self.assertTrue(s3_key.startswith("nft_metadata/"))
        mock_s3.put_object.assert_called_once()

    @patch("agents.nft.pinata_nft_storage.boto3.client")
    def test_store_json_metadata_s3_failure(self, mock_boto_client):
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        self.storage.s3_bucket_name = "test-bucket"
        self.storage.s3_client = mock_s3

        mock_s3.put_object.side_effect = Exception("S3 error")

        s3_key = self.storage.store_json_metadata_s3(self.sample_metadata)
        self.assertIsNone(s3_key)

    @patch.object(PinataNFTStorage, "pin_json_metadata")
    @patch.object(PinataNFTStorage, "store_json_metadata_s3")
    def test_store_metadata_pinata_success(self, mock_s3, mock_pinata):
        mock_pinata.return_value = "QmPinataHash"
        mock_s3.return_value = None

        result = self.storage.store_metadata(self.sample_metadata)
        self.assertEqual(result, "QmPinataHash")
        mock_pinata.assert_called_once()
        mock_s3.assert_not_called()

    @patch.object(PinataNFTStorage, "pin_json_metadata")
    @patch.object(PinataNFTStorage, "store_json_metadata_s3")
    def test_store_metadata_fallback_to_s3(self, mock_s3, mock_pinata):
        mock_pinata.return_value = None
        mock_s3.return_value = "s3://bucket/key.json"

        result = self.storage.store_metadata(self.sample_metadata)
        self.assertEqual(result, "s3://bucket/key.json")
        mock_pinata.assert_called_once()
        mock_s3.assert_called_once()

    @patch.object(PinataNFTStorage, "pin_json_metadata")
    @patch.object(PinataNFTStorage, "store_json_metadata_s3")
    def test_store_metadata_failure(self, mock_s3, mock_pinata):
        mock_pinata.return_value = None
        mock_s3.return_value = None

        result = self.storage.store_metadata(self.sample_metadata)
        self.assertIsNone(result)
        mock_pinata.assert_called_once()
        mock_s3.assert_called_once()


if __name__ == "__main__":
    unittest.main()
