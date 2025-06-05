# AUTHOR - MATTHEW RAYNER | TWO PLAYER CARD GAME


# LIBRARIES
import random
from collections import namedtuple, Counter
import pygame
import os
import sys
import time


# CONFIG
CONFIG = {
        'green': [34, 139, 34],
        'green-dark': [34, 133, 85],
        'red': [241, 97, 84],
        'blue': [84, 166, 223],
        'grey_transparent': [0, 0, 0, 80],
        'white': [255, 255, 255],
        'black': [0, 0, 0],
        'menu-bg': [47, 51, 57],
        'button-bg': [145, 96, 0],
        'button-dark': [26, 33, 38],
        'orange': [255, 140, 0],
        'font': 'assets/FSEX302.ttf'
        }


# CONSTANTS
UI_SCALING = 1 
CROP_WIDTH = 142
CROP_HEIGHT = 190
CARD_WIDTH = CROP_WIDTH * UI_SCALING
CARD_HEIGHT = CROP_HEIGHT * UI_SCALING
ROWS = 5
CARD_SPACING_X = 210 * UI_SCALING
CARD_SPACING_Y = 50 * UI_SCALING 
MENU_WIDTH = 250 * UI_SCALING
WINDOW_SCALING = 0.90  
CARDS_PER_ROW = 5
SUIT_ORDER = {'Hearts': 1, 'Diamonds': 2, 'Clubs': 3, 'Spades':4}
RANK_ORDER = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
PLAYER_SHADOW_OFFSETS = {
    0: (-15, 5),
    1: (-7, 7),
    2: (0, 10),
    3: (7, 7),
    4: (15, 5)
}
OPPONENT_SHADOW_OFFSETS = {
    0: (-15, -5),
    1: (-7, -7),
    2: (0, -10),
    3: (7, -7),
    4: (15, -5)
}


