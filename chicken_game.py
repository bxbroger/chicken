import pygame
import random
import math
from collections import deque

# 初始化 Pygame
pygame.init()

# 常數設定 - 基準解析度
BASE_WIDTH = 800
BASE_HEIGHT = 600
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
GRID_SIZE = 20

# 顏色定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
DARK_RED = (139, 0, 0)
CYAN = (0, 255, 255)
PINK = (255, 192, 203)

# 道具類型
POWERUP_SPEED = "speed"  # 加速道具
POWERUP_SCARE = "scare"  # 驅趕老鷹
POWERUP_SHIELD = "shield"  # 防護罩
POWERUP_FREEZE = "freeze"  # 時間凍結

# Boids 演算法參數
BOID_SEPARATION_DISTANCE = GRID_SIZE * 1.2  # 分離距離(減少讓小雞可以更靠近)
BOID_ALIGNMENT_DISTANCE = GRID_SIZE * 4   # 對齊距離
BOID_COHESION_DISTANCE = GRID_SIZE * 5    # 凝聚距離
BOID_SEPARATION_WEIGHT = 1.2  # 分離權重(減少以允許更近)
BOID_ALIGNMENT_WEIGHT = 1.0   # 對齊權重
BOID_COHESION_WEIGHT = 1.0    # 凝聚權重

