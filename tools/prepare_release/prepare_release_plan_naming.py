"""Branch-name helpers for prepare-release planning."""

import re


def promotion_branch_name(branch: str, target: str) -> str:
    """Return a valid suggested landing-branch name without creating it."""
    sanitized = re.sub(r"[^A-Za-z0-9._/-]+", "-", branch).strip("-./")
    target_sanitized = re.sub(r"[^A-Za-z0-9._/-]+", "-", target).strip("-./")
    return f"prepare-release/{sanitized}-onto-{target_sanitized}"


# eof
