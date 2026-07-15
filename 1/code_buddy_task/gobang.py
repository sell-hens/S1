import pygame
import sys
import random
import math
import platform

# ========== 常量定义 ==========
BOARD_SIZE = 15             # 15x15 棋盘
CELL_SIZE = 36              # 每格像素大小

# 棋盘区域参数
BOARD_PADDING = 30          # 棋盘线到棋盘面板边缘的间距
BOARD_BORDER = 18           # 棋盘面板外边框厚度
BOARD_LINE_LENGTH = CELL_SIZE * (BOARD_SIZE - 1)

# 棋盘面板总尺寸
BOARD_PANEL_W = BOARD_LINE_LENGTH + BOARD_PADDING * 2
BOARD_PANEL_H = BOARD_LINE_LENGTH + BOARD_PADDING * 2

# 窗口大小
LEFT_MARGIN = 36
RIGHT_PANEL_W = 220
GAP_BETWEEN_PANELS = 24       # 棋盘与右侧面板的间距
WINDOW_WIDTH = LEFT_MARGIN + BOARD_PANEL_W + GAP_BETWEEN_PANELS + RIGHT_PANEL_W + 30
WINDOW_HEIGHT = BOARD_PANEL_H + 60

# 定位
PANEL_X = LEFT_MARGIN
PANEL_Y = 40
GRID_OFFSET = BOARD_PADDING
OFFSET_X = PANEL_X + GRID_OFFSET
OFFSET_Y = PANEL_Y + GRID_OFFSET
RIGHT_PANEL_X = PANEL_X + BOARD_PANEL_W + GAP_BETWEEN_PANELS
# 右侧面板与棋盘面板上/下边缘严格对齐
RIGHT_PANEL_Y = PANEL_Y
RIGHT_PANEL_H = BOARD_PANEL_H

# ========== 颜色定义 ==========
# 背景 - 温暖的奶油色调
COLOR_BG = (245, 240, 232)

# 棋盘 - 柔和的木色渐变
COLOR_BOARD_OUTER = (130, 95, 55)     # 外框深木色
COLOR_BOARD_MID = (175, 130, 75)      # 中层木色
COLOR_BOARD_INNER = (235, 208, 150)   # 棋盘面暖木色
COLOR_BOARD_SHADOW = (145, 115, 80)   # 阴影色

# 网格线 - 细腻的深褐色
COLOR_GRID_LINE = (80, 60, 35)
COLOR_GRID_OUTER = (65, 45, 25)

# 星位点
COLOR_STAR = (70, 48, 28)

# 棋子颜色
COLOR_BLACK_BASE = (35, 35, 35)
COLOR_WHITE_BASE = (248, 248, 242)
COLOR_WHITE_BORDER = (155, 155, 150)

# 文字颜色
COLOR_TEXT = (55, 38, 20)
COLOR_TEXT_LIGHT = (130, 100, 70)
COLOR_ACCENT = (185, 55, 40)
COLOR_GOLD = (210, 165, 55)

# 胜利连子高亮颜色
COLOR_WIN_HIGHLIGHT = (255, 215, 0)    # 金色外发光
COLOR_WIN_GLOW = (255, 80, 40)         # 红色内芯

# 面板颜色
COLOR_PANEL_BG = (240, 233, 220)
COLOR_PANEL_BORDER = (175, 145, 105)

# 按钮配色 - 统一柔和风格
COLOR_BTN_RESTART = (90, 145, 95)
COLOR_BTN_RESTART_HOVER = (110, 170, 115)
COLOR_BTN_UNDO = (185, 135, 55)
COLOR_BTN_UNDO_HOVER = (210, 155, 68)
COLOR_BTN_QUIT = (175, 78, 68)
COLOR_BTN_QUIT_HOVER = (200, 95, 80)
COLOR_BTN_MODE_PVP = (72, 108, 155)
COLOR_BTN_MODE_PVP_HOVER = (90, 130, 180)
COLOR_BTN_MODE_PVE = (125, 78, 135)
COLOR_BTN_MODE_PVE_HOVER = (150, 95, 160)

# 右侧面板按钮布局常量（draw_right_panel 与 get_btn_rects 共享）
BTN_PANEL_MARGIN_X = 16
BTN_BOX_PADDING = 12
BTN_HEIGHT = 36
BTN_SPACING = 6
BTN_COUNT = 4
BTN_BOX_MARGIN_BOTTOM = 12

# 星位点
STAR_POINTS = [
    (3, 3), (3, 7), (3, 11),
    (7, 3), (7, 7), (7, 11),
    (11, 3), (11, 7), (11, 11),
]

# AI 难度等级
DIFFICULTY_EASY = 1
DIFFICULTY_MEDIUM = 2
DIFFICULTY_HARD = 3
DIFFICULTY_NAMES = {
    DIFFICULTY_EASY: "简单",
    DIFFICULTY_MEDIUM: "中等",
    DIFFICULTY_HARD: "困难",
}

# ===================== 工具函数 =====================

def get_font(size, bold=False):
    """获取字体：优先系统自带中文字体，回退到 pygame 默认字体"""
    system = platform.system()
    if system == "Windows":
        font_paths = [
            "C:/Windows/Fonts/simhei.ttf",
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/simsun.ttc",
        ]
    elif system == "Darwin":
        font_paths = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/Library/Fonts/Arial Unicode.ttf",
        ]
    else:
        # Linux 等：尝试常见中文字体路径
        font_paths = [
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
        ]

    for path in font_paths:
        try:
            font = pygame.font.Font(path, size)
            font.set_bold(bold)
            return font
        except (FileNotFoundError, pygame.error):
            continue

    font = pygame.font.Font(None, size)
    font.set_bold(bold)
    return font


def board_to_pixel(row, col):
    """棋盘坐标 → 窗口像素坐标"""
    return OFFSET_X + col * CELL_SIZE, OFFSET_Y + row * CELL_SIZE


def pixel_to_board(px, py):
    """窗口像素坐标 → 最近棋盘坐标（超出返回 None）"""
    col = round((px - OFFSET_X) / CELL_SIZE)
    row = round((py - OFFSET_Y) / CELL_SIZE)
    if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
        return row, col
    return None


def draw_text_centered(screen, text, font, color, cx, cy):
    """便捷函数：在 (cx, cy) 居中绘制文字"""
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(cx, cy))
    screen.blit(surf, rect)


def lerp_color(c1, c2, t):
    """在两个颜色之间线性插值，t ∈ [0, 1]"""
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


