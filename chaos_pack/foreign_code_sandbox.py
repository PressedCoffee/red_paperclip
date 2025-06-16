import logging
import re
import threading
import requests
import traceback

# Feature flag control - should be controlled externally in real deployment
EXPERIMENTAL_FEATURES = {
    "chaos_pack": True
}

logger = logging.getLogger(__name__)


class CodeSandboxRunner:
    def __init__(self, agent_submitted_code: str, compute_budget: int):
        self.agent_submitted_code = agent_submitted_code
        # token budget, currently not strictly enforced
        self.compute_budget = compute_budget
        self.sandbox_result = None
        self._execution_thread = None
        self._execution_exception = None

    def safety_validator(self) -> bool:
        """
        Validate the submitted code for safety.
        Disallow dangerous keywords and patterns.
        Returns True if safe, False otherwise.
        """
        if not EXPERIMENTAL_FEATURES.get("chaos_pack", False):
            logger.info(
                "Chaos Pack feature disabled; skipping safety validation.")
            return False

        disallowed_patterns = [
            r"\bimport\b",
            r"\bopen\b",
            r"\beval\b",
            r"\bexec\b",
            r"\bos\b",
            r"\bsys\b",
            r"\bsubprocess\b",
            r"\bthreading\b",
            r"\basyncio\b",
            r"\bcompile\b",
            r"\binput\b",
            r"\bexit\b",
            r"\bquit\b",
            r"\bglobals\b",
            r"\blocals\b",
            r"\bdel\b",
            r"\b__import__\b",
            r"\bmemoryview\b",
            r"\bbuffer\b",
            r"\bproperty\b",
            r"\bclassmethod\b",
            r"\bstaticmethod\b",
            r"\bcompile\b",
            r"\bhelp\b",
            r"\bdir\b",
            r"\bvars\b",
            r"\bgetattr\b",
            r"\bsetattr\b",
            r"\bhasattr\b",
            r"\bobject\b",
            r"\btype\b",
            r"\bBaseException\b",
            r"\bException\b",
            r"\bfinally\b",
            r"\btry\b",
            r"\braise\b",
            r"\bassert\b",
            r"\bwith\b",
            r"\bproperty\b",
            r"\bclass\b",
            r"\bdef\b",
            r"\blambda\b",
            r"\basync\b",
            r"\bawait\b",
        ]

        for pattern in disallowed_patterns:
            if re.search(pattern, self.agent_submitted_code):
                logger.warning(
                    f"Safety validation failed: disallowed pattern found: {pattern}")
                return False

        # Additional heuristic checks can be added here

        logger.info("Safety validation passed.")
        return True

    def _execute_code(self):
        """
        Internal method to execute the submitted code in a restricted environment.
        """
        try:
            # Restricted globals and locals
            restricted_globals = {
                "__builtins__": {
                    "print": print,
                    "range": range,
                    "len": len,
                    "int": int,
                    "float": float,
                    "str": str,
                    "bool": bool,
                    "list": list,
                    "dict": dict,
                    "set": set,
                    "tuple": tuple,
                    "enumerate": enumerate,
                    "abs": abs,
                    "min": min,
                    "max": max,
                    "sum": sum,
                    # Add more safe builtins as needed
                }
            }
            restricted_locals = {}

            exec(self.agent_submitted_code, restricted_globals, restricted_locals)
            self.sandbox_result = restricted_locals
            logger.info("Code executed successfully in sandbox.")
        except Exception as e:
            self._execution_exception = e
            logger.error(
                f"Exception during sandbox execution: {traceback.format_exc()}")

    def execute_sandbox(self, timeout_seconds: int = 5):
        """
        Execute the submitted code in a sandbox with timeout and safety checks.
        Returns the sandbox result or raises an exception if failed.
        """
        if not EXPERIMENTAL_FEATURES.get("chaos_pack", False):
            logger.info(
                "Chaos Pack feature disabled; skipping sandbox execution.")
            return None

        if not self.safety_validator():
            logger.error("Code safety validation failed; aborting execution.")
            raise RuntimeError("Code safety validation failed.")

        self._execution_thread = threading.Thread(target=self._execute_code)
        self._execution_thread.start()
        self._execution_thread.join(timeout=timeout_seconds)

        if self._execution_thread.is_alive():
            logger.error("Code execution timed out; terminating.")
            raise TimeoutError("Code execution timed out.")

        if self._execution_exception:
            raise self._execution_exception

        return self.sandbox_result

    def import_code_from_github_repo(self, url: str) -> str:
        """
        Optional method to import code from a GitHub repo URL.
        Supports raw file URLs or standard GitHub URLs.
        Returns the code as a string.
        """
        if not EXPERIMENTAL_FEATURES.get("chaos_pack", False):
            logger.info("Chaos Pack feature disabled; skipping GitHub import.")
            return ""

        try:
            raw_url = self._convert_to_raw_github_url(url)
            logger.info(f"Fetching code from GitHub raw URL: {raw_url}")
            response = requests.get(raw_url, timeout=10)
            response.raise_for_status()
            logger.info("Code fetched successfully from GitHub.")
            return response.text
        except Exception as e:
            logger.error(f"Failed to fetch code from GitHub: {e}")
            return ""

    def _convert_to_raw_github_url(self, url: str) -> str:
        """
        Convert a GitHub URL to a raw content URL.
        Supports URLs like:
        https://github.com/user/repo/blob/branch/path/to/file.py
        Converts to:
        https://raw.githubusercontent.com/user/repo/branch/path/to/file.py
        """
        pattern = r"https://github\.com/(?P<user>[^/]+)/(?P<repo>[^/]+)/blob/(?P<branch>[^/]+)/(?P<path>.+)"
        match = re.match(pattern, url)
        if not match:
            logger.warning(
                "URL does not match expected GitHub blob pattern; returning original URL.")
            return url  # Return as is, maybe raw URL already

        user = match.group("user")
        repo = match.group("repo")
        branch = match.group("branch")
        path = match.group("path")

        raw_url = f"https://raw.githubusercontent.com/{user}/{repo}/{branch}/{path}"
        return raw_url