class Hen:
    """母雞類別"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = [0, 0]  # 初始靜止
        self.size = GRID_SIZE
        self.base_speed = 3  # 基礎速度
        self.speed = self.base_speed
        self.speed_boost = 1.0  # 速度倍率
        self.animation_frame = 0  # 動畫幀計數器
        self.wing_offset = 0  # 翅膀擺動偏移
        self.facing_right = True  # 面向方向
        
    def move(self):
        """移動母雞,撞牆停止"""
        new_x = self.x + self.direction[0]
        new_y = self.y + self.direction[1]
        
        # 邊界檢查,撞牆停止
        if new_x < 0:
            self.x = 0
        elif new_x >= WINDOW_WIDTH - self.size:
            self.x = WINDOW_WIDTH - self.size
        else:
            self.x = new_x
            
        if new_y < 0:
            self.y = 0
        elif new_y >= WINDOW_HEIGHT - self.size:
            self.y = WINDOW_HEIGHT - self.size
        else:
            self.y = new_y
        
        # 更新動畫
        if self.direction[0] != 0 or self.direction[1] != 0:
            self.animation_frame += 1
            self.wing_offset = math.sin(self.animation_frame * 0.3) * 3
            # 根據水平移動方向更新面向
            if abs(self.direction[0]) > 0.1:
                self.facing_right = self.direction[0] > 0
    
    def change_direction(self, direction):
        """改變方向"""
        effective_speed = self.speed * self.speed_boost
        if direction == "UP":
            self.direction = [0, -effective_speed]
        elif direction == "DOWN":
            self.direction = [0, effective_speed]
        elif direction == "LEFT":
            self.direction = [-effective_speed, 0]
        elif direction == "RIGHT":
            self.direction = [effective_speed, 0]
        elif direction == "STOP":
            self.direction = [0, 0]
    
    def get_position(self):
        return (self.x, self.y)
    
    def draw(self, screen):
        # 計算方向偏移
        direction = 1 if self.facing_right else -1
        center_x = self.x + self.size * 0.5
        
        # 身體 (橢圓形,上下輕微擺動,使用白色)
        body_bounce = math.sin(self.animation_frame * 0.2) * 1
        body_color = (255, 255, 255)  # 白色身體
        pygame.draw.ellipse(screen, body_color, (self.x, self.y + 4 + body_bounce, self.size, self.size - 4))
        # 身體陰影
        pygame.draw.ellipse(screen, (220, 220, 220), (self.x + 2, self.y + 6 + body_bounce, self.size - 4, self.size - 6))
        
        # 頭部 (圓形,使用淺色)
        head_color = (255, 220, 200)  # 淺膚色頭部
        pygame.draw.circle(screen, head_color, (int(center_x), int(self.y + 6 + body_bounce)), 7)
        # 頭部輪廓
        pygame.draw.circle(screen, (200, 160, 140), (int(center_x), int(self.y + 6 + body_bounce)), 7, 1)
        
        # 雞冠 (鋸齒狀,隨頭部擺動,鮮紅色)
        comb_points = [
            (center_x - 2 * direction, self.y + 2 + body_bounce),
            (center_x - 1 * direction, self.y - 2 + body_bounce),
            (center_x, self.y + 1 + body_bounce),
            (center_x + 1 * direction, self.y - 2 + body_bounce),
            (center_x + 2 * direction, self.y + 2 + body_bounce)
        ]
        pygame.draw.polygon(screen, RED, comb_points)
        pygame.draw.polygon(screen, DARK_RED, comb_points, 1)
        
        # 眼睛位置(根據方向調整,顯示在面向側)
        if self.facing_right:
            eye_x = center_x + 4
        else:
            eye_x = center_x - 4
        eye_y = self.y + 5 + body_bounce
        
        # 眼睛外圈 (白色)
        pygame.draw.circle(screen, WHITE, (int(eye_x), int(eye_y)), 4)
        # 眼珠 (黑色)
        pygame.draw.circle(screen, BLACK, (int(eye_x), int(eye_y)), 2)
        
        # 嘴巴 (橘色三角形,根據方向調整,更大更明顯)
        beak_tip_x = center_x + (6 * direction)
        beak_base_y_top = self.y + 8 + body_bounce
        beak_base_y_bottom = self.y + 11 + body_bounce
        beak_points = [
            (center_x + (1 * direction), beak_base_y_top),
            (beak_tip_x, self.y + 9.5 + body_bounce),
            (center_x + (1 * direction), beak_base_y_bottom)
        ]
        pygame.draw.polygon(screen, ORANGE, beak_points)
        # 嘴巴輪廓(較暗的橘色)
        pygame.draw.polygon(screen, (200, 120, 0), beak_points, 1)
        
        # 翅膀 (白色橢圓,上下擺動,根據方向顯示)
        wing_color = (255, 255, 255)  # 白色翅膀
        wing_shadow = (220, 220, 220)  # 翅膀陰影
        if self.facing_right:
            # 面向右側:左翅在背後,右翅在前面
            pygame.draw.ellipse(screen, wing_shadow, (self.x + 2, self.y + 8 + body_bounce + self.wing_offset, 6, 8))  # 左翅(背後,較暗)
            pygame.draw.ellipse(screen, wing_color, (self.x + self.size - 8, self.y + 8 + body_bounce - self.wing_offset, 6, 8))  # 右翅(前面)
        else:
            # 面向左側:右翅在背後,左翅在前面
            pygame.draw.ellipse(screen, wing_shadow, (self.x + self.size - 8, self.y + 8 + body_bounce + self.wing_offset, 6, 8))  # 右翅(背後,較暗)
            pygame.draw.ellipse(screen, wing_color, (self.x + 2, self.y + 8 + body_bounce - self.wing_offset, 6, 8))  # 左翅(前面)

class Chick:
    """小雞類別"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = GRID_SIZE
        self.animation_frame = 0  # 動畫幀計數器
        self.hop_offset = 0  # 跳躍偏移
        # Boids 速度向量(增加初始隨機速度)
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(-1, 1)
        self.max_speed = 2.5  # 增加最大速度
        self.max_force = 0.4  # 增加最大力量
        # 額外動畫屬性
        self.facing_right = True  # 面向方向
        self.wing_offset = 0  # 翅膀擺動
        self.blink_timer = 0  # 眼睛眨眼計時器
        self.is_blinking = False  # 是否正在眨眼
    
    def update_position(self, x, y):
        self.x = x
        self.y = y
        # 更新動畫
        self.animation_frame += 1
        self.hop_offset = abs(math.sin(self.animation_frame * 0.4)) * 2
    
    def apply_boids(self, chicks, hen_pos, speed_multiplier=1.0):
        """應用 Boids 演算法"""
        separation = self.separation(chicks)
        alignment = self.alignment(chicks)
        cohesion = self.cohesion(hen_pos)  # 向母雞聚集
        
        # 應用力
        self.vx += separation[0] + alignment[0] + cohesion[0]
        self.vy += separation[1] + alignment[1] + cohesion[1]
        
        # 限制速度
        speed = math.sqrt(self.vx ** 2 + self.vy ** 2)
        effective_max_speed = self.max_speed * speed_multiplier
        if speed > effective_max_speed:
            self.vx = (self.vx / speed) * effective_max_speed
            self.vy = (self.vy / speed) * effective_max_speed
        
        # 更新位置
        self.x += self.vx
        self.y += self.vy
        
        # 邊界檢查
        self.x = max(0, min(self.x, WINDOW_WIDTH - self.size))
        self.y = max(0, min(self.y, WINDOW_HEIGHT - self.size))
        
        # 更新動畫
        self.animation_frame += 1
        # 更快的跳躍節奏
        self.hop_offset = abs(math.sin(self.animation_frame * 0.5)) * 3
        # 翅膀擺動
        self.wing_offset = math.sin(self.animation_frame * 0.4) * 2
        
        # 根據移動方向更新面向
        if abs(self.vx) > 0.1:
            self.facing_right = self.vx > 0
        
        # 眨眼效果
        self.blink_timer += 1
        if self.blink_timer > 120:  # 每 2 秒眨一次
            self.is_blinking = True
            if self.blink_timer > 125:  # 眨眼持續 5 幀
                self.is_blinking = False
                self.blink_timer = random.randint(0, 60)  # 隨機下次眨眼時間
    
    def separation(self, chicks):
        """分離:避免與其他小雞靠太近"""
        steer_x, steer_y = 0, 0
        count = 0
        
        for other in chicks:
            if other is self:
                continue
            
            dist = math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)
            if dist > 0 and dist < BOID_SEPARATION_DISTANCE:
                diff_x = self.x - other.x
                diff_y = self.y - other.y
                diff_x /= dist
                diff_y /= dist
                steer_x += diff_x
                steer_y += diff_y
                count += 1
        
        if count > 0:
            steer_x /= count
            steer_y /= count
            # 正規化並應用權重
            length = math.sqrt(steer_x ** 2 + steer_y ** 2)
            if length > 0:
                steer_x = (steer_x / length) * self.max_force * BOID_SEPARATION_WEIGHT
                steer_y = (steer_y / length) * self.max_force * BOID_SEPARATION_WEIGHT
        
        return (steer_x, steer_y)
    
    def alignment(self, chicks):
        """對齊:與附近小雞的平均速度對齊"""
        avg_vx, avg_vy = 0, 0
        count = 0
        
        for other in chicks:
            if other is self:
                continue
            
            dist = math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)
            if dist > 0 and dist < BOID_ALIGNMENT_DISTANCE:
                avg_vx += other.vx
                avg_vy += other.vy
                count += 1
        
        if count > 0:
            avg_vx /= count
            avg_vy /= count
            # 正規化並應用權重
            length = math.sqrt(avg_vx ** 2 + avg_vy ** 2)
            if length > 0:
                avg_vx = (avg_vx / length) * self.max_force * BOID_ALIGNMENT_WEIGHT
                avg_vy = (avg_vy / length) * self.max_force * BOID_ALIGNMENT_WEIGHT
            return (avg_vx, avg_vy)
        
        return (0, 0)
    
    def cohesion(self, hen_pos):
        """凝聚:向母雞位置移動"""
        target_x, target_y = hen_pos
        desired_x = target_x - self.x
        desired_y = target_y - self.y
        
        dist = math.sqrt(desired_x ** 2 + desired_y ** 2)
        if dist > 0:
            desired_x /= dist
            desired_y /= dist
            desired_x *= self.max_force * BOID_COHESION_WEIGHT
            desired_y *= self.max_force * BOID_COHESION_WEIGHT
        
        return (desired_x, desired_y)
    
    def get_position(self):
        return (self.x, self.y)
    
    def draw(self, screen):
        # 計算方向偏移(左右翻轉)
        direction = 1 if self.facing_right else -1
        center_x = self.x + self.size * 0.5
        
        # 身體 (圓形,輕微跳躍)
        pygame.draw.circle(screen, YELLOW, (int(center_x), int(self.y + self.size * 0.6 - self.hop_offset)), 8)
        # 頭部 (小圓形)
        pygame.draw.circle(screen, YELLOW, (int(center_x), int(self.y + 5 - self.hop_offset)), 5)
        
        # 翅膀 (小橢圓,會擺動) - 根據方向顯示在不同側
        wing_y = self.y + 10 - self.hop_offset + self.wing_offset
        if self.facing_right:
            # 面向右側:左翅在背後,右翅在前面
            pygame.draw.ellipse(screen, (200, 150, 0), (int(center_x - 8), int(wing_y), 5, 6))  # 左翅(背後,較暗)
            pygame.draw.ellipse(screen, ORANGE, (int(center_x + 3), int(wing_y - self.wing_offset), 5, 6))  # 右翅(前面)
        else:
            # 面向左側:右翅在背後,左翅在前面
            pygame.draw.ellipse(screen, (200, 150, 0), (int(center_x + 3), int(wing_y), 5, 6))  # 右翅(背後,較暗)
            pygame.draw.ellipse(screen, ORANGE, (int(center_x - 8), int(wing_y - self.wing_offset), 5, 6))  # 左翅(前面)
        
        # 眼睛位置(根據方向調整,顯示在面向側)
        if self.facing_right:
            eye_x = center_x + 3  # 眼睛在右側
        else:
            eye_x = center_x - 3  # 眼睛在左側
        eye_y = self.y + 4 - self.hop_offset
        
        if not self.is_blinking:
            # 眼睛外圈 (白色)
            pygame.draw.circle(screen, WHITE, (int(eye_x), int(eye_y)), 2)
            # 眼珠 (黑色)
            pygame.draw.circle(screen, BLACK, (int(eye_x), int(eye_y)), 1)
        else:
            # 眨眼時畫線
            pygame.draw.line(screen, BLACK, (int(eye_x - 1), int(eye_y)), (int(eye_x + 1), int(eye_y)), 1)
        
        # 嘴巴 (橘色小三角形,根據方向調整,指向移動方向)
        beak_tip_x = center_x + (4 * direction)
        beak_points = [
            (center_x, self.y + 6 - self.hop_offset),
            (beak_tip_x, self.y + 7 - self.hop_offset),
            (center_x, self.y + 8 - self.hop_offset)
        ]
        pygame.draw.polygon(screen, ORANGE, beak_points)
        
        # 腳 (橘色細線,跳躍時腳會縮短)
        leg_length = 2 - self.hop_offset * 0.3
        leg1_x = center_x - 2
        leg2_x = center_x + 2
        pygame.draw.line(screen, ORANGE, (int(leg1_x), int(self.y + 16 - self.hop_offset)), (int(leg1_x - 2), int(self.y + 16 + leg_length)), 2)
        pygame.draw.line(screen, ORANGE, (int(leg2_x), int(self.y + 16 - self.hop_offset)), (int(leg2_x + 2), int(self.y + 16 + leg_length)), 2)
        pygame.draw.line(screen, ORANGE, (int(leg2_x), int(self.y + 16 - self.hop_offset)), (int(leg2_x + 2), int(self.y + 16 + leg_length)), 2)

