# CODE v3.5.7 - FIXED LAYOUT "SYS.EXCH" + FIXED FUNCTION DEFINITION ORDER

import pygame
import time
from pygame import gfxdraw
import sys
import os
import random
import math

# --- Pygame Initialization ---
pygame.init()
WIDTH, HEIGHT = 1300, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Blockchain Simulation v3.5.7 - UI Fix v2") # New Version
clock = pygame.time.Clock()

# --- Constants ---
TOTAL_COINS = 5_000_000_000
YEARLY_REWARD_RATE = 0.02
DAYS_PER_YEAR = 365
MIN_STAKE = 100_000
DAY_DURATION = 3 # Slowed down
INITIAL_USERS = 10
INITIAL_USER_USD = 20.0 # Decreased
EXCHANGE_INITIAL_COIN_LIQUIDITY = 30_333_333.0
EXCHANGE_INITIAL_USD_LIQUIDITY = 10_000_000.0
EXCHANGE_FEE_RATE = 0.003
DAILY_ACTIVE_USER_PERCENT = 0.15
TRADES_PER_ACTIVE_USER = 2
SIMULATED_TRADE_MIN_COINS = 10.0
SIMULATED_TRADE_MAX_COINS = 50000.0
USER_TRADE_PERCENT_MAX = 0.30
GRAPH_MAX_POINTS = 365
SITE_TRAFFIC_USER_PERCENT = 0.30
SITE_USD_REVENUE_PER_TRAFFIC_UNIT = 0.02
SITE_COIN_REWARD_PER_TRAFFIC_UNIT = 0.5

# --- Color Palette ---
COLOR_BACKGROUND = (20, 25, 30); COLOR_PANEL = (35, 40, 50); COLOR_PANEL_LIGHT = (50, 55, 65)
COLOR_BORDER = (70, 75, 85); COLOR_TEXT = (210, 215, 220); COLOR_TEXT_HEADINGS = (255, 255, 255)
COLOR_ACCENT = (0, 190, 220); COLOR_ACCENT_DARK = (0, 150, 180); COLOR_SUCCESS = (0, 200, 100)
COLOR_ERROR = (220, 50, 80); COLOR_WARNING = (255, 180, 0); COLOR_PLACEHOLDER = (100, 105, 115)
COLOR_CONTEST = (200, 120, 255); COLOR_EXCHANGE = (255, 150, 50); COLOR_GRAPH_LINE = (255, 210, 0)
COLOR_SITE = (100, 220, 100); COLOR_SYSTEM_EX = (60, 100, 200)

# --- Fonts ---
FONT_PATH_REGULAR = "Roboto-Regular.ttf"; FONT_PATH_BOLD = "Roboto-Bold.ttf"
def load_font(path, size):
    if not os.path.exists(path): print(f"Err: Font '{path}' not found. Using system default.", file=sys.stderr); return pygame.font.SysFont("Arial", size)
    try: return pygame.font.Font(path, size)
    except pygame.error as e: print(f"Err loading font '{path}': {e}. Using system default.", file=sys.stderr); return pygame.font.SysFont("Arial", size)
font_reg_16 = load_font(FONT_PATH_REGULAR, 16); font_reg_18 = load_font(FONT_PATH_REGULAR, 18); font_reg_20 = load_font(FONT_PATH_REGULAR, 20); font_reg_24 = load_font(FONT_PATH_REGULAR, 24)
font_bold_20 = load_font(FONT_PATH_BOLD, 20); font_bold_24 = load_font(FONT_PATH_BOLD, 24); font_bold_28 = load_font(FONT_PATH_BOLD, 28)

# --- Global UI Variables ---
MENU_PADDING = 25; INPUT_HEIGHT = 40; BUTTON_HEIGHT = 45
active_input_field = None; message_display = {"text": "", "color": COLOR_TEXT, "time": 0}; HOVER_DELAY = 0.05

# --- Helper Functions ---
def draw_panel(surface, rect, color=COLOR_PANEL, border_color=COLOR_BORDER, radius=8, border_width=1):
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border_width > 0 and border_color: pygame.draw.rect(surface, border_color, rect, border_width, border_radius=radius)
def draw_text(surface, text, pos, font, color=COLOR_TEXT, center_x=False, center_y=False, right_align=False):
    text_surface = font.render(text, True, color); text_rect = text_surface.get_rect()
    if center_x: text_rect.centerx = pos[0]
    elif right_align: text_rect.right = pos[0]
    else: text_rect.left = pos[0]
    if center_y: text_rect.centery = pos[1]
    else: text_rect.top = pos[1]
    surface.blit(text_surface, text_rect); return text_rect
def format_num(number, decimals=0):
    try:
        if number is None or (isinstance(number, float) and (math.isnan(number) or math.isinf(number))): return "N/A"
        if decimals > 0: return f"{float(number):,.{decimals}f}"
        else: return f"{int(number):,}"
    except (ValueError, TypeError): return str(number)