# CLASSES
class Card:
    def __init__(self, rank, suit, image, card_back):
        self.rank = rank
        self.suit = suit
        self.image = image
        self.card_back = card_back
        self.rect = pygame.Rect(0, 0, (CARD_WIDTH * UI_SCALING), (CARD_HEIGHT * UI_SCALING))
        self.hovered_scale = 1 
        self.current_scale = 1

    def draw(self, screen, x, y, rotate=False, shadow=False, shadow_offset=(5, 5), hidden=False, is_player=True):
        """ Draws the card on the screen, rotating it if indicated, and adding some shadow """
        mouse_x, mouse_y = pygame.mouse.get_pos()
        hovered = self.rect.collidepoint(mouse_x, mouse_y) if is_player else False

        self.target_scale = 1.05 if hovered else 1.0
        self.current_scale += (self.target_scale - self.current_scale) * 0.15
        
        card_width = int(CARD_WIDTH * self.current_scale)
        card_height = int(CARD_HEIGHT * self.current_scale)

        if shadow:
            shadow_surface = pygame.Surface(((CARD_WIDTH), (CARD_HEIGHT)), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surface, (0, 0, 0, 80), (0, 0, (CARD_WIDTH), (CARD_HEIGHT)), border_radius=10)
            screen.blit(shadow_surface, (x + shadow_offset[0], y + shadow_offset[1]))

        card_image = self.card_back if hidden else self.image
        card_image = pygame.transform.scale(card_image, (card_width, card_height))

        if rotate:
            card_image = pygame.transform.rotate(card_image, 180)

        screen.blit(card_image, (x - (card_width - CARD_WIDTH) // 2, y - (card_height - CARD_HEIGHT) // 2))
        self.rect.topleft = (x, y)
        self.rect.size = (card_width, card_height)


class Deck:
    def __init__(self, sprite_sheet, card_back):
        self.cards = self.create_deck(sprite_sheet, card_back)
        random.shuffle(self.cards)
        self.card_back = card_back

    def create_deck(self, sprite_sheet, card_back):
        cards = []
        suits = ['Hearts', 'Clubs', 'Diamonds', 'Spades']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

        for row, suit in enumerate(suits):
            for col, rank in enumerate(ranks):
                card_surface = pygame.Surface(((CROP_WIDTH), (CROP_HEIGHT)), pygame. SRCALPHA)
                pygame.draw.rect(card_surface, (255, 255, 255), (0, 0, (CROP_WIDTH), (CROP_HEIGHT)), border_radius=10)
                card_crop = pygame.Rect(col * CROP_WIDTH, row * CROP_HEIGHT, CROP_WIDTH, CROP_HEIGHT)
                card_image = sprite_sheet.subsurface(card_crop)
                card_surface.blit(card_image, (0, 0))
                cards.append(Card(rank, suit, card_surface, card_back))

        return cards

    def deal_card(self):
        return self.cards.pop() if self.cards else None

    def draw_stack(self, screen, x, y):
        """ Draws the deck stack with a decreasing effect """
        for i in range(min(len(self.cards), 2)):
            back_image = pygame.transform.scale(self.card_back, (CARD_WIDTH, CARD_HEIGHT))
            screen.blit(back_image, (x -  i * 5, y - i * 5))


class Button:
    def __init__(self, x, y, width, height, text, color, outline_color, text_color, action):
        self.rect = pygame.Rect(x+3, y+3, width * UI_SCALING - 6, height * UI_SCALING - 6)
        self.back_rect = pygame.Rect(x, y, width * UI_SCALING, height * UI_SCALING)
        self.text = text
        self.color = color
        self.outline_color = outline_color
        self.text_color = text_color
        self.action = action

    def button_draw(self, screen):
        pygame.draw.rect(screen, self.outline_color, self.back_rect, border_radius=10)
        pygame.draw.rect(screen, self.color, self.rect, border_radius=10)
        self.font = pygame.font.Font(CONFIG['font'], int(self.rect.height * 0.5))
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.action()


class GameState:
    def __init__(self, sprite_sheet, card_back):
        self.sprite_sheet = sprite_sheet
        self.card_back = card_back
        self.deck = Deck(self.sprite_sheet, self.card_back)
        self.player_hand = [] 
        self.opponent_hand = []
        self.player_turn = True 
        self.drawn_card = None

    def draw_card(self):
        if self.player_turn == True and self.deck.cards:
            self.drawn_card = self.deck.deal_card()
        elif self.player_turn == False and self.deck.cards:
            self.drawn_card = self.deck.deal_card()

    def shuffle_deck(self):
        self.deck = Deck(self.sprite_sheet, self.card_back)
        random.shuffle(self.deck.cards) 
        self.player_hand = [[self.deck.deal_card()] for _ in range(ROWS)]
        self.opponent_hand = [[self.deck.deal_card()] for _ in range(ROWS)]
        self.drawn_card = None
        self.player_turn = True


class RowFlames:
    def __init__(self, x, y, direction):
        self.particles = []
        self.x = x
        self.y = y
        self.direction = direction
        self.width = 0
        self.max_width = 50
        self.growth_speed = 5
        self.flame_color = CONFIG['orange'] 

    def update(self):
        if self.width < self.max_width:
            self.width += self.growth_speed

    def draw(self, screen, row_content_rect):
        if self.direction == "left":
            flame_rect = pygame.Rect(row_content_rect.left, row_content_rect.top, self.width, row_content_rect.height)
        else:
            flame_rect = pygame.Rect(row_content_rect.right - self.width, row_content_rect.top, self.width, row_content_rect.height)

        pygame.draw.rect(screen, self.flame_color, flame_rect, border_radius=10)


# FUNCTIONS           
def load_background(SCREEN_WIDTH, SCREEN_HEIGHT):
    """ Attempts to load the background texture for the table """
    try:
        texture = pygame.image.load(os.path.join("assets", "table_texture.png")).convert()
        return pygame.transform.scale(texture, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except:
        return None # Fallback if background texture fails to load


def load_assets():
    """ Load all game assets """
    try:
        return pygame.image.load(os.path.join("assets", "card_designs.png")).convert_alpha()
    except pygame.error as e:
        print(f'Error loading sprite sheet: {e}')
        sys.exit(1)
        

def draw_hand(screen, hand, row_x, row_y, shadow_offsets, is_opponent=False):
    for row_index, row in enumerate(hand):
        for col_index, card in enumerate(row):
            card_x = row_x + (row_index * CARD_SPACING_X)
            card_y = row_y + (col_index * CARD_SPACING_Y) * (-1 if is_opponent else 1)
            card.draw(screen, card_x, card_y, shadow=True, shadow_offset=shadow_offsets[row_index], is_player=False if is_opponent else True)


def draw_deck_counter(screen, count, x, y):
    """ Draws the deck counter near the deck area """
    font = pygame.font.Font(CONFIG['font'], 25)
    text_surface = font.render(f"{count}/52", True, CONFIG['white'])
    screen.blit(text_surface, (x, y))


def bounce_card(card):
    original_size = card.image.get_size()
    enlarged_size = (int(original_size[0] * 1.1), int(original_size[1] * 1.1))

    card.image = pygame.transform.scale(card.image, enlarged_size)
    time.sleep(0.05)

    card.image = pygame.transform.scale(card.image, original_size) 


def min_cards_in_row(rows):
    """ Returns the current minimum number of cards in the rows """
    return min(len(row) for row in rows)


def validate_row(row, rows):
    """ Checks if a card can be placed in the chosen row, using the minimum number of cards """
    return len(row) == min_cards_in_row(rows) and len(row) < CARDS_PER_ROW


def rank_hand(hand):
    """ Evaluates a poker hand assigns a numberic value for comparison """
    ranks = sorted([RANK_ORDER[card.rank] for card in hand], reverse=True)
    suits = [card.suit for card in hand]
    rank_counts = Counter(ranks)
    rank_frequencies = sorted(rank_counts.values(), reverse=True)

    is_flush = len(set(suits)) == 1 and len(hand) == 5
    is_straight = ranks == list(range(ranks[0], ranks[0] - 5, -1))

    if is_flush and is_straight and ranks[0] == 14: 
        return [10, ranks, 'Royal Flush']
    elif is_flush and is_straight:
        return [9, ranks, 'Straight Flush']
    elif max(rank_frequencies) == 4:
        return [8, ranks, 'Four of a Kind']
    elif rank_frequencies == [3, 2]:
        return [7, ranks, 'Full House']
    elif is_flush:
        return [6, ranks, 'Flush']
    elif is_straight:
        return [5, ranks, 'Straight']
    elif 3 in rank_frequencies:
        return [4, ranks, 'Three of a Kind']
    elif rank_frequencies.count(2) == 2:
        return [3, ranks, 'Two Pair']
    elif 2 in rank_frequencies:
        return [2, ranks, 'Pair']
    else: # High Card
        return [1, ranks, 'High']


def compare_rows(player_hand, opponent_hand):
    """ Compares all rows and determines the overall winner """
    player_wins = 0
    opponent_wins = 0
    row_wins = {}

    for i in range(ROWS):
        player_rank = rank_hand(player_hand[i])
        opponent_rank = rank_hand(opponent_hand[i])

        if player_rank > opponent_rank:
            player_wins += 1
            row_wins[i] = 'player'
        elif opponent_rank > player_rank:
            opponent_wins += 1
            row_wins[i] = 'opponent'
        else:
            row_wins[i] = 'draw'

    if player_wins > opponent_wins:
        return ["Players Wins!", row_wins]
    elif opponent_wins > player_wins:
        return ["Opponent Wins!", row_wins]
    else:
        return ["It's a draw!", row_wins]


def get_max_card(hand_ranks, rank_frequencies, hand_rank):
    """ Returns the most relevant high card based on hand ranking """
    if not hand_ranks:
        return 0

    sorted_ranks = sorted(hand_ranks, key=lambda r: (r != 14, rank_frequencies[r], r), reverse=True)
    
    if hand_rank in {1, 2, 3, 6}:
        max_pair_card = max((r for r in sorted_ranks if rank_frequencies[r] > 1), default=None)
        
        if max_pair_card: 
            max_card = max_pair_card
        else:
            max_card = max(sorted_ranks)
    else:
        max_card = max(sorted_ranks)

    return max_card 


def menu_row_state(screen, SCREEN_WIDTH, SCREEN_HEIGHT, state=None, player_hand=None, opponent_hand=None):
    """ Draws an overlay display on the menu area that gives the player information on how a row is doing """
    if not player_hand:
        return

    # Initialize fonts
    header_font = pygame.font.Font(CONFIG['font'], 24) 
    content_font_player = pygame.font.Font(CONFIG['font'], 22)
    content_font_opponent = pygame.font.Font(CONFIG['font'], 18)
    row_results = {}

    # Array with items to be displayed
    for i in range(ROWS):
        if (tuple(player_hand[i]), tuple(opponent_hand[i])) not in row_results:
            player_rank = rank_hand(player_hand[i])
            opponent_rank = rank_hand(opponent_hand[i])
            row_results[(tuple(player_hand[i]), tuple(opponent_hand[i]))] = (player_rank, opponent_rank)
        else:
            player_rank, opponent_rank = row_results[(tuple(player_hand[i]), tuple(opponent_hand[i]))]

        max_player = get_max_card(player_rank[1], Counter(player_rank[1]), player_rank[0])
        max_opponent = get_max_card(opponent_rank[1], Counter(opponent_rank[1]), opponent_rank[0])

        display_player_card = {14: 'A', 13: 'K', 12: 'Q', 11: 'J'}.get(max_player, str(max_player))
        display_opponent_card = {14: 'A', 13: 'K', 12: 'Q', 11: 'J'}.get(max_opponent, str(max_opponent))

        if player_rank[0] == opponent_rank[0]:
            if max_player > max_opponent:
                player_winning, opponent_winning = True, False
            elif max_opponent > max_player:
                player_winning, opponent_winning = False, True
            else:
                player_winning, opponent_winning = False, False
        else:
            player_winning = player_rank[0] > opponent_rank[0]
            opponent_winning = opponent_rank[0] > player_rank[0]

        # Outer Rectangle
        menu_display_rect = pygame.Rect(65, 100 + (i * 120), MENU_WIDTH - 10, 110)
        pygame.draw.rect(screen, CONFIG['button-dark'], menu_display_rect, border_radius=10)

        # Row content rectangle
        row_content_rect = pygame.Rect(
                menu_display_rect.left + 5,
                menu_display_rect.top + 40,
                menu_display_rect.width - 10,
                60
        )
        pygame.draw.rect(screen, CONFIG['menu-bg'], row_content_rect, border_radius=10)

        # Flame particles
        if player_winning:
            row_flames = RowFlames(row_content_rect.left, row_content_rect.centery, 'left')
        elif opponent_winning:
            row_flames = RowFlames(row_content_rect.right, row_content_rect.centery, 'right')
        else:
            row_flames = None

        if row_flames:
            row_flames.update()
            row_flames.draw(screen, row_content_rect)

        # Render header
        header_surface = header_font.render(f'Row {i + 1}', True, CONFIG['white'])
        screen.blit(header_surface, (MENU_WIDTH / 2 + 30, menu_display_rect.top + 10))

        # Render player & opponent rankings
        player_text = f'{player_rank[2]} {display_player_card}'
        opponent_text = f'{opponent_rank[2]} {display_opponent_card}'
        
        player_surface = content_font_player.render(player_text, True, CONFIG['white'])
        opponent_surface = content_font_opponent.render(opponent_text, True, CONFIG['white'])
        opponent_rect = opponent_surface.get_rect(right=row_content_rect.right - 10, bottom=row_content_rect.bottom - 10)

        screen.blit(player_surface, (row_content_rect.left + 10, row_content_rect.top + 10))
        screen.blit(opponent_surface, opponent_rect)


def check_game_end(player_hand, opponent_hand):
    """ Checks if all rows are full and determines the winner """
    if all(len(row) == CARDS_PER_ROW for row in player_hand) and all(len(row) == CARDS_PER_ROW for row in opponent_hand) and player_hand and opponent_hand:
        return compare_rows(player_hand, opponent_hand)
    return None


def show_winner_message(screen, result, SCREEN_WIDTH, SCREEN_HEIGHT):
    """ Displays a semi-transparent winner message overly """
    font = pygame.font.Font(CONFIG['font'], 72)
    text = f'{result}'

    text_surface = font.render(result, True, CONFIG['white'])
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    
    screen.blit(text_surface, text_rect)


def draw_ui(screen, button):
    button.button_draw(screen)

# MAIN
def main():
    # PYGAME INITIALIZATION 
    pygame.init()
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    info = pygame.display.Info()
    SCREEN_WIDTH, SCREEN_HEIGHT = int(info.current_w * WINDOW_SCALING), int(info.current_h * WINDOW_SCALING)

    # Create a window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Card Game')

    # Initialize core functions
    background_texture = load_background(SCREEN_WIDTH, SCREEN_HEIGHT)
    card_sprites = load_assets()
    card_back = pygame.image.load(os.path.join('assets', 'card_back.png')).convert_alpha()
    game_state = GameState(card_sprites, card_back)
    arrow_player = pygame.image.load(os.path.join('assets', 'arrow_player.png')).convert_alpha()
    arrow_opponent = pygame.image.load(os.path.join('assets', 'arrow_opponent.png')).convert_alpha()
    drag_card = None 
    drag_offset_x, drag_offset_y = 0, 0
    clock = pygame.time.Clock()
    DRAW_AREA_X = SCREEN_WIDTH - 250 
    DRAW_AREA_Y = {'player': SCREEN_HEIGHT - 290, 'opponent': 100, 'deck': SCREEN_HEIGHT / 2 - 95}
    ROW_AREA_X_initial = MENU_WIDTH + 60 + 75
    ROW_AREA_Y = {'player': SCREEN_HEIGHT / 2 + 50, 'opponent': SCREEN_HEIGHT / 2 - 240}
    shuffle_button = Button(65, SCREEN_HEIGHT - 265, MENU_WIDTH - 10, 75, 'Shuffle', CONFIG['button-bg'], CONFIG['button-dark'], CONFIG['white'], game_state.shuffle_deck)
    draw_button = Button(65, SCREEN_HEIGHT - 175, MENU_WIDTH - 10, 75, 'Draw', CONFIG['button-bg'], CONFIG['button-dark'], CONFIG['white'], game_state.draw_card)
    buttons = [shuffle_button, draw_button]

    running = True
    while running:
        screen.fill(CONFIG['green'])
        if background_texture:
            screen.blit(background_texture, (0,0))

        # Menu and button overlays 
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(overlay, CONFIG['menu-bg'], (60, 0, MENU_WIDTH, SCREEN_HEIGHT))
        pygame.draw.rect(overlay, CONFIG['button-bg'], (59, -3, MENU_WIDTH + 2, SCREEN_HEIGHT + 6), width=2) # Menu outline

        # Card area/shadow overlays
        pygame.draw.rect(overlay, CONFIG['grey_transparent'], (DRAW_AREA_X, DRAW_AREA_Y['player'], ((CARD_WIDTH * UI_SCALING) * UI_SCALING) + 10, (CARD_HEIGHT * UI_SCALING)), border_radius=10)
        pygame.draw.rect(overlay, CONFIG['grey_transparent'], (DRAW_AREA_X, DRAW_AREA_Y['opponent'], (CARD_WIDTH * UI_SCALING) + 10, (CARD_HEIGHT * UI_SCALING) + 10), border_radius=10)
        pygame.draw.rect(overlay, CONFIG['grey_transparent'], (DRAW_AREA_X, DRAW_AREA_Y['deck'] + 5, (CARD_WIDTH * UI_SCALING) + 5, (CARD_HEIGHT * UI_SCALING) - 5), border_radius=10)
        screen.blit(overlay, (0,0))

        # Deck Visual Creation
        game_state.deck.draw_stack(screen, DRAW_AREA_X, DRAW_AREA_Y['deck'] - 2)
        draw_deck_counter(screen, len(game_state.deck.cards), DRAW_AREA_X + 100, DRAW_AREA_Y['deck'] + 195)
       
        # Handle mouse hover detection for cards
        mouse_x, mouse_y = pygame.mouse.get_pos()
        for row in game_state.player_hand:
            for card in row:
                card.hovered = card.rect.collidepoint(mouse_x, mouse_y)

        # Draw cards from the players initial hands
        draw_hand(screen, game_state.player_hand, ROW_AREA_X_initial, ROW_AREA_Y['player'], PLAYER_SHADOW_OFFSETS)
        draw_hand(screen, game_state.opponent_hand, ROW_AREA_X_initial, ROW_AREA_Y['opponent'], OPPONENT_SHADOW_OFFSETS, is_opponent=True)

        # Draw Buttons
        for i in range(len(buttons)):
            draw_ui(screen, buttons[i])

        # Draw initial menu game state overlay
        if not game_state.player_hand: 
            menu_row_state(screen, SCREEN_WIDTH, SCREEN_HEIGHT)

        # Draw row indicators on the board
        if game_state.player_hand:
            current_state = compare_rows(game_state.player_hand, game_state.opponent_hand)
            menu_row_state(screen, SCREEN_WIDTH, SCREEN_HEIGHT, state=current_state, player_hand=game_state.player_hand, opponent_hand=game_state.opponent_hand)

        # Draw player's initial card
        if game_state.drawn_card:
            card_x, card_y = pygame.mouse.get_pos() if drag_card else (DRAW_AREA_X, DRAW_AREA_Y['player'] - 5)
            game_state.drawn_card.draw(screen, card_x - drag_offset_x, card_y - drag_offset_y)

        for event in pygame.event.get():
            # Initialize Button Utility
            for button in buttons:
                button.handle_event(event)

            # Allows game to be quit 
            if event.type == pygame.QUIT:
                running = False
        
            # Allows card to be clicked and be dragged
            elif event.type == pygame.MOUSEBUTTONDOWN and game_state.player_turn and game_state.drawn_card:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if game_state.drawn_card.rect.collidepoint(mouse_x, mouse_y):
                    drag_card = game_state.drawn_card
                    drag_offset_x = mouse_x - game_state.drawn_card.rect.x
                    drag_offset_y = mouse_y - game_state.drawn_card.rect.y
        
            # Checks if the card is let go in a valid row
            elif event.type == pygame.MOUSEBUTTONUP and drag_card:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for row_index, row in enumerate(game_state.player_hand):
                    row_x = ROW_AREA_X_initial + (row_index * CARD_SPACING_X)
                    if row_x < mouse_x < row_x + (CARD_WIDTH * UI_SCALING) and mouse_y > ROW_AREA_Y['player'] - 1:
                        if validate_row(row, game_state.player_hand):
                            bounce_card(drag_card)
                            row.append(drag_card)
                            game_state.player_turn = False 
                            drag_card = None
                            game_state.drawn_card = None
                            drag_offset_x, drag_offset_y = 0, 0
                            break
                drag_card = None
                drag_offset_x, drag_offset_y = 0, 0

            # Updates card position when the mouse moves
            elif event.type == pygame.MOUSEMOTION and drag_card:
                drag_card.rect.x = event.pos[0] + drag_offset_x
                drag_card.rect.y = event.pos[1] + drag_offset_y


            # Allows AI to place card when it's their turn
            elif not game_state.player_turn:
                ai_card = game_state.deck.deal_card()
                ai_card.draw(screen, DRAW_AREA_X, DRAW_AREA_Y['opponent'] + 5, hidden=True)
                valid_rows = [row for row in game_state.opponent_hand if validate_row(row, game_state.opponent_hand)]
                if valid_rows:
                    chosen_row = random.choice(valid_rows)
                    chosen_row.append(ai_card)
                game_state.player_turn = True 

            # Check if all rows are full and the game has ended
            result = check_game_end(game_state.player_hand, game_state.opponent_hand)
            if result:
                winner_message = show_winner_message(screen, result[0], SCREEN_WIDTH, SCREEN_HEIGHT)

        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
