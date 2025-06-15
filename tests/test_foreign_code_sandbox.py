import unittest
from unittest.mock import patch, MagicMock
from foreign_code_sandbox import CodeSandboxRunner, EXPERIMENTAL_FEATURES
import logging


class TestCodeSandboxRunner(unittest.TestCase):
    def setUp(self):
        # Ensure feature flag is enabled for tests
        EXPERIMENTAL_FEATURES["chaos_pack"] = True

    def test_safety_validator_safe_code(self):
        safe_code = "print('Hello world')\\na = 5\\nfor i in range(a):\\n    print(i)"
        runner = CodeSandboxRunner(safe_code, compute_budget=100)
        self.assertTrue(runner.safety_validator())

    def test_safety_validator_unsafe_code(self):
        unsafe_code = "import os\\nos.system('rm -rf /')"
        runner = CodeSandboxRunner(unsafe_code, compute_budget=100)
        self.assertFalse(runner.safety_validator())

    def test_execute_sandbox_success(self):
        code = "result = 0\\nfor i in range(5):\\n    result += i"
        runner = CodeSandboxRunner(code, compute_budget=100)
        result = runner.execute_sandbox(timeout_seconds=2)
        self.assertIsInstance(result, dict)
        self.assertIn("result", result)
        self.assertEqual(result["result"], 10)

    def test_execute_sandbox_timeout(self):
        # Code with infinite loop to trigger timeout
        code = "while True:\\n    pass"
        runner = CodeSandboxRunner(code, compute_budget=100)
        with self.assertRaises(TimeoutError):
            runner.execute_sandbox(timeout_seconds=1)

    def test_execute_sandbox_exception(self):
        code = "raise ValueError('Test error')"
        runner = CodeSandboxRunner(code, compute_budget=100)
        with self.assertRaises(ValueError):
            runner.execute_sandbox(timeout_seconds=2)

    @patch("foreign_code_sandbox.requests.get")
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

    @patch("foreign_code_sandbox.requests.get")
    def test_import_code_from_github_repo_failure(self, mock_get):
        mock_get.side_effect = Exception("Network error")
        runner = CodeSandboxRunner("", compute_budget=100)
        url = "https://github.com/user/repo/blob/main/file.py"
        code = runner.import_code_from_github_repo(url)
        self.assertEqual(code, "")

    def test_feature_flag_disabled(self):
        EXPERIMENTAL_FEATURES["chaos_pack"] = False
        code = "print('Hello')"
        runner = CodeSandboxRunner(code, compute_budget=100)
        self.assertFalse(runner.safety_validator())
        self.assertIsNone(runner.execute_sandbox())
        self.assertEqual(runner.import_code_from_github_repo(
            "https://github.com/user/repo/blob/main/file.py"), "")


if __name__ == "__main__":
    unittest.main()