def draw_price_graph(surface, rect, history, max_points=GRAPH_MAX_POINTS, title="Price History (USD/COIN)"):
    graph_padding = 20; axis_label_space = 45
    draw_panel(surface, rect, COLOR_PANEL, COLOR_BORDER)
    draw_text(surface, title, (rect.centerx, rect.top + 5), font_bold_20, COLOR_TEXT_HEADINGS, center_x=True)
    if not history: draw_text(surface, "No data", rect.center, font_reg_20, COLOR_PLACEHOLDER, center_x=True, center_y=True); return
    visible_history_raw = history[-max_points:]
    visible_history_filtered = []
    for i, price in enumerate(visible_history_raw):
         if price is not None and isinstance(price, (float, int)) and not math.isinf(price) and not math.isnan(price):
              visible_history_filtered.append((i, price))
    if not visible_history_filtered: draw_text(surface, "No valid data", rect.center, font_reg_20, COLOR_PLACEHOLDER, center_x=True, center_y=True); return
    if len(visible_history_filtered) < 2:
         draw_text(surface, "Need more data points", rect.center, font_reg_20, COLOR_PLACEHOLDER, center_x=True, center_y=True)
         if len(visible_history_filtered) == 1:
              prices = [p for i, p in visible_history_filtered]; price_val = prices[0]
              draw_area = pygame.Rect(rect.left + graph_padding + axis_label_space, rect.top + graph_padding + 20, rect.width - graph_padding * 2 - axis_label_space, rect.height - graph_padding * 2 - 20)
              draw_text(surface, f"${format_num(price_val, 4)}", (draw_area.left - 5, draw_area.centery - font_reg_16.get_height()//2), font_reg_16, COLOR_PLACEHOLDER, right_align=True)
              pygame.draw.circle(surface, COLOR_GRAPH_LINE, (draw_area.left, draw_area.centery), 3)
         return
    prices = [p for i, p in visible_history_filtered]; min_price = min(prices); max_price = max(prices)
    price_range = max_price - min_price
    if price_range < 1e-9: price_range = max(min_price * 0.1, 1e-6); max_price += price_range * 0.5; min_price -= price_range * 0.5;
    if min_price < 0: min_price = 0; price_range = max_price - min_price
    if price_range < 1e-9: price_range = 1.0; min_price = max(0, prices[-1] - 0.5); max_price = prices[-1] + 0.5;
    draw_area = pygame.Rect(rect.left + graph_padding + axis_label_space, rect.top + graph_padding + 20, rect.width - graph_padding * 2 - axis_label_space, rect.height - graph_padding * 2 - 20)
    label_max_y = draw_area.top; label_min_y = draw_area.bottom
    draw_text(surface, f"${format_num(max_price, 4)}", (draw_area.left - 5, label_max_y), font_reg_16, COLOR_PLACEHOLDER, right_align=True)
    draw_text(surface, f"${format_num(min_price, 4)}", (draw_area.left - 5, label_min_y - font_reg_16.get_height()), font_reg_16, COLOR_PLACEHOLDER, right_align=True)
    num_valid_points = len(visible_history_filtered); x_scale = draw_area.width / max(1, num_valid_points - 1); y_scale = draw_area.height / price_range if price_range > 1e-9 else 0
    points = []
    for i, (original_index_ignored, price) in enumerate(visible_history_filtered):
        px = draw_area.left + i * x_scale; py = draw_area.bottom
        if y_scale != 0: py = draw_area.bottom - (price - min_price) * y_scale
        py = max(draw_area.top, min(draw_area.bottom, py)); points.append((px, py))
    if len(points) >= 2: pygame.draw.aalines(surface, COLOR_GRAPH_LINE, False, points)
    elif len(points) == 1: pygame.draw.circle(surface, COLOR_GRAPH_LINE, (int(points[0][0]), int(points[0][1])), 3)

# --- UI Element Classes ---
class InputField: # ... (no internal Russian text) ...
    def __init__(self, rect, placeholder="", initial_value="", font=font_reg_20, allowed_chars=None, max_len=None):
        self.rect = pygame.Rect(rect); self.placeholder = placeholder; self.value = str(initial_value); self.font = font
        self.active = False; self.cursor_visible = True; self.cursor_timer = 0; self.allowed_chars = allowed_chars; self.max_len = max_len
    def handle_event(self, event):
        global active_input_field; interacted = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if active_input_field != self:
                    if active_input_field: active_input_field.active = False
                    self.active = True; active_input_field = self; self.cursor_timer = time.time(); self.cursor_visible = True
                interacted = True
        if self.active and event.type == pygame.KEYDOWN:
            interacted = True
            if event.key == pygame.K_BACKSPACE: self.value = self.value[:-1]
            elif event.key in [pygame.K_RETURN, pygame.K_KP_ENTER]: pass
            else:
                char = event.unicode; valid = True
                if self.allowed_chars == "0-9":
                    if not char.isdigit(): valid = False
                elif self.allowed_chars == "0-9.,":
                    current_val = self.value.replace(',', '.');
                    if not (char.isdigit() or (char in ['.', ','] and '.' not in current_val)): valid = False
                elif self.allowed_chars is not None:
                    if char not in self.allowed_chars: valid = False
                if valid and (self.max_len is None or len(self.value) < self.max_len): self.value += char
            self.cursor_timer = time.time(); self.cursor_visible = True
        return interacted
    def update(self):
        if self.active:
            if time.time() - self.cursor_timer > 0.5: self.cursor_visible = not self.cursor_visible; self.cursor_timer = time.time()
        else: self.cursor_visible = False
    def draw(self, surface):
        bg_color = COLOR_PANEL_LIGHT if self.active else COLOR_PANEL; draw_panel(surface, self.rect, bg_color, COLOR_BORDER, radius=5)
        text_color = COLOR_TEXT; text_to_render = self.value
        if not self.value and not self.active: text_to_render = self.placeholder; text_color = COLOR_PLACEHOLDER
        text_surface = self.font.render(text_to_render, True, text_color); text_rect = text_surface.get_rect(centery=self.rect.centery); text_rect.left = self.rect.left + 10
        max_width = self.rect.width - 20
        if text_rect.width > max_width:
            visible_chars = 0; current_width = 0
            try:
                for i in range(len(text_to_render) -1, -1, -1):
                    char_surf = self.font.render(text_to_render[i], True, text_color); w = char_surf.get_width()
                    if current_width + w <= max_width: current_width += w; visible_chars += 1
                    else: break
                if visible_chars > 0: text_surface = self.font.render(text_to_render[-visible_chars:], True, text_color)
                else: text_surface = self.font.render("...", True, text_color)
                text_rect = text_surface.get_rect(centery=self.rect.centery); text_rect.right = self.rect.right - 10
            except Exception: text_surface = self.font.render("Err", True, COLOR_ERROR); text_rect = text_surface.get_rect(centery=self.rect.centery); text_rect.left = self.rect.left + 10
        surface.blit(text_surface, text_rect)
        if self.active and self.cursor_visible:
            cursor_x = min(text_rect.right + 2, self.rect.right - 3)
            if not self.value: cursor_x = self.rect.left + 10
            pygame.draw.line(surface, COLOR_ACCENT, (cursor_x, self.rect.top + 5), (cursor_x, self.rect.bottom - 5), 1)

class Button: # ... (no internal Russian text) ...
    def __init__(self, rect, text, font=font_bold_20, on_click=None, base_color=COLOR_ACCENT, hover_color=COLOR_PANEL_LIGHT, click_color=COLOR_ACCENT_DARK, text_color=COLOR_BACKGROUND):
        self.rect = pygame.Rect(rect); self.text = text; self.font = font; self.on_click = on_click
        self.base_color = base_color; self.hover_color = hover_color; self.click_color = click_color; self.text_color = text_color
        self.is_hovered = False; self.is_clicked = False; self.hover_start_time = 0
    def handle_event(self, event):
        global active_input_field
        clicked_on_me = False
        mouse_pos = pygame.mouse.get_pos()
        was_hovered = self.is_hovered
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        if self.is_hovered and not was_hovered: self.hover_start_time = time.time()
        elif not self.is_hovered: self.hover_start_time = 0; self.is_clicked = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
            self.is_clicked = True; clicked_on_me = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_clicked:
                if self.is_hovered:
                    if self.on_click:
                        if active_input_field: active_input_field.active=False; active_input_field=None
                        self.on_click()
                        clicked_on_me = True
                self.is_clicked = False
        return clicked_on_me or self.is_hovered
    def draw(self, surface):
        color = self.base_color; apply_hover = self.is_hovered and (time.time() - self.hover_start_time >= HOVER_DELAY)
        if self.is_clicked: color = self.click_color
        elif apply_hover: color = self.hover_color
        draw_panel(surface, self.rect, color, border_color=None, radius=6)
        txt_color = self.text_color if not apply_hover else COLOR_ACCENT
        draw_text(surface, self.text, self.rect.center, self.font, txt_color, center_x=True, center_y=True)


# --- Entity Classes ---
class User: # ... (no internal Russian text) ...
    def __init__(self, user_id): self.id = user_id; self.coin_balance = 0.0; self.usd_balance = INITIAL_USER_USD

class Node: # ... (debug prints commented out) ...
    def __init__(self, stake, commission, is_our_node=True): self.initial_stake=stake; self.stake=stake; self.commission=commission; self.balance=0.0; self.active=True; self.is_our_node=is_our_node
    def stop(self):
        if not self.active: return None;
        stk, bal = self.stake, self.balance;
        self.active=False; self.stake=0; self.balance=0; # Also reset balance on stop
        return stk, bal
    def start(self): self.active = True

# --- Exchange Class ---
class Exchange: # ... (no internal Russian text, print statement translated) ...
    def __init__(self, initial_coin_pool, initial_usd_pool, fee_rate=EXCHANGE_FEE_RATE):
        self.coin_pool = float(initial_coin_pool); self.usd_pool = float(initial_usd_pool); self.fee_rate = float(fee_rate)
        if self.coin_pool <= 1e-9 or self.usd_pool <= 1e-9: print(f"Warning: Exchange initialized with near-zero pools."); self.k = 0.0
        else: self.k = self.coin_pool * self.usd_pool
        print(f"Exchange initialized. Coin Pool: {format_num(self.coin_pool)}, USD Pool: ${format_num(self.usd_pool, 2)}, k={format_num(self.k, 2) if self.k is not None else 'N/A'}")
    def _recalculate_k(self):
        if self.coin_pool > 1e-9 and self.usd_pool > 1e-9: self.k = self.coin_pool * self.usd_pool
        else: self.k = 0.0
    def get_spot_price(self):
        try:
            if self.coin_pool is None or self.usd_pool is None: return None
            if abs(self.coin_pool) < 1e-9: return float('inf')
            price = self.usd_pool / self.coin_pool
            if math.isnan(price) or math.isinf(price): return None
            return price
        except TypeError: return None
        except Exception as e: print(f"ERROR in get_spot_price: {e}"); return None
    def get_buy_quote(self, coin_amount_to_buy):
        if coin_amount_to_buy <= 0 or self.k == 0.0: return None
        if coin_amount_to_buy >= self.coin_pool - 1e-9: return None
        x = self.coin_pool; y = self.usd_pool; dx = float(coin_amount_to_buy)
        dy_gross = self.k / (x - dx) - y; fee = dy_gross * self.fee_rate; dy_net = dy_gross + fee
        effective_price = dy_net / dx if dx > 0 else 0
        if dy_net <= 0: return None
        return {"usd_cost": dy_net, "fee": fee, "effective_price": effective_price}
    def get_sell_quote(self, coin_amount_to_sell):
        if coin_amount_to_sell <= 0 or self.k == 0.0: return None
        x = self.coin_pool; y = self.usd_pool; dx = float(coin_amount_to_sell)
        target_y = self.k / (x + dx)
        if target_y < 1e-9: dy_gross = y
        else: dy_gross = y - target_y
        fee = dy_gross * self.fee_rate; dy_net = dy_gross - fee
        effective_price = dy_net / dx if dx > 0 else 0
        if dy_net <= 0: return None
        usd_to_withdraw = dy_net + fee
        if usd_to_withdraw > self.usd_pool + 1e-9: return None
        return {"usd_received": dy_net, "fee": fee, "effective_price": effective_price}
    def get_system_buy_quote_for_usd(self, usd_amount_to_spend):
        if usd_amount_to_spend <= 0 or self.k == 0.0: return None
        if usd_amount_to_spend >= self.usd_pool - 1e-9: return None
        x = self.coin_pool; y = self.usd_pool; dy = float(usd_amount_to_spend)
        dx_received = x - self.k / (y + dy)
        if dx_received <= 0 or dx_received >= self.coin_pool - 1e-9: return None
        effective_price = dy / dx_received if dx_received > 0 else float('inf')
        return {"coins_received": dx_received, "usd_spent": dy, "effective_price": effective_price}
    def get_system_sell_quote_for_coins(self, coin_amount_to_sell):
        if coin_amount_to_sell <= 0 or self.k == 0.0: return None
        x = self.coin_pool; y = self.usd_pool; dx = float(coin_amount_to_sell)
        dy_received = y - self.k / (x + dx)
        if dy_received <= 0 or dy_received >= self.usd_pool - 1e-9: return None
        effective_price = dy_received / dx if dx > 0 else 0
        return {"usd_received": dy_received, "coins_sold": dx, "effective_price": effective_price}
    def buy_coins(self, user, coin_amount_to_buy_str):
        global message_display
        try: coin_amount = float(coin_amount_to_buy_str.replace(',', '.')); assert coin_amount > 0
        except(ValueError,TypeError,AssertionError): message_display={"text":"Invalid coin amount (>0)","color":COLOR_ERROR,"time":time.time()}; return False
        quote = self.get_buy_quote(coin_amount)
        if quote is None: message_display={"text":"Cannot buy","color":COLOR_ERROR,"time":time.time()}; return False
        usd_cost = quote["usd_cost"]; fee = quote["fee"]
        if user.usd_balance < usd_cost: message_display={"text":f"Insufficient USD ({format_num(user.usd_balance,2)}<{format_num(usd_cost,2)})","color":COLOR_ERROR,"time":time.time()}; return False
        user.usd_balance -= usd_cost; user.coin_balance += coin_amount; self.coin_pool -= coin_amount; self.usd_pool += usd_cost; self._recalculate_k()
        return True
    def sell_coins(self, user, coin_amount_to_sell_str):
        global message_display
        try: coin_amount = float(coin_amount_to_sell_str.replace(',', '.')); assert coin_amount > 0
        except(ValueError,TypeError,AssertionError): message_display={"text":"Invalid coin amount (>0)","color":COLOR_ERROR,"time":time.time()}; return False
        if user.coin_balance < coin_amount: message_display={"text":f"Insufficient coins ({format_num(user.coin_balance)}<{format_num(coin_amount)})","color":COLOR_ERROR,"time":time.time()}; return False
        quote = self.get_sell_quote(coin_amount)
        if quote is None: message_display={"text":"Cannot sell","color":COLOR_ERROR,"time":time.time()}; return False
        usd_received = quote["usd_received"]; fee = quote["fee"]; usd_taken_from_pool = usd_received + fee
        if usd_taken_from_pool > self.usd_pool + 1e-9 : message_display={"text":"Error: insufficient USD in pool","color":COLOR_ERROR,"time":time.time()}; print(f"Error: Tried take {usd_taken_from_pool} USD, pool has {self.usd_pool}"); return False
        user.coin_balance -= coin_amount; user.usd_balance += usd_received; self.coin_pool += coin_amount; self.usd_pool -= usd_taken_from_pool; self._recalculate_k()
        return True

# --- Network Class ---
class Network: # ... (debug prints commented out, other print statements translated) ...
    def __init__(self):
        self.base_emission = TOTAL_COINS; self.total_emission = TOTAL_COINS; self.nodes = []; self.users = []; self.next_user_id = 1
        self.day = 0; self.last_reward_time = time.time(); self.added_emission = 0; self.remainder = TOTAL_COINS
        self.price_history = []
        self.our_usd_balance = 0.0
        self.add_node(MIN_STAKE, 0.05, is_our=True, silent=True); # Add initial node silently
        initial_coins_for_exchange = min(EXCHANGE_INITIAL_COIN_LIQUIDITY, self.remainder * 0.5)
        initial_usd_for_exchange = EXCHANGE_INITIAL_USD_LIQUIDITY
        if self.remainder >= initial_coins_for_exchange:
            self.remainder -= initial_coins_for_exchange
            self.exchange = Exchange(initial_coins_for_exchange, initial_usd_for_exchange)
            print(f"Exchange seeded. Took {format_num(initial_coins_for_exchange)} coins. Remainder: {format_num(self.remainder)}")
        else: print("Warning: Not enough coins to seed exchange!"); self.exchange = Exchange(1.0, 1.0)
        for _ in range(INITIAL_USERS): self.add_user(silent=True)
        self.last_simulated_day = -1

    def add_user(self, silent=False):
        global message_display; new_user = User(self.next_user_id); self.users.append(new_user); self.next_user_id += 1
        if not silent: print(f"User {new_user.id} added. Total: {len(self.users)}"); message_display = {"text": f"User {new_user.id} added","color": COLOR_SUCCESS,"time": time.time()}; return True
    def add_multiple_users(self, count_str):
        global message_display
        try: count = int(count_str); assert count > 0
        except(ValueError,TypeError,AssertionError): message_display={"text":"Invalid count (>0)","color":COLOR_ERROR,"time":time.time()}; return False
        added=0;
        for _ in range(count): self.add_user(silent=True); added+=1
        if added > 0: message_display={"text":f"Added {added} users","color":COLOR_SUCCESS,"time":time.time()}; print(f"Added {added} users via menu. Total: {len(self.users)}"); return True

    def process_daily_site_activity(self): # ... (no internal Russian text) ...
        if not self.users or not self.exchange: return
        num_traffic_users = max(0, int(len(self.users) * SITE_TRAFFIC_USER_PERCENT))
        if num_traffic_users == 0: return
        traffic_users = random.sample(self.users, min(num_traffic_users, len(self.users)))
        total_usd_revenue = num_traffic_users * SITE_USD_REVENUE_PER_TRAFFIC_UNIT
        self.our_usd_balance += total_usd_revenue
        total_coins_needed = len(traffic_users) * SITE_COIN_REWARD_PER_TRAFFIC_UNIT
        paid_coin_count = 0; paid_coin_total = 0
        if self.remainder >= total_coins_needed:
            self.remainder -= total_coins_needed
            for user in traffic_users: user.coin_balance += SITE_COIN_REWARD_PER_TRAFFIC_UNIT; paid_coin_count += 1
            paid_coin_total = total_coins_needed
        else:
            # Optionally: print a warning or handle insufficient coins
            # print(f"Warning: Not enough remainder coins ({format_num(self.remainder)}) for site rewards ({format_num(total_coins_needed)}).")
            pass

    def distribute_rewards(self): # ... (no internal Russian text) ...
        current_time=time.time(); time_passed=current_time-self.last_reward_time; days_to_process=int(time_passed//DAY_DURATION)
        if days_to_process>0:
            active_nodes=[n for n in self.nodes if n.active]; total_stake=sum(n.stake for n in active_nodes)
            for _ in range(days_to_process):
                self.day+=1
                daily_reward=(self.base_emission*YEARLY_REWARD_RATE)/DAYS_PER_YEAR
                if total_stake>0:
                    for node in active_nodes: node.balance+=(node.stake/total_stake)*daily_reward
                    self.total_emission+=daily_reward; self.added_emission+=daily_reward
                self.process_daily_site_activity()
                self.simulate_user_activity()
                if self.exchange:
                     current_price = self.exchange.get_spot_price()
                     if isinstance(current_price, (int, float)) and not math.isinf(current_price) and not math.isnan(current_price):
                          self.price_history.append(current_price)
                          if len(self.price_history) > GRAPH_MAX_POINTS + 50: self.price_history = self.price_history[-(GRAPH_MAX_POINTS + 50):]
                     else:
                          last_valid_price = None
                          for price in reversed(self.price_history):
                              if price is not None and isinstance(price, (float, int)) and not math.isinf(price) and not math.isnan(price):
                                  last_valid_price = price; break
                          self.price_history.append(last_valid_price) # Append last valid or None if none found
            self.last_reward_time+=days_to_process*DAY_DURATION

    def launch_contest(self, total_reward_str, num_winners_str): # ... (print statements translated) ...
        global message_display;
        try: total_reward=int(total_reward_str); num_winners=int(num_winners_str); assert total_reward>0 and num_winners>0
        except(ValueError,TypeError,AssertionError): message_display={"text":"Reward/Winners must be > 0","color":COLOR_ERROR,"time":time.time()}; return False
        if total_reward>self.remainder: msg=f"Not enough coins ({format_num(self.remainder)})"; message_display={"text":msg,"color":COLOR_ERROR,"time":time.time()}; print(f"Contest Err: {msg}"); return False
        if num_winners > len(self.users): num_winners = len(self.users)
        if num_winners == 0: message_display={"text":"No users for contest","color":COLOR_WARNING,"time":time.time()}; return False
        self.remainder-=total_reward; print(f"Contest: Took {format_num(total_reward)} coins. Remainder: {format_num(self.remainder)}")
        winners=random.sample(self.users,num_winners); print(f"Contest Winners (User IDs): {[u.id for u in winners]}")
        rewards_dist=0; rem_reward=total_reward; rem_winners=num_winners
        if rem_winners>=1: r1=int(total_reward*0.30) if num_winners>=3 else(int(total_reward*0.60) if num_winners==2 else total_reward); r1=min(r1,rem_reward); winners[0].coin_balance+=r1; rewards_dist+=r1; rem_reward-=r1; rem_winners-=1; print(f"- User {winners[0].id} (1st): +{format_num(r1)} coins")
        if rem_winners>=1: r2=int(total_reward*0.20) if num_winners>=3 else(int(total_reward*0.40) if num_winners==2 else 0); r2=min(r2,rem_reward); winners[1].coin_balance+=r2; rewards_dist+=r2; rem_reward-=r2; rem_winners-=1; print(f"- User {winners[1].id} (2nd): +{format_num(r2)} coins")
        if rem_winners>=1 and num_winners>=3: r3=int(total_reward*0.15); r3=min(r3,rem_reward); winners[2].coin_balance+=r3; rewards_dist+=r3; rem_reward-=r3; rem_winners-=1; print(f"- User {winners[2].id} (3rd): +{format_num(r3)} coins")
        if rem_winners>0: r_other=rem_reward//rem_winners if rem_winners>0 else 0; start_idx=num_winners-rem_winners
        for i in range(start_idx,num_winners): actual_r=min(r_other,rem_reward); winners[i].coin_balance+=actual_r; rewards_dist+=actual_r; rem_reward-=actual_r; print(f"- User {winners[i].id} (Other): +{format_num(actual_r)} coins")
        if rem_reward>0 and winners: winners[0].coin_balance+=rem_reward; print(f"- User {winners[0].id} (Remainder adj.): +{format_num(rem_reward)} coins"); rewards_dist+=rem_reward
        print(f"Contest finished. Total Distributed: {format_num(rewards_dist)} coins"); message_display={"text":f"Contest! {num_winners} winners.","color":COLOR_SUCCESS,"time":time.time()}; return True

    def add_node(self, stake, commission, is_our=True, silent=False): # Added is_our and silent flags
        global message_display;
        try: stake_val=int(stake); commission_val=float(commission); assert 0<=commission_val<=1
        except(ValueError,TypeError,AssertionError):
            if not silent: message_display={"text":"Node input error (stake/commission)","color":COLOR_ERROR,"time":time.time()};
            return False
        if stake_val<MIN_STAKE:
             if not silent: msg=f"Stake < min ({format_num(MIN_STAKE)})"; message_display={"text":msg,"color":COLOR_ERROR,"time":time.time()};
             return False
        if self.remainder>=stake_val:
            self.nodes.append(Node(stake_val,commission_val,is_our)); self.remainder-=stake_val;
            if not silent: msg=f"Node added! Remainder: {format_num(self.remainder)}"; print(msg); message_display={"text":"Node added","color":COLOR_SUCCESS,"time":time.time()};
            return True
        else:
             if not silent: msg=f"Not enough coins in Summa ({format_num(self.remainder)})"; message_display={"text":msg,"color":COLOR_ERROR,"time":time.time()};
             return False

    def stop_node(self, node_index_str): # <<< debug prints commented out, messages translated
        global message_display;
        try:
            node_index=int(node_index_str)-1;
            if not (0 <= node_index < len(self.nodes)):
                 message_display={"text":"Invalid node number (out of bounds)","color":COLOR_ERROR,"time":time.time()}; return False
        except ValueError:
            message_display={"text":"Invalid node number (not integer)","color":COLOR_ERROR,"time":time.time()}; return False
        except Exception as e_parse:
             print(f"[Network.stop_node] Error during parsing/validation: {e_parse}", file=sys.stderr)
             message_display={"text":"Invalid node number (validation error)","color":COLOR_ERROR,"time":time.time()}; return False

        node = self.nodes[node_index];

        if node.active and node.is_our_node:
            result = node.stop()
            if result is not None:
                try:
                    if isinstance(result, (tuple, list)) and len(result) == 2:
                        stk_ret, bal_ret = result;
                        remainder_before = self.remainder
                        stk_float = float(stk_ret)
                        bal_float = float(bal_ret)
                        self.remainder += stk_float + bal_float # Return stake AND balance to remainder
                        remainder_after = self.remainder
                        msg=f"Node {node_index+1} stopped. Returned: {format_num(stk_ret)} (stake) + {format_num(bal_ret)} (bal). Remainder: {format_num(self.remainder)}";
                        print(msg); # Original print for game console
                        message_display={"text":f"Node {node_index+1} stopped","color":COLOR_SUCCESS,"time":time.time()}; return True
                    else:
                        print(f"[Network.stop_node] ERROR: node.stop() returned non-None, but not a 2-element tuple/list: {result}", file=sys.stderr)
                        message_display = {"text": f"Node {node_index + 1} return format error", "color": COLOR_ERROR, "time": time.time()};
                        return False
                except (ValueError, TypeError) as e_cast:
                    print(f"[Network.stop_node] ERROR: Failed to cast returned stake={stk_ret} or balance={bal_ret} to float. Error: {e_cast}", file=sys.stderr)
                    message_display={"text":f"Node {node_index+1} data type error","color":COLOR_ERROR,"time":time.time()};
                    return False
                except Exception as e_add:
                     print(f"[Network.stop_node] ERROR: Failed to add returned values to remainder. Error: {e_add}", file=sys.stderr)
                     message_display={"text":f"Node {node_index+1} funds return error","color":COLOR_ERROR,"time":time.time()};
                     return False
            else: # node.stop() returned None
                 msg=f"Failed to stop Node {node_index+1} (already stopped?)"; message_display={"text":msg,"color":COLOR_ERROR,"time":time.time()}; return False
        elif not node.active:
            msg=f"Node {node_index+1} already stopped"; message_display={"text":msg,"color":COLOR_WARNING,"time":time.time()}; return False
        else: # not node.is_our_node
            msg=f"Node {node_index+1} is not yours"; message_display={"text":msg,"color":COLOR_ERROR,"time":time.time()}; return False

    def simulate_user_activity(self): # ... (no internal Russian text) ...
        global message_display
        if self.day <= self.last_simulated_day: return
        self.last_simulated_day = self.day
        if not self.users or not self.exchange or self.exchange.k == 0.0: return
        num_active_users = max(1, int(len(self.users) * DAILY_ACTIVE_USER_PERCENT))
        active_users_today = random.sample(self.users, min(num_active_users, len(self.users)))
        for user in active_users_today:
            for _ in range(TRADES_PER_ACTIVE_USER):
                action = random.choice(["buy", "sell"])
                coins_to_trade = random.uniform(SIMULATED_TRADE_MIN_COINS, SIMULATED_TRADE_MAX_COINS)
                if action == "buy" and user.usd_balance > 0.01:
                    min_buy_quote = self.exchange.get_buy_quote(SIMULATED_TRADE_MIN_COINS)
                    if min_buy_quote and user.usd_balance < min_buy_quote['usd_cost']: continue # Cannot afford even minimum
                    quote = self.exchange.get_buy_quote(coins_to_trade)
                    if quote and user.usd_balance >= quote['usd_cost']:
                         self.exchange.buy_coins(user, str(coins_to_trade))
                         # print(f" Sim User {user.id} bought {format_num(coins_to_trade)} coins") # Optional debug
                    else: # Try buying smaller amount if can't afford desired amount
                        spot_price = self.exchange.get_spot_price()
                        if spot_price is not None and not math.isinf(spot_price) and not math.isnan(spot_price) and spot_price > 1e-9:
                            # Estimate affordable coins based on spot price, leave a small margin
                            affordable_coins_est = (user.usd_balance / (1 + self.exchange.fee_rate)) / spot_price
                            affordable_coins = max(affordable_coins_est * 0.95, SIMULATED_TRADE_MIN_COINS) # Try to buy at least min
                            if affordable_coins < SIMULATED_TRADE_MIN_COINS: continue # Don't bother if can't afford min
                            quote_affordable = self.exchange.get_buy_quote(affordable_coins)
                            if quote_affordable and user.usd_balance >= quote_affordable['usd_cost']:
                                self.exchange.buy_coins(user, str(affordable_coins))
                                # print(f" Sim User {user.id} bought (adjusted) {format_num(affordable_coins)} coins") # Optional debug
                elif action == "sell" and user.coin_balance > 0:
                     # Sell a fraction of balance or the fixed amount, whichever is smaller and >= min
                     max_sell_fraction = user.coin_balance * USER_TRADE_PERCENT_MAX
                     amount_to_sell = min(coins_to_trade, max_sell_fraction, user.coin_balance)
                     if amount_to_sell >= SIMULATED_TRADE_MIN_COINS:
                         self.exchange.sell_coins(user, str(amount_to_sell))
                         # print(f" Sim User {user.id} sold {format_num(amount_to_sell)} coins") # Optional debug

    def system_buy_coins(self, usd_to_spend_str): # ... (messages and print translated) ...
        global message_display
        try: usd_to_spend = float(usd_to_spend_str.replace(',', '.')); assert usd_to_spend > 0
        except (ValueError, TypeError, AssertionError): message_display = {"text": "Invalid USD amount (>0)", "color": COLOR_ERROR, "time": time.time()}; return False
        if self.our_usd_balance < usd_to_spend: message_display = {"text": f"Insufficient system USD ({format_num(self.our_usd_balance, 2)}<{format_num(usd_to_spend,2)})", "color": COLOR_ERROR, "time": time.time()}; return False
        if not self.exchange: message_display = {"text": "Exchange not initialized", "color": COLOR_ERROR, "time": time.time()}; return False
        quote = self.exchange.get_system_buy_quote_for_usd(usd_to_spend)
        if quote is None: message_display = {"text": "Cannot buy COIN (insufficient pool liquidity?)", "color": COLOR_ERROR, "time": time.time()}; return False
        coins_received = quote["coins_received"]
        self.our_usd_balance -= usd_to_spend; self.remainder += coins_received; self.exchange.coin_pool -= coins_received; self.exchange.usd_pool += usd_to_spend; self.exchange._recalculate_k()
        print(f"SYS BUY: Bought {format_num(coins_received)} COIN for ${format_num(usd_to_spend,2)}. Our USD: ${format_num(self.our_usd_balance,2)}, Remainder: {format_num(self.remainder)}")
        message_display = {"text": f"System bought {format_num(coins_received)} COIN", "color": COLOR_SUCCESS, "time": time.time()}; return True

    def system_sell_coins(self, coins_to_sell_str): # ... (messages and print translated) ...
        global message_display
        try: coins_to_sell = float(coins_to_sell_str.replace(',', '.')); assert coins_to_sell > 0
        except (ValueError, TypeError, AssertionError): message_display = {"text": "Invalid COIN amount (>0)", "color": COLOR_ERROR, "time": time.time()}; return False
        if self.remainder < coins_to_sell: message_display = {"text": f"Insufficient COIN in Summa ({format_num(self.remainder)}<{format_num(coins_to_sell)})", "color": COLOR_ERROR, "time": time.time()}; return False
        if not self.exchange: message_display = {"text": "Exchange not initialized", "color": COLOR_ERROR, "time": time.time()}; return False
        quote = self.exchange.get_system_sell_quote_for_coins(coins_to_sell)
        if quote is None: message_display = {"text": "Cannot sell COIN (insufficient pool liquidity?)", "color": COLOR_ERROR, "time": time.time()}; return False
        usd_received = quote["usd_received"]
        self.remainder -= coins_to_sell; self.our_usd_balance += usd_received; self.exchange.coin_pool += coins_to_sell; self.exchange.usd_pool -= usd_received; self.exchange._recalculate_k() # USD received already accounts for fee implicitly
        print(f"SYS SELL: Sold {format_num(coins_to_sell)} COIN for ${format_num(usd_received,2)}. Our USD: ${format_num(self.our_usd_balance,2)}, Remainder: {format_num(self.remainder)}")
        message_display = {"text": f"System sold {format_num(coins_to_sell)} COIN", "color": COLOR_SUCCESS, "time": time.time()}; return True

    def get_staked(self): return sum(n.stake for n in self.nodes if n.active)
    def get_free_float(self): return self.remainder
    def get_our_nodes_stake(self): return sum(n.stake for n in self.nodes if n.is_our_node and n.active)
    def get_our_nodes_rewards_total(self): return sum(n.balance for n in self.nodes if n.is_our_node)
    def get_total_user_coin_balance(self): return sum(u.coin_balance for u in self.users)
    def get_total_user_usd_balance(self): return sum(u.usd_balance for u in self.users)

# --- Function to print data to console ---
def print_game_data_to_console(network_obj): # ... (all internal text is English) ...
    print("\n--- Game State ---", file=sys.stderr)
    print("[Network]", file=sys.stderr); print(f" Day: {network_obj.day}", file=sys.stderr)
    print(f" Total Coins: {format_num(network_obj.total_emission)}", file=sys.stderr); print(f" Staked: {format_num(network_obj.get_staked())}", file=sys.stderr)
    print(f" Remainder (Summa): {format_num(network_obj.remainder)}", file=sys.stderr); print(f" Our Stake: {format_num(network_obj.get_our_nodes_stake())}", file=sys.stderr)
    print(f" Our Rewards: {format_num(network_obj.get_our_nodes_rewards_total())}", file=sys.stderr); print(f" Users: {len(network_obj.users)}", file=sys.stderr)
    print(f" User Coins: {format_num(network_obj.get_total_user_coin_balance())}", file=sys.stderr); print(f" User USD: ${format_num(network_obj.get_total_user_usd_balance(), 2)}", file=sys.stderr)
    print(f" Our USD: ${format_num(network_obj.our_usd_balance, 2)}", file=sys.stderr)
    print("[Exchange]", file=sys.stderr)
    current_exchange = getattr(network_obj, 'exchange', None)
    if current_exchange:
        print(f" Pool COIN: {format_num(current_exchange.coin_pool)}", file=sys.stderr)
        print(f" Pool USD: ${format_num(current_exchange.usd_pool, 2)}", file=sys.stderr)
        try:
            spot_price = current_exchange.get_spot_price()
            k_value = current_exchange.k
            if isinstance(spot_price, (int, float)) and not math.isinf(spot_price) and not math.isnan(spot_price):
                print(f" Price (USD/COIN): {spot_price:.6f}", file=sys.stderr)
            else:
                print(f" Price (USD/COIN): N/A (value: {spot_price})", file=sys.stderr)
            print(f" k: {format_num(k_value, 2) if k_value is not None else 'N/A'}", file=sys.stderr)
        except AttributeError as e:
             print(f" Error accessing exchange attribute: {e}", file=sys.stderr); print(f" Price: Error", file=sys.stderr); print(f" k: Error", file=sys.stderr)
    else: print(" Exchange object not found.", file=sys.stderr)
    print("[Nodes]", file=sys.stderr)
    if not network_obj.nodes: print(" No nodes.", file=sys.stderr)
    else: h=f"  {'#':<3}|{'St':<5}|{'Own':<4}|{'Stake':<15}|{'Rewards':<18}|{'Fee':<7}"; print(h,file=sys.stderr); print("  "+"-"*(len(h)-2),file=sys.stderr); # Added 'Own' column
    for i,n in enumerate(network_obj.nodes):
        s="Act" if n.active else "Stop";
        o = "Yes" if n.is_our_node else "No" # Check if it's our node
        st=format_num(n.stake); r=format_num(n.balance); c=f"{n.commission*100:.1f}%";
        print(f"  {i+1:<3}|{s:<5}|{o:<4}|{st:<15}|{r:<18}|{c:<7}",file=sys.stderr); # Print 'Own' status
        print("  "+"-"*(len(h)-2),file=sys.stderr) # Separator line adjusted if needed
    print("--- End State ---", file=sys.stderr)


# --- Network Initialization ---
network = Network()

# --- Create UI Menu Elements ---
menu_visible = False; menu_rect = pygame.Rect(0, 0, 600, 550); menu_rect.center = (WIDTH // 2, HEIGHT // 2)
y_pos_inputs = menu_rect.top + 100; input_width = menu_rect.width - MENU_PADDING*2
# Input Fields
stake_input = InputField((menu_rect.left+MENU_PADDING, y_pos_inputs, input_width, INPUT_HEIGHT), placeholder=f"Stake (min.{format_num(MIN_STAKE)})", font=font_reg_20, allowed_chars="0-9")
commission_input = InputField((menu_rect.left+MENU_PADDING, stake_input.rect.bottom+15, input_width, INPUT_HEIGHT), placeholder="Commission (0-100 %)", font=font_reg_20, allowed_chars="0-9.,")
stop_node_input = InputField((menu_rect.left+MENU_PADDING, y_pos_inputs, input_width, INPUT_HEIGHT), placeholder="Node number to stop", font=font_reg_20, allowed_chars="0-9")
contest_reward_input = InputField((menu_rect.left+MENU_PADDING, y_pos_inputs, input_width, INPUT_HEIGHT), placeholder="Contest reward amount (COIN)", font=font_reg_20, allowed_chars="0-9")
contest_winners_input = InputField((menu_rect.left+MENU_PADDING, contest_reward_input.rect.bottom+15, input_width, INPUT_HEIGHT), placeholder="Number of winners", font=font_reg_20, allowed_chars="0-9")
add_users_input = InputField((menu_rect.left+MENU_PADDING, y_pos_inputs, input_width, INPUT_HEIGHT), placeholder="How many users to add?", font=font_reg_20, allowed_chars="0-9")
exchange_amount_input = InputField((menu_rect.left + MENU_PADDING, y_pos_inputs + 80, input_width, INPUT_HEIGHT), placeholder="Amount of COIN to exchange", font=font_reg_20, allowed_chars="0-9.,")
sys_ex_usd_input = InputField((menu_rect.left + MENU_PADDING, y_pos_inputs + 20, input_width, INPUT_HEIGHT), placeholder="USD amount for system COIN purchase", font=font_reg_20, allowed_chars="0-9.,")
sys_ex_coin_input = InputField((menu_rect.left + MENU_PADDING, y_pos_inputs + 20 + INPUT_HEIGHT + 15 + BUTTON_HEIGHT + 25, input_width, INPUT_HEIGHT), placeholder="COIN amount for system sale", font=font_reg_20, allowed_chars="0-9.,") # Recalculated Y position

# --- Button Click Handler Functions (DEFINED BEFORE BUTTON CREATION) ---
def on_add_node_click():
    global message_display; s = stake_input.value; c = commission_input.value.replace(',', '.');
    if not s or not c: message_display={"text":"Please fill both fields","color":COLOR_ERROR,"time":time.time()}; return
    try:
        cp=float(c); assert 0<=cp<=100; cf=cp/100.0; scs=network.add_node(s, cf); # Uses default is_our=True
        if scs: stake_input.value=""; commission_input.value=""
    except(ValueError,AssertionError): message_display={"text":"Invalid commission (0-100)","color":COLOR_ERROR,"time":time.time()}
    except Exception as e: print(f"Err adding node:{e}",file=sys.stderr); message_display={"text":f"Error: {e}","color":COLOR_ERROR,"time":time.time()}

def on_stop_node_click():
    global message_display;
    n = stop_node_input.value;
    if not n: message_display={"text":"Enter node number","color":COLOR_ERROR,"time":time.time()}; return
    try:
        scs=network.stop_node(n);
        if scs: stop_node_input.value=""
    except Exception as e: print(f"Err stopping node:{e}",file=sys.stderr); message_display={"text":f"Error: {e}","color":COLOR_ERROR,"time":time.time()}

def on_launch_contest_click():
    global message_display; r = contest_reward_input.value; w = contest_winners_input.value;
    if not r or not w: message_display={"text":"Please fill both fields","color":COLOR_ERROR,"time":time.time()}; return
    try:
        scs=network.launch_contest(r, w);
        if scs: contest_reward_input.value=""; contest_winners_input.value=""
    except Exception as e: print(f"Err launching contest:{e}",file=sys.stderr); message_display={"text":f"Error: {e}","color":COLOR_ERROR,"time":time.time()}

def on_add_users_click():
    global message_display; count_str = add_users_input.value
    if not count_str: message_display={"text":"Enter user count","color":COLOR_ERROR,"time":time.time()}; return
    try:
        success=network.add_multiple_users(count_str);
        if success: add_users_input.value=""
    except Exception as e: print(f"Err adding users:{e}",file=sys.stderr); message_display={"text":f"Error: {e}","color":COLOR_ERROR,"time":time.time()}

def on_buy_click():
    global message_display; amount_str = exchange_amount_input.value
    if not amount_str: message_display={"text":"Enter COIN amount","color":COLOR_ERROR,"time":time.time()}; return
    if network.users:
        test_user = network.users[0]; # Use first user for UI testing
        success = network.exchange.buy_coins(test_user, amount_str);
        if success: exchange_amount_input.value = "" # Clear input on success
    else: message_display={"text":"No users to trade","color":COLOR_ERROR,"time":time.time()}

def on_sell_click():
    global message_display; amount_str = exchange_amount_input.value
    if not amount_str: message_display={"text":"Enter COIN amount","color":COLOR_ERROR,"time":time.time()}; return
    if network.users:
        test_user = network.users[0]; # Use first user for UI testing
        success = network.exchange.sell_coins(test_user, amount_str);
        if success: exchange_amount_input.value = "" # Clear input on success
    else: message_display={"text":"No users to trade","color":COLOR_ERROR,"time":time.time()}

def on_system_buy_click():
    global message_display; usd_str = sys_ex_usd_input.value
    if not usd_str: message_display={"text":"Enter USD amount","color":COLOR_ERROR,"time":time.time()}; return
    try:
        success = network.system_buy_coins(usd_str)
        if success: sys_ex_usd_input.value = ""
    except Exception as e: print(f"Err system buy:{e}", file=sys.stderr); message_display = {"text": f"Error: {e}", "color": COLOR_ERROR, "time": time.time()}

def on_system_sell_click():
    global message_display; coin_str = sys_ex_coin_input.value
    if not coin_str: message_display={"text":"Enter COIN amount","color":COLOR_ERROR,"time":time.time()}; return
    try:
        success = network.system_sell_coins(coin_str)
        if success: sys_ex_coin_input.value = ""
    except Exception as e: print(f"Err system sell:{e}", file=sys.stderr); message_display = {"text": f"Error: {e}", "color": COLOR_ERROR, "time": time.time()}


# --- Mode Switching Functions ---
state = {'current_menu_mode': "add", 'message_data': message_display} # Renamed state keys
def switch_mode(mode_name):
    global active_input_field
    if state['current_menu_mode'] != mode_name:
        state['current_menu_mode'] = mode_name;
        state['message_data']['text'] = ""; # Clear message on mode switch
    # Deactivate input field when switching modes
    if active_input_field:
        active_input_field.active=False;
        active_input_field=None
def create_switch_lambda(mode_name, current_state): return lambda: switch_mode(mode_name)

# --- Action and Tab Buttons (DEFINED AFTER HANDLER FUNCTIONS) ---
# Calculate Y positions for action buttons based on related input fields
by_add = commission_input.rect.bottom + 30
by_stop = stop_node_input.rect.bottom + 30
by_contest = contest_winners_input.rect.bottom + 30
by_users = add_users_input.rect.bottom + 30
by_exchange = exchange_amount_input.rect.bottom + 85 # Y pos for buy/sell buttons (under quote info)

# Action Buttons
add_button = Button((menu_rect.left+MENU_PADDING, by_add, input_width, BUTTON_HEIGHT), "Add Node", on_click=on_add_node_click)
stop_button = Button((menu_rect.left+MENU_PADDING, by_stop, input_width, BUTTON_HEIGHT), "Stop Node", on_click=on_stop_node_click, base_color=COLOR_WARNING)
contest_button = Button((menu_rect.left+MENU_PADDING, by_contest, input_width, BUTTON_HEIGHT), "Launch Contest", on_click=on_launch_contest_click, base_color=COLOR_CONTEST)
add_users_button = Button((menu_rect.left+MENU_PADDING, by_users, input_width, BUTTON_HEIGHT), "Add Users", on_click=on_add_users_click, base_color=COLOR_SUCCESS)
buy_button = Button((menu_rect.left+MENU_PADDING, by_exchange, input_width//2-5, BUTTON_HEIGHT), "Buy COIN (User)", on_click=on_buy_click, base_color=COLOR_SUCCESS)
sell_button = Button((buy_button.rect.right+10, by_exchange, input_width//2-5, BUTTON_HEIGHT), "Sell COIN (User)", on_click=on_sell_click, base_color=COLOR_ERROR)
# System buttons use updated Y positions based on their input fields
sys_buy_button = Button((menu_rect.left + MENU_PADDING, sys_ex_usd_input.rect.bottom + 15, input_width, BUTTON_HEIGHT), "Buy COIN (Sys)", on_click=on_system_buy_click, base_color=COLOR_SYSTEM_EX)
sys_sell_button = Button((menu_rect.left + MENU_PADDING, sys_ex_coin_input.rect.bottom + 15, input_width, BUTTON_HEIGHT), "Sell COIN (Sys)", on_click=on_system_sell_click, base_color=COLOR_SYSTEM_EX)

# Tab Buttons
tabs_y = menu_rect.top + 45; num_tabs = 6; tab_width = (menu_rect.width - MENU_PADDING*(num_tabs+1)) // num_tabs
toggle_add = Button((menu_rect.left+MENU_PADDING, tabs_y, tab_width, 35), "Nodes+", font=font_reg_18, on_click=create_switch_lambda("add", state), text_color=COLOR_TEXT)
toggle_stop = Button((toggle_add.rect.right+MENU_PADDING, tabs_y, tab_width, 35), "Nodes-", font=font_reg_18, on_click=create_switch_lambda("stop", state), text_color=COLOR_TEXT)
toggle_contest = Button((toggle_stop.rect.right+MENU_PADDING, tabs_y, tab_width, 35), "Contest", font=font_reg_18, on_click=create_switch_lambda("contest", state), text_color=COLOR_TEXT)
toggle_users = Button((toggle_contest.rect.right+MENU_PADDING, tabs_y, tab_width, 35), "Users+", font=font_reg_18, on_click=create_switch_lambda("users", state), text_color=COLOR_TEXT)
toggle_exchange = Button((toggle_users.rect.right+MENU_PADDING, tabs_y, tab_width, 35), "Exchange", font=font_reg_18, on_click=create_switch_lambda("exchange", state), text_color=COLOR_TEXT)
toggle_sys_ex = Button((toggle_exchange.rect.right+MENU_PADDING, tabs_y, tab_width, 35), "Sys.Exch", font=font_reg_18, on_click=create_switch_lambda("system_exchange", state), text_color=COLOR_TEXT)

# Lists of elements for each tab
all_toggles = [toggle_add, toggle_stop, toggle_contest, toggle_users, toggle_exchange, toggle_sys_ex]
add_elements = [stake_input, commission_input, add_button] + all_toggles
stop_elements = [stop_node_input, stop_button] + all_toggles
contest_elements = [contest_reward_input, contest_winners_input, contest_button] + all_toggles
users_elements = [add_users_input, add_users_button] + all_toggles
exchange_elements = [exchange_amount_input, buy_button, sell_button] + all_toggles
system_exchange_elements = [sys_ex_usd_input, sys_buy_button, sys_ex_coin_input, sys_sell_button] + all_toggles

# --- Main Game Loop ---
running = True
while running:
    events = pygame.event.get(); mouse_interacted_ui = False
    current_mode = state['current_menu_mode'] # Get current menu mode

    # Determine active elements for event handling and drawing based on the current mode
    if current_mode == "add": active_els = add_elements
    elif current_mode == "stop": active_els = stop_elements
    elif current_mode == "contest": active_els = contest_elements
    elif current_mode == "users": active_els = users_elements
    elif current_mode == "exchange": active_els = exchange_elements
    elif current_mode == "system_exchange": active_els = system_exchange_elements
    else: active_els = [] # Should not happen, but good for safety

    # --- Calculate quotes (only if needed for the current view) ---
    buy_quote_info = None; sell_quote_info = None
    sys_buy_quote = None; sys_sell_quote = None
    if network.exchange:
        if current_mode == "exchange" and exchange_amount_input.value:
            try:
                amount = float(exchange_amount_input.value.replace(',', '.'))
                if amount > 0:
                    buy_quote_info = network.exchange.get_buy_quote(amount)
                    sell_quote_info = network.exchange.get_sell_quote(amount)
            except ValueError: pass # Ignore if not a valid number yet
            except Exception as e: print(f"Error getting user quotes: {e}", file=sys.stderr);
        elif current_mode == "system_exchange":
            if sys_ex_usd_input.value:
                try:
                    usd_amount = float(sys_ex_usd_input.value.replace(',', '.'))
                    if usd_amount > 0:
                        sys_buy_quote = network.exchange.get_system_buy_quote_for_usd(usd_amount)
                except ValueError: pass
                except Exception as e: print(f"Error getting sys buy quote: {e}", file=sys.stderr);
            if sys_ex_coin_input.value:
                 try:
                    coin_amount = float(sys_ex_coin_input.value.replace(',', '.'))
                    if coin_amount > 0:
                        sys_sell_quote = network.exchange.get_system_sell_quote_for_coins(coin_amount)
                 except ValueError: pass
                 except Exception as e: print(f"Error getting sys sell quote: {e}", file=sys.stderr);

    # --- Event Handling ---
    for event in events:
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m: # Toggle Menu
                menu_visible=not menu_visible;
                state['message_data']['text']=""; # Clear message when toggling menu
                # Deactivate input field if menu is closed or opened
                if active_input_field:
                    active_input_field.active=False; active_input_field=None
            elif event.key == pygame.K_c: # Print console data
                print_game_data_to_console(network)

        # Process UI events only if the menu is visible
        if menu_visible:
            keyboard_interacted = False
            # Keyboard input handling
            if event.type == pygame.KEYDOWN:
                if active_input_field:
                    active_input_field.handle_event(event);
                    keyboard_interacted = True # Assume interaction if field is active
                # Handle Enter key for specific actions based on active field/mode
                if event.key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
                    keyboard_interacted = True; aif = active_input_field # Keep track of active field
                    if current_mode == 'add':
                        if aif == stake_input: # Focus next field
                             aif.active=False; commission_input.active=True; active_input_field=commission_input;
                             active_input_field.cursor_timer=time.time(); active_input_field.cursor_visible=True
                        elif aif == commission_input: add_button.on_click() # Trigger action
                        else: add_button.on_click() # Trigger action if no field active
                    elif current_mode == 'stop':
                        if aif == stop_node_input: stop_button.on_click()
                        else: stop_button.on_click()
                    elif current_mode == 'contest':
                        if aif == contest_reward_input: # Focus next field
                            aif.active=False; contest_winners_input.active=True; active_input_field=contest_winners_input;
                            active_input_field.cursor_timer=time.time(); active_input_field.cursor_visible=True
                        elif aif == contest_winners_input: contest_button.on_click()
                        else: contest_button.on_click()
                    elif current_mode == 'users':
                        if aif == add_users_input: add_users_button.on_click()
                        else: add_users_button.on_click()
                    elif current_mode == 'exchange':
                        # Enter doesn't trigger buy/sell to avoid accidents, user must click
                        pass
                    elif current_mode == 'system_exchange':
                        if aif == sys_ex_usd_input: sys_buy_button.on_click()
                        elif aif == sys_ex_coin_input: sys_sell_button.on_click()
                    # Ensure active_input_field reflects changes
                    # active_input_field = aif # aif is local, global active_input_field is modified directly where needed

            # Mouse input handling
            elif event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION]:
                temp_mouse_interacted = False
                # Pass event to all active elements of the current tab
                for element in active_els:
                    if hasattr(element, 'handle_event'):
                        handled = element.handle_event(event)
                        if handled: temp_mouse_interacted = True
                # If mouse interacted with any UI element, set flag
                if temp_mouse_interacted: mouse_interacted_ui = True

            # Deselect input field if clicking outside UI elements
            if event.type == pygame.MOUSEBUTTONDOWN and not mouse_interacted_ui:
                 if active_input_field and not active_input_field.rect.collidepoint(event.pos):
                     # Check if click was outside any active element rect
                     clicked_on_any_active = False
                     for el in active_els:
                         if hasattr(el, 'rect') and el.rect.collidepoint(event.pos):
                             clicked_on_any_active = True
                             break
                     if not clicked_on_any_active:
                         active_input_field.active = False; active_input_field = None

    # --- Game State Update ---
    network.distribute_rewards() # Process daily rewards, simulation, etc.
    if menu_visible:
        # Update UI elements (e.g., cursor blink)
        for element in active_els:
            if hasattr(element,'update'): element.update()
        # Hide old messages
        if state['message_data']["text"] and time.time()-state['message_data']["time"] > 4:
            state['message_data']["text"]=""

    # --- Drawing ---
    screen.fill(COLOR_BACKGROUND)

    # --- Draw Main Panels ---
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< START OF CORRECTED BLOCK >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    data_panel_rect = pygame.Rect(20, 20, WIDTH - 40, 190); draw_panel(screen, data_panel_rect)
    dp = 20  # Padding
    c1x = data_panel_rect.left + dp  # X for left column labels
    c2x = data_panel_rect.centerx + dp / 2  # X for right column labels
    dy = data_panel_rect.top + dp
    lh = 28  # Line height

    # Define X coordinates for right-alignment of values in each column
    col1_val_align_x = data_panel_rect.centerx - dp # Right edge for left column values
    col2_val_align_x = data_panel_rect.right - dp    # Right edge for right column values

    # --- Left Column ---
    draw_text(screen, "Base Em.:", (c1x, dy), font_reg_20, COLOR_TEXT)
    draw_text(screen, format_num(network.base_emission), (col1_val_align_x, dy), font_bold_20, COLOR_TEXT_HEADINGS, right_align=True)
    dy += lh
    draw_text(screen, "Add. Em.:", (c1x, dy), font_reg_20, COLOR_TEXT)
    draw_text(screen, format_num(network.added_emission), (col1_val_align_x, dy), font_bold_20, COLOR_TEXT_HEADINGS, right_align=True)
    dy += lh
    draw_text(screen, "Total Em.:", (c1x, dy), font_reg_20, COLOR_TEXT)
    draw_text(screen, format_num(network.total_emission), (col1_val_align_x, dy), font_bold_20, COLOR_TEXT_HEADINGS, right_align=True)
    dy += lh
    draw_text(screen, "Staked:", (c1x, dy), font_reg_20, COLOR_TEXT)
    draw_text(screen, format_num(network.get_staked()), (col1_val_align_x, dy), font_bold_20, COLOR_TEXT_HEADINGS, right_align=True)
    dy += lh
    draw_text(screen, "Summa(free):", (c1x, dy), font_reg_20, COLOR_TEXT)
    draw_text(screen, format_num(network.remainder), (col1_val_align_x, dy), font_bold_20, COLOR_TEXT_HEADINGS, right_align=True)
    dy += lh
    draw_text(screen, "Our USD:", (c1x, dy), font_reg_20, COLOR_TEXT)
    draw_text(screen, f"${format_num(network.our_usd_balance, 2)}", (col1_val_align_x, dy), font_bold_20, COLOR_SUCCESS, right_align=True)

    # Reset Y for second column
    dy = data_panel_rect.top + dp

    # --- Right Column ---
    draw_text(screen, "Day:", (c2x, dy), font_reg_20, COLOR_TEXT)
    draw_text(screen, str(network.day), (col2_val_align_x, dy), font_bold_20, COLOR_TEXT_HEADINGS, right_align=True)
    dy += lh
    draw_text(screen, "Our Rwds:", (c2x, dy), font_reg_20, COLOR_TEXT)
    draw_text(screen, format_num(network.get_our_nodes_rewards_total()), (col2_val_align_x, dy), font_bold_20, COLOR_TEXT_HEADINGS, right_align=True)
    dy += lh
    draw_text(screen, "Users:", (c2x, dy), font_reg_20, COLOR_TEXT)
    draw_text(screen, str(len(network.users)), (col2_val_align_x, dy), font_bold_20, COLOR_TEXT_HEADINGS, right_align=True)
    dy += lh
    draw_text(screen, "User COIN:", (c2x, dy), font_reg_20, COLOR_TEXT)
    draw_text(screen, format_num(network.get_total_user_coin_balance()), (col2_val_align_x, dy), font_bold_20, COLOR_TEXT_HEADINGS, right_align=True)
    dy += lh
    draw_text(screen, "User USD:", (c2x, dy), font_reg_20, COLOR_TEXT)
    draw_text(screen, f"${format_num(network.get_total_user_usd_balance(), 2)}", (col2_val_align_x, dy), font_bold_20, COLOR_TEXT_HEADINGS, right_align=True)
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< END OF CORRECTED BLOCK >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

    # Exchange Panel
    exchange_panel_y = data_panel_rect.bottom + 20; exchange_panel_height = 80; exchange_panel_rect = pygame.Rect(20, exchange_panel_y, WIDTH - 40, exchange_panel_height)
    draw_panel(screen, exchange_panel_rect, color=COLOR_EXCHANGE); ex_y = exchange_panel_rect.top + 15; ex_lh = 25; ex_x1 = exchange_panel_rect.left + 20; ex_x2 = exchange_panel_rect.centerx + 10
    draw_text(screen,"EXCHANGE:", (exchange_panel_rect.centerx, ex_y), font_bold_20, COLOR_BACKGROUND, center_x=True); ex_y += ex_lh
    draw_text(screen,f"Pool COIN:", (ex_x1, ex_y), font_reg_20, COLOR_BACKGROUND); draw_text(screen,f"{format_num(network.exchange.coin_pool)}", (ex_x2-20, ex_y), font_bold_20, COLOR_BACKGROUND, right_align=True)
    draw_text(screen,f"Pool USD:", (ex_x2, ex_y), font_reg_20, COLOR_BACKGROUND); draw_text(screen,f"${format_num(network.exchange.usd_pool, 2)}", (exchange_panel_rect.right-20, ex_y), font_bold_20, COLOR_BACKGROUND, right_align=True)

    # Nodes List and Graph Panels
    nodes_graph_y = exchange_panel_rect.bottom + 20; nodes_graph_height = HEIGHT - nodes_graph_y - 20
    nodes_width = (WIDTH - 60) * 0.6; graph_width = (WIDTH - 60) * 0.4
    nodes_rect=pygame.Rect(20, nodes_graph_y, nodes_width, nodes_graph_height)
    graph_rect = pygame.Rect(nodes_rect.right + 20, nodes_graph_y, graph_width, nodes_graph_height)

    # Draw Nodes List
    draw_panel(screen,nodes_rect); np=15; ny=nodes_rect.top+np; nlh=35;
    # Adjusted column X positions for 'Own' column
    cx = [nodes_rect.left+np, nodes_rect.left+np+40, nodes_rect.left+np+100, nodes_rect.left+np+160, nodes_rect.left+np+360, nodes_rect.right-np-80]; hy=ny+5
    draw_text(screen,"#",(cx[0],hy),font_bold_20,COLOR_ACCENT);
    draw_text(screen,"St",(cx[1],hy),font_bold_20,COLOR_ACCENT, center_x=True); # Status
    draw_text(screen,"Own",(cx[2],hy),font_bold_20,COLOR_ACCENT, center_x=True); # Owner
    draw_text(screen,"Stake",(cx[3],hy),font_bold_20,COLOR_ACCENT);
    draw_text(screen,"Rewards",(cx[4],hy),font_bold_20,COLOR_ACCENT);
    draw_text(screen,"Fee",(cx[5],hy),font_bold_20,COLOR_ACCENT)
    ny+=nlh-5; pygame.draw.line(screen,COLOR_BORDER,(nodes_rect.left+5,ny),(nodes_rect.right-5,ny),1); ny+=5
    for i,n in enumerate(network.nodes):
        rr=pygame.Rect(nodes_rect.left+1,ny,nodes_rect.width-2,nlh)
        if rr.bottom>nodes_rect.bottom-np: draw_text(screen,"...",(nodes_rect.centerx,ny+nlh//2),font_reg_24,COLOR_TEXT,center_x=True,center_y=True); break
        if i%2==1: pygame.draw.rect(screen,COLOR_PANEL_LIGHT,rr,border_radius=3)
        rcy=rr.centery;
        draw_text(screen,f"{i+1}",(cx[0],rcy),font_reg_20,COLOR_TEXT,center_y=True)
        # Status circle
        s_col=COLOR_SUCCESS if n.active else COLOR_ERROR; pygame.draw.circle(screen,s_col,(cx[1],rcy),8)
        # Owner text
        o_text = "Y" if n.is_our_node else "N"; o_col = COLOR_TEXT if n.is_our_node else COLOR_PLACEHOLDER
        draw_text(screen, o_text, (cx[2], rcy), font_reg_18, o_col, center_x=True, center_y=True)
        # Stake, Rewards, Fee
        draw_text(screen,format_num(n.stake),(cx[3],rcy),font_reg_20,COLOR_TEXT,center_y=True);
        draw_text(screen,format_num(n.balance),(cx[4],rcy),font_reg_20,COLOR_TEXT,center_y=True);
        draw_text(screen,f"{n.commission*100:.1f}%",(cx[5],rcy),font_reg_20,COLOR_TEXT,center_y=True)
        ny+=nlh

    # Draw Price Graph
    draw_price_graph(screen, graph_rect, network.price_history)

    # --- Draw Menu (if visible) ---
    if menu_visible:
        # Draw semi-transparent overlay
        overlay=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA); overlay.fill((0,0,0,180)); screen.blit(overlay,(0,0))
        # Draw menu panel
        draw_panel(screen,menu_rect,COLOR_PANEL,COLOR_BORDER,radius=10); draw_text(screen,"Management",(menu_rect.centerx,menu_rect.top+15),font_bold_24,COLOR_TEXT_HEADINGS,center_x=True)

        # Determine active *menu* elements (for drawing inside the menu)
        if current_mode=="add": active_els_menu=add_elements
        elif current_mode=="stop": active_els_menu=stop_elements
        elif current_mode=="contest": active_els_menu=contest_elements
        elif current_mode=="users": active_els_menu=users_elements
        elif current_mode=="exchange": active_els_menu=exchange_elements
        elif current_mode=="system_exchange": active_els_menu = system_exchange_elements
        else: active_els_menu = []

        # Set tab button colors based on current mode
        toggle_add.base_color=COLOR_ACCENT if current_mode=="add" else COLOR_PANEL_LIGHT
        toggle_stop.base_color=COLOR_ACCENT if current_mode=="stop" else COLOR_PANEL_LIGHT
        toggle_contest.base_color=COLOR_ACCENT if current_mode=="contest" else COLOR_PANEL_LIGHT
        toggle_users.base_color=COLOR_ACCENT if current_mode=="users" else COLOR_PANEL_LIGHT
        toggle_exchange.base_color=COLOR_ACCENT if current_mode=="exchange" else COLOR_PANEL_LIGHT
        toggle_sys_ex.base_color = COLOR_ACCENT if current_mode == "system_exchange" else COLOR_PANEL_LIGHT

        # Draw all tab buttons
        for b in all_toggles: b.draw(screen)

        # Draw active elements for the current tab (excluding the tab buttons themselves)
        for el in active_els_menu:
             if el not in all_toggles: # Don't redraw tabs
                 if hasattr(el, 'draw'):
                     el.draw(screen)

        # Draw additional info for exchange tabs
        if current_mode == "exchange":
            quote_y = exchange_amount_input.rect.bottom + 10
            if network.users:
                test_user = network.users[0]; # Use first user for display
                bal_text = f"Your balance (User {test_user.id}): {format_num(test_user.coin_balance, 2)} COIN / ${format_num(test_user.usd_balance, 2)} USD";
                draw_text(screen, bal_text, (menu_rect.left + MENU_PADDING, quote_y), font_reg_18, COLOR_TEXT);
                quote_y += 25
            else:
                draw_text(screen, "No users available for trading", (menu_rect.left + MENU_PADDING, quote_y), font_reg_18, COLOR_WARNING);
                quote_y += 25
            # Draw buy/sell quote info if available
            if buy_quote_info:
                buy_text = f"Buy Cost: ~${format_num(buy_quote_info['usd_cost'], 2)} (Eff. Price: ${buy_quote_info['effective_price']:.4f})";
                draw_text(screen, buy_text, (menu_rect.left + MENU_PADDING, quote_y), font_reg_18, COLOR_SUCCESS); quote_y += 20
            else:
                 # Show placeholder or error if quote failed (e.g., insufficient liquidity)
                 if exchange_amount_input.value: # Only show if amount is entered
                      draw_text(screen, "Buy Cost: N/A (Check amount/liquidity)", (menu_rect.left + MENU_PADDING, quote_y), font_reg_18, COLOR_WARNING); quote_y += 20

            if sell_quote_info:
                sell_text = f"Sell Revenue: ~${format_num(sell_quote_info['usd_received'], 2)} (Eff. Price: ${sell_quote_info['effective_price']:.4f})";
                draw_text(screen, sell_text, (menu_rect.left + MENU_PADDING, quote_y), font_reg_18, COLOR_ERROR); quote_y += 20
            else:
                 if exchange_amount_input.value: # Only show if amount is entered
                      draw_text(screen, "Sell Revenue: N/A (Check amount/liquidity)", (menu_rect.left + MENU_PADDING, quote_y), font_reg_18, COLOR_WARNING); quote_y += 20

        elif current_mode == "system_exchange":
             sys_quote_y = sys_sell_button.rect.bottom + 10 # Start drawing below the sell button
             bal_text = f"System Balance: {format_num(network.remainder)} COIN / ${format_num(network.our_usd_balance, 2)} USD"
             draw_text(screen, bal_text, (menu_rect.left + MENU_PADDING, sys_quote_y), font_reg_18, COLOR_TEXT); sys_quote_y += 25

             # Draw system buy quote info
             if sys_buy_quote:
                 buy_text = f"Sys Buy ~{format_num(sys_buy_quote['coins_received'],2)} COIN for ${format_num(sys_buy_quote['usd_spent'],2)} (Price:${sys_buy_quote['effective_price']:.4f})" ;
                 draw_text(screen, buy_text, (menu_rect.left + MENU_PADDING, sys_quote_y), font_reg_18, COLOR_SUCCESS); sys_quote_y += 20
             else:
                 if sys_ex_usd_input.value:
                     draw_text(screen, "Sys Buy: N/A (Check amount/liquidity)", (menu_rect.left + MENU_PADDING, sys_quote_y), font_reg_18, COLOR_WARNING); sys_quote_y += 20

             # Draw system sell quote info
             if sys_sell_quote:
                 sell_text = f"Sys Sell {format_num(sys_sell_quote['coins_sold'],2)} COIN for ~${format_num(sys_sell_quote['usd_received'],2)} (Price:${sys_sell_quote['effective_price']:.4f})";
                 draw_text(screen, sell_text, (menu_rect.left + MENU_PADDING, sys_quote_y), font_reg_18, COLOR_ERROR); sys_quote_y += 20
             else:
                  if sys_ex_coin_input.value:
                      draw_text(screen, "Sys Sell: N/A (Check amount/liquidity)", (menu_rect.left + MENU_PADDING, sys_quote_y), font_reg_18, COLOR_WARNING); sys_quote_y += 20


        # Draw messages (like errors or success confirmations)
        if state['message_data']["text"]:
             msg_y=menu_rect.bottom-35
             draw_text(screen,state['message_data']["text"],(menu_rect.centerx,msg_y),font_reg_20,state['message_data']["color"],center_x=True)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()