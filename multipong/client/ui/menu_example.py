"""
Example integration of menu system into Pygame client.
Shows how to use MenuUI, LobbyUI, and CountdownUI.
"""

import pygame
import asyncio
from multipong.client.ui.menu import MenuUI, LobbyUI, CountdownUI, GameState


class GameClient:
    """
    Example game client with menu, lobby, and countdown states.
    """
    
    def __init__(self, width=800, height=600):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("MULTIPONG")
        
        self.width = width
        self.height = height
        self.clock = pygame.time.Clock()
        self.running = True
        
        # State management
        self.state = GameState.MENU
        
        # UI components
        self.menu_ui = MenuUI(width, height)
        self.lobby_ui = LobbyUI(width, height)
        self.countdown_ui = CountdownUI(width, height)
        
        # Setup UI
        self._setup_ui()
        
        # WebSocket connection (placeholder)
        self.ws_connection = None
        self.my_player_id = None
        
        # Countdown timer
        self.countdown_start_time = None
        self.countdown_duration = 3  # seconds
    
    def _setup_ui(self):
        """Initialize all UI components."""
        # Menu
        self.menu_ui.setup_fonts()
        self.menu_ui.on_multiplayer = self.on_multiplayer_click
        self.menu_ui.on_local = self.on_local_click
        self.menu_ui.on_settings = self.on_settings_click
        self.menu_ui.on_quit = self.on_quit_click
        self.menu_ui.setup_buttons()
        
        # Lobby
        self.lobby_ui.setup_fonts()
        self.lobby_ui.setup_slot_buttons()
        self.lobby_ui.on_choose_slot = self.on_choose_slot
        self.lobby_ui.on_set_ready = self.on_set_ready
        
        # Countdown
        self.countdown_ui.setup_fonts()
    
    def on_multiplayer_click(self):
        """Handle multiplayer button click."""
        print("🌐 Multiplayer clicked - connecting to server...")
        self.state = GameState.LOBBY
        # TODO: Establish WebSocket connection
        # asyncio.create_task(self.connect_to_server())
    
    def on_local_click(self):
        """Handle local game button click."""
        print("🏠 Local game clicked - starting local match...")
        self.state = GameState.GAME
        # TODO: Start local game
    
    def on_settings_click(self):
        """Handle settings button click."""
        print("⚙️ Settings clicked")
        # TODO: Open settings menu
    
    def on_quit_click(self):
        """Handle quit button click."""
        print("👋 Quit clicked")
        self.running = False
    
    def on_choose_slot(self, slot: str):
        """Handle slot selection in lobby."""
        print(f"🎯 Slot {slot} selected")
        # TODO: Send choose_slot message to server
        # await self.send_message({"type": "choose_slot", "slot": slot})
        self.lobby_ui.my_slot = slot
    
    def on_set_ready(self, is_ready: bool):
        """Handle ready state change."""
        print(f"✓ Ready state: {is_ready}")
        # TODO: Send set_ready message to server
        # await self.send_message({"type": "set_ready", "ready": is_ready})
    
    def on_lobby_update(self, lobby_state: dict):
        """Handle lobby update from server."""
        print(f"📊 Lobby update received")
        self.lobby_ui.update_lobby_state(lobby_state)
    
    def on_start_match(self, countdown: int):
        """Handle start match message from server."""
        print(f"🚀 Match starting with countdown: {countdown}")
        self.state = GameState.COUNTDOWN
        self.countdown_duration = countdown
        self.countdown_start_time = pygame.time.get_ticks()
        self.countdown_ui.set_countdown(countdown)
    
    def update_countdown(self):
        """Update countdown and transition to game."""
        if self.countdown_start_time is None:
            return
        
        elapsed = (pygame.time.get_ticks() - self.countdown_start_time) / 1000.0
        remaining = max(0, self.countdown_duration - elapsed)
        
        if remaining <= 0:
            # Countdown finished, start game
            print("🎮 Countdown finished - starting game!")
            self.state = GameState.GAME
            self.countdown_start_time = None
        else:
            # Update countdown display
            self.countdown_ui.set_countdown(int(remaining) + 1)
    
    def handle_events(self):
        """Handle pygame events based on current state."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if self.state == GameState.MENU:
                self.menu_ui.handle_event(event)
            
            elif self.state == GameState.LOBBY:
                self.lobby_ui.handle_event(event)
            
            # Add game state event handling here
    
    def render(self):
        """Render current state."""
        if self.state == GameState.MENU:
            self.menu_ui.draw(self.screen)
        
        elif self.state == GameState.LOBBY:
            self.lobby_ui.draw(self.screen)
        
        elif self.state == GameState.COUNTDOWN:
            self.countdown_ui.draw(self.screen)
        
        elif self.state == GameState.GAME:
            # TODO: Render game
            self.screen.fill((0, 0, 0))
            font = pygame.font.Font(None, 48)
            text = font.render("GAME IN PROGRESS", True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(text, text_rect)
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop."""
        while self.running:
            # Handle events
            self.handle_events()
            
            # Update state-specific logic
            if self.state == GameState.COUNTDOWN:
                self.update_countdown()
            
            # Render
            self.render()
            
            # Cap at 60 FPS
            self.clock.tick(60)
        
        pygame.quit()


def main():
    """Run the example client."""
    client = GameClient()
    
    # Simulate lobby update (in real scenario, this comes from WebSocket)
    example_lobby_state = {
        "slots": {
            "A1": {"nickname": "Alice", "is_ai": False, "is_ready": True},
            "A2": {"nickname": None, "is_ai": False, "is_ready": False},
            "A3": {"nickname": None, "is_ai": False, "is_ready": False},
            "A4": {"nickname": None, "is_ai": False, "is_ready": False},
            "B1": {"nickname": "Bot", "is_ai": True, "ai_level": "simple", "is_ready": True},
            "B2": {"nickname": None, "is_ai": False, "is_ready": False},
            "B3": {"nickname": None, "is_ai": False, "is_ready": False},
            "B4": {"nickname": None, "is_ai": False, "is_ready": False},
        },
        "ready_players": ["Alice", "Bot"],
        "settings": {
            "match_duration": 180,
            "goal_size": 200,
        }
    }
    
    # For testing, you can uncomment this to go directly to lobby with test data
    # client.state = GameState.LOBBY
    # client.on_lobby_update(example_lobby_state)
    
    client.run()


if __name__ == "__main__":
    main()
