import pygame
import random
import math
from collections import deque

# 初始化 Pygame
pygame.init()

# 常數設定
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
        
    def move(self):
        """移動母雞，撞牆停止"""
        new_x = self.x + self.direction[0]
        new_y = self.y + self.direction[1]
        
        # 邊界檢查，撞牆停止
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
        pygame.draw.rect(screen, RED, (self.x, self.y, self.size, self.size))
        # 畫眼睛
        pygame.draw.circle(screen, WHITE, (self.x + 5, self.y + 5), 3)
        pygame.draw.circle(screen, WHITE, (self.x + 15, self.y + 5), 3)

class Chick:
    """小雞類別"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = GRID_SIZE
    
    def update_position(self, x, y):
        self.x = x
        self.y = y
    
    def get_position(self):
        return (self.x, self.y)
    
    def draw(self, screen):
        pygame.draw.rect(screen, YELLOW, (self.x, self.y, self.size, self.size))

class Egg:
    """雞蛋類別"""
    def __init__(self):
        self.x = random.randint(0, (WINDOW_WIDTH // GRID_SIZE) - 1) * GRID_SIZE
        self.y = random.randint(0, (WINDOW_HEIGHT // GRID_SIZE) - 1) * GRID_SIZE
        self.size = GRID_SIZE
    
    def get_position(self):
        return (self.x, self.y)
    
    def draw(self, screen):
        pygame.draw.ellipse(screen, WHITE, (self.x + 2, self.y + 2, self.size - 4, self.size - 4))
        pygame.draw.circle(screen, YELLOW, (self.x + GRID_SIZE // 2, self.y + GRID_SIZE // 2), 6)

class PowerUp:
    """道具類別"""
    def __init__(self, powerup_type):
        self.x = random.randint(0, (WINDOW_WIDTH // GRID_SIZE) - 1) * GRID_SIZE
        self.y = random.randint(0, (WINDOW_HEIGHT // GRID_SIZE) - 1) * GRID_SIZE
        self.size = GRID_SIZE
        self.type = powerup_type
        self.duration = 300  # 效果持續時間 (5秒)
    
    def get_position(self):
        return (self.x, self.y)
    
    def draw(self, screen):
        if self.type == POWERUP_SPEED:
            # 加速道具 - 藍色閃電
            pygame.draw.circle(screen, CYAN, (self.x + GRID_SIZE // 2, self.y + GRID_SIZE // 2), GRID_SIZE // 2)
            pygame.draw.polygon(screen, YELLOW, [
                (self.x + GRID_SIZE // 2, self.y + 3),
                (self.x + GRID_SIZE // 2 + 3, self.y + GRID_SIZE // 2),
                (self.x + GRID_SIZE // 2, self.y + GRID_SIZE // 2 - 2),
                (self.x + GRID_SIZE // 2 - 3, self.y + GRID_SIZE - 3)
            ])
        elif self.type == POWERUP_SCARE:
            # 驅趕道具 - 粉紅色警告
            pygame.draw.circle(screen, PINK, (self.x + GRID_SIZE // 2, self.y + GRID_SIZE // 2), GRID_SIZE // 2)
            # 畫一個驚嘆號
            pygame.draw.circle(screen, RED, (self.x + GRID_SIZE // 2, self.y + 5), 2)
            pygame.draw.rect(screen, RED, (self.x + GRID_SIZE // 2 - 1, self.y + 8, 3, 6))

class Eagle:
    """老鷹類別"""
    def __init__(self, is_special=False):
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
        self.base_speed = 2.5 if is_special else 2.0
        self.speed = self.base_speed
        self.has_caught = False  # 是否已抓到小雞
        self.caught_chick = None  # 被抓到的小雞
        self.spawn_side = side  # 記錄生成位置
        self.leaving = False  # 是否正在離開
    
    def move_towards(self, target_x, target_y, hen_x=None, hen_y=None):
        """向目標位置移動,同時閃避母雞"""
        # 檢查是否需要閃避母雞
        if hen_x is not None and hen_y is not None:
            hen_distance = math.sqrt((hen_x - self.x) ** 2 + (hen_y - self.y) ** 2)
            # 如果母雞太近(小於 3 個格子距離),閃避母雞
            if hen_distance < GRID_SIZE * 3:
                # 計算遠離母雞的方向
                avoid_dx = self.x - hen_x
                avoid_dy = self.y - hen_y
                avoid_distance = math.sqrt(avoid_dx ** 2 + avoid_dy ** 2)
                
                if avoid_distance > 0:
                    # 閃避母雞,往相反方向移動
                    self.x += (avoid_dx / avoid_distance) * self.speed * 1.5
                    self.y += (avoid_dy / avoid_distance) * self.speed * 1.5
                return
        
        # 正常追逐目標
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        
        if distance > 0:
            # 正規化向量並乘以速度
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed
    
    def leave_screen(self):
        """離開螢幕，往生成的邊緣方向移動"""
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
        color = PURPLE if self.is_special else DARK_RED
        pygame.draw.rect(screen, color, (int(self.x), int(self.y), self.size, self.size))
        # 畫翅膀標記
        pygame.draw.polygon(screen, BLACK, [
            (int(self.x), int(self.y + GRID_SIZE // 2)),
            (int(self.x - 5), int(self.y)),
            (int(self.x), int(self.y))
        ])
        pygame.draw.polygon(screen, BLACK, [
            (int(self.x + GRID_SIZE), int(self.y + GRID_SIZE // 2)),
            (int(self.x + GRID_SIZE + 5), int(self.y)),
            (int(self.x + GRID_SIZE), int(self.y))
        ])
        # 如果抓到小雞,繪製小雞在老鷹下方
        if self.caught_chick:
            pygame.draw.rect(screen, YELLOW, (int(self.x), int(self.y + GRID_SIZE), self.size, self.size))

class Game:
    """遊戲主類別"""
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("老鷹抓小雞")
        self.clock = pygame.time.Clock()
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
        # 20% 機率生成特殊老鷹
        is_special = random.random() < 0.2
        eagle = Eagle(is_special)
        eagle.speed = eagle.base_speed * self.difficulty_multiplier
        self.eagles.append(eagle)
    
    def spawn_powerup(self):
        """生成道具"""
        # 隨機選擇道具類型
        powerup_type = random.choice([POWERUP_SPEED, POWERUP_SCARE])
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
        
        # 更新小雞位置
        if len(self.position_history) > GRID_SIZE:
            for i, chick in enumerate(self.chicks):
                # 每隻小雞跟隨前一個位置
                history_index = -(i + 1) * GRID_SIZE
                if abs(history_index) <= len(self.position_history):
                    pos = self.position_history[history_index]
                    chick.update_position(pos[0], pos[1])
        
        # 檢查母雞吃蛋
        for egg in self.eggs[:]:
            if self.check_collision(current_pos, egg.get_position()):
                self.eggs.remove(egg)
                self.score += 1
                self.update_difficulty()
                # 添加新小雞
                self.chicks.append(Chick(current_pos[0], current_pos[1]))
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
            elif not eagle.has_caught:
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
                
                # 傳遞母雞位置讓老鷹可以閃避
                hen_pos = self.hen.get_position()
                eagle.move_towards(target_pos[0], target_pos[1], hen_pos[0], hen_pos[1])
                
                # 檢查老鷹抓小雞
                for chick in self.chicks[:]:
                    if self.check_collision(eagle.get_position(), chick.get_position(), GRID_SIZE):
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
        self.screen.fill(GREEN)
        
        # 繪製雞蛋
        for egg in self.eggs:
            egg.draw(self.screen)
        
        # 繪製道具
        for powerup in self.powerups:
            powerup.draw(self.screen)
        
        # 繪製小雞
        for chick in self.chicks:
            chick.draw(self.screen)
        
        # 繪製母雞
        self.hen.draw(self.screen)
        
        # 繪製老鷹
        for eagle in self.eagles:
            eagle.draw(self.screen)
        
        # 繪製 UI
        score_text = self.font.render(f"分數: {self.score}", True, BLACK)
        chicks_text = self.font.render(f"小雞: {len(self.chicks)}", True, BLACK)
        difficulty_text = self.small_font.render(f"難度: x{self.difficulty_multiplier:.1f}", True, BLACK)
        
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(chicks_text, (10, 50))
        self.screen.blit(difficulty_text, (10, 90))
        
        # 顯示活躍道具效果
        y_offset = 120
        if POWERUP_SPEED in self.active_powerups:
            speed_text = self.small_font.render(f"加速: {self.active_powerups[POWERUP_SPEED] // 60 + 1}秒", True, CYAN)
            self.screen.blit(speed_text, (10, y_offset))
            y_offset += 30
        if POWERUP_SCARE in self.active_powerups:
            scare_text = self.small_font.render("驅趕中!", True, PINK)
            self.screen.blit(scare_text, (10, y_offset))
        
        # 遊戲結束畫面
        if self.game_over:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            game_over_text = self.font.render("遊戲結束!", True, RED)
            final_score_text = self.font.render(f"最終分數: {self.score}", True, WHITE)
            restart_text = self.small_font.render("按 R 重新開始", True, WHITE)
            
            self.screen.blit(game_over_text, (WINDOW_WIDTH // 2 - 80, WINDOW_HEIGHT // 2 - 60))
            self.screen.blit(final_score_text, (WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 - 20))
            self.screen.blit(restart_text, (WINDOW_WIDTH // 2 - 80, WINDOW_HEIGHT // 2 + 20))
        
        pygame.display.flip()
    
    def handle_input(self):
        """處理輸入"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
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
