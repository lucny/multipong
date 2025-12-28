"""Statická AI – pálka se vůbec nehýbe (útečná pro debugging)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base_ai import Action, BaseAI

if TYPE_CHECKING:  # typové importy pouze pro lint/IDE
    from multipong.engine import Arena, Ball, Paddle


class StaticAI(BaseAI):
    """Pálka zůstává nehybná – užitečné pro testování fyziky bez AI rušivého faktoru."""

    def decide(self, paddle: "Paddle", ball: "Ball", arena: "Arena") -> Action:  # noqa: ARG002, ARG003
        """Nikdy se nepohybuje."""
        return {"up": False, "down": False}