# ===================== 绘制棋盘 =====================

def draw_board(screen):
    """绘制棋盘：多层木色边框 + 网格线 + 星位 + 坐标"""
    screen.fill(COLOR_BG)

    # 柔和阴影 - 向下向右偏移
    shadow_rect = pygame.Rect(PANEL_X + 5, PANEL_Y + 5, BOARD_PANEL_W, BOARD_PANEL_H)
    pygame.draw.rect(screen, COLOR_BOARD_SHADOW, shadow_rect, border_radius=8)

    # 外框（深木色）
    outer_rect = pygame.Rect(PANEL_X, PANEL_Y, BOARD_PANEL_W, BOARD_PANEL_H)
    pygame.draw.rect(screen, COLOR_BOARD_OUTER, outer_rect, border_radius=8)

    # 中层
    mid_rect = pygame.Rect(
        PANEL_X + BOARD_BORDER // 3, PANEL_Y + BOARD_BORDER // 3,
        BOARD_PANEL_W - BOARD_BORDER * 2 // 3,
        BOARD_PANEL_H - BOARD_BORDER * 2 // 3
    )
    pygame.draw.rect(screen, COLOR_BOARD_MID, mid_rect, border_radius=5)

    # 内层（棋盘面）- 暖木色
    inner_rect = pygame.Rect(
        PANEL_X + BOARD_BORDER, PANEL_Y + BOARD_BORDER,
        BOARD_PANEL_W - BOARD_BORDER * 2,
        BOARD_PANEL_H - BOARD_BORDER * 2
    )
    pygame.draw.rect(screen, COLOR_BOARD_INNER, inner_rect, border_radius=3)

    # 网格线 - 用比棋盘面略深的颜色
    for i in range(BOARD_SIZE):
        sx, sy = board_to_pixel(0, i)
        ex, ey = board_to_pixel(BOARD_SIZE - 1, i)
        pygame.draw.line(screen, COLOR_GRID_LINE, (sx, sy), (ex, ey), 1)
        sx, sy = board_to_pixel(i, 0)
        ex, ey = board_to_pixel(i, BOARD_SIZE - 1)
        pygame.draw.line(screen, COLOR_GRID_LINE, (sx, sy), (ex, ey), 1)

    # 最外圈加粗
    corners = [
        (board_to_pixel(0, 0), board_to_pixel(0, BOARD_SIZE - 1)),
        (board_to_pixel(BOARD_SIZE - 1, 0), board_to_pixel(BOARD_SIZE - 1, BOARD_SIZE - 1)),
        (board_to_pixel(0, 0), board_to_pixel(BOARD_SIZE - 1, 0)),
        (board_to_pixel(0, BOARD_SIZE - 1), board_to_pixel(BOARD_SIZE - 1, BOARD_SIZE - 1)),
    ]
    for p1, p2 in corners:
        pygame.draw.line(screen, COLOR_GRID_OUTER, p1, p2, 2)

    # 星位点 - 镂空圆环效果
    for r, c in STAR_POINTS:
        cx, cy = board_to_pixel(r, c)
        pygame.draw.circle(screen, COLOR_STAR, (cx, cy), 4)
        pygame.draw.circle(screen, COLOR_BOARD_INNER, (cx, cy), 1)

    # 坐标标签
    label_font = get_font(10)
    for i in range(BOARD_SIZE):
        label = label_font.render(chr(ord('A') + i), True, COLOR_TEXT_LIGHT)
        cx, _ = board_to_pixel(0, i)
        screen.blit(label, label.get_rect(center=(cx, PANEL_Y - 8)))
        label = label_font.render(str(i + 1), True, COLOR_TEXT_LIGHT)
        _, cy = board_to_pixel(i, 0)
        screen.blit(label, label.get_rect(center=(PANEL_X - 14, cy)))


# ===================== 绘制棋子 =====================