class Egg:
    """雞蛋類別"""
    def __init__(self):
        self.x = random.randint(0, (WINDOW_WIDTH // GRID_SIZE) - 1) * GRID_SIZE
        self.y = random.randint(0, (WINDOW_HEIGHT // GRID_SIZE) - 1) * GRID_SIZE
        self.size = GRID_SIZE
    
    def get_position(self):
        return (self.x, self.y)
    
    def draw(self, screen):
        # 外殼 (白色橢圓)
        pygame.draw.ellipse(screen, WHITE, (self.x + 3, self.y + 4, self.size - 6, self.size - 6))
        # 陰影效果 (淺灰色橢圓)
        pygame.draw.ellipse(screen, (220, 220, 220), (self.x + 4, self.y + 5, self.size - 8, self.size - 8))
        # 高光效果 (亮白色小橢圓)
        pygame.draw.ellipse(screen, (255, 255, 255), (self.x + 7, self.y + 6, 4, 3))
        # 蛋黃 (漸層效果)
        pygame.draw.circle(screen, ORANGE, (int(self.x + GRID_SIZE // 2), int(self.y + GRID_SIZE // 2)), 5)
        pygame.draw.circle(screen, YELLOW, (int(self.x + GRID_SIZE // 2), int(self.y + GRID_SIZE // 2)), 4)
        # 蛋黃高光
        pygame.draw.circle(screen, (255, 255, 200), (int(self.x + GRID_SIZE // 2 - 1), int(self.y + GRID_SIZE // 2 - 1)), 2)

class FollowingEgg:
    """跟隨的蛋類別(尚未孵化的蛋)"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = GRID_SIZE
        self.hatch_timer = 300  # 孵化計時器 (5秒)
        self.animation_frame = 0
        self.shake_offset = 0  # 搖晃偏移
    
    def update_position(self, x, y):
        self.x = x
        self.y = y
        self.animation_frame += 1
        # 孵化倒數
        self.hatch_timer -= 1
        # 快要孵化時會搖晃
        if self.hatch_timer < 60:
            self.shake_offset = math.sin(self.animation_frame * 0.5) * 2
        
    def is_ready_to_hatch(self):
        """是否準備好孵化"""
        return self.hatch_timer <= 0
    
    def get_position(self):
        return (self.x, self.y)
    
    def draw(self, screen):
        shake_x = self.shake_offset if self.hatch_timer < 60 else 0
        
        # 外殼 (白色橢圓,會搖晃)
        pygame.draw.ellipse(screen, WHITE, (int(self.x + 3 + shake_x), self.y + 4, self.size - 6, self.size - 6))
        # 陰影效果 (淺灰色橢圓)
        pygame.draw.ellipse(screen, (220, 220, 220), (int(self.x + 4 + shake_x), self.y + 5, self.size - 8, self.size - 8))
        # 高光效果 (亮白色小橢圓)
        pygame.draw.ellipse(screen, (255, 255, 255), (int(self.x + 7 + shake_x), self.y + 6, 4, 3))
        
        # 根據孵化進度顯示不同程度的裂紋
        progress = 1 - (self.hatch_timer / 300)
        crack_color = (120, 120, 120)
        
        if progress > 0.3:  # 30% 進度後開始出現第一條裂紋
            pygame.draw.line(screen, crack_color, 
                           (int(self.x + 10 + shake_x), self.y + 6), 
                           (int(self.x + 10 + shake_x), self.y + 12), 1)
        
        if progress > 0.5:  # 50% 進度後出現第二條裂紋
            pygame.draw.line(screen, crack_color, 
                           (int(self.x + 8 + shake_x), self.y + 8), 
                           (int(self.x + 12 + shake_x), self.y + 10), 1)
        
        if progress > 0.7:  # 70% 進度後出現更多裂紋
            pygame.draw.line(screen, crack_color, 
                           (int(self.x + 12 + shake_x), self.y + 7), 
                           (int(self.x + 14 + shake_x), self.y + 11), 1)
            pygame.draw.line(screen, crack_color, 
                           (int(self.x + 7 + shake_x), self.y + 10), 
                           (int(self.x + 9 + shake_x), self.y + 14), 1)
        
        if progress > 0.85:  # 85% 進度後裂紋變粗且更多
            pygame.draw.line(screen, crack_color, 
                           (int(self.x + 9 + shake_x), self.y + 6), 
                           (int(self.x + 13 + shake_x), self.y + 14), 2)
            pygame.draw.line(screen, crack_color, 
                           (int(self.x + 11 + shake_x), self.y + 5), 
                           (int(self.x + 8 + shake_x), self.y + 13), 2)
            pygame.draw.line(screen, crack_color, 
                           (int(self.x + 6 + shake_x), self.y + 9), 
                           (int(self.x + 14 + shake_x), self.y + 9), 2)

class PowerUp:
    """道具類別"""
    def __init__(self, powerup_type, x=None, y=None):
        if x is not None and y is not None:
            self.x = x
            self.y = y
        else:
            self.x = random.randint(0, (WINDOW_WIDTH // GRID_SIZE) - 1) * GRID_SIZE
            self.y = random.randint(0, (WINDOW_HEIGHT // GRID_SIZE) - 1) * GRID_SIZE
        self.size = GRID_SIZE
        self.type = powerup_type
        self.duration = 300  # 效果持續時間 (5秒)
        self.animation_frame = 0  # 動畫幀計數器
    
    def get_position(self):
        return (self.x, self.y)
    
    def draw(self, screen):
        # 更新動畫
        self.animation_frame += 1
        pulse = abs(math.sin(self.animation_frame * 0.1)) * 3
        
        if self.type == POWERUP_SPEED:
            # 加速道具 - 藍色光環(脈動效果)
            # 外圈光環
            pygame.draw.circle(screen, (0, 200, 255), (int(self.x + GRID_SIZE // 2), int(self.y + GRID_SIZE // 2)), int(GRID_SIZE // 2 + pulse), 2)
            # 內圈填充
            pygame.draw.circle(screen, CYAN, (int(self.x + GRID_SIZE // 2), int(self.y + GRID_SIZE // 2)), GRID_SIZE // 2 - 2)
            # 閃電圖案 (更精緻)
            lightning_points = [
                (self.x + GRID_SIZE // 2 + 1, self.y + 4),
                (self.x + GRID_SIZE // 2 + 4, self.y + GRID_SIZE // 2 - 1),
                (self.x + GRID_SIZE // 2 + 2, self.y + GRID_SIZE // 2 - 1),
                (self.x + GRID_SIZE // 2 + 5, self.y + GRID_SIZE - 5),
                (self.x + GRID_SIZE // 2 - 2, self.y + GRID_SIZE // 2 + 2),
                (self.x + GRID_SIZE // 2, self.y + GRID_SIZE // 2 + 2),
                (self.x + GRID_SIZE // 2 - 3, self.y + 4)
            ]
            pygame.draw.polygon(screen, YELLOW, lightning_points)
            # 閃電邊框
            pygame.draw.polygon(screen, ORANGE, lightning_points, 1)
            # 光暈效果(脈動)
            pygame.draw.circle(screen, (200, 255, 255), (int(self.x + GRID_SIZE // 2 - 2), int(self.y + GRID_SIZE // 2 - 2)), int(3 + pulse * 0.3))
        elif self.type == POWERUP_SCARE:
            # 驅趕道具 - 警告標誌(脈動效果)
            # 外圈光環
            pygame.draw.circle(screen, (255, 150, 180), (int(self.x + GRID_SIZE // 2), int(self.y + GRID_SIZE // 2)), int(GRID_SIZE // 2 + pulse), 2)
            # 內圈填充
            pygame.draw.circle(screen, PINK, (int(self.x + GRID_SIZE // 2), int(self.y + GRID_SIZE // 2)), GRID_SIZE // 2 - 2)
            # 驚嘆號 (更大更明顯,閃爍效果)
            blink = 1 if (self.animation_frame // 15) % 2 == 0 else 0.7
            pygame.draw.circle(screen, (int(RED[0] * blink), 0, 0), (int(self.x + GRID_SIZE // 2), int(self.y + 14)), 2)
            pygame.draw.rect(screen, (int(RED[0] * blink), 0, 0), (int(self.x + GRID_SIZE // 2 - 1.5), int(self.y + 6), 3, 7))
            # 驚嘆號外框
            pygame.draw.circle(screen, DARK_RED, (int(self.x + GRID_SIZE // 2), int(self.y + 14)), 2, 1)
            pygame.draw.rect(screen, DARK_RED, (int(self.x + GRID_SIZE // 2 - 1.5), int(self.y + 6), 3, 7), 1)
            # 光暈效果(脈動)
            pygame.draw.circle(screen, (255, 220, 230), (int(self.x + GRID_SIZE // 2 - 2), int(self.y + GRID_SIZE // 2 - 2)), int(3 + pulse * 0.3))
        elif self.type == POWERUP_SHIELD:
            # 防護罩道具 - 盾牌圖案
            pygame.draw.circle(screen, (100, 100, 255), (int(self.x + GRID_SIZE // 2), int(self.y + GRID_SIZE // 2)), int(GRID_SIZE // 2 + pulse), 2)
            pygame.draw.circle(screen, (200, 200, 255), (int(self.x + GRID_SIZE // 2), int(self.y + GRID_SIZE // 2)), GRID_SIZE // 2 - 2)
            # 十字盾牌標誌
            pygame.draw.rect(screen, WHITE, (int(self.x + GRID_SIZE // 2 - 2), int(self.y + 4), 4, 12))
            pygame.draw.rect(screen, WHITE, (int(self.x + 4), int(self.y + GRID_SIZE // 2 - 2), 12, 4))
            # 光暈效果
            pygame.draw.circle(screen, (180, 180, 255), (int(self.x + GRID_SIZE // 2 - 2), int(self.y + GRID_SIZE // 2 - 2)), int(3 + pulse * 0.3))
        elif self.type == POWERUP_FREEZE:
            # 凍結道具 - 雪花圖案
            pygame.draw.circle(screen, (0, 200, 255), (int(self.x + GRID_SIZE // 2), int(self.y + GRID_SIZE // 2)), int(GRID_SIZE // 2 + pulse), 2)
            pygame.draw.circle(screen, (150, 230, 255), (int(self.x + GRID_SIZE // 2), int(self.y + GRID_SIZE // 2)), GRID_SIZE // 2 - 2)
            # 雪花圖案
            center = (int(self.x + GRID_SIZE // 2), int(self.y + GRID_SIZE // 2))
            pygame.draw.line(screen, WHITE, (center[0] - 6, center[1]), (center[0] + 6, center[1]), 2)
            pygame.draw.line(screen, WHITE, (center[0], center[1] - 6), (center[0], center[1] + 6), 2)
            pygame.draw.line(screen, WHITE, (center[0] - 4, center[1] - 4), (center[0] + 4, center[1] + 4), 2)
            pygame.draw.line(screen, WHITE, (center[0] - 4, center[1] + 4), (center[0] + 4, center[1] - 4), 2)
            # 光暈效果
            pygame.draw.circle(screen, (200, 240, 255), (int(self.x + GRID_SIZE // 2 - 2), int(self.y + GRID_SIZE // 2 - 2)), int(3 + pulse * 0.3))

class Eagle:
    """老鷹類別"""
    def __init__(self, is_special=False, is_hovering=False):
        # 從邊界隨機位置生成
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            self.x = random.randint(0, WINDOW_WIDTH - GRID_SIZE)
            self.y = 0
        elif side == 'bottom':
            self.x = random.randint(0, WINDOW_WIDTH - GRID_SIZE)
            self.y = WINDOW_HEIGHT - GRID_SIZE
        elif side == 'left':
            self.x = 0
            self.y = random.randint(0, WINDOW_HEIGHT - GRID_SIZE)
        else:  # right
            self.x = WINDOW_WIDTH - GRID_SIZE
            self.y = random.randint(0, WINDOW_HEIGHT - GRID_SIZE)
        
        self.size = GRID_SIZE
        self.is_special = is_special
        self.is_hovering = is_hovering  # 是否為盤旋老鷹
        self.base_speed = 1.8 if is_special else 1.2  # 降低起始速度
        self.speed = self.base_speed
        self.has_caught = False  # 是否已抓到小雞
        self.caught_chick = None  # 被抓到的小雞
        self.spawn_side = side  # 記錄生成位置
        self.leaving = False  # 是否正在離開
        self.animation_frame = 0  # 動畫幀計數器
        self.wing_flap = 0  # 翅膀拍打角度
        # Boids 速度向量
        self.vx = 0
        self.vy = 0
        self.max_speed = self.speed
        self.max_force = 0.5
        
        # 盤旋老鷹特有屬性
        if self.is_hovering:
            # 設定盤旋中心點(隨機位置)
            self.hover_center_x = random.randint(GRID_SIZE * 5, WINDOW_WIDTH - GRID_SIZE * 5)
            self.hover_center_y = random.randint(GRID_SIZE * 5, WINDOW_HEIGHT - GRID_SIZE * 5)
            self.hover_radius = random.randint(GRID_SIZE * 3, GRID_SIZE * 6)  # 盤旋半徑
            self.hover_angle = random.uniform(0, math.pi * 2)  # 盤旋角度
            self.hover_timer = random.randint(300, 600)  # 盤旋時間 (5-10秒)
            self.hover_speed = 0.03  # 盤旋角速度
    
    def move_towards(self, target_x, target_y, hen_x=None, hen_y=None, eagles=None):
        """使用 Boids 演算法向目標位置移動"""
        # 更新動畫
        self.animation_frame += 1
        self.wing_flap = math.sin(self.animation_frame * 0.4) * 8
        
        # 計算各種力
        seek_force = self.seek(target_x, target_y)
        avoid_force = self.avoid_hen(hen_x, hen_y) if hen_x is not None else (0, 0)
        separation_force = self.separation_eagles(eagles) if eagles else (0, 0)
        
        # 應用力
        self.vx += seek_force[0] + avoid_force[0] + separation_force[0]
        self.vy += seek_force[1] + avoid_force[1] + separation_force[1]
        
        # 限制速度
        speed = math.sqrt(self.vx ** 2 + self.vy ** 2)
        if speed > self.max_speed:
            self.vx = (self.vx / speed) * self.max_speed
            self.vy = (self.vy / speed) * self.max_speed
        
        # 更新位置
        self.x += self.vx
        self.y += self.vy
    
    def hover_move(self):
        """盤旋移動"""
        # 更新動畫
        self.animation_frame += 1
        self.wing_flap = math.sin(self.animation_frame * 0.3) * 6  # 盤旋時翅膀擺動較慢
        
        # 更新盤旋角度
        self.hover_angle += self.hover_speed
        if self.hover_angle > math.pi * 2:
            self.hover_angle -= math.pi * 2
        
        # 計算盤旋目標位置
        target_x = self.hover_center_x + math.cos(self.hover_angle) * self.hover_radius
        target_y = self.hover_center_y + math.sin(self.hover_angle) * self.hover_radius
        
        # 平滑移動到目標位置
        dx = target_x - self.x
        dy = target_y - self.y
        
        self.x += dx * 0.1
        self.y += dy * 0.1
        
        # 盤旋時間倒數
        self.hover_timer -= 1
        if self.hover_timer <= 0:
            self.leaving = True
    
    def seek(self, target_x, target_y):
        """追逐目標"""
        desired_x = target_x - self.x
        desired_y = target_y - self.y
        
        dist = math.sqrt(desired_x ** 2 + desired_y ** 2)
        if dist > 0:
            desired_x = (desired_x / dist) * self.max_force
            desired_y = (desired_y / dist) * self.max_force
        
        return (desired_x, desired_y)
    
    def avoid_hen(self, hen_x, hen_y):
        """閃避母雞"""
        if hen_x is None or hen_y is None:
            return (0, 0)
        
        hen_distance = math.sqrt((hen_x - self.x) ** 2 + (hen_y - self.y) ** 2)
        # 如果母雞太近(小於 4 個格子距離),強力閃避母雞
        if hen_distance < GRID_SIZE * 4 and hen_distance > 0:
            # 計算遠離母雞的方向
            avoid_x = self.x - hen_x
            avoid_y = self.y - hen_y
            # 距離越近,逃避力量越大
            avoid_strength = (GRID_SIZE * 4 - hen_distance) / (GRID_SIZE * 4)
            avoid_x = (avoid_x / hen_distance) * self.max_force * 3 * (1 + avoid_strength)
            avoid_y = (avoid_y / hen_distance) * self.max_force * 3 * (1 + avoid_strength)
            return (avoid_x, avoid_y)
        
        return (0, 0)
    
    def separation_eagles(self, eagles):
        """與其他老鷹保持距離"""
        steer_x, steer_y = 0, 0
        count = 0
        
        for other in eagles:
            if other is self or other.has_caught:
                continue
            
            dist = math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)
            if dist > 0 and dist < BOID_SEPARATION_DISTANCE * 1.5:
                diff_x = self.x - other.x
                diff_y = self.y - other.y
                diff_x /= dist
                diff_y /= dist
                steer_x += diff_x
                steer_y += diff_y
                count += 1
        
        if count > 0:
            steer_x /= count
            steer_y /= count
            length = math.sqrt(steer_x ** 2 + steer_y ** 2)
            if length > 0:
                steer_x = (steer_x / length) * self.max_force
                steer_y = (steer_y / length) * self.max_force
        
        return (steer_x, steer_y)
    
    def leave_screen(self):
        """離開螢幕,往生成的邊緣方向移動"""
        # 更新動畫
        self.animation_frame += 1
        self.wing_flap = math.sin(self.animation_frame * 0.5) * 10
        
        if self.spawn_side == 'top':
            self.y -= self.speed * 2
        elif self.spawn_side == 'bottom':
            self.y += self.speed * 2
        elif self.spawn_side == 'left':
            self.x -= self.speed * 2
        else:  # right
            self.x += self.speed * 2
    
    def is_off_screen(self):
        """檢查是否已離開螢幕"""
        return (self.x < -GRID_SIZE * 2 or self.x > WINDOW_WIDTH + GRID_SIZE or 
                self.y < -GRID_SIZE * 2 or self.y > WINDOW_HEIGHT + GRID_SIZE)
    
    def get_position(self):
        return (self.x, self.y)
    
    def draw(self, screen):
        # 盤旋老鷹使用不同顏色(灰色)
        if self.is_hovering:
            color = (100, 100, 100)
            wing_color = (80, 80, 80)
        elif self.is_special:
            color = PURPLE
            wing_color = (80, 0, 80)
        else:
            color = DARK_RED
            wing_color = (100, 0, 0)
        
        # 身體 (橢圓形)
        pygame.draw.ellipse(screen, color, (int(self.x + 4), int(self.y + 2), self.size - 8, self.size - 4))
        # 頭部 (圓形)
        pygame.draw.circle(screen, color, (int(self.x + self.size // 2), int(self.y + 4)), 6)
        # 嘴巴 (尖銳的喙)
        beak_points = [
            (int(self.x + self.size // 2), int(self.y + 4)),
            (int(self.x + self.size // 2 - 2), int(self.y + 6)),
            (int(self.x + self.size // 2 + 2), int(self.y + 6))
        ]
        pygame.draw.polygon(screen, ORANGE, beak_points)
        # 眼睛 (銳利的眼神)
        pygame.draw.circle(screen, YELLOW, (int(self.x + self.size // 2 - 2), int(self.y + 3)), 2)
        pygame.draw.circle(screen, YELLOW, (int(self.x + self.size // 2 + 2), int(self.y + 3)), 2)
        pygame.draw.circle(screen, BLACK, (int(self.x + self.size // 2 - 2), int(self.y + 3)), 1)
        pygame.draw.circle(screen, BLACK, (int(self.x + self.size // 2 + 2), int(self.y + 3)), 1)
        # 左翅膀 (更大更細緻,會拍打)
        left_wing = [
            (int(self.x + 3), int(self.y + 8)),
            (int(self.x - 6), int(self.y + 2 + self.wing_flap)),
            (int(self.x - 8), int(self.y + 6 + self.wing_flap)),
            (int(self.x - 5), int(self.y + 12 + self.wing_flap * 0.5)),
            (int(self.x + 2), int(self.y + 10))
        ]
        pygame.draw.polygon(screen, wing_color, left_wing)
        pygame.draw.polygon(screen, BLACK, left_wing, 1)
        # 右翅膀 (拍打方向相反)
        right_wing = [
            (int(self.x + self.size - 3), int(self.y + 8)),
            (int(self.x + GRID_SIZE + 6), int(self.y + 2 - self.wing_flap)),
            (int(self.x + GRID_SIZE + 8), int(self.y + 6 - self.wing_flap)),
            (int(self.x + GRID_SIZE + 5), int(self.y + 12 - self.wing_flap * 0.5)),
            (int(self.x + self.size - 2), int(self.y + 10))
        ]
        pygame.draw.polygon(screen, wing_color, right_wing)
        pygame.draw.polygon(screen, BLACK, right_wing, 1)
        # 爪子 (銳利的爪子)
        pygame.draw.line(screen, BLACK, (int(self.x + 7), int(self.y + self.size - 2)), (int(self.x + 5), int(self.y + self.size + 2)), 2)
        pygame.draw.line(screen, BLACK, (int(self.x + 13), int(self.y + self.size - 2)), (int(self.x + 15), int(self.y + self.size + 2)), 2)
        # 如果抓到小雞,繪製小雞在老鷹爪下(小雞會掙扎)
        if self.caught_chick:
            struggle = math.sin(self.animation_frame * 0.6) * 1.5
            # 小雞身體
            pygame.draw.circle(screen, YELLOW, (int(self.x + self.size * 0.5 + struggle), int(self.y + self.size + 4)), 6)
            # 小雞頭部
            pygame.draw.circle(screen, YELLOW, (int(self.x + self.size * 0.5 + struggle), int(self.y + self.size)), 4)
            # 小雞眼睛 (害怕的表情)
            pygame.draw.circle(screen, BLACK, (int(self.x + self.size * 0.5 - 1 + struggle), int(self.y + self.size - 1)), 1)
            pygame.draw.circle(screen, BLACK, (int(self.x + self.size * 0.5 + 1 + struggle), int(self.y + self.size - 1)), 1)

class Game:
    """遊戲主類別"""
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("老鷹抓小雞")
        self.clock = pygame.time.Clock()
        self.current_width = WINDOW_WIDTH
        self.current_height = WINDOW_HEIGHT
        self.scale_x = 1.0
        self.scale_y = 1.0
        # 使用系統中文字體
        try:
            # Windows 系統使用微軟正黑體或標楷體
            self.font = pygame.font.SysFont('microsoftyahei', 36)
            self.small_font = pygame.font.SysFont('microsoftyahei', 24)
        except:
            # 備用方案：使用其他中文字體
            try:
                self.font = pygame.font.SysFont('kaiti', 36)
                self.small_font = pygame.font.SysFont('kaiti', 24)
            except:
                # 最後備用：使用預設字體（可能不顯示中文）
                self.font = pygame.font.Font(None, 36)
                self.small_font = pygame.font.Font(None, 24)
        self.reset_game()
    
    def reset_game(self):
        """重置遊戲"""
        self.hen = Hen(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        self.chicks = []
        self.following_eggs = []  # 跟隨的蛋列表
        self.position_history = deque(maxlen=1000)  # 存儲位置歷史
        self.eggs = [Egg()]
        self.eagles = []
        self.powerups = []  # 道具列表
        self.active_powerups = {}  # 活躍的道具效果 {type: remaining_time}
        self.score = 0
        self.game_over = False
        self.eagle_spawn_timer = 0
        self.eagle_spawn_interval = 180  # 3 秒 (180 幀)
        self.powerup_spawn_timer = 0
        self.powerup_spawn_interval = 600  # 10 秒 (600 幀)
        self.difficulty_multiplier = 1.0
    
    def spawn_eagle(self):
        """生成老鷹"""
        # 30% 機率生成盤旋老鷹, 20% 機率生成特殊老鷹
        rand = random.random()
        if rand < 0.3:
            # 盤旋老鷹(不會追小雞)
            eagle = Eagle(is_special=False, is_hovering=True)
        elif rand < 0.5:
            # 特殊老鷹(追最近的小雞)
            eagle = Eagle(is_special=True, is_hovering=False)
        else:
            # 普通老鷹(追最後一隻小雞)
            eagle = Eagle(is_special=False, is_hovering=False)
        
        eagle.speed = eagle.base_speed * self.difficulty_multiplier
        self.eagles.append(eagle)
        self.eagles.append(eagle)
    
    def spawn_powerup(self):
        """生成道具"""
        # 隨機選擇道具類型
        powerup_type = random.choice([POWERUP_SPEED, POWERUP_SCARE, POWERUP_SHIELD, POWERUP_FREEZE])
        self.powerups.append(PowerUp(powerup_type))
    
    def activate_powerup(self, powerup_type):
        """啟用道具效果"""
        if powerup_type == POWERUP_SPEED:
            # 母雞加速 2 倍
            self.hen.speed_boost = 2.0
            self.active_powerups[POWERUP_SPEED] = 300  # 5 秒
        elif powerup_type == POWERUP_SCARE:
            # 所有老鷹飛走
            for eagle in self.eagles:
                if not eagle.has_caught:
                    eagle.leaving = True
            self.active_powerups[POWERUP_SCARE] = 60  # 1 秒 (只是標記效果)
        elif powerup_type == POWERUP_SHIELD:
            # 開啟防護罩
            self.active_powerups[POWERUP_SHIELD] = 99999  # 持續直到被消耗
        elif powerup_type == POWERUP_FREEZE:
            # 凍結老鷹 5 秒
            self.active_powerups[POWERUP_FREEZE] = 300  # 5 秒
    
    def update_powerups(self):
        """更新道具效果"""
        # 更新活躍道具效果時間
        for powerup_type in list(self.active_powerups.keys()):
            self.active_powerups[powerup_type] -= 1
            if self.active_powerups[powerup_type] <= 0:
                del self.active_powerups[powerup_type]
                # 效果結束
                if powerup_type == POWERUP_SPEED:
                    self.hen.speed_boost = 1.0
    
    def update_difficulty(self):
        """根據分數更新難度"""
        # 每 5 分提升 10% 速度
        new_multiplier = 1.0 + (self.score // 5) * 0.1
        if new_multiplier != self.difficulty_multiplier:
            self.difficulty_multiplier = new_multiplier
            # 更新現有老鷹的速度
            for eagle in self.eagles:
                eagle.speed = eagle.base_speed * self.difficulty_multiplier
    
    def check_collision(self, pos1, pos2, threshold=GRID_SIZE):
        """檢查碰撞"""
        x1, y1 = pos1
        x2, y2 = pos2
        return abs(x1 - x2) < threshold and abs(y1 - y2) < threshold
    
    def find_nearest_chick(self, eagle_pos):
        """找到最近的小雞"""
        if not self.chicks:
            return self.hen.get_position()
        
        min_distance = float('inf')
        nearest_chick = self.chicks[0]
        
        for chick in self.chicks:
            chick_pos = chick.get_position()
            distance = math.sqrt((eagle_pos[0] - chick_pos[0]) ** 2 + 
                               (eagle_pos[1] - chick_pos[1]) ** 2)
            if distance < min_distance:
                min_distance = distance
                nearest_chick = chick
        
        return nearest_chick.get_position()
    
    def update(self):
        """更新遊戲狀態"""
        if self.game_over:
            return
        
        # 移動母雞
        self.hen.move()
        current_pos = self.hen.get_position()
        self.position_history.append(current_pos)
        
        # 使用 Boids 更新小雞位置
        for chick in self.chicks:
            chick.apply_boids(self.chicks, current_pos, self.hen.speed_boost)
        
        # 更新跟隨的蛋位置
        follow_spacing = 12  # 縮短跟隨距離 (原為 GRID_SIZE = 20)
        if len(self.position_history) > follow_spacing:
            for i, following_egg in enumerate(self.following_eggs[:]):
                # 每個蛋跟隨在小雞之後
                history_index = -(len(self.chicks) + i + 1) * follow_spacing
                if abs(history_index) <= len(self.position_history):
                    pos = self.position_history[history_index]
                    following_egg.update_position(pos[0], pos[1])
                
                # 檢查是否準備好孵化
                if following_egg.is_ready_to_hatch():
                    self.following_eggs.remove(following_egg)
                    
                    # 20% 機率孵化出道具
                    if random.random() < 0.2:
                        powerup_type = random.choice([POWERUP_SPEED, POWERUP_SCARE])
                        # 道具出現在蛋的位置
                        self.powerups.append(PowerUp(powerup_type, following_egg.x, following_egg.y))
                    else:
                        # 孵化成小雞
                        new_chick = Chick(following_egg.x, following_egg.y)
                        self.chicks.append(new_chick)
                        # 孵化成功才算分
                        self.score += 1
                        self.update_difficulty()
        
        # 檢查母雞吃蛋
        for egg in self.eggs[:]:
            if self.check_collision(current_pos, egg.get_position()):
                self.eggs.remove(egg)
                # 添加跟隨的蛋(而非直接變成小雞)
                self.following_eggs.append(FollowingEgg(current_pos[0], current_pos[1]))
                # 生成新雞蛋
                self.eggs.append(Egg())
        
        # 老鷹生成計時器
        self.eagle_spawn_timer += 1
        if self.eagle_spawn_timer >= self.eagle_spawn_interval:
            self.spawn_eagle()
            self.eagle_spawn_timer = 0
        
        # 道具生成計時器
        self.powerup_spawn_timer += 1
        if self.powerup_spawn_timer >= self.powerup_spawn_interval:
            self.spawn_powerup()
            self.powerup_spawn_timer = 0
        
        # 檢查母雞吃道具
        for powerup in self.powerups[:]:
            if self.check_collision(current_pos, powerup.get_position()):
                self.powerups.remove(powerup)
                self.activate_powerup(powerup.type)
        
        # 更新道具效果
        self.update_powerups()
        
        # 更新老鷹位置
        for eagle in self.eagles[:]:
            if eagle.leaving:
                # 如果已經抓到小雞，往邊緣離開
                eagle.leave_screen()
                # 如果離開螢幕，移除老鷹
                if eagle.is_off_screen():
                    self.eagles.remove(eagle)
            elif eagle.is_hovering:
                # 盤旋老鷹只會盤旋,不會追小雞
                # 如果被凍結，不移動
                if POWERUP_FREEZE not in self.active_powerups:
                    eagle.hover_move()
            elif not eagle.has_caught:
                # 如果被凍結，不移動
                if POWERUP_FREEZE not in self.active_powerups:
                    # 如果還沒抓到小雞,繼續追逐
                    if eagle.is_special:
                        # 特殊老鷹追最近的小雞
                        target_pos = self.find_nearest_chick(eagle.get_position())
                    else:
                        # 普通老鷹追最後一隻小雞
                        if self.chicks:
                            target_pos = self.chicks[-1].get_position()
                        else:
                            target_pos = self.hen.get_position()
                    
                    # 傳遞母雞位置和其他老鷹讓老鷹可以使用 Boids
                    hen_pos = self.hen.get_position()
                    eagle.move_towards(target_pos[0], target_pos[1], hen_pos[0], hen_pos[1], self.eagles)
                
                # 檢查老鷹抓小雞
                for chick in self.chicks[:]:
                    if self.check_collision(eagle.get_position(), chick.get_position(), GRID_SIZE):
                        # 檢查是否有防護罩
                        if POWERUP_SHIELD in self.active_powerups:
                            # 消耗防護罩，老鷹被彈開
                            del self.active_powerups[POWERUP_SHIELD]
                            eagle.leaving = True
                            break
                        
                        # 原本的抓小雞邏輯
                        self.chicks.remove(chick)
                        eagle.has_caught = True
                        eagle.caught_chick = chick  # 記錄被抓的小雞
                        eagle.leaving = True
                        # 檢查是否所有小雞都被抓光
                        if len(self.chicks) == 0 and self.score > 0:
                            self.game_over = True
                        break
    
    def draw(self):
        """繪製遊戲畫面"""
        # 建立基準解析度的虛擬畫面
        virtual_screen = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
        virtual_screen.fill(GREEN)
        
        # 繪製雞蛋
        for egg in self.eggs:
            egg.draw(virtual_screen)
        
        # 繪製道具
        for powerup in self.powerups:
            powerup.draw(virtual_screen)
        
        # 繪製跟隨的蛋
        for following_egg in self.following_eggs:
            following_egg.draw(virtual_screen)
        
        # 繪製小雞
        for chick in self.chicks:
            chick.draw(virtual_screen)
        
        # 繪製母雞
        self.hen.draw(virtual_screen)
        
        # 如果有防護罩，繪製防護圈
        if POWERUP_SHIELD in self.active_powerups:
            hen_pos = self.hen.get_position()
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 3
            pygame.draw.circle(virtual_screen, (100, 150, 255), 
                             (int(hen_pos[0] + GRID_SIZE/2), int(hen_pos[1] + GRID_SIZE/2)), 
                             int(GRID_SIZE * 1.5 + pulse), 2)
            pygame.draw.circle(virtual_screen, (150, 200, 255), 
                             (int(hen_pos[0] + GRID_SIZE/2), int(hen_pos[1] + GRID_SIZE/2)), 
                             int(GRID_SIZE * 1.3 + pulse * 0.5), 1)
        
        # 繪製老鷹
        for eagle in self.eagles:
            eagle.draw(virtual_screen)
        
        # 繪製 UI
        score_text = self.font.render(f"分數: {self.score}", True, BLACK)
        chicks_text = self.font.render(f"小雞: {len(self.chicks)}", True, BLACK)
        eggs_text = self.small_font.render(f"孵化中: {len(self.following_eggs)}", True, ORANGE)
        difficulty_text = self.small_font.render(f"難度: x{self.difficulty_multiplier:.1f}", True, BLACK)
        
        virtual_screen.blit(score_text, (10, 10))
        virtual_screen.blit(chicks_text, (10, 50))
        virtual_screen.blit(eggs_text, (10, 90))
        virtual_screen.blit(difficulty_text, (10, 120))
        
        # 顯示活躍道具效果
        y_offset = 150
        if POWERUP_SPEED in self.active_powerups:
            speed_text = self.small_font.render(f"加速: {self.active_powerups[POWERUP_SPEED] // 60 + 1}秒", True, CYAN)
            virtual_screen.blit(speed_text, (10, y_offset))
            y_offset += 30
        if POWERUP_SCARE in self.active_powerups:
            scare_text = self.small_font.render("驅趕中!", True, PINK)
            virtual_screen.blit(scare_text, (10, y_offset))
            y_offset += 30
        if POWERUP_FREEZE in self.active_powerups:
            freeze_text = self.small_font.render(f"凍結: {self.active_powerups[POWERUP_FREEZE] // 60 + 1}秒", True, CYAN)
            virtual_screen.blit(freeze_text, (10, y_offset))
            y_offset += 30
        if POWERUP_SHIELD in self.active_powerups:
            shield_text = self.small_font.render("防護罩啟動", True, (100, 150, 255))
            virtual_screen.blit(shield_text, (10, y_offset))
        
        # 遊戲結束畫面
        if self.game_over:
            overlay = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            virtual_screen.blit(overlay, (0, 0))
            
            game_over_text = self.font.render("遊戲結束!", True, RED)
            final_score_text = self.font.render(f"最終分數: {self.score}", True, WHITE)
            restart_text = self.small_font.render("按 R 重新開始", True, WHITE)
            
            virtual_screen.blit(game_over_text, (BASE_WIDTH // 2 - 80, BASE_HEIGHT // 2 - 60))
            virtual_screen.blit(final_score_text, (BASE_WIDTH // 2 - 100, BASE_HEIGHT // 2 - 20))
            virtual_screen.blit(restart_text, (BASE_WIDTH // 2 - 80, BASE_HEIGHT // 2 + 20))
        
        # 將虛擬畫面縮放到實際視窗大小
        if self.current_width != BASE_WIDTH or self.current_height != BASE_HEIGHT:
            scaled_screen = pygame.transform.scale(virtual_screen, (self.current_width, self.current_height))
            self.screen.blit(scaled_screen, (0, 0))
        else:
            self.screen.blit(virtual_screen, (0, 0))
        
        pygame.display.flip()
    
    def handle_input(self):
        """處理輸入"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.VIDEORESIZE:
                self.current_width = event.w
                self.current_height = event.h
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                self.scale_x = event.w / BASE_WIDTH
                self.scale_y = event.h / BASE_HEIGHT
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.game_over:
                    self.reset_game()
                
                if not self.game_over:
                    if event.key == pygame.K_UP:
                        self.hen.change_direction("UP")
                    elif event.key == pygame.K_DOWN:
                        self.hen.change_direction("DOWN")
                    elif event.key == pygame.K_LEFT:
                        self.hen.change_direction("LEFT")
                    elif event.key == pygame.K_RIGHT:
                        self.hen.change_direction("RIGHT")
        
        return True
    
    def run(self):
        """運行遊戲"""
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
