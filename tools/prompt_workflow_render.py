"""Render host-prefixed prompt-workflow commands.

This cohesive host adapter is independent of workflow state and document
selection, preserving one-way imports from the main skill router.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping

HOST_CLAUDE = "claude"
HOST_CODEX = "codex"
CLAUDE_ENV_VAR = "CLAUDECODE"
CODEX_ENV_VAR = "CODEX_THREAD_ID"
HOST_PREFIXES = {HOST_CLAUDE: "/", HOST_CODEX: "$"}
DEFAULT_HOST = HOST_CLAUDE
MD_SUFFIX = ".md"
CODEX_SKILL_NAMESPACE = "llm-shared:"


def detect_host(env: Mapping[str, str]) -> str:
    """Return the host token read from the process environment."""
    if env.get(CLAUDE_ENV_VAR):
        return HOST_CLAUDE
    if env.get(CODEX_ENV_VAR):
        return HOST_CODEX
    return DEFAULT_HOST


def host_prefix(env: Mapping[str, str], override: str | None = None) -> str:
    """Return the command prefix for the detected or explicitly selected host."""
    host = override if override is not None else detect_host(env)
    return HOST_PREFIXES[host]


def render_command(prefix: str, instruction: str, document: str) -> str:
    """Render one bare host-prefixed next-step command line."""
    name = instruction.removesuffix(MD_SUFFIX)
    if prefix == HOST_PREFIXES[HOST_CODEX] and ":" not in name:
        name = f"{CODEX_SKILL_NAMESPACE}{name}"
    return f"{prefix}{name} on {document}"


def render_step_command(
    prefix: str,
    instruction: str,
    document: str,
    implementation_step: str,
) -> str:
    """Append the explicit implementation-step token to an ordinary command."""
    return f"{render_command(prefix, instruction, document)} step {implementation_step}"


def render_umbrella_command(
    prefix: str,
    instruction: str,
    document: str,
    umbrella: str | None,
) -> str:
    """Append the umbrella a review role must carry in its exchange context.

    A reviewer builds its core context from this line. Omitting the umbrella
    there while the published request and the coordination record both carry
    one makes every exchange operation report `inconsistent` with the opaque
    "artifact context differs from core context", naming neither the umbrella
    nor the missing flag. Naming it here is what lets the reviewer discover it.

    Args:
        prefix: The host command prefix.
        instruction: The instruction or role name, with or without its suffix.
        document: The repository-relative reviewed document.
        umbrella: The repository-relative umbrella draft, or None when the
            effort has none.

    Returns:
        The ordinary command when there is no umbrella, and the same command
        followed by ``with umbrella <path>`` when there is one.
    """
    command = render_command(prefix, instruction, document)
    if umbrella is None:
        return command
    return f"{command} with umbrella {umbrella}"


# eof
