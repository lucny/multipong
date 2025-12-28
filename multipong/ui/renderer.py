"""
Renderer – Pygame vykreslovač pro MULTIPONG klienta.

Vykresluje herní scénu na základě stavového snapshotu (interpolovaného
StateBufferem). Neobsahuje žádnou herní logiku.
"""

from __future__ import annotations

from typing import Dict, Any

try:  # pragma: no cover - import pygame může chybět v CI
    import pygame
except Exception:  # pragma: no cover
    pygame = None  # type: ignore

from multipong import settings

# Základní barvy UI
COLOR_BACKGROUND = (30, 30, 30)
COLOR_BALL = (200, 80, 80)
COLOR_GOAL = (80, 160, 240)
COLOR_GOAL_HILITE = (120, 200, 255)
COLOR_PADDLE_LEFT = (220, 220, 220)
COLOR_PADDLE_RIGHT = (220, 220, 220)
COLOR_TEXT = (230, 230, 230)


class Renderer:
    """Jednoduchý renderer pro vykreslení scény dle state dictu."""

    def __init__(self, screen: "pygame.Surface") -> None:
        self.screen = screen
        self._font_score = None
        self._font_small = None
        if pygame:
            self._font_score = pygame.font.SysFont("consolas", 28)
            self._font_small = pygame.font.SysFont("consolas", 18)

    def draw(self, state: Dict[str, Any]) -> None:
        if not pygame:  # pragma: no cover
            return

        self.screen.fill(COLOR_BACKGROUND)

        # Brankové zóny (sloupky)
        goal_width = 8
        goal_left = state.get("goal_left", {})
        goal_right = state.get("goal_right", {})

        # Levá branka
        if goal_left:
            pygame.draw.rect(
                self.screen,
                COLOR_GOAL,
                pygame.Rect(
                    0,
                    int(goal_left.get("top", 0)),
                    goal_width,
                    int(goal_left.get("bottom", 0) - goal_left.get("top", 0)),
                ),
                border_radius=3,
            )
        # Pravá branka
        if goal_right:
            pygame.draw.rect(
                self.screen,
                COLOR_GOAL,
                pygame.Rect(
                    settings.WINDOW_WIDTH - goal_width,
                    int(goal_right.get("top", 0)),
                    goal_width,
                    int(goal_right.get("bottom", 0) - goal_right.get("top", 0)),
                ),
                border_radius=3,
            )

        # Míček
        ball = state.get("ball", {})
        if ball:
            bx = int(ball.get("x", settings.WINDOW_WIDTH // 2))
            by = int(ball.get("y", settings.WINDOW_HEIGHT // 2))
            br = int(ball.get("radius", 10))
            pygame.draw.circle(self.screen, COLOR_BALL, (bx, by), br)

            # Zvýraznění branky pokud je míček uvnitř jejího vertikálního rozsahu
            if goal_left and goal_left.get("top") <= by <= goal_left.get("bottom"):
                pygame.draw.rect(
                    self.screen,
                    COLOR_GOAL_HILITE,
                    pygame.Rect(
                        0,
                        int(goal_left.get("top", 0)),
                        goal_width,
                        int(goal_left.get("bottom", 0) - goal_left.get("top", 0)),
                    ),
                    border_radius=3,
                )
            if goal_right and goal_right.get("top") <= by <= goal_right.get("bottom"):
                pygame.draw.rect(
                    self.screen,
                    COLOR_GOAL_HILITE,
                    pygame.Rect(
                        settings.WINDOW_WIDTH - goal_width,
                        int(goal_right.get("top", 0)),
                        goal_width,
                        int(goal_right.get("bottom", 0) - goal_right.get("top", 0)),
                    ),
                    border_radius=3,
                )

        # Pálky obou týmů
        for team_key, color in (("team_left", COLOR_PADDLE_LEFT), ("team_right", COLOR_PADDLE_RIGHT)):
            team = state.get(team_key, {})
            for p in team.get("paddles", []):
                x = int(p.get("x", 0))
                y = int(p.get("y", 0))
                w = int(p.get("width", 10))
                h = int(p.get("height", 50))
                pygame.draw.rect(self.screen, color, pygame.Rect(x, y, w, h), border_radius=3)

        # Skóre (pokud je k dispozici)
        if self._font_score:
            left = state.get("team_left", {}).get("score", 0)
            right = state.get("team_right", {}).get("score", 0)
            txt = self._font_score.render(f"A {left} : {right} B", True, COLOR_TEXT)
            self.screen.blit(txt, (settings.WINDOW_WIDTH // 2 - txt.get_width() // 2, 20))

        pygame.display.flip()
