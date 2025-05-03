import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import random
from PIL import Image, ImageTk
import os
import sys

# Card suits and values
SUITS = ["♠", "♥", "♦", "♣"]
RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]

# Monochromatic Color Scheme
DARK_COLOR = "#1a1a2e"  # Very dark blue-gray for background
MID_DARK_COLOR = "#16213e"  # Dark blue-gray for frames
MID_COLOR = "#0f3460"  # Medium blue-gray for buttons
LIGHT_COLOR = "#e2e2e2"  # Light gray for text
ACCENT_COLOR = "#4361ee"  # Accent blue for highlights
CARD_COLOR = "#ffffff"  # White for cards
CARD_TEXT_COLOR = "#1a1a2e"  # Dark blue-gray for card text
CARD_BORDER_COLOR = "#c2c2c2"  # Light gray for card borders

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        self.face_up = True
    
    def get_value(self):
        if self.rank in ["J", "Q", "K"]:
            return 10
        elif self.rank == "A":
            return 11  # Ace is initially 11, can be adjusted to 1 if needed
        else:
            return int(self.rank)
    
    def __str__(self):
        return f"{self.rank}{self.suit}"

class Deck:
    def __init__(self):
        self.cards = []
        self.build()
    
    def build(self):
        self.cards = [Card(suit, rank) for suit in SUITS for rank in RANKS]
        random.shuffle(self.cards)
    
    def deal(self):
        if len(self.cards) > 0:
            return self.cards.pop()
        else:
            # Rebuild deck if empty
            self.build()
            return self.cards.pop()

class Hand:
    def __init__(self):
        self.cards = []
        self.value = 0
        self.aces = 0
    
    def add_card(self, card):
        self.cards.append(card)
        self.value += card.get_value()
        
        # Track aces
        if card.rank == "A":
            self.aces += 1
        
        # Adjust for aces if busting
        self.adjust_for_ace()
    
    def adjust_for_ace(self):
        # Convert ace from 11 to 1 if would bust
        while self.value > 21 and self.aces > 0:
            self.value -= 10
            self.aces -= 1
    
    def __str__(self):
        return ", ".join(str(card) for card in self.cards)

class Player:
    def __init__(self, name, bankroll=1000):
        self.name = name
        self.bankroll = bankroll
        self.hands = [Hand()]  # Support for splitting
    
    def place_bet(self, amount):
        if amount > self.bankroll:
            return False
        self.bankroll -= amount
        return True
    
    def add_winnings(self, amount):
        self.bankroll += amount

class CustomDialog(tk.Toplevel):
    def __init__(self, parent, title, prompt, min_value=1, max_value=None):
        super().__init__(parent)
        self.title(title)
        self.result = None
        self.configure(bg=DARK_COLOR)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Position dialog in center of parent
        x = parent.winfo_x() + parent.winfo_width() // 2 - 150
        y = parent.winfo_y() + parent.winfo_height() // 2 - 75
        self.geometry(f"300x150+{x}+{y}")
        
        # Create widgets
        frame = tk.Frame(self, bg=DARK_COLOR, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        prompt_label = tk.Label(
            frame, 
            text=prompt, 
            font=("Helvetica", 12),
            bg=DARK_COLOR,
            fg=LIGHT_COLOR,
            wraplength=260
        )
        prompt_label.pack(pady=(0, 10))
        
        self.entry = ttk.Entry(frame, font=("Helvetica", 12), width=15)
        self.entry.pack(pady=5)
        self.entry.focus_set()
        
        button_frame = tk.Frame(frame, bg=DARK_COLOR)
        button_frame.pack(pady=10)
        
        ok_button = ttk.Button(button_frame, text="OK", command=self.on_ok)
        ok_button.pack(side=tk.LEFT, padx=5)
        
        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.on_cancel)
        cancel_button.pack(side=tk.LEFT, padx=5)
        
        # Store validation values
        self.min_value = min_value
        self.max_value = max_value
        
        # Bind events
        self.bind("<Return>", lambda event: self.on_ok())
        self.bind("<Escape>", lambda event: self.on_cancel())
        
        # Wait for window to be destroyed
        self.wait_window()
    
    def on_ok(self):
        try:
            value = int(self.entry.get())
            if self.min_value is not None and value < self.min_value:
                messagebox.showerror("Error", f"Value must be at least {self.min_value}")
                return
            if self.max_value is not None and value > self.max_value:
                messagebox.showerror("Error", f"Value cannot exceed {self.max_value}")
                return
            self.result = value
            self.destroy()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
    
    def on_cancel(self):
        self.result = None
        self.destroy()

class BlackjackGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Blackjack")
        self.root.geometry("900x700")
        self.root.configure(bg=DARK_COLOR)
        
        # Configure ttk styles
        self.configure_styles()
        
        # Game variables
        self.deck = Deck()
        self.player = Player("Player")
        self.dealer = Player("Dealer")
        self.bet = 0
        self.current_hand_index = 0
        self.game_in_progress = False
        
        # Create UI elements
        self.create_widgets()
        
        # Start the game
        self.show_welcome()
    
    def configure_styles(self):
        style = ttk.Style()
        style.theme_use('clam')  # Use a theme that supports customization
        
        # Configure button style
        style.configure(
            'TButton',
            background=MID_COLOR,
            foreground=LIGHT_COLOR,
            font=('Helvetica', 11),
            padding=10,
            borderwidth=1,
            relief='raised'
        )
        
        # Configure button hover style
        style.map(
            'TButton',
            background=[('active', ACCENT_COLOR)],
            relief=[('pressed', 'sunken')]
        )
        
        # Configure entry style
        style.configure(
            'TEntry',
            fieldbackground=LIGHT_COLOR,
            foreground=DARK_COLOR,
            padding=5
        )
    
    def create_widgets(self):
        # Main container
        self.main_frame = tk.Frame(self.root, bg=DARK_COLOR, padx=20, pady=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title with separator
        title_frame = tk.Frame(self.main_frame, bg=DARK_COLOR)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.title_label = tk.Label(
            title_frame, 
            text="BLACKJACK", 
            font=("Helvetica", 28, "bold"), 
            bg=DARK_COLOR, 
            fg=LIGHT_COLOR
        )
        self.title_label.pack(pady=(0, 5))
        
        separator = ttk.Separator(title_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=5)
        
        # Info panel (bankroll and bet)
        self.info_frame = tk.Frame(self.main_frame, bg=MID_DARK_COLOR, padx=15, pady=10)
        self.info_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.bankroll_label = tk.Label(
            self.info_frame, 
            text=f"Bankroll: ${self.player.bankroll}", 
            font=("Helvetica", 14), 
            bg=MID_DARK_COLOR, 
            fg=LIGHT_COLOR
        )
        self.bankroll_label.pack(side=tk.LEFT)
        
        self.bet_label = tk.Label(
            self.info_frame, 
            text=f"Current Bet: ${self.bet}", 
            font=("Helvetica", 14), 
            bg=MID_DARK_COLOR, 
            fg=LIGHT_COLOR
        )
        self.bet_label.pack(side=tk.RIGHT)
        
        # Message area
        self.message_frame = tk.Frame(self.main_frame, bg=MID_DARK_COLOR, padx=15, pady=10)
        self.message_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.message_label = tk.Label(
            self.message_frame, 
            text="Welcome to Blackjack!", 
            font=("Helvetica", 14), 
            bg=MID_DARK_COLOR, 
            fg=LIGHT_COLOR,
            wraplength=800,
            justify=tk.LEFT
        )
        self.message_label.pack(fill=tk.X)
        
        # Game area
        self.game_frame = tk.Frame(self.main_frame, bg=DARK_COLOR)
        self.game_frame.pack(fill=tk.BOTH, expand=True)
        
        # Dealer area
        self.dealer_section = tk.Frame(self.game_frame, bg=MID_DARK_COLOR, padx=15, pady=15)
        self.dealer_section.pack(fill=tk.X, pady=(0, 15))
        
        dealer_header = tk.Frame(self.dealer_section, bg=MID_DARK_COLOR)
        dealer_header.pack(fill=tk.X)
        
        self.dealer_label = tk.Label(
            dealer_header, 
            text="Dealer's Cards", 
            font=("Helvetica", 14, "bold"), 
            bg=MID_DARK_COLOR, 
            fg=LIGHT_COLOR
        )
        self.dealer_label.pack(side=tk.LEFT)
        
        self.dealer_value_label = tk.Label(
            dealer_header, 
            text="Value: 0", 
            font=("Helvetica", 14), 
            bg=MID_DARK_COLOR, 
            fg=LIGHT_COLOR
        )
        self.dealer_value_label.pack(side=tk.RIGHT)
        
        # Separator
        dealer_separator = ttk.Separator(self.dealer_section, orient='horizontal')
        dealer_separator.pack(fill=tk.X, pady=5)
        
        # Dealer cards container
        self.dealer_cards_frame = tk.Frame(self.dealer_section, bg=MID_DARK_COLOR)
        self.dealer_cards_frame.pack(fill=tk.X, pady=10)
        
        # Player area
        self.player_section = tk.Frame(self.game_frame, bg=MID_DARK_COLOR, padx=15, pady=15)
        self.player_section.pack(fill=tk.X)
        
        player_header = tk.Frame(self.player_section, bg=MID_DARK_COLOR)
        player_header.pack(fill=tk.X)
        
        self.player_label = tk.Label(
            player_header, 
            text="Your Cards", 
            font=("Helvetica", 14, "bold"), 
            bg=MID_DARK_COLOR, 
            fg=LIGHT_COLOR
        )
        self.player_label.pack(side=tk.LEFT)
        
        self.player_value_label = tk.Label(
            player_header, 
            text="Value: 0", 
            font=("Helvetica", 14), 
            bg=MID_DARK_COLOR, 
            fg=LIGHT_COLOR
        )
        self.player_value_label.pack(side=tk.RIGHT)
        
        # Separator
        player_separator = ttk.Separator(self.player_section, orient='horizontal')
        player_separator.pack(fill=tk.X, pady=5)
        
        # Player cards container
        self.player_cards_frame = tk.Frame(self.player_section, bg=MID_DARK_COLOR)
        self.player_cards_frame.pack(fill=tk.X, pady=10)
        
        # Buttons area
        self.button_section = tk.Frame(self.main_frame, bg=DARK_COLOR, pady=15)
        self.button_section.pack(fill=tk.X)
        
        # Game action buttons
        self.action_buttons = tk.Frame(self.button_section, bg=DARK_COLOR)
        self.action_buttons.pack()
        
        self.hit_button = ttk.Button(
            self.action_buttons, 
            text="Hit",
            command=self.hit,
            width=12
        )
        self.hit_button.grid(row=0, column=0, padx=8, pady=5)
        
        self.stand_button = ttk.Button(
            self.action_buttons, 
            text="Stand",
            command=self.stand,
            width=12
        )
        self.stand_button.grid(row=0, column=1, padx=8, pady=5)
        
        self.double_button = ttk.Button(
            self.action_buttons, 
            text="Double Down",
            command=self.double_down,
            width=12
        )
        self.double_button.grid(row=0, column=2, padx=8, pady=5)
        
        self.split_button = ttk.Button(
            self.action_buttons, 
            text="Split",
            command=self.split,
            width=12
        )
        self.split_button.grid(row=0, column=3, padx=8, pady=5)
        
        # Game control buttons
        self.control_buttons = tk.Frame(self.button_section, bg=DARK_COLOR, pady=10)
        self.control_buttons.pack()
        
        self.deal_button = ttk.Button(
            self.control_buttons, 
            text="Deal",
            command=self.start_round,
            width=15
        )
        self.deal_button.grid(row=0, column=0, padx=10)
        
        self.new_game_button = ttk.Button(
            self.control_buttons, 
            text="New Game",
            command=self.new_game,
            width=15
        )
        self.new_game_button.grid(row=0, column=1, padx=10)
        
        # Add tooltips
        self.create_tooltip(self.hit_button, "Take another card")
        self.create_tooltip(self.stand_button, "End your turn")
        self.create_tooltip(self.double_button, "Double your bet and take exactly one more card")
        self.create_tooltip(self.split_button, "Split your hand into two separate hands")
        self.create_tooltip(self.deal_button, "Start a new round")
        self.create_tooltip(self.new_game_button, "Reset the game with a fresh bankroll")
        
        # Initially disable game action buttons
        self.disable_game_buttons()
    
    def create_tooltip(self, widget, text):
        def enter(event):
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 25
            
            # Create a toplevel window
            self.tooltip = tk.Toplevel(widget)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")
            
            label = tk.Label(
                self.tooltip, 
                text=text, 
                bg=LIGHT_COLOR, 
                fg=DARK_COLOR,
                font=("Helvetica", 10),
                relief="solid", 
                borderwidth=1,
                padx=5,
                pady=2
            )
            label.pack()
            
        def leave(event):
            if hasattr(self, 'tooltip'):
                self.tooltip.destroy()
                
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)
    
    def show_welcome(self):
        self.message_label.config(text="Welcome to Blackjack! Press 'Deal' to start a new round.")
        self.update_bankroll_display()
        self.enable_deal_button()
    
    def update_bankroll_display(self):
        self.bankroll_label.config(text=f"Bankroll: ${self.player.bankroll}")
        self.bet_label.config(text=f"Current Bet: ${self.bet}")
    
    def clear_cards(self):
        # Clear dealer cards
        for widget in self.dealer_cards_frame.winfo_children():
            widget.destroy()
        
        # Clear player cards
        for widget in self.player_cards_frame.winfo_children():
            widget.destroy()
        
        # Reset value labels
        self.dealer_value_label.config(text="Value: 0")
        self.player_value_label.config(text="Value: 0")
    
    def create_card_widget(self, card, parent_frame):
        # Create a frame for the card with rounded corners effect
        card_frame = tk.Frame(
            parent_frame,
            width=90,
            height=130,
            bg=CARD_COLOR,
            highlightbackground=CARD_BORDER_COLOR,
            highlightthickness=2,
            padx=5,
            pady=5
        )
        card_frame.pack_propagate(False)  # Prevent the frame from shrinking
        card_frame.pack(side=tk.LEFT, padx=8, pady=5)
        
        if not card.face_up:
            # Card back
            card_back = tk.Frame(card_frame, bg=MID_COLOR, width=80, height=120)
            card_back.pack(fill=tk.BOTH, expand=True)
            
            # Pattern on card back
            for i in range(5):
                line = tk.Frame(card_back, bg=MID_DARK_COLOR, height=2)
                line.place(relx=0.1, rely=0.2 + i*0.15, relwidth=0.8, height=2)
            
            # Small circle in center
            circle_frame = tk.Frame(card_back, bg=ACCENT_COLOR, width=20, height=20)
            circle_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        else:
            # Card rank at top-left
            rank_label = tk.Label(
                card_frame,
                text=card.rank,
                font=("Helvetica", 16, "bold"),
                bg=CARD_COLOR,
                fg=CARD_TEXT_COLOR
            )
            rank_label.place(x=5, y=5)
            
            # Card suit in center
            suit_label = tk.Label(
                card_frame,
                text=card.suit,
                font=("Helvetica", 36),
                bg=CARD_COLOR,
                fg=CARD_TEXT_COLOR
            )
            suit_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            
            # Card rank at bottom-right (upside down)
            rank_label_bottom = tk.Label(
                card_frame,
                text=card.rank,
                font=("Helvetica", 16, "bold"),
                bg=CARD_COLOR,
                fg=CARD_TEXT_COLOR
            )
            rank_label_bottom.place(relx=1.0, rely=1.0, x=-10, y=-10, anchor=tk.SE)
    
    def update_card_display(self):
        # Clear existing cards
        for widget in self.dealer_cards_frame.winfo_children():
            widget.destroy()
        
        for widget in self.player_cards_frame.winfo_children():
            widget.destroy()
        
        # Display dealer cards
        dealer_hand = self.dealer.hands[0]
        for i, card in enumerate(dealer_hand.cards):
            # First card is face down if game is in progress
            if i == 1 and self.game_in_progress:
                card.face_up = False
            else:
                card.face_up = True
            
            # Add slight delay for animation effect
            self.root.update()
            self.root.after(100)
            
            self.create_card_widget(card, self.dealer_cards_frame)
        
        # Update dealer value
        if self.game_in_progress:
            # Only show value of first card if game is in progress
            self.dealer_value_label.config(text=f"Value: {dealer_hand.cards[0].get_value()}")
        else:
            self.dealer_value_label.config(text=f"Value: {dealer_hand.value}")
        
        # Display player cards
        player_hand = self.player.hands[self.current_hand_index]
        
        # If multiple hands, highlight the current one
        if len(self.player.hands) > 1:
            if self.current_hand_index == 0:
                self.player_label.config(text="Your Cards (Hand 1) ★")
            else:
                self.player_label.config(text="Your Cards (Hand 2) ★")
        else:
            self.player_label.config(text="Your Cards")
        
        for card in player_hand.cards:
            # Add slight delay for animation effect
            self.root.update()
            self.root.after(100)
            
            self.create_card_widget(card, self.player_cards_frame)
        
        # Update player value
        self.player_value_label.config(text=f"Value: {player_hand.value}")
    
    def enable_game_buttons(self):
        self.hit_button.config(state=tk.NORMAL)
        self.stand_button.config(state=tk.NORMAL)
        
        # Enable double down only on first two cards
        player_hand = self.player.hands[self.current_hand_index]
        if len(player_hand.cards) == 2 and self.player.bankroll >= self.bet:
            self.double_button.config(state=tk.NORMAL)
        else:
            self.double_button.config(state=tk.DISABLED)
        
        # Enable split only if first two cards are the same rank and player has enough money
        if (len(player_hand.cards) == 2 and 
            player_hand.cards[0].rank == player_hand.cards[1].rank and 
            self.player.bankroll >= self.bet and
            len(self.player.hands) < 2):  # Limit to one split for simplicity
            self.split_button.config(state=tk.NORMAL)
        else:
            self.split_button.config(state=tk.DISABLED)
        
        self.deal_button.config(state=tk.DISABLED)
    
    def disable_game_buttons(self):
        self.hit_button.config(state=tk.DISABLED)
        self.stand_button.config(state=tk.DISABLED)
        self.double_button.config(state=tk.DISABLED)
        self.split_button.config(state=tk.DISABLED)
    
    def enable_deal_button(self):
        self.deal_button.config(state=tk.NORMAL)
        self.disable_game_buttons()
    
    def get_bet(self):
        dialog = CustomDialog(
            self.root,
            "Place Your Bet",
            f"Your bankroll: ${self.player.bankroll}\nEnter your bet amount:",
            min_value=1,
            max_value=self.player.bankroll
        )
        
        bet = dialog.result
        if bet is None:  # User cancelled
            return False
        
        self.bet = bet
        return self.player.place_bet(bet)
    
    def start_round(self):
        # Reset hands
        self.player.hands = [Hand()]
        self.dealer.hands = [Hand()]
        self.current_hand_index = 0
        
        # Get bet
        if not self.get_bet():
            self.message_label.config(text="Please place a valid bet to start the game.")
            return
        
        self.game_in_progress = True
        self.update_bankroll_display()
        self.clear_cards()
        
        # Deal initial cards
        for _ in range(2):
            self.player.hands[0].add_card(self.deck.deal())
            self.dealer.hands[0].add_card(self.deck.deal())
        
        self.update_card_display()
        
        # Check for blackjack
        player_hand = self.player.hands[0]
        dealer_hand = self.dealer.hands[0]
        
        if self.check_blackjack(player_hand) or self.check_blackjack(dealer_hand):
            self.game_in_progress = False
            # Show all cards
            for card in dealer_hand.cards:
                card.face_up = True
            self.update_card_display()
            
            outcome = self.determine_outcome(player_hand)
            self.settle_bet(outcome)
            self.enable_deal_button()
        else:
            self.message_label.config(text="Your turn. Choose an action.")
            self.enable_game_buttons()
    
    def check_blackjack(self, hand):
        return len(hand.cards) == 2 and hand.value == 21
    
    def hit(self):
        player_hand = self.player.hands[self.current_hand_index]
        player_hand.add_card(self.deck.deal())
        self.update_card_display()
        
        # Check if player busts
        if player_hand.value > 21:
            self.message_label.config(text="Bust! You went over 21.")
            self.process_next_hand()
        else:
            # Disable double down after hitting
            self.double_button.config(state=tk.DISABLED)
            self.split_button.config(state=tk.DISABLED)
    
    def stand(self):
        self.process_next_hand()
    
    def double_down(self):
        player_hand = self.player.hands[self.current_hand_index]
        
        # Double the bet
        if not self.player.place_bet(self.bet):
            self.message_label.config(text="Not enough money to double down!")
            return
        
        self.bet *= 2
        self.update_bankroll_display()
        
        # Deal one more card
        player_hand.add_card(self.deck.deal())
        self.update_card_display()
        
        # Move to next hand or dealer's turn
        self.process_next_hand()
    
    def split(self):
        player_hand = self.player.hands[self.current_hand_index]
        
        # Create a new hand with the second card
        new_hand = Hand()
        new_hand.add_card(player_hand.cards.pop())
        
        # Adjust the value of the original hand
        player_hand.value = 0
        player_hand.aces = 0
        for card in player_hand.cards:
            if card.rank == "A":
                player_hand.aces += 1
            player_hand.value += card.get_value()
        player_hand.adjust_for_ace()
        
        # Add a new card to each hand
        player_hand.add_card(self.deck.deal())
        new_hand.add_card(self.deck.deal())
        
        # Place the additional bet
        if not self.player.place_bet(self.bet):
            self.message_label.config(text="Not enough money to split!")
            return
        
        # Add the new hand to the player's hands
        self.player.hands.append(new_hand)
        
        self.update_bankroll_display()
        self.update_card_display()
        self.message_label.config(text="Hand split! Playing first hand.")
    
    def process_next_hand(self):
        # Move to the next hand if there is one
        if self.current_hand_index < len(self.player.hands) - 1:
            self.current_hand_index += 1
            self.update_card_display()
            self.enable_game_buttons()
            self.message_label.config(text=f"Playing hand {self.current_hand_index + 1}. Choose an action.")
        else:
            # All hands played, move to dealer's turn
            self.dealer_turn()
    
    def dealer_turn(self):
        self.game_in_progress = False
        dealer_hand = self.dealer.hands[0]
        
        # Show all dealer cards
        for card in dealer_hand.cards:
            card.face_up = True
        self.update_card_display()
        self.message_label.config(text="Dealer's turn...")
        
        # Dealer hits until 17 or higher
        while dealer_hand.value < 17:
            self.root.update()
            self.root.after(800)  # Pause for better visualization
            dealer_hand.add_card(self.deck.deal())
            self.update_card_display()
            self.root.update()
        
        # Determine outcomes for all hands
        for i, hand in enumerate(self.player.hands):
            self.current_hand_index = i
            self.root.after(800)  # Pause between hands
            outcome = self.determine_outcome(hand)
            self.settle_bet(outcome)
        
        self.enable_deal_button()
    
    def determine_outcome(self, player_hand):
        dealer_hand = self.dealer.hands[0]
        player_blackjack = self.check_blackjack(player_hand)
        dealer_blackjack = self.check_blackjack(dealer_hand)
        
        # Determine outcome
        if player_hand.value > 21:
            self.message_label.config(text="You bust! Dealer wins.")
            return "lose"
        elif dealer_hand.value > 21:
            self.message_label.config(text="Dealer busts! You win.")
            return "win"
        elif player_blackjack and not dealer_blackjack:
            self.message_label.config(text="Blackjack! You win 3:2.")
            return "blackjack"
        elif dealer_blackjack and not player_blackjack:
            self.message_label.config(text="Dealer has Blackjack! You lose.")
            return "lose"
        elif player_blackjack and dealer_blackjack:
            self.message_label.config(text="Both have Blackjack! Push.")
            return "push"
        elif player_hand.value > dealer_hand.value:
            self.message_label.config(text="You win!")
            return "win"
        elif player_hand.value < dealer_hand.value:
            self.message_label.config(text="Dealer wins!")
            return "lose"
        else:
            self.message_label.config(text="Push! It's a tie.")
            return "push"
    
    def settle_bet(self, outcome):
        original_bet = self.bet / len(self.player.hands)  # Split the bet among hands
        
        if outcome == "win":
            self.player.add_winnings(original_bet * 2)  # Original bet + winnings
        elif outcome == "blackjack":
            self.player.add_winnings(original_bet * 2.5)  # Original bet + 3:2 payout
        elif outcome == "push":
            self.player.add_winnings(original_bet)  # Return original bet
        
        self.update_bankroll_display()
    
    def new_game(self):
        result = messagebox.askyesno(
            "New Game", 
            "Start a new game with $1000?",
            icon=messagebox.QUESTION
        )
        
        if result:
            self.player.bankroll = 1000
            self.bet = 0
            self.deck = Deck()
            self.clear_cards()
            self.update_bankroll_display()
            self.show_welcome()

# Run the game
if __name__ == "__main__":
    root = tk.Tk()
    game = BlackjackGUI(root)
    root.mainloop()