def draw_piece(screen, row, col, player, radius=None):
    """绘制一颗立体棋子（多层渐变 + 阴影 + 高光）"""
    cx, cy = board_to_pixel(row, col)
    if radius is None:
        radius = CELL_SIZE // 2 - 2

    if player == 1:  # 黑子 - 墨玉质感
        # 外层柔和阴影
        for i in range(3):
            offset = 3 - i
            shadow_alpha = 40 - i * 12
            s = pygame.Surface((radius * 2 + 6, radius * 2 + 6), pygame.SRCALPHA)
            pygame.draw.circle(s, (0, 0, 0, shadow_alpha),
                               (radius + 3, radius + 3 + offset), radius + 1)
            screen.blit(s, (cx - radius - 3, cy - radius - 3))

        # 底层
        pygame.draw.circle(screen, (80, 70, 60), (cx + 2, cy + 2), radius)
        # 主体
        pygame.draw.circle(screen, COLOR_BLACK_BASE, (cx, cy), radius)
        # 渐变层次 - 从深到浅的同心圆
        for i, clr in enumerate([(50, 48, 45), (65, 62, 58), (85, 80, 75), (115, 108, 100)]):
            r = radius - i * 3
            if r > 0:
                pygame.draw.circle(screen, clr, (cx - 1, cy - 1), r)
        # 高光点
        hl_r = max(radius // 3, 3)
        hl_x, hl_y = cx - radius * 2 // 5, cy - radius * 2 // 5
        pygame.draw.circle(screen, (150, 145, 140), (hl_x, hl_y), hl_r)
        pygame.draw.circle(screen, (195, 190, 185), (hl_x + 1, hl_y + 1), hl_r // 2)

    else:  # 白子 - 陶瓷质感
        # 外层柔和阴影
        for i in range(3):
            offset = 3 - i
            shadow_alpha = 35 - i * 10
            s = pygame.Surface((radius * 2 + 6, radius * 2 + 6), pygame.SRCALPHA)
            pygame.draw.circle(s, (0, 0, 0, shadow_alpha),
                               (radius + 3, radius + 3 + offset), radius + 1)
            screen.blit(s, (cx - radius - 3, cy - radius - 3))

        # 底层阴影
        pygame.draw.circle(screen, (160, 155, 145), (cx + 2, cy + 2), radius)
        # 主体
        pygame.draw.circle(screen, (215, 212, 205), (cx, cy), radius)
        # 渐变层次
        for i, clr in enumerate([(228, 226, 220), (238, 236, 230), (248, 246, 242), (253, 252, 250)]):
            r = radius - i * 3
            if r > 0:
                pygame.draw.circle(screen, clr, (cx - 1, cy - 1), r)
        # 边框
        pygame.draw.circle(screen, (165, 162, 155), (cx, cy), radius, 1)
        # 高光
        hl_r = max(radius // 3, 3)
        hl_x, hl_y = cx - radius * 2 // 5, cy - radius * 2 // 5
        pygame.draw.circle(screen, (255, 255, 255), (hl_x, hl_y), hl_r)
        pygame.draw.circle(screen, (255, 255, 255), (hl_x + 1, hl_y + 1), hl_r // 3)


def draw_pieces(screen, board):
    """遍历棋盘绘制所有棋子"""
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col] != 0:
                draw_piece(screen, row, col, board[row][col])


def draw_winning_highlight(screen, winning_line, anim_frame):
    """在获胜连子上绘制脉冲高亮效果"""
    if not winning_line:
        return

    pulse = 0.55 + math.sin(anim_frame * 0.12) * 0.45
    glow_alpha = int(160 + 80 * math.sin(anim_frame * 0.09))

    for row, col in winning_line:
        cx, cy = board_to_pixel(row, col)
        radius = CELL_SIZE // 2

        # 外层金色光晕
        glow_r = int(radius * (1.2 + pulse * 0.25))
        s_outer = pygame.Surface((glow_r * 2 + 6, glow_r * 2 + 6), pygame.SRCALPHA)
        for i in range(4):
            r = glow_r - i * 2
            alpha = max(0, glow_alpha - i * 30)
            pygame.draw.circle(s_outer, (*COLOR_WIN_HIGHLIGHT, alpha),
                               (glow_r + 3, glow_r + 3), max(0, r))
        screen.blit(s_outer, (cx - glow_r - 3, cy - glow_r - 3))

    # 红色内芯闪烁（在所有棋子上叠加）
    for row, col in winning_line:
        cx, cy = board_to_pixel(row, col)
        inner_r = max(CELL_SIZE // 2 - 4, 4)
        inner_alpha = int(100 + 60 * math.sin(anim_frame * 0.1 + row + col))
        s_inner = pygame.Surface((inner_r * 2 + 2, inner_r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(s_inner, (*COLOR_WIN_GLOW, inner_alpha),
                           (inner_r + 1, inner_r + 1), inner_r)
        screen.blit(s_inner, (cx - inner_r - 1, cy - inner_r - 1))


# ===================== 悬停预览 =====================

def draw_hover_preview(screen, board, current_player, mouse_pos):
    """鼠标悬停时在空交叉点绘制半透明预览棋子"""
    mx, my = mouse_pos
    pos = pixel_to_board(mx, my)
    if pos is None:
        return
    row, col = pos
    if board[row][col] != 0:
        return
    cx, cy = board_to_pixel(row, col)
    radius = CELL_SIZE // 2 - 2
    s = pygame.Surface((radius * 2 + 6, radius * 2 + 6), pygame.SRCALPHA)
    if current_player == 1:
        pygame.draw.circle(s, (35, 35, 35, 130), (radius + 3, radius + 3), radius)
    else:
        pygame.draw.circle(s, (240, 238, 232, 120), (radius + 3, radius + 3), radius)
        pygame.draw.circle(s, (170, 168, 162, 120), (radius + 3, radius + 3), radius, 1)
    screen.blit(s, (cx - radius - 3, cy - radius - 3))


# ===================== 按钮工具 =====================

def draw_button(screen, rect, text, normal_color, hover_color, font=None):
    """
    绘制一个圆角矩形按钮，带阴影和悬停高亮效果。
    """
    mx, my = pygame.mouse.get_pos()
    hovered = rect.collidepoint(mx, my)

    if hovered:
        # 悬停时：轻微放大 + 发光阴影
        shadow_rect = rect.inflate(4, 4)
        s = pygame.Surface((shadow_rect.w, shadow_rect.h), pygame.SRCALPHA)
        pygame.draw.rect(s, (*hover_color, 80), s.get_rect(), border_radius=10)
        screen.blit(s, shadow_rect.topleft)
        color = hover_color
    else:
        # 正常时：微阴影
        shadow_rect = pygame.Rect(rect.x + 1, rect.y + 2, rect.w, rect.h)
        s = pygame.Surface((shadow_rect.w, shadow_rect.h), pygame.SRCALPHA)
        pygame.draw.rect(s, (0, 0, 0, 30), s.get_rect(), border_radius=8)
        screen.blit(s, shadow_rect.topleft)
        color = normal_color

    pygame.draw.rect(screen, color, rect, border_radius=8)

    if font is None:
        font = get_font(14, bold=True)
    draw_text_centered(screen, text, font, (255, 252, 245),
                       rect.centerx, rect.centery)


# ===================== 右侧控制面板 =====================

def draw_right_panel(screen, current_player, step_count, game_over,
                     winner_text, message, game_mode="pvp", difficulty=None):
    """
    绘制右侧完整控制面板。
    """
    panel_y = RIGHT_PANEL_Y
    panel_h = RIGHT_PANEL_H

    # ---- 面板底板 ----
    panel_rect = pygame.Rect(RIGHT_PANEL_X, panel_y, RIGHT_PANEL_W, panel_h)

    # 面板阴影（向右偏移，与棋盘阴影方向一致）
    shadow_r = pygame.Rect(RIGHT_PANEL_X + 4, panel_y + 4, RIGHT_PANEL_W, panel_h)
    s = pygame.Surface((shadow_r.w, shadow_r.h), pygame.SRCALPHA)
    pygame.draw.rect(s, (0, 0, 0, 28), s.get_rect(), border_radius=10)
    screen.blit(s, shadow_r.topleft)

    pygame.draw.rect(screen, COLOR_PANEL_BG, panel_rect, border_radius=10)
    pygame.draw.rect(screen, COLOR_PANEL_BORDER, panel_rect, border_radius=10, width=2)

    # 面板内容边距
    px = RIGHT_PANEL_X + BTN_PANEL_MARGIN_X
    pw = RIGHT_PANEL_W - BTN_PANEL_MARGIN_X * 2
    py = panel_y + 18

    # ---- 标题 ----
    title_font = get_font(19, bold=True)
    draw_text_centered(screen, "控制面板", title_font,
                       COLOR_TEXT, RIGHT_PANEL_X + RIGHT_PANEL_W // 2, py + 6)
    py += 34

    # 分隔线
    line_color = (190, 170, 140)
    pygame.draw.line(screen, line_color, (px, py), (px + pw, py), 1)
    py += 14

    # ---- 对战模式 ----
    mode_label_font = get_font(12)
    mode_val_font = get_font(14, bold=True)
    mode_label = mode_label_font.render("对战模式", True, COLOR_TEXT_LIGHT)
    screen.blit(mode_label, (px, py))
    py += 18

    mode_display = "双人对战" if game_mode == "pvp" else "人机对战"
    mode_color = COLOR_TEXT if game_mode == "pvp" else (42, 82, 165)
    mode_value = mode_val_font.render(mode_display, True, mode_color)
    screen.blit(mode_value, (px + 2, py))
    py += 24

    # 人机模式：显示当前难度
    if game_mode == "pve" and difficulty is not None:
        diff_font = get_font(11)
        diff_name = DIFFICULTY_NAMES.get(difficulty, "中等")
        diff_label = diff_font.render(f"难度：{diff_name}", True, (125, 78, 135))
        screen.blit(diff_label, (px + 2, py))
    py += 26

    # 分隔线
    pygame.draw.line(screen, line_color, (px, py), (px + pw, py), 1)
    py += 14

    # ---- 当前回合 ----
    turn_label_font = get_font(12)
    turn_val_font = get_font(14, bold=True)
    turn_label = turn_label_font.render("当前回合", True, COLOR_TEXT_LIGHT)
    screen.blit(turn_label, (px, py))
    py += 18

    # 棋子指示器：控制半径不超出面板内容区
    dot_radius = 9
    dot_cx = px + dot_radius + 2   # 圆心距左边距留余量
    dot_cy = py + dot_radius + 2

    if game_over:
        winner = "黑棋" if "黑" in winner_text else "白棋"
        dot_color = COLOR_BLACK_BASE if "黑" in winner_text else COLOR_WHITE_BASE
        is_white_winner = "白" in winner_text
    else:
        dot_color = COLOR_BLACK_BASE if current_player == 1 else COLOR_WHITE_BASE
        is_white_winner = current_player == 2

    # 阴影 + 主体棋子
    s_dot = pygame.Surface((dot_radius * 2 + 4, dot_radius * 2 + 4), pygame.SRCALPHA)
    pygame.draw.circle(s_dot, (0, 0, 0, 35), (dot_radius + 2, dot_radius + 3), dot_radius)
    screen.blit(s_dot, (dot_cx - dot_radius - 2, dot_cy - dot_radius - 2))

    pygame.draw.circle(screen, dot_color, (dot_cx, dot_cy), dot_radius)
    if is_white_winner:
        pygame.draw.circle(screen, COLOR_WHITE_BORDER, (dot_cx, dot_cy), dot_radius, 1)

    # 回合文字
    text_x = dot_cx + dot_radius + 8
    text_y = dot_cy - dot_radius // 2
    if game_over:
        turn_text = turn_val_font.render(f"{winner}（胜）", True, COLOR_ACCENT)
    else:
        player_text = "黑棋" if current_player == 1 else "白棋"
        turn_text = turn_val_font.render(f"{player_text} 落子", True, COLOR_TEXT)
    screen.blit(turn_text, (text_x, text_y))
    py += dot_radius * 2 + 10

    # 分隔线
    pygame.draw.line(screen, line_color, (px, py), (px + pw, py), 1)
    py += 14

    # ---- 步数 ----
    step_label = get_font(12).render("步数统计", True, COLOR_TEXT_LIGHT)
    screen.blit(step_label, (px, py))
    py += 18
    step_value = get_font(14, bold=True).render(f"{step_count} 手", True, COLOR_TEXT)
    screen.blit(step_value, (px + 2, py))
    py += 30

    # 分隔线
    pygame.draw.line(screen, line_color, (px, py), (px + pw, py), 1)
    py += 14

    # ---- 提示 / 胜利信息 ----
    if message:
        if game_over:
            info_font = get_font(13, bold=True)
            info_surf = info_font.render(message, True, COLOR_ACCENT)
            info_rect = info_surf.get_rect(
                center=(RIGHT_PANEL_X + RIGHT_PANEL_W // 2, py + 10)
            )
            bg_rect = info_rect.inflate(14, 8)
            bg_surf = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            bg_surf.fill((255, 235, 220, 200))
            pygame.draw.rect(bg_surf, (255, 180, 140, 100),
                             bg_surf.get_rect(), border_radius=6, width=1)
            screen.blit(bg_surf, bg_rect.topleft)
            screen.blit(info_surf, info_rect)
        else:
            info_font = get_font(11)
            info_surf = info_font.render(message, True, COLOR_ACCENT)
            screen.blit(info_surf, (px, py))

    # ---- 操作区外框 ----
    btn_w = pw - BTN_BOX_PADDING * 2
    box_h = (BTN_HEIGHT * BTN_COUNT
             + BTN_SPACING * (BTN_COUNT - 1)
             + BTN_BOX_PADDING * 2)
    box_y = panel_y + panel_h - box_h - BTN_BOX_MARGIN_BOTTOM

    box_rect = pygame.Rect(px, box_y, pw, box_h)
    # 操作区底板
    pygame.draw.rect(screen, (228, 218, 200), box_rect, border_radius=10)
    pygame.draw.rect(screen, (190, 170, 140), box_rect, border_radius=10, width=1)

    # 四个按钮垂直排列
    btn_start_y = box_y + BTN_BOX_PADDING
    btn_start_x = px + BTN_BOX_PADDING
    btn_font = get_font(13, bold=True)

    # 返回选择按钮
    mode_btn_color = (138, 118, 98)
    mode_btn_hover = (160, 138, 112)
    mode_label_text = "返回选择"

    rect_mode = pygame.Rect(btn_start_x, btn_start_y, btn_w, BTN_HEIGHT)
    draw_button(screen, rect_mode, mode_label_text, mode_btn_color, mode_btn_hover, btn_font)

    rect_restart = pygame.Rect(btn_start_x, btn_start_y + (BTN_HEIGHT + BTN_SPACING), btn_w, BTN_HEIGHT)
    draw_button(screen, rect_restart, "再来一局 (R)",
                COLOR_BTN_RESTART, COLOR_BTN_RESTART_HOVER, btn_font)

    rect_undo = pygame.Rect(btn_start_x, btn_start_y + (BTN_HEIGHT + BTN_SPACING) * 2, btn_w, BTN_HEIGHT)
    draw_button(screen, rect_undo, "悔    棋",
                COLOR_BTN_UNDO, COLOR_BTN_UNDO_HOVER, btn_font)

    rect_quit = pygame.Rect(btn_start_x, btn_start_y + (BTN_HEIGHT + BTN_SPACING) * 3, btn_w, BTN_HEIGHT)
    draw_button(screen, rect_quit, "退出游戏",
                COLOR_BTN_QUIT, COLOR_BTN_QUIT_HOVER, btn_font)


# ===================== 启动模式选择界面 =====================

def show_difficulty_select_screen(screen, clock):
    """
    选择 AI 难度，返回 DIFFICULTY_EASY / MEDIUM / HARD。
    三张卡片：简单、中等、困难。
    """
    card_w, card_h = 170, 155
    card_gap = 22
    total_w = card_w * 3 + card_gap * 2
    start_x = WINDOW_WIDTH // 2 - total_w // 2
    card_y = WINDOW_HEIGHT // 2 - card_h // 2 + 25

    difficulties = [
        (DIFFICULTY_EASY, "简单", "适合初学者\nAI 偶尔放水", COLOR_BTN_RESTART, COLOR_BTN_RESTART_HOVER, (85, 160, 90)),
        (DIFFICULTY_MEDIUM, "中等", "均衡对抗\n攻守兼备", COLOR_BTN_UNDO, COLOR_BTN_UNDO_HOVER, (195, 145, 60)),
        (DIFFICULTY_HARD, "困难", "高手挑战\n精准计算", COLOR_BTN_QUIT, COLOR_BTN_QUIT_HOVER, (185, 70, 60)),
    ]

    rects = [pygame.Rect(start_x + i * (card_w + card_gap), card_y, card_w, card_h) for i in range(3)]

    choosing = True
    while choosing:
        clock.tick(60)
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i, rect in enumerate(rects):
                    if rect.collidepoint(mx, my):
                        return difficulties[i][0]
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return DIFFICULTY_MEDIUM
                elif event.key == pygame.K_1:
                    return DIFFICULTY_EASY
                elif event.key == pygame.K_2:
                    return DIFFICULTY_MEDIUM
                elif event.key == pygame.K_3:
                    return DIFFICULTY_HARD

        # ---- 绘制 ----
        screen.fill(COLOR_BG)

        # 标题
        title_font = get_font(26, bold=True)
        draw_text_centered(screen, "选择 AI 难度", title_font, COLOR_TEXT,
                           WINDOW_WIDTH // 2, card_y - 65)

        sub_font = get_font(14)
        draw_text_centered(screen, "选择电脑对手的强度", sub_font, COLOR_TEXT_LIGHT,
                           WINDOW_WIDTH // 2, card_y - 36)

        for i, (diff_id, name, desc, color, hover_color, accent_color) in enumerate(difficulties):
            rect = rects[i]
            hovered = rect.collidepoint(mx, my)

            scale = 1.07 if hovered else 1.0
            sw, sh = int(card_w * scale), int(card_h * scale)
            scaled_rect = pygame.Rect(
                rect.centerx - sw // 2, rect.centery - sh // 2, sw, sh
            )

            # 阴影
            shadow_r = scaled_rect.inflate(6, 6)
            s = pygame.Surface((shadow_r.w, shadow_r.h), pygame.SRCALPHA)
            pygame.draw.rect(s, (0, 0, 0, 30), s.get_rect(), border_radius=14)
            screen.blit(s, shadow_r.topleft)

            # 背景
            bg = (252, 246, 232) if hovered else COLOR_PANEL_BG
            pygame.draw.rect(screen, bg, scaled_rect, border_radius=14)
            border = accent_color if hovered else COLOR_PANEL_BORDER
            pygame.draw.rect(screen, border, scaled_rect, border_radius=14,
                             width=3 if hovered else 2)

            # 难度名称
            name_font = get_font(19, bold=True)
            draw_text_centered(screen, name, name_font, COLOR_TEXT,
                               scaled_rect.centerx, scaled_rect.y + 36)

            # 描述文字
            desc_font = get_font(12)
            desc_lines = desc.split("\n")
            for j, line in enumerate(desc_lines):
                draw_text_centered(screen, line, desc_font, COLOR_TEXT_LIGHT,
                                   scaled_rect.centerx, scaled_rect.y + 66 + j * 16)

            # 快捷键提示
            key_font = get_font(18, bold=True)
            key_label = key_font.render(str(i + 1), True, accent_color)
            key_rect = key_label.get_rect(center=(scaled_rect.centerx, scaled_rect.y + card_h - 18))
            screen.blit(key_label, key_rect)

        # 底部提示
        hint_font = get_font(12)
        hint = hint_font.render("点击卡片 或 按 1 / 2 / 3 选择难度  |  Esc 默认中等", True, (170, 150, 120))
        hint_rect = hint.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 30))
        screen.blit(hint, hint_rect)

        pygame.display.flip()


def show_mode_select_screen(screen, clock):
    """
    启动前显示模式选择界面，返回 "pvp" 或 "pve"。
    两个大卡片按钮 + 居中标题，风格与棋盘一致。
    """
    card_w, card_h = 220, 180
    card_gap = 30
    total_w = card_w * 2 + card_gap
    start_x = WINDOW_WIDTH // 2 - total_w // 2
    card_y = WINDOW_HEIGHT // 2 - card_h // 2 + 20

    # 预计算两张卡片的 rect
    rect_pvp = pygame.Rect(start_x, card_y, card_w, card_h)
    rect_pve = pygame.Rect(start_x + card_w + card_gap, card_y, card_w, card_h)

    anim_t = 0.0
    choosing = True

    while choosing:
        dt = clock.tick(60) / 1000.0
        anim_t += dt

        mx, my = pygame.mouse.get_pos()
        hover_pvp = rect_pvp.collidepoint(mx, my)
        hover_pve = rect_pve.collidepoint(mx, my)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if hover_pvp:
                    return "pvp"
                elif hover_pve:
                    return "pve"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return "pvp"
                elif event.key == pygame.K_2:
                    return "pve"

        # ---- 绘制 ----
        screen.fill(COLOR_BG)

        # 标题
        title_font = get_font(28, bold=True)
        title_surf = title_font.render("选择对战模式", True, COLOR_TEXT)
        title_rect = title_surf.get_rect(center=(WINDOW_WIDTH // 2, card_y - 65))
        screen.blit(title_surf, title_rect)

        # 副标题
        sub_font = get_font(14)
        sub_surf = sub_font.render("选择一种模式开始游戏", True, COLOR_TEXT_LIGHT)
        sub_rect = sub_surf.get_rect(center=(WINDOW_WIDTH // 2, card_y - 38))
        screen.blit(sub_surf, sub_rect)

        # 绘制两张卡片
        def draw_mode_card(rect, title, desc, icon_player, is_hover):
            """绘制单张模式选择卡片"""
            # 悬停放大效果
            scale = 1.06 if is_hover else 1.0
            if is_hover:
                scaled_w = int(rect.w * scale)
                scaled_h = int(rect.h * scale)
                scaled_rect = pygame.Rect(
                    rect.centerx - scaled_w // 2,
                    rect.centery - scaled_h // 2,
                    scaled_w, scaled_h,
                )
            else:
                scaled_rect = rect

            # 阴影
            shadow_r = pygame.Rect(scaled_rect.x + 3, scaled_rect.y + 3,
                                   scaled_rect.w, scaled_rect.h)
            s = pygame.Surface((shadow_r.w, shadow_r.h), pygame.SRCALPHA)
            pygame.draw.rect(s, (0, 0, 0, 30), s.get_rect(), border_radius=14)
            screen.blit(s, shadow_r.topleft)

            # 背景
            bg_color = (248, 242, 228) if is_hover else COLOR_PANEL_BG
            pygame.draw.rect(screen, bg_color, scaled_rect, border_radius=14)
            border_color = COLOR_PANEL_BORDER if not is_hover else (140, 105, 65)
            border_w = 2 if not is_hover else 3
            pygame.draw.rect(screen, border_color, scaled_rect, border_radius=14, width=border_w)

            # 顶部图标区 - 棋子预览
            icon_y = scaled_rect.y + 22
            if icon_player == 1:
                # 双人模式：黑白棋子并排
                dot_r = 16
                dot_cx1 = scaled_rect.centerx - 18
                dot_cx2 = scaled_rect.centerx + 18
                dot_cy = icon_y + 16

                s_b = pygame.Surface((dot_r * 2 + 4, dot_r * 2 + 4), pygame.SRCALPHA)
                pygame.draw.circle(s_b, (0, 0, 0, 35), (dot_r + 2, dot_r + 3), dot_r)
                screen.blit(s_b, (dot_cx1 - dot_r - 2, dot_cy - dot_r - 2))
                pygame.draw.circle(screen, COLOR_BLACK_BASE, (dot_cx1, dot_cy), dot_r)

                s_w = pygame.Surface((dot_r * 2 + 4, dot_r * 2 + 4), pygame.SRCALPHA)
                pygame.draw.circle(s_w, (0, 0, 0, 30), (dot_r + 2, dot_r + 3), dot_r)
                screen.blit(s_w, (dot_cx2 - dot_r - 2, dot_cy - dot_r - 2))
                pygame.draw.circle(screen, COLOR_WHITE_BASE, (dot_cx2, dot_cy), dot_r)
                pygame.draw.circle(screen, COLOR_WHITE_BORDER, (dot_cx2, dot_cy), dot_r, 1)
            else:
                # 人机模式：人 vs AI 图标
                dot_r = 16
                dot_cy = icon_y + 16
                dot_cx1 = scaled_rect.centerx - 20
                dot_cx2 = scaled_rect.centerx + 20

                s_b = pygame.Surface((dot_r * 2 + 4, dot_r * 2 + 4), pygame.SRCALPHA)
                pygame.draw.circle(s_b, (0, 0, 0, 35), (dot_r + 2, dot_r + 3), dot_r)
                screen.blit(s_b, (dot_cx1 - dot_r - 2, dot_cy - dot_r - 2))
                pygame.draw.circle(screen, COLOR_BLACK_BASE, (dot_cx1, dot_cy), dot_r)

                # AI 用紫色圆环表示
                s_ai = pygame.Surface((dot_r * 2 + 4, dot_r * 2 + 4), pygame.SRCALPHA)
                pygame.draw.circle(s_ai, (0, 0, 0, 30), (dot_r + 2, dot_r + 3), dot_r)
                screen.blit(s_ai, (dot_cx2 - dot_r - 2, dot_cy - dot_r - 2))
                pygame.draw.circle(screen, (200, 195, 185), (dot_cx2, dot_cy), dot_r)
                pygame.draw.circle(screen, (125, 78, 135), (dot_cx2, dot_cy), dot_r, 2)
                # AI 文字标识
                ai_font = get_font(10, bold=True)
                ai_label = ai_font.render("AI", True, (125, 78, 135))
                ai_lr = ai_label.get_rect(center=(dot_cx2, dot_cy))
                screen.blit(ai_label, ai_lr)

            # 卡片标题
            card_title_font = get_font(17, bold=True)
            draw_text_centered(screen, title, card_title_font, COLOR_TEXT,
                               scaled_rect.centerx, scaled_rect.y + 78)

            # 描述文字
            desc_font = get_font(12)
            desc_lines = desc.split("\n")
            for i, line in enumerate(desc_lines):
                draw_text_centered(screen, line, desc_font, COLOR_TEXT_LIGHT,
                                   scaled_rect.centerx, scaled_rect.y + 102 + i * 16)

            # 底部快捷键提示
            hint_font = get_font(11)
            hint_text = "按 1" if icon_player == 1 else "按 2"
            draw_text_centered(screen, hint_text, hint_font, (170, 150, 120),
                               scaled_rect.centerx, scaled_rect.y + card_h - 18)

        draw_mode_card(
            rect_pvp, "双人对战", "两位玩家轮流落子\n面对面一决胜负",
            icon_player=1, is_hover=hover_pvp,
        )
        draw_mode_card(
            rect_pve, "人机对战", "挑战电脑 AI\n看看你能否战胜它",
            icon_player=2, is_hover=hover_pve,
        )

        # 底部提示
        footer_font = get_font(12)
        footer = footer_font.render("点击卡片 或 按 1 / 2 选择模式", True, (170, 150, 120))
        footer_rect = footer.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 30))
        screen.blit(footer, footer_rect)

        pygame.display.flip()


# ===================== 顶部标题 / 胜利横幅 =====================

def draw_title(screen, winner_text="", anim_frame=0):
    """
    绘制窗口顶部。
    正常显示"优雅五子棋"；胜利时显示动画横幅。
    """
    if winner_text:
        # 动画参数：基于帧数的正弦脉冲
        pulse = 1.0 + math.sin(anim_frame * 0.08) * 0.04
        color_phase = (math.sin(anim_frame * 0.06) + 1) / 2  # 0~1 波动

        banner_y = 2
        banner_h = 36

        # 暗色渐变背景
        banner_surf = pygame.Surface((BOARD_PANEL_W, banner_h), pygame.SRCALPHA)
        for i in range(banner_h):
            alpha = 210 + int(30 * (i / banner_h))
            clr = (40, 15, 5, alpha)
            pygame.draw.line(banner_surf, clr, (0, i), (BOARD_PANEL_W, i))
        screen.blit(banner_surf, (PANEL_X, banner_y))

        # 双层金色边框
        banner_rect = pygame.Rect(PANEL_X, banner_y, BOARD_PANEL_W, banner_h)
        pygame.draw.rect(screen, COLOR_GOLD, banner_rect, border_radius=8, width=2)

        # 脉冲缩放文字
        gold_color = lerp_color((255, 230, 140), (255, 200, 80), color_phase)
        font_size = int(23 * pulse)
        font = get_font(font_size, bold=True)

        # 文字发光底层
        glow_font = get_font(font_size + 2, bold=True)
        draw_text_centered(screen, winner_text, glow_font, (80, 40, 10),
                           PANEL_X + BOARD_PANEL_W // 2 + 1, banner_y + banner_h // 2 + 1)

        draw_text_centered(screen, winner_text, font, gold_color,
                           PANEL_X + BOARD_PANEL_W // 2, banner_y + banner_h // 2)
    else:
        # 正常标题 - 优雅的衬线风格
        font = get_font(24, bold=True)
        # 标题下方装饰线
        title_y = 20
        draw_text_centered(screen, "优雅五子棋", font, COLOR_TEXT,
                           PANEL_X + BOARD_PANEL_W // 2, title_y)
        # 装饰小点
        decor_y = title_y + 16
        for dx in [-30, -15, 0, 15, 30]:
            pygame.draw.circle(screen, COLOR_GOLD,
                               (PANEL_X + BOARD_PANEL_W // 2 + dx, decor_y), 2)


# ===================== 游戏逻辑 =====================

def check_win(board, row, col):
    """
    判断 (row, col) 落子后是否连成五子。
    返回获胜连子位置列表（包含所有连续同色棋子），无胜者返回空列表。
    """
    player = board[row][col]

    for dr, dc in [(0, 1), (1, 0), (1, 1), (1, -1)]:
        pieces = [(row, col)]
        # 正方向
        r, c = row + dr, col + dc
        while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == player:
            pieces.append((r, c))
            r += dr
            c += dc
        # 反方向
        r, c = row - dr, col - dc
        while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == player:
            pieces.append((r, c))
            r -= dr
            c -= dc
        if len(pieces) >= 5:
            return pieces
    return []


# ===================== AI 引擎 =====================

def evaluate_line(board, row, col, player):
    """
    评估某个方向上的连子得分。
    """
    score_map = {
        (5, 0): 100000,
        (5, 1): 100000,
        (5, 2): 100000,
        (4, 2): 5000,
        (4, 1): 1200,
        (3, 2): 800,
        (3, 1): 200,
        (2, 2): 120,
        (2, 1): 30,
        (1, 2): 10,
    }

    total_score = 0
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

    for dr, dc in directions:
        count = 1
        open_ends = 0

        # 正方向
        r, c = row + dr, col + dc
        while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == player:
            count += 1
            r += dr
            c += dc
        if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == 0:
            open_ends += 1

        # 反方向
        r, c = row - dr, col - dc
        while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == player:
            count += 1
            r -= dr
            c -= dc
        if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == 0:
            open_ends += 1

        if count >= 5:
            total_score += 100000
        else:
            total_score += score_map.get((count, open_ends), 0)

    return total_score


def ai_move(board, difficulty=DIFFICULTY_MEDIUM):
    """
    AI 落子决策：防守优先 + 进攻辅助，支持难度分级。
    - 简单：搜索范围小、权重低、有概率随机落子
    - 中等：均衡攻防、标准搜索
    - 困难：扩大搜索、加重权重、位置偏好
    """
    ai_player = 2
    human_player = 1

    # 根据难度设置参数
    if difficulty == DIFFICULTY_EASY:
        search_range = 1
        defense_weight = 0.8
        attack_weight = 1.0
        random_chance = 0.25
    elif difficulty == DIFFICULTY_MEDIUM:
        search_range = 1
        defense_weight = 1.2
        attack_weight = 1.0
        random_chance = 0.0
    else:  # HARD
        search_range = 2
        defense_weight = 1.3
        attack_weight = 1.15
        random_chance = 0.0

    best_score = -1
    best_moves = []

    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col] != 0:
                continue

            # 只考虑已有棋子相邻范围内的空位
            has_neighbor = False
            for dr in range(-search_range, search_range + 1):
                for dc in range(-search_range, search_range + 1):
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = row + dr, col + dc
                    if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and board[nr][nc] != 0:
                        has_neighbor = True
                        break
                if has_neighbor:
                    break
            if not has_neighbor:
                continue

            # 防守评分
            board[row][col] = human_player
            defense_score = evaluate_line(board, row, col, human_player)
            board[row][col] = 0

            # 进攻评分
            board[row][col] = ai_player
            attack_score = evaluate_line(board, row, col, ai_player)
            board[row][col] = 0

            total_score = defense_score * defense_weight + attack_score * attack_weight

            # 困难模式：中心位置偏好
            if difficulty == DIFFICULTY_HARD:
                center = BOARD_SIZE // 2
                dist = abs(row - center) + abs(col - center)
                total_score += max(0, (BOARD_SIZE - dist)) * 1.5

            if total_score > best_score:
                best_score = total_score
                best_moves = [(row, col)]
            elif total_score == best_score:
                best_moves.append((row, col))

    # 简单模式：有概率随机落子
    if difficulty == DIFFICULTY_EASY and random.random() < random_chance:
        if best_moves and len(best_moves) > 2:
            return random.choice(best_moves[:max(1, len(best_moves) // 2)])
        elif best_moves:
            return random.choice(best_moves)

    if not best_moves:
        return (BOARD_SIZE // 2, BOARD_SIZE // 2)

    return random.choice(best_moves)


# ===================== 主函数 =====================

def main():
    """游戏主函数"""
    pygame.init()
    pygame.display.set_caption("优雅五子棋")
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    # ---- 启动模式选择 ----
    game_mode = show_mode_select_screen(screen, clock)
    difficulty = DIFFICULTY_MEDIUM
    if game_mode == "pve":
        difficulty = show_difficulty_select_screen(screen, clock)

    # 游戏状态
    board = [[0] * BOARD_SIZE for _ in range(BOARD_SIZE)]
    current_player = 1
    game_over = False
    message = ""
    message_timer = 0
    winner_text = ""
    winning_line = []         # 胜利连子位置列表
    move_history = []
    ai_thinking = False
    ai_move_result = None
    ai_delay = 0
    frame_count = 0          # 全局帧计数（用于动画）

    def reset_game():
        """重置游戏状态"""
        nonlocal board, current_player, game_over, message, winner_text, winning_line
        nonlocal move_history, message_timer, ai_thinking, ai_move_result, ai_delay
        board = [[0] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        current_player = 1
        game_over = False
        message = ""
        message_timer = 0
        winner_text = ""
        winning_line = []
        move_history = []
        ai_thinking = False
        ai_move_result = None
        ai_delay = 0

    def undo_move():
        """悔棋：撤销最近一步"""
        nonlocal current_player, message, game_over, winner_text, winning_line
        nonlocal message_timer, ai_thinking, ai_move_result, ai_delay
        if not move_history:
            message = "没有棋子可悔"
            message_timer = 120
            return
        if game_mode == "pve" and len(move_history) >= 2:
            for _ in range(2):
                r, c, p = move_history.pop()
                board[r][c] = 0
            current_player = 1
        else:
            row, col, player = move_history.pop()
            board[row][col] = 0
            current_player = player
        message = "已悔棋"
        game_over = False
        winner_text = ""
        winning_line = []
        ai_thinking = False
        ai_move_result = None
        ai_delay = 0
        message_timer = 120

    def back_to_select():
        """返回模式选择界面"""
        nonlocal game_mode, difficulty
        game_mode = show_mode_select_screen(screen, clock)
        if game_mode == "pve":
            difficulty = show_difficulty_select_screen(screen, clock)
        reset_game()

    # 预计算按钮区域（与 draw_right_panel 共享 BTN_* 布局常量）
    def get_btn_rects():
        px = RIGHT_PANEL_X + BTN_PANEL_MARGIN_X
        pw = RIGHT_PANEL_W - BTN_PANEL_MARGIN_X * 2
        btn_w_inner = pw - BTN_BOX_PADDING * 2
        box_h = (BTN_HEIGHT * BTN_COUNT
                 + BTN_SPACING * (BTN_COUNT - 1)
                 + BTN_BOX_PADDING * 2)
        box_y = RIGHT_PANEL_Y + RIGHT_PANEL_H - box_h - BTN_BOX_MARGIN_BOTTOM
        btn_start_y = box_y + BTN_BOX_PADDING
        btn_start_x = px + BTN_BOX_PADDING

        return {
            "mode":    pygame.Rect(btn_start_x, btn_start_y, btn_w_inner, BTN_HEIGHT),
            "restart": pygame.Rect(btn_start_x, btn_start_y + (BTN_HEIGHT + BTN_SPACING), btn_w_inner, BTN_HEIGHT),
            "undo":    pygame.Rect(btn_start_x, btn_start_y + (BTN_HEIGHT + BTN_SPACING) * 2, btn_w_inner, BTN_HEIGHT),
            "quit":    pygame.Rect(btn_start_x, btn_start_y + (BTN_HEIGHT + BTN_SPACING) * 3, btn_w_inner, BTN_HEIGHT),
        }

    btn_rects = get_btn_rects()

    running = True
    while running:
        # ---- 事件处理 ----
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos

                # 按钮点击检测
                if btn_rects["mode"].collidepoint(mx, my):
                    back_to_select()
                    continue
                if btn_rects["restart"].collidepoint(mx, my):
                    reset_game()
                    continue
                if btn_rects["undo"].collidepoint(mx, my):
                    undo_move()
                    continue
                if btn_rects["quit"].collidepoint(mx, my):
                    running = False
                    continue

                # 棋盘落子
                if game_over:
                    continue
                if game_mode == "pve" and current_player == 2:
                    continue

                pos = pixel_to_board(mx, my)
                if pos is None:
                    continue
                row, col = pos

                if board[row][col] != 0:
                    message = "此处已有棋子"
                    message_timer = 120
                    continue

                move_history.append((row, col, current_player))
                board[row][col] = current_player
                message = ""

                win_line = check_win(board, row, col)
                if win_line:
                    winning_line = win_line
                    winner = "黑棋" if current_player == 1 else "白棋"
                    winner_text = f"  {winner} 胜利！"
                    message = f"{winner} 五子连珠！"
                    game_over = True
                else:
                    current_player = 3 - current_player

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_game()

        # ---- AI 自动落子 ----
        if game_mode == "pve" and current_player == 2 and not game_over and not ai_thinking:
            ai_thinking = True
            ai_move_result = ai_move(board, difficulty)
            ai_delay = 30

        if ai_thinking and ai_delay > 0:
            ai_delay -= 1
            if ai_delay == 0 and ai_move_result is not None:
                row, col = ai_move_result
                if board[row][col] == 0:
                    move_history.append((row, col, current_player))
                    board[row][col] = current_player
                    message = ""

                    win_line = check_win(board, row, col)
                    if win_line:
                        winning_line = win_line
                        winner = "黑棋" if current_player == 1 else "白棋"
                        winner_text = f"  {winner} 胜利！"
                        message = f"{winner} 五子连珠！"
                        game_over = True
                    else:
                        current_player = 3 - current_player

                ai_thinking = False
                ai_move_result = None

        # ---- 计算数据 ----
        step_count = sum(row.count(1) + row.count(2) for row in board)
        mouse_pos = pygame.mouse.get_pos()
        frame_count += 1

        # 消息自动清除倒计时
        if message_timer > 0:
            message_timer -= 1
            if message_timer == 0:
                message = ""

        # ---- 绘制渲染 ----
        draw_board(screen)
        if not game_over:
            draw_hover_preview(screen, board, current_player, mouse_pos)
        draw_pieces(screen, board)
        if winning_line:
            draw_winning_highlight(screen, winning_line, frame_count)
        draw_title(screen, winner_text, frame_count)
        draw_right_panel(screen, current_player, step_count,
                         game_over, winner_text, message, game_mode, difficulty)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"游戏启动失败: {e}", file=sys.stderr)
        try:
            pygame.quit()
        except Exception:
            pass
        sys.exit(1)
