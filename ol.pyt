"""
Windows OS Simulator - Python Pygame
A full-featured desktop OS simulation with:
- Desktop with icons
- Taskbar with Start Menu, Clock, System Tray
- Draggable, resizable windows
- File Explorer
- Notepad
- Calculator
- Paint app
- Terminal
- Settings panel
- Context menus
- Minimize/Maximize/Close
"""

import pygame
import sys
import math
import random
import datetime
import os

pygame.init()
pygame.font.init()

# ─── CONSTANTS ───────────────────────────────────────────────────────────────
SCREEN_W, SCREEN_H = 1280, 720
TASKBAR_H = 48
FPS = 60

# Windows XP / 7 style palette
COL_DESKTOP     = (58, 110, 165)
COL_TASKBAR     = (25, 75, 135)
COL_TASKBAR_BTN = (40, 100, 160)
COL_WIN_TITLE   = (16, 85, 185)
COL_WIN_TITLE2  = (166, 202, 240)
COL_WIN_BG      = (236, 233, 216)
COL_WIN_BORDER  = (0, 60, 116)
COL_BTN         = (212, 208, 200)
COL_BTN_HOVER   = (230, 230, 230)
COL_BTN_PRESS   = (180, 180, 180)
COL_WHITE       = (255, 255, 255)
COL_BLACK       = (0, 0, 0)
COL_RED         = (220, 50, 50)
COL_GREEN       = (50, 200, 50)
COL_BLUE        = (0, 100, 255)
COL_GRAY        = (160, 160, 160)
COL_LGRAY       = (220, 220, 220)
COL_DGRAY       = (80, 80, 80)
COL_YELLOW      = (255, 220, 50)
COL_START_BTN   = (70, 130, 50)
COL_STARTMENU   = (30, 60, 120)
COL_ICON_BG     = (255, 255, 255, 60)
COL_CLOSE       = (180, 30, 30)
COL_MINIMIZE    = (200, 160, 30)
COL_MAXIMIZE    = (40, 160, 40)
COL_TERM_BG     = (12, 12, 12)
COL_TERM_TEXT   = (204, 204, 204)

# Fonts
try:
    FONT_SM  = pygame.font.SysFont("Segoe UI", 12)
    FONT_MD  = pygame.font.SysFont("Segoe UI", 14)
    FONT_LG  = pygame.font.SysFont("Segoe UI", 16, bold=True)
    FONT_XL  = pygame.font.SysFont("Segoe UI", 22, bold=True)
    FONT_ICON= pygame.font.SysFont("Segoe UI", 11)
    FONT_MONO= pygame.font.SysFont("Courier New", 13)
    FONT_CALC= pygame.font.SysFont("Segoe UI", 24, bold=True)
    FONT_CLOCK=pygame.font.SysFont("Segoe UI", 13, bold=True)
except:
    FONT_SM = FONT_MD = FONT_LG = FONT_XL = FONT_ICON = FONT_MONO = FONT_CALC = FONT_CLOCK = pygame.font.Font(None, 18)

# ─── HELPERS ─────────────────────────────────────────────────────────────────

def draw_rect_rounded(surf, color, rect, radius=6):
    pygame.draw.rect(surf, color, rect, border_radius=radius)

def draw_gradient_rect(surf, color1, color2, rect, vertical=True):
    x, y, w, h = rect
    for i in range(h if vertical else w):
        t = i / max(h if vertical else w, 1)
        c = tuple(int(color1[j] + (color2[j] - color1[j]) * t) for j in range(3))
        if vertical:
            pygame.draw.line(surf, c, (x, y + i), (x + w, y + i))
        else:
            pygame.draw.line(surf, c, (x + i, y), (x + i, y + h))

def clamp(val, lo, hi):
    return max(lo, min(hi, val))

def text_surf(text, font, color=COL_BLACK):
    return font.render(str(text), True, color)

# ─── DESKTOP ICON ────────────────────────────────────────────────────────────

class DesktopIcon:
    SIZE = 72
    def __init__(self, name, icon_color, x, y, app_type):
        self.name = name
        self.icon_color = icon_color
        self.x = x
        self.y = y
        self.app_type = app_type
        self.selected = False
        self.rect = pygame.Rect(x, y, self.SIZE, self.SIZE + 18)

    def draw(self, surf):
        # Shadow
        pygame.draw.rect(surf, (0,0,0,40), (self.x+3, self.y+3, 48, 48), border_radius=8)
        # Icon body
        draw_rect_rounded(surf, self.icon_color, (self.x, self.y, 48, 48), 8)
        # Shine overlay
        shine = pygame.Surface((48, 24), pygame.SRCALPHA)
        shine.fill((255,255,255,40))
        surf.blit(shine, (self.x, self.y))
        # Draw symbol inside icon
        self._draw_symbol(surf)
        # Selection highlight
        if self.selected:
            s = pygame.Surface((self.SIZE, self.SIZE+18), pygame.SRCALPHA)
            s.fill((100,150,255,60))
            surf.blit(s, (self.x - 12, self.y - 4))
        # Label background
        label = FONT_ICON.render(self.name, True, COL_WHITE)
        lw = label.get_width()
        bx = self.x + 24 - lw//2 - 3
        bg = pygame.Surface((lw+6, 16), pygame.SRCALPHA)
        bg.fill((0,0,0,100) if not self.selected else (50,100,200,160))
        surf.blit(bg, (bx, self.y+50))
        surf.blit(label, (bx+3, self.y+51))

    def _draw_symbol(self, surf):
        cx, cy = self.x+24, self.y+24
        t = self.app_type
        if t == "notepad":
            pygame.draw.rect(surf, COL_WHITE, (self.x+10, self.y+8, 28, 32), border_radius=2)
            for i in range(4):
                pygame.draw.line(surf, COL_LGRAY, (self.x+14, self.y+14+i*6), (self.x+34, self.y+14+i*6), 1)
            pygame.draw.line(surf, COL_BLUE, (self.x+12, self.y+12), (self.x+22, self.y+36), 2)
        elif t == "calculator":
            pygame.draw.rect(surf, (50,50,80), (self.x+10, self.y+8, 28, 32), border_radius=3)
            pygame.draw.rect(surf, COL_WHITE, (self.x+13, self.y+11, 22, 8), border_radius=1)
            for r in range(3):
                for c in range(3):
                    pygame.draw.rect(surf, COL_LGRAY, (self.x+13+c*7, self.y+22+r*6, 5, 4), border_radius=1)
        elif t == "explorer":
            pygame.draw.rect(surf, (220,180,80), (self.x+8, self.y+16, 32, 24), border_radius=3)
            pygame.draw.rect(surf, (200,155,60), (self.x+8, self.y+12, 16, 8), border_radius=2)
            pygame.draw.line(surf, COL_WHITE, (self.x+14, self.y+22), (self.x+34, self.y+22), 1)
            pygame.draw.line(surf, COL_WHITE, (self.x+14, self.y+27), (self.x+30, self.y+27), 1)
        elif t == "paint":
            pygame.draw.ellipse(surf, (220,60,60), (self.x+8, self.y+8, 32, 32))
            pygame.draw.ellipse(surf, (60,180,60), (self.x+14, self.y+8, 20, 20))
            pygame.draw.ellipse(surf, (60,60,220), (self.x+8, self.y+20, 20, 20))
            pygame.draw.ellipse(surf, COL_WHITE, (self.x+18, self.y+18, 12, 12))
        elif t == "terminal":
            pygame.draw.rect(surf, COL_TERM_BG, (self.x+8, self.y+8, 32, 32), border_radius=4)
            surf.blit(FONT_MONO.render(">_", True, COL_GREEN), (self.x+10, self.y+18))
        elif t == "settings":
            pygame.draw.circle(surf, COL_LGRAY, (cx, cy), 14)
            pygame.draw.circle(surf, self.icon_color, (cx, cy), 8)
            for angle in range(0, 360, 45):
                rad = math.radians(angle)
                sx = cx + int(math.cos(rad)*14)
                sy = cy + int(math.sin(rad)*14)
                pygame.draw.circle(surf, COL_LGRAY, (sx, sy), 4)
                pygame.draw.circle(surf, COL_WHITE, (sx, sy), 2)
        elif t == "recycle":
            pygame.draw.polygon(surf, (100,200,100), [(cx, self.y+10),(cx+14,self.y+30),(cx-14,self.y+30)])
            pygame.draw.polygon(surf, (60,160,60), [(cx-2,self.y+26),(cx+12,self.y+40),(cx-14,self.y+40)])
        else:
            pygame.draw.rect(surf, COL_WHITE, (self.x+10,self.y+10,28,28), border_radius=4)

