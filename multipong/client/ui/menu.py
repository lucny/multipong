"""
Menu states and lobby UI for Multipong client.
Handles STATE_MENU, STATE_LOBBY, countdown, and transitions to game.
"""

import pygame
from typing import Optional, Dict, Callable
from dataclasses import dataclass
from enum import Enum


class GameState(Enum):
    """Game states for the client."""
    MENU = "menu"
    LOBBY = "lobby"
    COUNTDOWN = "countdown"
    GAME = "game"
    RESULTS = "results"


@dataclass
class Button:
    """Simple button for UI."""
    rect: pygame.Rect
    text: str
    color: tuple
    hover_color: tuple
    action: Callable
    
    def draw(self, screen, font, is_hover=False):
        """Draw button on screen."""
        color = self.hover_color if is_hover else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2, border_radius=8)
        
        text_surf = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
    
    def is_hovered(self, mouse_pos):
        """Check if mouse is over button."""
        return self.rect.collidepoint(mouse_pos)


class MenuUI:
    """Main menu UI."""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.buttons = []
        self.font_large = None
        self.font_medium = None
        self.on_multiplayer = None
        self.on_local = None
        self.on_settings = None
        self.on_quit = None
        
    def setup_fonts(self):
        """Initialize fonts."""
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        
    def setup_buttons(self):
        """Create menu buttons."""
        button_width = 300
        button_height = 60
        button_x = (self.screen_width - button_width) // 2
        start_y = 250
        spacing = 80
        
        self.buttons = [
            Button(
                pygame.Rect(button_x, start_y, button_width, button_height),
                "Multiplayer",
                (50, 100, 200),
                (70, 120, 220),
                self.on_multiplayer or (lambda: None)
            ),
            Button(
                pygame.Rect(button_x, start_y + spacing, button_width, button_height),
                "Local Game",
                (50, 150, 100),
                (70, 170, 120),
                self.on_local or (lambda: None)
            ),
            Button(
                pygame.Rect(button_x, start_y + spacing * 2, button_width, button_height),
                "Settings",
                (100, 100, 100),
                (120, 120, 120),
                self.on_settings or (lambda: None)
            ),
            Button(
                pygame.Rect(button_x, start_y + spacing * 3, button_width, button_height),
                "Quit",
                (150, 50, 50),
                (170, 70, 70),
                self.on_quit or (lambda: None)
            ),
        ]
    
    def handle_event(self, event):
        """Handle menu events."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            print(f"🖱️ Click at {mouse_pos}")  # Debug
            for button in self.buttons:
                if button.is_hovered(mouse_pos):
                    print(f"✓ Button clicked: {button.text}")  # Debug
                    button.action()
                    break
    
    def draw(self, screen):
        """Draw menu screen."""
        screen.fill((20, 20, 40))
        
        # Title
        if self.font_large:
            title = self.font_large.render("MULTIPONG", True, (255, 255, 255))
            title_rect = title.get_rect(center=(self.screen_width // 2, 120))
            screen.blit(title, title_rect)
        
        # Buttons
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            button.draw(screen, self.font_medium, button.is_hovered(mouse_pos))


class LobbyUI:
    """Lobby UI for slot selection and ready state."""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font_large = None
        self.font_medium = None
        self.font_small = None
        self.lobby_state = {}
        self.my_slot = None
        self.slot_buttons = {}
        self.ready_button = None
        self.on_choose_slot = None
        self.on_set_ready = None
        
    def setup_fonts(self):
        """Initialize fonts."""
        self.font_large = pygame.font.Font(None, 56)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
    
    def setup_slot_buttons(self):
        """Create slot selection buttons."""
        self.slot_buttons = {}
        
        # Team A slots (left side)
        team_a_x = 100
        start_y = 150
        slot_height = 60
        slot_width = 250
        spacing = 70
        
        for i in range(1, 5):
            slot = f"A{i}"
            self.slot_buttons[slot] = pygame.Rect(
                team_a_x, start_y + (i - 1) * spacing, slot_width, slot_height
            )
        
        # Team B slots (right side)
        team_b_x = self.screen_width - team_a_x - slot_width
        for i in range(1, 5):
            slot = f"B{i}"
            self.slot_buttons[slot] = pygame.Rect(
                team_b_x, start_y + (i - 1) * spacing, slot_width, slot_height
            )
        
        # Ready button (bottom center)
        self.ready_button = pygame.Rect(
            (self.screen_width - 200) // 2, self.screen_height - 100, 200, 50
        )
    
    def update_lobby_state(self, state: dict):
        """Update lobby state from server."""
        self.lobby_state = state
    
    def handle_event(self, event):
        """Handle lobby events."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            
            # Check slot buttons
            for slot, rect in self.slot_buttons.items():
                if rect.collidepoint(mouse_pos):
                    if self.on_choose_slot:
                        self.on_choose_slot(slot)
                    return
            
            # Check ready button
            if self.ready_button and self.ready_button.collidepoint(mouse_pos):
                if self.on_set_ready and self.my_slot:
                    # Toggle ready state
                    is_ready = self._is_my_ready()
                    self.on_set_ready(not is_ready)
    
    def _is_my_ready(self) -> bool:
        """Check if current player is ready."""
        slots = self.lobby_state.get("slots", {})
        if self.my_slot and self.my_slot in slots:
            return slots[self.my_slot].get("is_ready", False)
        return False
    
    def draw(self, screen):
        """Draw lobby screen."""
        screen.fill((20, 20, 40))
        
        # Title
        if self.font_large:
            title = self.font_large.render("LOBBY", True, (255, 255, 255))
            title_rect = title.get_rect(center=(self.screen_width // 2, 60))
            screen.blit(title, title_rect)
        
        # Team labels
        if self.font_medium:
            team_a_label = self.font_medium.render("Team A", True, (100, 150, 255))
            screen.blit(team_a_label, (120, 110))
            
            team_b_label = self.font_medium.render("Team B", True, (255, 100, 100))
            screen.blit(team_b_label, (self.screen_width - 220, 110))
        
        # Draw slots
        slots = self.lobby_state.get("slots", {})
        for slot, rect in self.slot_buttons.items():
            self._draw_slot(screen, slot, rect, slots.get(slot, {}))
        
        # Draw ready button
        if self.ready_button and self.my_slot:
            is_ready = self._is_my_ready()
            color = (100, 200, 100) if is_ready else (200, 100, 100)
            text = "READY ✓" if is_ready else "NOT READY"
            
            pygame.draw.rect(screen, color, self.ready_button, border_radius=8)
            pygame.draw.rect(screen, (255, 255, 255), self.ready_button, 2, border_radius=8)
            
            if self.font_medium:
                text_surf = self.font_medium.render(text, True, (255, 255, 255))
                text_rect = text_surf.get_rect(center=self.ready_button.center)
                screen.blit(text_surf, text_rect)
        
        # Ready count
        ready_players = self.lobby_state.get("ready_players", [])
        if self.font_small:
            info_text = f"Ready: {len(ready_players)}"
            info_surf = self.font_small.render(info_text, True, (200, 200, 200))
            screen.blit(info_surf, (self.screen_width // 2 - 40, self.screen_height - 140))
    
    def _draw_slot(self, screen, slot: str, rect: pygame.Rect, slot_data: dict):
        """Draw a single slot button."""
        is_my_slot = (slot == self.my_slot)
        nickname = slot_data.get("nickname")
        is_ai = slot_data.get("is_ai", False)
        is_ready = slot_data.get("is_ready", False)
        
        # Determine color
        if is_my_slot:
            color = (50, 150, 50)
        elif nickname:
            color = (80, 80, 120) if not is_ready else (50, 120, 50)
        else:
            color = (60, 60, 60)
        
        # Draw slot box
        pygame.draw.rect(screen, color, rect, border_radius=8)
        pygame.draw.rect(screen, (255, 255, 255), rect, 2, border_radius=8)
        
        # Draw slot label
        if self.font_medium:
            label = f"{slot}:"
            label_surf = self.font_medium.render(label, True, (255, 255, 255))
            screen.blit(label_surf, (rect.x + 10, rect.y + 8))
        
        # Draw player info
        if nickname:
            if self.font_small:
                player_text = f"{nickname}"
                if is_ai:
                    ai_level = slot_data.get("ai_level", "simple")
                    player_text += f" (AI: {ai_level})"
                
                player_surf = self.font_small.render(player_text, True, (220, 220, 220))
                screen.blit(player_surf, (rect.x + 10, rect.y + 35))
                
                if is_ready:
                    ready_surf = self.font_small.render("✓ Ready", True, (100, 255, 100))
                    screen.blit(ready_surf, (rect.x + rect.width - 70, rect.y + 8))
        else:
            if self.font_small:
                empty_surf = self.font_small.render("[Empty]", True, (150, 150, 150))
                screen.blit(empty_surf, (rect.x + 10, rect.y + 35))


class CountdownUI:
    """Countdown UI before match start."""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font_huge = None
        self.countdown_value = 3
        
    def setup_fonts(self):
        """Initialize fonts."""
        self.font_huge = pygame.font.Font(None, 200)
    
    def set_countdown(self, value: int):
        """Set countdown value."""
        self.countdown_value = value
    
    def draw(self, screen):
        """Draw countdown screen."""
        screen.fill((20, 20, 40))
        
        if self.font_huge and self.countdown_value > 0:
            text = str(self.countdown_value)
            color = (255, 200, 50)
            
            if self.countdown_value <= 1:
                color = (50, 255, 50)
            
            text_surf = self.font_huge.render(text, True, color)
            text_rect = text_surf.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            screen.blit(text_surf, text_rect)
        elif self.font_huge:
            # "GO!"
            go_surf = self.font_huge.render("GO!", True, (50, 255, 50))
            go_rect = go_surf.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            screen.blit(go_surf, go_rect)
