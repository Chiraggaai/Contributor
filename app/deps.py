from typing import Annotated

from fastapi import Header


def get_contributor_id(
    x_contributor_id: Annotated[str | None, Header(alias="X-Contributor-Id")] = None,
) -> str:
    """Resolve contributor; replace with JWT/session in production."""
    return x_contributor_id or "default"