# ─── WINDOW BASE CLASS ───────────────────────────────────────────────────────

class Window:
    MIN_W, MIN_H = 200, 150
    TITLE_H = 30

    def __init__(self, title, x, y, w, h, app_type="generic"):
        self.title = title
        self.rect = pygame.Rect(x, y, w, h)
        self.app_type = app_type
        self.dragging = False
        self.drag_offset = (0, 0)
        self.resizing = False
        self.resize_edge = None
        self.minimized = False
        self.maximized = False
        self._pre_max_rect = None
        self.focused = True
        self.alive = True
        self.taskbar_btn = None  # assigned by OS

    @property
    def title_rect(self):
        return pygame.Rect(self.rect.x, self.rect.y, self.rect.w, self.TITLE_H)

    @property
    def close_btn(self):
        return pygame.Rect(self.rect.right - 30, self.rect.y + 5, 22, 20)

    @property
    def max_btn(self):
        return pygame.Rect(self.rect.right - 54, self.rect.y + 5, 22, 20)

    @property
    def min_btn(self):
        return pygame.Rect(self.rect.right - 78, self.rect.y + 5, 22, 20)

    @property
    def content_rect(self):
        return pygame.Rect(self.rect.x+2, self.rect.y+self.TITLE_H, self.rect.w-4, self.rect.h-self.TITLE_H-2)

    def draw(self, surf, focused=True):
        if self.minimized:
            return
        # Window shadow
        shadow = pygame.Surface((self.rect.w+8, self.rect.h+8), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0,0,0,60), (4, 4, self.rect.w, self.rect.h), border_radius=6)
        surf.blit(shadow, (self.rect.x-4, self.rect.y-4))

        # Title bar gradient
        tc1 = COL_WIN_TITLE if focused else COL_GRAY
        tc2 = COL_WIN_TITLE2 if focused else COL_LGRAY
        draw_gradient_rect(surf, tc1, tc2, (self.rect.x, self.rect.y, self.rect.w, self.TITLE_H), vertical=False)
        pygame.draw.rect(surf, COL_WIN_BORDER, self.rect, 2, border_radius=4)

        # Title text
        t = FONT_MD.render(self.title, True, COL_WHITE if focused else COL_DGRAY)
        surf.blit(t, (self.rect.x + 8, self.rect.y + 7))

        # Control buttons
        self._draw_ctrl_btn(surf, self.close_btn,   COL_CLOSE,    "✕")
        self._draw_ctrl_btn(surf, self.max_btn,     COL_MAXIMIZE, "□")
        self._draw_ctrl_btn(surf, self.min_btn,     COL_MINIMIZE, "─")

        # Window background
        pygame.draw.rect(surf, COL_WIN_BG, self.content_rect)

        # Content
        self.draw_content(surf)

    def _draw_ctrl_btn(self, surf, r, color, sym):
        mx, my = pygame.mouse.get_pos()
        hovered = r.collidepoint(mx, my)
        c = tuple(min(255, v+40) for v in color) if hovered else color
        draw_rect_rounded(surf, c, r, 4)
        s = FONT_SM.render(sym, True, COL_WHITE)
        surf.blit(s, (r.centerx - s.get_width()//2, r.centery - s.get_height()//2))

    def draw_content(self, surf):
        pass  # override in subclasses

    def handle_event(self, event):
        pass  # override in subclasses

    def handle_titlebar_event(self, event, os_ref):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if self.close_btn.collidepoint(mx, my):
                self.alive = False
                return True
            elif self.max_btn.collidepoint(mx, my):
                self.toggle_maximize(os_ref)
                return True
            elif self.min_btn.collidepoint(mx, my):
                self.minimized = True
                return True
            elif self.title_rect.collidepoint(mx, my) and not self.maximized:
                self.dragging = True
                self.drag_offset = (mx - self.rect.x, my - self.rect.y)
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                mx, my = event.pos
                self.rect.x = mx - self.drag_offset[0]
                self.rect.y = my - self.drag_offset[1]
                self.rect.y = clamp(self.rect.y, 0, SCREEN_H - TASKBAR_H - self.TITLE_H)
        return False

    def toggle_maximize(self, os_ref):
        if not self.maximized:
            self._pre_max_rect = pygame.Rect(self.rect)
            self.rect = pygame.Rect(0, 0, SCREEN_W, SCREEN_H - TASKBAR_H)
            self.maximized = True
        else:
            self.rect = pygame.Rect(self._pre_max_rect)
            self.maximized = False

# ─── NOTEPAD APP ─────────────────────────────────────────────────────────────

class NotepadWindow(Window):
    def __init__(self, x, y):
        super().__init__("📄 Notepad", x, y, 500, 400, "notepad")
        self.text = "Welcome to PyNotepad!\n\nStart typing here...\n"
        self.cursor_pos = len(self.text)
        self.scroll_y = 0
        self.blink = 0

    def draw_content(self, surf):
        cr = self.content_rect
        # Toolbar
        pygame.draw.rect(surf, COL_BTN, (cr.x, cr.y, cr.w, 26))
        for i, lbl in enumerate(["File", "Edit", "Format", "View", "Help"]):
            t = FONT_MD.render(lbl, True, COL_BLACK)
            surf.blit(t, (cr.x + 8 + i*60, cr.y + 5))
        pygame.draw.line(surf, COL_GRAY, (cr.x, cr.y+26), (cr.right, cr.y+26))

        # Text area
        ta = pygame.Rect(cr.x+2, cr.y+28, cr.w-18, cr.h-30)
        pygame.draw.rect(surf, COL_WHITE, ta)
        pygame.draw.rect(surf, COL_GRAY, ta, 1)

        # Render text lines
        lines = self.text.split('\n')
        y_off = ta.y + 4 - self.scroll_y
        for li, line in enumerate(lines):
            if y_off > ta.bottom: break
            if y_off + 16 > ta.y:
                t = FONT_MONO.render(line if line else " ", True, COL_BLACK)
                surf.blit(t, (ta.x+4, y_off))
                # Draw cursor
                if self.blink % 60 < 30:
                    self._draw_cursor(surf, lines, ta, y_off, li)
            y_off += 18

        # Scrollbar
        total_h = len(lines) * 18
        if total_h > ta.h:
            sb_h = max(20, int(ta.h * ta.h / total_h))
            sb_y = ta.y + int(self.scroll_y / total_h * ta.h)
            pygame.draw.rect(surf, COL_LGRAY, (ta.right, ta.y, 16, ta.h))
            pygame.draw.rect(surf, COL_GRAY, (ta.right+2, sb_y, 12, sb_h), border_radius=4)

        self.blink = (self.blink + 1) % 60

    def _draw_cursor(self, surf, lines, ta, y_off, cur_line):
        # Count chars before cursor
        before = sum(len(lines[i])+1 for i in range(cur_line))
        pos_in_line = self.cursor_pos - before
        if 0 <= pos_in_line <= len(lines[cur_line]):
            cx = ta.x + 4 + FONT_MONO.size(lines[cur_line][:pos_in_line])[0]
            pygame.draw.line(surf, COL_BLACK, (cx, y_off), (cx, y_off+16), 2)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                if self.cursor_pos > 0:
                    self.text = self.text[:self.cursor_pos-1] + self.text[self.cursor_pos:]
                    self.cursor_pos -= 1
            elif event.key == pygame.K_DELETE:
                if self.cursor_pos < len(self.text):
                    self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos+1:]
            elif event.key == pygame.K_RETURN:
                self.text = self.text[:self.cursor_pos] + '\n' + self.text[self.cursor_pos:]
                self.cursor_pos += 1
            elif event.key == pygame.K_LEFT:
                self.cursor_pos = max(0, self.cursor_pos-1)
            elif event.key == pygame.K_RIGHT:
                self.cursor_pos = min(len(self.text), self.cursor_pos+1)
            elif event.unicode and event.unicode.isprintable():
                self.text = self.text[:self.cursor_pos] + event.unicode + self.text[self.cursor_pos:]
                self.cursor_pos += 1
        elif event.type == pygame.MOUSEWHEEL:
            self.scroll_y = clamp(self.scroll_y - event.y*18, 0, max(0, len(self.text.split('\n'))*18 - 200))

# ─── CALCULATOR APP ──────────────────────────────────────────────────────────

class CalculatorWindow(Window):
    BTNS = [
        ['C', '±', '%', '÷'],
        ['7', '8', '9', '×'],
        ['4', '5', '6', '−'],
        ['1', '2', '3', '+'],
        ['0', '.', '='],
    ]
    def __init__(self, x, y):
        super().__init__("🧮 Calculator", x, y, 260, 360, "calculator")
        self.display = "0"
        self.prev = None
        self.op = None
        self.new_num = True
        self._btn_rects = {}

    def draw_content(self, surf):
        cr = self.content_rect
        # Display
        pygame.draw.rect(surf, (30,30,50), (cr.x+8, cr.y+8, cr.w-16, 52), border_radius=6)
        txt = FONT_CALC.render(self.display[-14:], True, COL_WHITE)
        surf.blit(txt, (cr.right - 16 - txt.get_width(), cr.y + 24))

        # Buttons
        bw, bh = (cr.w-16)//4, 48
        self._btn_rects = {}
        mx, my = pygame.mouse.get_pos()
        by_start = cr.y + 70
        for ri, row in enumerate(self.BTNS):
            cols = len(row)
            span = 4 // cols if cols < 4 else 1
            for ci, lbl in enumerate(row):
                if lbl == '0' and cols == 3:
                    bx = cr.x + 8
                    bwr = bw * 2 - 4
                elif lbl == '.' and cols == 3:
                    bx = cr.x + 8 + bw*2
                    bwr = bw - 4
                elif lbl == '=' and cols == 3:
                    bx = cr.x + 8 + bw*3
                    bwr = bw - 4
                else:
                    bx = cr.x + 8 + ci * bw
                    bwr = bw - 4
                br = pygame.Rect(bx, by_start + ri*bh, bwr, bh-4)
                self._btn_rects[lbl] = br
                hov = br.collidepoint(mx, my)
                if lbl in ('÷','×','−','+','='):
                    c = (255, 160, 50) if not hov else (255, 200, 100)
                elif lbl in ('C','±','%'):
                    c = (100,100,120) if not hov else (140,140,160)
                else:
                    c = (60,60,80) if not hov else (90,90,110)
                draw_rect_rounded(surf, c, br, 8)
                t = FONT_LG.render(lbl, True, COL_WHITE)
                surf.blit(t, (br.centerx - t.get_width()//2, br.centery - t.get_height()//2))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for lbl, r in self._btn_rects.items():
                if r.collidepoint(mx, my):
                    self._press(lbl)

    def _press(self, lbl):
        if lbl.isdigit() or lbl == '.':
            if self.new_num:
                self.display = lbl
                self.new_num = False
            else:
                if lbl == '.' and '.' in self.display: return
                self.display = self.display + lbl if self.display != '0' else lbl
        elif lbl == 'C':
            self.display = '0'; self.prev = None; self.op = None; self.new_num = True
        elif lbl == '±':
            val = float(self.display)
            self.display = str(-val if val != 0 else 0)
        elif lbl == '%':
            self.display = str(float(self.display)/100)
        elif lbl in ('÷','×','−','+'):
            self.prev = float(self.display)
            self.op = lbl; self.new_num = True
        elif lbl == '=':
            if self.prev is not None and self.op:
                cur = float(self.display)
                if   self.op == '÷': res = self.prev/cur if cur else 0
                elif self.op == '×': res = self.prev*cur
                elif self.op == '−': res = self.prev-cur
                elif self.op == '+': res = self.prev+cur
                else: res = cur
                self.display = str(int(res)) if res == int(res) else str(round(res,8))
                self.prev = None; self.op = None; self.new_num = True

# ─── FILE EXPLORER ───────────────────────────────────────────────────────────

class ExplorerWindow(Window):
    FILES = [
        ("📁 Documents", "folder"), ("📁 Pictures", "folder"), ("📁 Downloads", "folder"),
        ("📁 Music", "folder"), ("📁 Videos", "folder"), ("📄 readme.txt", "file"),
        ("📄 notes.txt", "file"), ("🖼️ wallpaper.png", "image"), ("🎵 song.mp3", "audio"),
        ("📊 data.xlsx", "sheet"), ("⚙️ config.ini", "config"), ("🗑️ trash", "recycle"),
    ]
    def __init__(self, x, y):
        super().__init__("📁 File Explorer", x, y, 640, 440, "explorer")
        self.path = "C:\\Users\\User"
        self.selected = None
        self.scroll_y = 0

    def draw_content(self, surf):
        cr = self.content_rect
        # Toolbar
        pygame.draw.rect(surf, COL_BTN, (cr.x, cr.y, cr.w, 28))
        for i, lbl in enumerate(["← Back", "→ Forward", "↑ Up", "🔄 Refresh"]):
            t = FONT_MD.render(lbl, True, COL_BLACK)
            surf.blit(t, (cr.x+8+i*80, cr.y+6))
        pygame.draw.line(surf, COL_GRAY, (cr.x, cr.y+28), (cr.right, cr.y+28))

        # Address bar
        addr_rect = pygame.Rect(cr.x, cr.y+28, cr.w, 26)
        pygame.draw.rect(surf, COL_WHITE, addr_rect)
        pygame.draw.rect(surf, COL_GRAY, addr_rect, 1)
        surf.blit(FONT_MD.render(self.path, True, COL_DGRAY), (cr.x+6, cr.y+34))
        pygame.draw.line(surf, COL_GRAY, (cr.x, cr.y+54), (cr.right, cr.y+54))

        # Sidebar
        sb_w = 130
        pygame.draw.rect(surf, COL_LGRAY, (cr.x, cr.y+54, sb_w, cr.h-54))
        pygame.draw.line(surf, COL_GRAY, (cr.x+sb_w, cr.y+54), (cr.x+sb_w, cr.bottom))
        for i, lbl in enumerate(["🖥️ Computer","👤 User","📁 Docs","🖼️ Pics","🎵 Music","🗑️ Recycle"]):
            t = FONT_SM.render(lbl, True, COL_DGRAY)
            surf.blit(t, (cr.x+6, cr.y+60+i*22))

        # Files grid
        fa = pygame.Rect(cr.x+sb_w+4, cr.y+56, cr.w-sb_w-8, cr.h-58)
        pygame.draw.rect(surf, COL_WHITE, fa)
        cols = max(1, fa.w // 80)
        for idx, (name, ftype) in enumerate(self.FILES):
            col_i = idx % cols
            row_i = idx // cols
            fx = fa.x + col_i*80 + 4
            fy = fa.y + row_i*80 + 4 - self.scroll_y
            if fy < fa.y - 80 or fy > fa.bottom: continue
            fr = pygame.Rect(fx, fy, 72, 72)
            if idx == self.selected:
                pygame.draw.rect(surf, (180,210,255), fr, border_radius=4)
            # Icon
            ic = {"folder":(220,180,60),"file":(200,220,255),"image":(180,255,200),
                  "audio":(255,200,150),"sheet":(180,255,180),"config":(220,220,180),
                  "recycle":(180,220,180)}.get(ftype, COL_LGRAY)
            draw_rect_rounded(surf, ic, (fx+20, fy+4, 32, 32), 4)
            t = FONT_ICON.render(name[:10], True, COL_BLACK)
            surf.blit(t, (fx + 36 - t.get_width()//2, fy+38))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            cr = self.content_rect
            fa = pygame.Rect(cr.x+134, cr.y+56, cr.w-138, cr.h-58)
            cols = max(1, fa.w // 80)
            mx, my = event.pos
            if fa.collidepoint(mx, my):
                col_i = (mx - fa.x) // 80
                row_i = (my - fa.y + self.scroll_y) // 80
                idx = row_i * cols + col_i
                if 0 <= idx < len(self.FILES):
                    self.selected = idx
        elif event.type == pygame.MOUSEWHEEL:
            self.scroll_y = clamp(self.scroll_y - event.y*20, 0, max(0, (len(self.FILES)//5)*80 - 200))

# ─── PAINT APP ───────────────────────────────────────────────────────────────

class PaintWindow(Window):
    COLORS = [(0,0,0),(255,255,255),(200,50,50),(50,200,50),(50,50,200),
              (255,220,0),(255,140,0),(180,50,180),(50,220,220),(128,128,128)]
    TOOLS  = ["✏️","🔲","○","↔","🪣","🗑️"]

    def __init__(self, x, y):
        super().__init__("🎨 Paint", x, y, 700, 480, "paint")
        self.canvas = pygame.Surface((700, 480))
        self.canvas.fill(COL_WHITE)
        self.cur_color = (0,0,0)
        self.cur_tool = "✏️"
        self.brush_size = 3
        self.drawing = False
        self.last_pos = None
        self.start_pos = None
        self._canvas_rect = None

    def _get_canvas_rect(self):
        cr = self.content_rect
        return pygame.Rect(cr.x+2, cr.y+60, cr.w-4, cr.h-62)

    def draw_content(self, surf):
        cr = self.content_rect
        # Toolbar
        pygame.draw.rect(surf, COL_BTN, (cr.x, cr.y, cr.w, 58))
        pygame.draw.line(surf, COL_GRAY, (cr.x, cr.y+58), (cr.right, cr.y+58))

        # Tool buttons
        for i, t in enumerate(self.TOOLS):
            br = pygame.Rect(cr.x+4+i*36, cr.y+4, 32, 28)
            sel = (t == self.cur_tool)
            draw_rect_rounded(surf, COL_BTN_PRESS if sel else COL_BTN, br, 4)
            pygame.draw.rect(surf, COL_GRAY, br, 1, border_radius=4)
            surf.blit(FONT_MD.render(t, True, COL_BLACK), (br.x+4, br.y+5))

        # Brush size
        surf.blit(FONT_SM.render("Size:", True, COL_BLACK), (cr.x+230, cr.y+8))
        for i, sz in enumerate([2,4,8,12]):
            br = pygame.Rect(cr.x+265+i*30, cr.y+6, 26, 22)
            draw_rect_rounded(surf, COL_BTN_PRESS if self.brush_size==sz else COL_BTN, br, 4)
            pygame.draw.rect(surf, COL_GRAY, br, 1, border_radius=4)
            surf.blit(FONT_SM.render(str(sz), True, COL_BLACK), (br.centerx-5, br.y+4))

        # Color palette
        surf.blit(FONT_SM.render("Colors:", True, COL_BLACK), (cr.x+4, cr.y+38))
        for i, c in enumerate(self.COLORS):
            cr2 = pygame.Rect(cr.x+54+i*26, cr.y+34, 22, 20)
            pygame.draw.rect(surf, c, cr2, border_radius=3)
            if c == self.cur_color:
                pygame.draw.rect(surf, COL_BLACK, cr2, 2, border_radius=3)

        # Current color preview
        pygame.draw.rect(surf, self.cur_color, (cr.right-50, cr.y+6, 44, 44), border_radius=4)
        pygame.draw.rect(surf, COL_BLACK, (cr.right-50, cr.y+6, 44, 44), 2, border_radius=4)

        # Canvas area
        cvr = self._get_canvas_rect()
        self._canvas_rect = cvr
        pygame.draw.rect(surf, COL_WHITE, cvr)
        # Blit canvas (clip to fit)
        clipped = self.canvas.subsurface(pygame.Rect(0, 0, min(cvr.w, self.canvas.get_width()), min(cvr.h, self.canvas.get_height())))
        surf.blit(clipped, (cvr.x, cvr.y))
        pygame.draw.rect(surf, COL_GRAY, cvr, 1)

    def handle_event(self, event):
        cr = self.content_rect
        cvr = self._get_canvas_rect() if self._canvas_rect else self._get_canvas_rect()
        # Color clicks
        for i, c in enumerate(self.COLORS):
            cr2 = pygame.Rect(cr.x+54+i*26, cr.y+34, 22, 20)
            if event.type == pygame.MOUSEBUTTONDOWN and cr2.collidepoint(event.pos):
                self.cur_color = c; return
        # Tool clicks
        for i, t in enumerate(self.TOOLS):
            br = pygame.Rect(cr.x+4+i*36, cr.y+4, 32, 28)
            if event.type == pygame.MOUSEBUTTONDOWN and br.collidepoint(event.pos):
                if t == "🗑️":
                    self.canvas.fill(COL_WHITE)
                else:
                    self.cur_tool = t; return
        # Size clicks
        for i, sz in enumerate([2,4,8,12]):
            br = pygame.Rect(cr.x+265+i*30, cr.y+6, 26, 22)
            if event.type == pygame.MOUSEBUTTONDOWN and br.collidepoint(event.pos):
                self.brush_size = sz; return

        # Drawing
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if cvr.collidepoint(event.pos):
                self.drawing = True
                lx = event.pos[0] - cvr.x
                ly = event.pos[1] - cvr.y
                self.last_pos = (lx, ly)
                self.start_pos = (lx, ly)
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.drawing and self.cur_tool in ("🔲","○") and self.start_pos:
                lx = event.pos[0] - cvr.x
                ly = event.pos[1] - cvr.y
                ex, ey = lx, ly
                sx, sy = self.start_pos
                if self.cur_tool == "🔲":
                    pygame.draw.rect(self.canvas, self.cur_color, (min(sx,ex),min(sy,ey),abs(ex-sx),abs(ey-sy)), self.brush_size)
                elif self.cur_tool == "○":
                    cx2, cy2 = (sx+ex)//2, (sy+ey)//2
                    rx, ry = abs(ex-sx)//2, abs(ey-sy)//2
                    if rx>0 and ry>0:
                        pygame.draw.ellipse(self.canvas, self.cur_color, (cx2-rx,cy2-ry,rx*2,ry*2), self.brush_size)
            self.drawing = False; self.last_pos = None
        elif event.type == pygame.MOUSEMOTION:
            if self.drawing and cvr.collidepoint(event.pos):
                lx = event.pos[0] - cvr.x
                ly = event.pos[1] - cvr.y
                if self.cur_tool == "✏️" and self.last_pos:
                    pygame.draw.line(self.canvas, self.cur_color, self.last_pos, (lx,ly), self.brush_size)
                elif self.cur_tool == "↔" and self.last_pos:
                    pygame.draw.line(self.canvas, self.cur_color, self.last_pos, (lx,ly), self.brush_size)
                self.last_pos = (lx, ly)

# ─── TERMINAL APP ────────────────────────────────────────────────────────────

class TerminalWindow(Window):
    CMDS = {
        "help"  : "Available: help, ls, dir, echo, date, time, clear, whoami, sysinfo, version",
        "ls"    : "Documents/  Downloads/  Music/  Pictures/  readme.txt  .bashrc",
        "dir"   : "Documents\\  Downloads\\  Music\\  Pictures\\  readme.txt  config.ini",
        "whoami": "User@PyOS",
        "version":"PyOS 1.0.0 (Pygame Edition) - Python {}.{}".format(*sys.version_info[:2]),
        "sysinfo":"OS: PyOS | CPU: Pygame Core | RAM: 9001 MB | Disk: ∞",
        "date"  : str(datetime.date.today()),
        "time"  : lambda: str(datetime.datetime.now().strftime("%H:%M:%S")),
        "echo"  : "echo",
        "clear" : "CLEAR",
    }
    def __init__(self, x, y):
        super().__init__("💻 Terminal", x, y, 560, 380, "terminal")
        self.lines = ["PyOS Terminal [Version 1.0.0]", "Type 'help' for commands.", ""]
        self.input = ""
        self.cursor_blink = 0

    def draw_content(self, surf):
        cr = self.content_rect
        pygame.draw.rect(surf, COL_TERM_BG, cr)
        y_off = cr.y + 4
        for line in self.lines[-(cr.h//18 - 1):]:
            t = FONT_MONO.render(line, True, COL_TERM_TEXT)
            surf.blit(t, (cr.x+6, y_off))
            y_off += 18
        # Input line
        prompt = "User@PyOS:~$ " + self.input
        if self.cursor_blink % 60 < 30:
            prompt += "█"
        t = FONT_MONO.render(prompt, True, (50,220,50))
        surf.blit(t, (cr.x+6, y_off))
        self.cursor_blink = (self.cursor_blink+1) % 60

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self._run_cmd()
            elif event.key == pygame.K_BACKSPACE:
                self.input = self.input[:-1]
            elif event.unicode and event.unicode.isprintable():
                self.input += event.unicode

    def _run_cmd(self):
        cmd_full = self.input.strip()
        self.lines.append("User@PyOS:~$ " + cmd_full)
        cmd = cmd_full.split()[0].lower() if cmd_full else ""
        args = cmd_full[len(cmd):].strip()
        if cmd in self.CMDS:
            val = self.CMDS[cmd]
            if callable(val):
                val = val()
            if val == "CLEAR":
                self.lines = []
            elif cmd == "echo":
                self.lines.append(args)
            else:
                self.lines.append(val)
        elif cmd == "":
            pass
        else:
            self.lines.append(f"'{cmd}': command not found. Try 'help'.")
        self.lines.append("")
        self.input = ""

# ─── SETTINGS WINDOW ─────────────────────────────────────────────────────────

class SettingsWindow(Window):
    THEMES = [("Classic Blue", (58,110,165)), ("Forest Green",(50,120,50)),
              ("Deep Purple",(80,30,120)), ("Midnight Dark",(20,20,30)),
              ("Sunset Orange",(180,80,20))]
    def __init__(self, x, y, os_ref):
        super().__init__("⚙️ Settings", x, y, 480, 380, "settings")
        self.os_ref = os_ref
        self.selected_theme = 0
        self.volume = 70
        self.brightness = 100
        self._vol_dragging = False
        self._bri_dragging = False

    def draw_content(self, surf):
        cr = self.content_rect
        # Sidebar
        pygame.draw.rect(surf, COL_LGRAY, (cr.x, cr.y, 130, cr.h))
        for i, lbl in enumerate(["🎨 Theme","🔊 Sound","💡 Display","🔒 Privacy","ℹ️ About"]):
            t = FONT_MD.render(lbl, True, COL_BLACK)
            sel = (i==0)
            if sel: pygame.draw.rect(surf, COL_WHITE, (cr.x, cr.y+i*36, 130, 34))
            surf.blit(t, (cr.x+8, cr.y+8+i*36))
        pygame.draw.line(surf, COL_GRAY, (cr.x+130, cr.y), (cr.x+130, cr.bottom))

        # Theme section
        panel = pygame.Rect(cr.x+138, cr.y+8, cr.w-146, cr.h-16)
        surf.blit(FONT_LG.render("Desktop Theme", True, COL_BLACK), (panel.x, panel.y))
        pygame.draw.line(surf, COL_LGRAY, (panel.x, panel.y+24), (panel.right, panel.y+24))

        for i, (name, color) in enumerate(self.THEMES):
            ty = panel.y + 34 + i*42
            # Preview swatch
            pygame.draw.rect(surf, color, (panel.x, ty, 60, 32), border_radius=4)
            pygame.draw.rect(surf, COL_BLACK if i==self.selected_theme else COL_GRAY,
                             (panel.x, ty, 60, 32), 2, border_radius=4)
            # Taskbar strip in preview
            pygame.draw.rect(surf, tuple(max(0,c-30) for c in color), (panel.x, ty+24, 60, 8))
            surf.blit(FONT_SM.render(name, True, COL_BLACK), (panel.x+68, ty+8))
            if i == self.selected_theme:
                surf.blit(FONT_SM.render("✔ Active", True, (0,160,0)), (panel.x+200, ty+8))

        # Volume slider
        vy = panel.y+34+len(self.THEMES)*42+8
        surf.blit(FONT_MD.render(f"Volume: {self.volume}%", True, COL_BLACK), (panel.x, vy))
        sw = panel.w-10
        pygame.draw.rect(surf, COL_LGRAY, (panel.x, vy+22, sw, 8), border_radius=4)
        vx = panel.x + int(self.volume/100*sw)
        pygame.draw.rect(surf, COL_TASKBAR, (panel.x, vy+22, vx-panel.x, 8), border_radius=4)
        pygame.draw.circle(surf, COL_WIN_TITLE, (vx, vy+26), 8)

    def handle_event(self, event):
        cr = self.content_rect
        panel_x = cr.x+138
        if event.type == pygame.MOUSEBUTTONDOWN and event.button==1:
            mx, my = event.pos
            for i, (name, color) in enumerate(self.THEMES):
                ty = cr.y+8 + 34 + i*42
                if pygame.Rect(panel_x, ty, 260, 32).collidepoint(mx, my):
                    self.selected_theme = i
                    self.os_ref.desktop_color = color
            # Volume drag
            vy = cr.y+8+34+len(self.THEMES)*42+30
            sw = cr.w-146-10
            if pygame.Rect(panel_x, vy, sw, 16).collidepoint(mx, my):
                self.volume = clamp(int((mx-panel_x)/sw*100), 0, 100)
                self._vol_dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self._vol_dragging = False
        elif event.type == pygame.MOUSEMOTION and self._vol_dragging:
            cr = self.content_rect
            panel_x = cr.x+138
            sw = cr.w-146-10
            self.volume = clamp(int((event.pos[0]-panel_x)/sw*100), 0, 100)

# ─── CONTEXT MENU ────────────────────────────────────────────────────────────

class ContextMenu:
    def __init__(self, x, y, items):
        self.x, self.y = x, y
        self.items = items  # list of (label, callback)
        self.item_h = 26
        self.w = 180
        self.alive = True
        self.rect = pygame.Rect(x, y, self.w, len(items)*self.item_h+8)

    def draw(self, surf):
        draw_rect_rounded(surf, COL_WHITE, self.rect, 4)
        pygame.draw.rect(surf, COL_GRAY, self.rect, 1, border_radius=4)
        mx, my = pygame.mouse.get_pos()
        for i, (lbl, _) in enumerate(self.items):
            ir = pygame.Rect(self.x+2, self.y+4+i*self.item_h, self.w-4, self.item_h)
            if ir.collidepoint(mx, my) and lbl != "---":
                pygame.draw.rect(surf, (200,220,255), ir, border_radius=3)
            if lbl == "---":
                pygame.draw.line(surf, COL_LGRAY, (self.x+8, self.y+4+i*self.item_h+13),
                                 (self.x+self.w-8, self.y+4+i*self.item_h+13))
            else:
                surf.blit(FONT_MD.render(lbl, True, COL_BLACK), (self.x+10, self.y+6+i*self.item_h))

    def handle_click(self, pos):
        mx, my = pos
        for i, (lbl, cb) in enumerate(self.items):
            ir = pygame.Rect(self.x+2, self.y+4+i*self.item_h, self.w-4, self.item_h)
            if ir.collidepoint(mx, my) and lbl != "---" and cb:
                cb()
                self.alive = False
                return True
        return False

# ─── CLOCK / TRAY ────────────────────────────────────────────────────────────

class SystemTray:
    def __init__(self):
        self.rect = pygame.Rect(SCREEN_W-140, 0, 140, TASKBAR_H)

    def draw(self, surf):
        pygame.draw.rect(surf, COL_TASKBAR, self.rect)
        now = datetime.datetime.now()
        time_str = now.strftime("%H:%M:%S")
        date_str = now.strftime("%d %b %Y")
        t1 = FONT_CLOCK.render(time_str, True, COL_WHITE)
        t2 = FONT_SM.render(date_str, True, (180,210,255))
        surf.blit(t1, (SCREEN_W-130, 5))
        surf.blit(t2, (SCREEN_W-130, 22))
        # Battery icon
        pygame.draw.rect(surf, COL_WHITE, (SCREEN_W-148, 14, 12, 20), 1)
        pygame.draw.rect(surf, COL_GREEN, (SCREEN_W-147, 22, 10, 11))
        pygame.draw.rect(surf, COL_WHITE, (SCREEN_W-144, 12, 6, 3))
        # Wifi icon
        for i in range(3):
            r = 4+i*3
            pygame.draw.arc(surf, COL_WHITE, (SCREEN_W-170-r, 18-r, r*2, r*2), 0.4, 2.74, 2)
        pygame.draw.circle(surf, COL_WHITE, (SCREEN_W-170, 28), 2)

# ─── START MENU ──────────────────────────────────────────────────────────────

class StartMenu:
    APPS = [
        ("📄 Notepad", "notepad"), ("🧮 Calculator", "calculator"),
        ("📁 File Explorer", "explorer"), ("🎨 Paint", "paint"),
        ("💻 Terminal", "terminal"), ("⚙️ Settings", "settings"),
    ]
    def __init__(self):
        self.visible = False
        self.w, self.h = 260, 380
        self.rect = pygame.Rect(0, SCREEN_H-TASKBAR_H-self.h, self.w, self.h)

    def toggle(self):
        self.visible = not self.visible

    def draw(self, surf):
        if not self.visible: return
        # Background
        draw_gradient_rect(surf, (40,80,160), COL_STARTMENU, self.rect.tuple() if hasattr(self.rect,'tuple') else (self.rect.x,self.rect.y,self.rect.w,self.rect.h))
        pygame.draw.rect(surf, COL_WIN_BORDER, self.rect, 2, border_radius=4)

        # Header
        pygame.draw.rect(surf, (20,50,110), (self.rect.x, self.rect.y, self.rect.w, 54))
        surf.blit(FONT_XL.render("PyOS", True, COL_WHITE), (self.rect.x+10, self.rect.y+8))
        surf.blit(FONT_SM.render("Welcome, User", True, (180,210,255)), (self.rect.x+10, self.rect.y+36))

        # Divider
        pygame.draw.line(surf, COL_WIN_TITLE2, (self.rect.x, self.rect.y+54), (self.rect.right, self.rect.y+54))

        # App list
        mx, my = pygame.mouse.get_pos()
        surf.blit(FONT_SM.render("Programs", True, (180,210,255)), (self.rect.x+10, self.rect.y+60))
        for i, (name, _) in enumerate(self.APPS):
            ir = pygame.Rect(self.rect.x, self.rect.y+76+i*38, self.rect.w, 36)
            if ir.collidepoint(mx, my):
                pygame.draw.rect(surf, (80,120,200), ir)
            t = FONT_MD.render(name, True, COL_WHITE)
            surf.blit(t, (self.rect.x+12, self.rect.y+84+i*38))

        # Footer
        pygame.draw.line(surf, COL_WIN_TITLE2, (self.rect.x, self.rect.bottom-36), (self.rect.right, self.rect.bottom-36))
        surf.blit(FONT_MD.render("🔴 Shut Down", True, COL_WHITE), (self.rect.x+12, self.rect.bottom-28))
        surf.blit(FONT_MD.render("🔁 Restart", True, COL_WHITE), (self.rect.x+130, self.rect.bottom-28))

    def handle_click(self, pos, os_ref):
        if not self.visible: return False
        mx, my = pos
        if not self.rect.collidepoint(mx, my):
            self.visible = False
            return False
        for i, (name, app_type) in enumerate(self.APPS):
            ir = pygame.Rect(self.rect.x, self.rect.y+76+i*38, self.rect.w, 36)
            if ir.collidepoint(mx, my):
                os_ref.launch_app(app_type)
                self.visible = False
                return True
        # Shutdown
        if pygame.Rect(self.rect.x+12, self.rect.bottom-28, 120, 20).collidepoint(mx, my):
            pygame.quit(); sys.exit()
        return True

# ─── TASKBAR ─────────────────────────────────────────────────────────────────

class Taskbar:
    def __init__(self):
        self.rect = pygame.Rect(0, SCREEN_H-TASKBAR_H, SCREEN_W, TASKBAR_H)
        self.start_btn = pygame.Rect(4, SCREEN_H-TASKBAR_H+4, 90, TASKBAR_H-8)
        self.tray = SystemTray()

    def draw(self, surf, windows, focused_win):
        draw_gradient_rect(surf, COL_TASKBAR, (15,55,115), (0, SCREEN_H-TASKBAR_H, SCREEN_W, TASKBAR_H))
        pygame.draw.line(surf, COL_WIN_TITLE2, (0, SCREEN_H-TASKBAR_H), (SCREEN_W, SCREEN_H-TASKBAR_H))

        # Start button
        mx, my = pygame.mouse.get_pos()
        sh = self.start_btn.collidepoint(mx, my)
        draw_gradient_rect(surf, (90,160,60) if sh else COL_START_BTN,
                           (50,110,30) if sh else (40,90,20), self.start_btn.inflate(0,0))
        pygame.draw.rect(surf, (20,80,10), self.start_btn, 1, border_radius=4)
        surf.blit(FONT_LG.render("⊞ Start", True, COL_WHITE),
                  (self.start_btn.x+6, self.start_btn.y+8))

        # Window buttons
        btn_x = 100
        for w in windows:
            if not w.alive: continue
            bw = min(160, max(80, 140))
            br = pygame.Rect(btn_x, SCREEN_H-TASKBAR_H+4, bw, TASKBAR_H-8)
            focused = (w is focused_win)
            bg = COL_WIN_TITLE if focused else COL_TASKBAR_BTN
            draw_rect_rounded(surf, bg, br, 4)
            pygame.draw.rect(surf, COL_WIN_BORDER if focused else COL_GRAY, br, 1, border_radius=4)
            if w.minimized:
                pygame.draw.line(surf, COL_WIN_TITLE2, (br.x+4, br.bottom-6), (br.right-4, br.bottom-6), 2)
            lbl = FONT_SM.render(w.title[:18], True, COL_WHITE)
            surf.blit(lbl, (br.x+6, br.centery-7))
            w.taskbar_btn = br
            btn_x += bw + 4

        self.tray.draw(surf)

# ─── OS CORE ─────────────────────────────────────────────────────────────────

class OperatingSystem:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("PyOS — Pygame Windows Simulator")
        self.clock = pygame.time.Clock()
        self.desktop_color = COL_DESKTOP
        self.windows = []
        self.focused_win = None
        self.taskbar = Taskbar()
        self.start_menu = StartMenu()
        self.context_menu = None
        self.desktop_icons = self._make_icons()
        self._win_counter = 0
        # Draw starfield
        self.stars = [(random.randint(0,SCREEN_W), random.randint(0,SCREEN_H-TASKBAR_H), random.random()) for _ in range(60)]

    def _make_icons(self):
        defs = [
            ("Notepad",   (70,130,220),  40, 40, "notepad"),
            ("Calculator",(80,160,80),  40,140, "calculator"),
            ("Explorer",  (220,170,50), 40,240, "explorer"),
            ("Paint",     (220,80,80),  40,340, "paint"),
            ("Terminal",  (30,30,30),   40,440, "terminal"),
            ("Settings",  (120,80,200), 40,540, "settings"),
            ("Recycle",   (80,180,80),  40,620, "recycle"),
        ]
        return [DesktopIcon(n,c,x,y,t) for n,c,x,y,t in defs]

    def launch_app(self, app_type, x=None, y=None):
        self._win_counter += 1
        ox = (200 + self._win_counter*25) % (SCREEN_W-400) if x is None else x
        oy = (60  + self._win_counter*25) % (SCREEN_H-TASKBAR_H-300) if y is None else y
        if   app_type == "notepad":    w = NotepadWindow(ox, oy)
        elif app_type == "calculator": w = CalculatorWindow(ox, oy)
        elif app_type == "explorer":   w = ExplorerWindow(ox, oy)
        elif app_type == "paint":      w = PaintWindow(ox, oy)
        elif app_type == "terminal":   w = TerminalWindow(ox, oy)
        elif app_type == "settings":   w = SettingsWindow(ox, oy, self)
        else: return
        self.windows.append(w)
        self.focused_win = w

    def _draw_desktop(self):
        # Gradient desktop background
        draw_gradient_rect(self.screen, self.desktop_color,
                           tuple(max(0,c-40) for c in self.desktop_color),
                           (0,0,SCREEN_W,SCREEN_H-TASKBAR_H))
        # Stars / dots
        for sx, sy, sz in self.stars:
            r = max(1, int(sz*3))
            pygame.draw.circle(self.screen, (255,255,255,int(sz*120)),
                               (sx,sy), r)
        # Grid pattern
        for gx in range(0, SCREEN_W, 60):
            pygame.draw.line(self.screen, (*self.desktop_color, 80),
                             (gx,0),(gx,SCREEN_H-TASKBAR_H), 1)
        for gy in range(0, SCREEN_H-TASKBAR_H, 60):
            pygame.draw.line(self.screen, (*self.desktop_color, 80),
                             (0,gy),(SCREEN_W,gy), 1)

    def run(self):
        while True:
            self.clock.tick(FPS)
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()

                # Context menu
                if self.context_menu and self.context_menu.alive:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if not self.context_menu.handle_click(event.pos):
                            self.context_menu.alive = False
                    continue

                # Start menu
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.taskbar.start_btn.collidepoint(event.pos):
                        self.start_menu.toggle()
                    elif self.start_menu.visible:
                        self.start_menu.handle_click(event.pos, self)

                # Taskbar window buttons
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for w in self.windows:
                        if w.taskbar_btn and w.taskbar_btn.collidepoint(event.pos):
                            if w.minimized:
                                w.minimized = False
                                self.focused_win = w
                            elif self.focused_win is w:
                                w.minimized = True
                            else:
                                self.focused_win = w

                # Desktop right-click
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                    mx, my = event.pos
                    if my < SCREEN_H - TASKBAR_H:
                        on_icon = False
                        for icon in self.desktop_icons:
                            if icon.rect.collidepoint(mx, my):
                                on_icon = True
                                self.context_menu = ContextMenu(mx, my, [
                                    ("▶ Open", lambda t=icon.app_type: self.launch_app(t)),
                                    ("---",None),
                                    ("Properties", None),
                                ])
                                break
                        if not on_icon:
                            self.context_menu = ContextMenu(mx, my, [
                                ("📄 New Notepad", lambda: self.launch_app("notepad")),
                                ("🎨 Open Paint",  lambda: self.launch_app("paint")),
                                ("💻 Terminal",    lambda: self.launch_app("terminal")),
                                ("---",None),
                                ("⚙️ Settings",    lambda: self.launch_app("settings")),
                                ("🖼️ Change Wallpaper", self._cycle_wallpaper),
                            ])

                # Desktop icon click
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    clicked_icon = False
                    for icon in self.desktop_icons:
                        if icon.rect.collidepoint(event.pos):
                            icon.selected = True
                            clicked_icon = True
                        else:
                            icon.selected = False
                    if not clicked_icon:
                        for icon in self.desktop_icons: icon.selected = False

                # Double-click icon to open
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Use click count trick
                    pass

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for icon in self.desktop_icons:
                        if icon.rect.collidepoint(event.pos):
                            if not hasattr(icon, '_last_click'):
                                icon._last_click = 0
                            now = pygame.time.get_ticks()
                            if now - icon._last_click < 400:
                                self.launch_app(icon.app_type)
                            icon._last_click = now

                # Window events
                handled_by_win = False
                for w in reversed(self.windows):
                    if not w.alive or w.minimized: continue
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if w.rect.collidepoint(event.pos):
                            self.focused_win = w
                            # Bring to front
                            self.windows.remove(w)
                            self.windows.append(w)
                    consumed = w.handle_titlebar_event(event, self)
                    if self.focused_win is w:
                        w.handle_event(event)
                    break 

            # Remove dead windows
            self.windows = [w for w in self.windows if w.alive]

            # ── DRAW ──
            self._draw_desktop()

            # Desktop icons
            for icon in self.desktop_icons:
                icon.draw(self.screen)

            # Windows (back to front)
            for w in self.windows:
                if not w.minimized:
                    w.draw(self.screen, focused=(w is self.focused_win))

            # Taskbar
            self.taskbar.draw(self.screen, self.windows, self.focused_win)

            # Start menu (on top)
            self.start_menu.draw(self.screen)

            # Context menu
            if self.context_menu and self.context_menu.alive:
                self.context_menu.draw(self.screen)

            pygame.display.flip()

    def _cycle_wallpaper(self):
        palettes = [
            (58,110,165), (50,120,50), (80,30,120), (20,20,30), (140,60,20)
        ]
        idx = 0
        for i, p in enumerate(palettes):
            if p == self.desktop_color:
                idx = (i+1) % len(palettes)
                break
        self.desktop_color = palettes[idx]

# ─── ENTRY POINT ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    os_sim = OperatingSystem()
    # Open a couple of starter windows
    os_sim.launch_app("notepad", 160, 60)
    os_sim.launch_app("calculator", 700, 60)
    os_sim.run()