import unittest
from unittest.mock import patch, MagicMock
from chaos_pack.foreign_code_sandbox import CodeSandboxRunner, EXPERIMENTAL_FEATURES
import logging


class TestCodeSandboxRunner(unittest.TestCase):
    def setUp(self):
        # Ensure feature flag is enabled for tests
        EXPERIMENTAL_FEATURES["chaos_pack"] = True
        # Suppress logging during tests
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        # Re-enable logging after tests
        logging.disable(logging.NOTSET)

    def test_compute_budget_calculation(self):
        runner = CodeSandboxRunner("print('test')", compute_budget=50)
        self.assertEqual(runner.compute_budget, 50)

    def test_execute_sandbox_simple_code(self):
        code = "result = 2 + 3"
        runner = CodeSandboxRunner(code, compute_budget=100)
        result = runner.execute_sandbox(timeout_seconds=5)
        self.assertEqual(result["result"], 5)

    def test_execute_sandbox_timeout(self):
        # Code with infinite loop to trigger timeout
        code = "while True:\n    pass"
        runner = CodeSandboxRunner(code, compute_budget=100)
        with self.assertRaises(TimeoutError):
            runner.execute_sandbox(timeout_seconds=1)

    def test_execute_sandbox_exception(self):
        code = "raise ValueError('Test error')"
        runner = CodeSandboxRunner(code, compute_budget=100)
        with self.assertRaises(ValueError):
            runner.execute_sandbox(timeout_seconds=2)

    @patch("chaos_pack.foreign_code_sandbox.requests.get")
    def test_import_code_from_github_repo_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "print('Hello from GitHub')"
        mock_get.return_value = mock_response

        runner = CodeSandboxRunner("", compute_budget=100)
        url = "https://github.com/user/repo/blob/main/file.py"
        code = runner.import_code_from_github_repo(url)
        self.assertEqual(code, "print('Hello from GitHub')")
        mock_get.assert_called_once()

    @patch("chaos_pack.foreign_code_sandbox.requests.get")
    def test_import_code_from_github_repo_failure(self, mock_get):
        mock_get.side_effect = Exception("Network error")
        runner = CodeSandboxRunner("", compute_budget=100)
        url = "https://github.com/user/repo/blob/main/file.py"
        code = runner.import_code_from_github_repo(url)
        self.assertEqual(code, "")

    def test_execute_sandbox_feature_disabled(self):
        # Temporarily disable the feature
        EXPERIMENTAL_FEATURES["chaos_pack"] = False
        runner = CodeSandboxRunner("print('test')", compute_budget=100)
        result = runner.execute_sandbox(timeout_seconds=5)
        # Should return None or default when feature is disabled
        self.assertIsNone(result)
        # Re-enable for other tests
        EXPERIMENTAL_FEATURES["chaos_pack"] = True

    def test_import_code_feature_disabled(self):
        # Temporarily disable the feature
        EXPERIMENTAL_FEATURES["chaos_pack"] = False
        runner = CodeSandboxRunner("", compute_budget=100)
        url = "https://github.com/user/repo/blob/main/file.py"
        code = runner.import_code_from_github_repo(url)
        self.assertEqual(code, "")
        # Re-enable for other tests
        EXPERIMENTAL_FEATURES["chaos_pack"] = True


if __name__ == "__main__":
    unittest.main()
