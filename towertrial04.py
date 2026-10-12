import pygame
import math
import json
import random
from enum import Enum

pygame.init()

# Constants
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 700
GRID_SIZE = 40
MAP_WIDTH = 20
MAP_HEIGHT = 15

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)
DARK_GREEN = (0, 128, 0)
LIGHT_BLUE = (173, 216, 230)
CYAN = (0, 255, 255)
PINK = (255, 192, 203)
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)
DARK_RED = (139, 0, 0)
LIME = (0, 255, 0)
MAGENTA = (255, 0, 255)
CRIMSON = (220, 20, 60)
DARK_PURPLE = (75, 0, 130)

class TowerType(Enum):
    BASIC = "basic"
    RAPID = "rapid"
    HEAVY = "heavy"
    ICE = "ice"
    LASER = "laser"
    EXPLOSIVE = "explosive"
    PLASMA = "plasma"
    QUANTUM = "quantum"
    NUCLEAR = "nuclear"

class EnemyType(Enum):
    BASIC = "basic"
    FAST = "fast"
    TANK = "tank"
    FLYING = "flying"
    STEALTH = "stealth"
    BOSS = "boss"
    ARMORED = "armored"
    REGENERATING = "regenerating"
    SWARM = "swarm"
    MEGA_BOSS = "mega_boss"
    # New formidable enemies
    DESTROYER = "destroyer"  # Can destroy towers
    BERSERKER = "berserker"  # Fast tower destroyer
    TITAN = "titan"         # Super tough every few waves
    DEMON_LORD = "demon_lord" # Ultimate boss every 10 waves

class UpgradeType(Enum):
    DAMAGE = "damage"
    RANGE = "range"
    SPEED = "speed"
    SPECIAL = "special"

class PowerUpType(Enum):
    AIR_STRIKE = "air_strike"
    FREEZE_ALL = "freeze_all"
    DOUBLE_DAMAGE = "double_damage"
    MONEY_BOOST = "money_boost"
    REPAIR_LIVES = "repair_lives"
    TIME_SLOW = "time_slow"
    LIGHTNING_STORM = "lightning_storm"
    NUKE = "nuke"

class PermanentUpgrade(Enum):
    STARTING_MONEY = "starting_money"
    INTEREST_RATE = "interest_rate"
    TOWER_DISCOUNT = "tower_discount"
    DAMAGE_MULTIPLIER = "damage_multiplier"
    RANGE_MULTIPLIER = "range_multiplier"
    SPEED_MULTIPLIER = "speed_multiplier"
    EXTRA_LIVES = "extra_lives"
    WAVE_SKIP = "wave_skip"

class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def distance_to(self, other):
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def normalize(self):
        length = math.sqrt(self.x**2 + self.y**2)
        if length > 0:
            return Vector2(self.x / length, self.y / length)
        return Vector2(0, 0)

def draw_hexagon(surface, color, center, size, border_color=None, border_width=0):
    """Draw a hexagonal shape"""
    points = []
    for i in range(6):
        angle = math.pi / 3 * i
        x = center[0] + size * math.cos(angle)
        y = center[1] + size * math.sin(angle)
        points.append((x, y))
    
    pygame.draw.polygon(surface, color, points)
    if border_color and border_width > 0:
        pygame.draw.polygon(surface, border_color, points, border_width)

def draw_enemy_shape(surface, enemy_type, center, size, color):
    """Draw different shapes for different enemy types"""
    x, y = int(center[0]), int(center[1])
    
    if enemy_type == EnemyType.BASIC:
        pygame.draw.circle(surface, color, (x, y), size)
        pygame.draw.circle(surface, BLACK, (x, y), size, 2)
    elif enemy_type == EnemyType.FAST:
        points = [(x, y - size), (x - size, y + size), (x + size, y + size)]
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, BLACK, points, 2)
    elif enemy_type == EnemyType.TANK:
        rect = pygame.Rect(x - size, y - size, size * 2, size * 2)
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, BLACK, rect, 2)
    elif enemy_type == EnemyType.FLYING:
        points = [(x, y - size), (x + size, y), (x, y + size), (x - size, y)]
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, BLACK, points, 2)
    elif enemy_type == EnemyType.STEALTH:
        points = []
        for i in range(10):
            angle = math.pi / 5 * i
            radius = size if i % 2 == 0 else size // 2
            px = x + radius * math.cos(angle - math.pi / 2)
            py = y + radius * math.sin(angle - math.pi / 2)
            points.append((px, py))
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, BLACK, points, 2)
    elif enemy_type in [EnemyType.BOSS, EnemyType.MEGA_BOSS]:
        draw_hexagon(surface, color, (x, y), size, BLACK, 3)
    elif enemy_type == EnemyType.ARMORED:
        pygame.draw.circle(surface, color, (x, y), size)
        pygame.draw.circle(surface, SILVER, (x, y), size - 2, 3)
        pygame.draw.circle(surface, BLACK, (x, y), size, 2)
    elif enemy_type == EnemyType.REGENERATING:
        pygame.draw.circle(surface, color, (x, y), size)
        pygame.draw.circle(surface, LIME, (x, y), size - 3, 2)
        pygame.draw.circle(surface, BLACK, (x, y), size, 2)
    elif enemy_type == EnemyType.SWARM:
        for offset in [(-3, -3), (3, -3), (0, 3)]:
            sub_x, sub_y = x + offset[0], y + offset[1]
            pygame.draw.circle(surface, color, (sub_x, sub_y), size // 2)
        pygame.draw.circle(surface, BLACK, (x, y), size, 1)
    elif enemy_type == EnemyType.DESTROYER:
        # Menacing spiky destroyer
        outer_points = []
        inner_points = []
        for i in range(8):
            angle = math.pi / 4 * i
            outer_x = x + size * math.cos(angle)
            outer_y = y + size * math.sin(angle)
            inner_x = x + (size * 0.6) * math.cos(angle + math.pi / 8)
            inner_y = y + (size * 0.6) * math.sin(angle + math.pi / 8)
            outer_points.append((outer_x, outer_y))
            inner_points.append((inner_x, inner_y))
        
        spike_points = []
        for i in range(8):
            spike_points.append(outer_points[i])
            spike_points.append(inner_points[i])
        
        pygame.draw.polygon(surface, color, spike_points)
        pygame.draw.polygon(surface, BLACK, spike_points, 2)
    elif enemy_type == EnemyType.BERSERKER:
        # Fast moving destroyer with jagged edges
        points = []
        for i in range(12):
            angle = math.pi / 6 * i
            radius = size if i % 3 == 0 else size * 0.7
            px = x + radius * math.cos(angle)
            py = y + radius * math.sin(angle)
            points.append((px, py))
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, BLACK, points, 2)
    elif enemy_type in [EnemyType.TITAN, EnemyType.DEMON_LORD]:
        # Massive intimidating shape
        draw_hexagon(surface, color, (x, y), size, BLACK, 4)
        # Add spikes
        for i in range(6):
            angle = math.pi / 3 * i
            spike_x = x + (size + 8) * math.cos(angle)
            spike_y = y + (size + 8) * math.sin(angle)
            pygame.draw.line(surface, BLACK, (x, y), (spike_x, spike_y), 3)
        
        if enemy_type == EnemyType.DEMON_LORD:
            # Extra menacing features
            pygame.draw.circle(surface, RED, (x, y), size // 3)
            # Glowing eyes
            eye_offset = size // 3
            pygame.draw.circle(surface, RED, (x - eye_offset, y - eye_offset//2), 3)
            pygame.draw.circle(surface, RED, (x + eye_offset, y - eye_offset//2), 3)

class Projectile:
    def __init__(self, start_pos, target, damage, speed, color=YELLOW, proj_type="basic"):
        self.pos = Vector2(start_pos.x, start_pos.y)
        self.target = target
        self.damage = damage
        self.speed = speed
        self.color = color
        self.active = True
        self.type = proj_type
        self.trail = []
        self.lifetime = 300  # Max frames before disappearing
    
    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0 or not self.active or not self.target.alive:
            self.active = False
            return
        
        if self.type in ["laser", "plasma"]:
            self.trail.append((self.pos.x, self.pos.y))
            if len(self.trail) > 8:
                self.trail.pop(0)
        
        dx = self.target.pos.x - self.pos.x
        dy = self.target.pos.y - self.pos.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance < 8:
            self.target.take_damage(self.damage)
            if self.type == "explosive":
                # Splash damage (simplified)
                pass
            self.active = False
        else:
            self.pos.x += (dx / distance) * self.speed
            self.pos.y += (dy / distance) * self.speed
    
    def draw(self, screen):
        if self.type in ["laser", "plasma"]:
            for i, trail_pos in enumerate(self.trail):
                alpha = (i + 1) / len(self.trail)
                color = (int(self.color[0] * alpha), int(self.color[1] * alpha), int(self.color[2] * alpha))
                pygame.draw.circle(screen, color, (int(trail_pos[0]), int(trail_pos[1])), 2)
        
        size = 5 if self.type == "explosive" else (4 if self.type == "quantum" else 3)
        pygame.draw.circle(screen, self.color, (int(self.pos.x), int(self.pos.y)), size)
        
        if self.type == "quantum":
            pygame.draw.circle(screen, WHITE, (int(self.pos.x), int(self.pos.y)), 2)

class Enemy:
    def __init__(self, enemy_type, path, wave_multiplier=1.0):
        self.type = enemy_type
        self.path = path
        self.path_index = 0
        self.pos = Vector2(path[0][0], path[0][1])
        self.alive = True
        self.frozen = False
        self.freeze_timer = 0
        self.stealth_timer = 0
        self.visible = True
        self.regen_timer = 0
        self.armor = 0
        self.wave_multiplier = wave_multiplier
        self.attack_timer = 0
        self.attack_range = 0
        self.tower_damage = 0
        self.last_tower_attack = 0
        
        # Base stats with exponential scaling
        base_stats = self._get_base_stats(enemy_type)
        self.max_health = int(base_stats['health'] * wave_multiplier)
        self.speed = base_stats['speed']
        self.reward = int(base_stats['reward'] * (1 + wave_multiplier * 0.1))
        self.color = base_stats['color']
        self.size = base_stats['size']
        self.armor = base_stats.get('armor', 0)
        self.attack_range = base_stats.get('attack_range', 0)
        self.tower_damage = base_stats.get('tower_damage', 0)
        
        if enemy_type == EnemyType.STEALTH:
            self.stealth_timer = 180
            self.visible = False
        
        self.health = self.max_health
    
    def _get_base_stats(self, enemy_type):
        stats = {
            EnemyType.BASIC: {'health': 120, 'speed': 1.0, 'reward': 15, 'color': RED, 'size': 8},
            EnemyType.FAST: {'health': 80, 'speed': 2.5, 'reward': 20, 'color': ORANGE, 'size': 6},
            EnemyType.TANK: {'health': 500, 'speed': 0.5, 'reward': 40, 'color': GRAY, 'size': 12},
            EnemyType.FLYING: {'health': 100, 'speed': 1.8, 'reward': 25, 'color': LIGHT_BLUE, 'size': 8},
            EnemyType.STEALTH: {'health': 150, 'speed': 1.2, 'reward': 35, 'color': PURPLE, 'size': 9},
            EnemyType.BOSS: {'health': 1200, 'speed': 0.8, 'reward': 100, 'color': GOLD, 'size': 18},
            EnemyType.ARMORED: {'health': 400, 'speed': 0.7, 'reward': 50, 'color': SILVER, 'size': 10, 'armor': 10},
            EnemyType.REGENERATING: {'health': 300, 'speed': 1.0, 'reward': 45, 'color': LIME, 'size': 9},
            EnemyType.SWARM: {'health': 60, 'speed': 2.0, 'reward': 8, 'color': PINK, 'size': 5},
            EnemyType.MEGA_BOSS: {'health': 3000, 'speed': 0.6, 'reward': 500, 'color': DARK_RED, 'size': 25},
            # New formidable enemies
            EnemyType.DESTROYER: {'health': 800, 'speed': 0.8, 'reward': 75, 'color': CRIMSON, 'size': 14, 
                                'armor': 8, 'attack_range': 60, 'tower_damage': 150},
            EnemyType.BERSERKER: {'health': 400, 'speed': 1.8, 'reward': 60, 'color': DARK_PURPLE, 'size': 10,
                                'armor': 3, 'attack_range': 45, 'tower_damage': 100},
            EnemyType.TITAN: {'health': 5000, 'speed': 0.4, 'reward': 1000, 'color': (100, 100, 100), 'size': 30,
                            'armor': 20, 'attack_range': 80, 'tower_damage': 300},
            EnemyType.DEMON_LORD: {'health': 10000, 'speed': 0.5, 'reward': 2000, 'color': (50, 0, 0), 'size': 35,
                                 'armor': 25, 'attack_range': 100, 'tower_damage': 500}
        }
        return stats[enemy_type]
    
    def update(self, towers=None):
        if not self.alive:
            return
        
        if self.frozen:
            self.freeze_timer -= 1
            if self.freeze_timer <= 0:
                self.frozen = False
            else:
                return
        
        if self.type == EnemyType.STEALTH:
            self.stealth_timer -= 1
            if self.stealth_timer <= 0:
                self.visible = not self.visible
                self.stealth_timer = 120 if self.visible else 180
        
        if self.type == EnemyType.REGENERATING:
            self.regen_timer += 1
            if self.regen_timer >= 60:  # Regen every second
                self.health = min(self.max_health, self.health + int(self.max_health * 0.03))
                self.regen_timer = 0
        
        # Tower attacking behavior for destroyer types
        if self.tower_damage > 0 and towers:
            self.attack_timer += 1
            if self.attack_timer >= 60:  # Attack every second
                nearby_towers = [tower for tower in towers 
                               if self.pos.distance_to(tower.pos) <= self.attack_range]
                if nearby_towers:
                    # Attack the most expensive tower in range
                    target_tower = max(nearby_towers, key=lambda t: t.total_value)
                    target_tower.take_damage(self.tower_damage)
                    self.attack_timer = 0
                    # Create visual effect
                    self.last_tower_attack = 30
        
        if self.last_tower_attack > 0:
            self.last_tower_attack -= 1
        
        # Move along path only if not attacking towers
        nearby_towers = []
        if self.tower_damage > 0 and towers:
            nearby_towers = [tower for tower in towers 
                           if self.pos.distance_to(tower.pos) <= self.attack_range]
        
        # If destroyer type has towers in range, slow down to attack
        speed_modifier = 0.3 if (self.tower_damage > 0 and nearby_towers) else 1.0
        
        if self.path_index < len(self.path) - 1:
            target_x, target_y = self.path[self.path_index + 1]
            dx = target_x - self.pos.x
            dy = target_y - self.pos.y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance < 5:
                self.path_index += 1
            else:
                move_x = (dx / distance) * self.speed * speed_modifier
                move_y = (dy / distance) * self.speed * speed_modifier
                self.pos.x += move_x
                self.pos.y += move_y
    
    def take_damage(self, damage):
        actual_damage = max(1, damage - self.armor)
        self.health -= actual_damage
        if self.health <= 0:
            self.alive = False
    
    def freeze(self, duration):
        self.frozen = True
        self.freeze_timer = duration
    
    def reached_end(self):
        return self.path_index >= len(self.path) - 1
    
    def draw(self, screen):
        if not self.visible:
            return
        
        color = LIGHT_BLUE if self.frozen else self.color
        
        # Add red glow for attacking enemies
        if self.last_tower_attack > 0:
            glow_size = self.size + 5
            pygame.draw.circle(screen, RED, (int(self.pos.x), int(self.pos.y)), glow_size, 3)
        
        draw_enemy_shape(screen, self.type, (self.pos.x, self.pos.y), self.size, color)
        
        # Draw attack range for destroyer types
        if self.tower_damage > 0 and self.last_tower_attack > 0:
            pygame.draw.circle(screen, (255, 0, 0, 50), 
                             (int(self.pos.x), int(self.pos.y)), self.attack_range, 2)
        
        # Draw health bar
        if self.health < self.max_health:
            bar_width = max(25, self.size * 2)
            bar_height = 5
            bar_x = int(self.pos.x - bar_width // 2)
            bar_y = int(self.pos.y - self.size - 10)
            
            pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
            health_width = int((self.health / self.max_health) * bar_width)
            pygame.draw.rect(screen, GREEN, (bar_x, bar_y, health_width, bar_height))
            
            # Show armor
            if self.armor > 0:
                armor_text = pygame.font.Font(None, 16).render(f"ARM:{self.armor}", True, WHITE)
                screen.blit(armor_text, (bar_x, bar_y - 15))

class Tower:
    def __init__(self, tower_type, x, y, global_multipliers=None):
        self.type = tower_type
        self.pos = Vector2(x, y)
        self.target = None
        self.shoot_timer = 0
        self.level = 1
        self.upgrades = {upgrade: 0 for upgrade in UpgradeType}
        self.global_multipliers = global_multipliers or {}
        self.max_health = 100
        self.health = self.max_health
        self.alive = True
        
        self.base_stats = self._get_base_stats(tower_type)
        self.base_cost = self._get_base_cost(tower_type)
        self.total_value = self.base_cost  # Track total investment
        self.update_stats()
    
    def _get_base_cost(self, tower_type):
        costs = {
            TowerType.BASIC: 50,
            TowerType.RAPID: 75,
            TowerType.HEAVY: 120,
            TowerType.ICE: 80,
            TowerType.LASER: 200,
            TowerType.EXPLOSIVE: 300,
            TowerType.PLASMA: 500,
            TowerType.QUANTUM: 800,
            TowerType.NUCLEAR: 1500
        }
        return costs[tower_type]
    
    def _get_base_stats(self, tower_type):
        stats = {
            TowerType.BASIC: {'range': 80, 'damage': 30, 'fire_rate': 60, 'color': GREEN, 'proj_color': YELLOW, 'proj_type': 'basic'},
            TowerType.RAPID: {'range': 60, 'damage': 18, 'fire_rate': 20, 'color': BLUE, 'proj_color': BLUE, 'proj_type': 'basic'},
            TowerType.HEAVY: {'range': 100, 'damage': 90, 'fire_rate': 120, 'color': PURPLE, 'proj_color': PURPLE, 'proj_type': 'basic'},
            TowerType.ICE: {'range': 70, 'damage': 12, 'fire_rate': 45, 'color': LIGHT_BLUE, 'proj_color': WHITE, 'proj_type': 'basic'},
            TowerType.LASER: {'range': 90, 'damage': 50, 'fire_rate': 30, 'color': RED, 'proj_color': RED, 'proj_type': 'laser'},
            TowerType.EXPLOSIVE: {'range': 85, 'damage': 75, 'fire_rate': 90, 'color': ORANGE, 'proj_color': ORANGE, 'proj_type': 'explosive'},
            TowerType.PLASMA: {'range': 95, 'damage': 100, 'fire_rate': 40, 'color': CYAN, 'proj_color': CYAN, 'proj_type': 'plasma'},
            TowerType.QUANTUM: {'range': 120, 'damage': 125, 'fire_rate': 80, 'color': MAGENTA, 'proj_color': WHITE, 'proj_type': 'quantum'},
            TowerType.NUCLEAR: {'range': 150, 'damage': 250, 'fire_rate': 180, 'color': YELLOW, 'proj_color': GOLD, 'proj_type': 'explosive'}
        }
        return stats[tower_type]
    
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.alive = False
            self.health = 0
    
    def repair(self, amount):
        self.health = min(self.max_health, self.health + amount)
    
    def update_stats(self):
        base = self.base_stats
        damage_mult = self.global_multipliers.get('damage', 1.0)
        range_mult = self.global_multipliers.get('range', 1.0)
        speed_mult = self.global_multipliers.get('speed', 1.0)
        
        # More expensive towers are more durable
        durability_mult = 1.0 + (self.base_cost / 200)
        self.max_health = int(100 * durability_mult)
        if self.health > self.max_health:
            self.health = self.max_health
        
        self.range = int((base['range'] + (self.upgrades[UpgradeType.RANGE] * 15)) * range_mult)
        self.damage = int((base['damage'] + (self.upgrades[UpgradeType.DAMAGE] * 12)) * damage_mult)
        self.fire_rate = max(5, int((base['fire_rate'] - (self.upgrades[UpgradeType.SPEED] * 10)) / speed_mult))
        self.color = base['color']
        self.projectile_color = base['proj_color']
        self.projectile_type = base['proj_type']
    
    def find_target(self, enemies):
        valid_enemies = [e for e in enemies if e.alive and e.visible and 
                        self.pos.distance_to(e.pos) <= self.range]
        
        if self.type == TowerType.ICE:
            valid_enemies = [e for e in valid_enemies if e.type != EnemyType.FLYING]
        
        if not valid_enemies:
            self.target = None
            return
        
        # Prioritize destroyer types and bosses
        def priority_score(enemy):
            distance = self.pos.distance_to(enemy.pos)
            type_priority = {
                EnemyType.DEMON_LORD: 10, EnemyType.TITAN: 9, EnemyType.DESTROYER: 8,
                EnemyType.BERSERKER: 7, EnemyType.MEGA_BOSS: 6, EnemyType.BOSS: 5,
                EnemyType.FAST: 3
            }.get(enemy.type, 0)
            return distance - (type_priority * 100)
        
        self.target = min(valid_enemies, key=priority_score)
    
    def update(self, enemies):
        if not self.alive:
            return
            
        if self.shoot_timer > 0:
            self.shoot_timer -= 1
        
        if not self.target or not self.target.alive or not self.target.visible or self.pos.distance_to(self.target.pos) > self.range:
            self.find_target(enemies)
    
    def can_shoot(self):
        return self.alive and self.shoot_timer <= 0 and self.target and self.target.alive and self.target.visible
    
    def shoot(self):
        if self.can_shoot():
            self.shoot_timer = self.fire_rate
            projectile = Projectile(self.pos, self.target, self.damage, 5, self.projectile_color, self.projectile_type)
            
            if self.type == TowerType.ICE and self.target:
                self.target.freeze(60)
            
            return projectile
        return None
    
    def get_upgrade_cost(self, upgrade_type):
        base_cost = 40
        return base_cost + (self.upgrades[upgrade_type] * 30)
    
    def upgrade(self, upgrade_type):
        if self.upgrades[upgrade_type] < 5:  # Max 5 upgrades per type
            cost = self.get_upgrade_cost(upgrade_type)
            self.upgrades[upgrade_type] += 1
            self.total_value += cost
            self.update_stats()
            return True
        return False
    
    def draw(self, screen, show_range=False):
        if not self.alive:
            # Draw destroyed tower
            pygame.draw.circle(screen, GRAY, (int(self.pos.x), int(self.pos.y)), 10)
            pygame.draw.line(screen, BLACK, 
                           (int(self.pos.x-8), int(self.pos.y-8)), 
                           (int(self.pos.x+8), int(self.pos.y+8)), 3)
            pygame.draw.line(screen, BLACK, 
                           (int(self.pos.x+8), int(self.pos.y-8)), 
                           (int(self.pos.x-8), int(self.pos.y+8)), 3)
            return
        
        if show_range:
            pygame.draw.circle(screen, (255, 255, 255, 50), (int(self.pos.x), int(self.pos.y)), self.range, 1)
        
        size = 15 + (self.level * 2)
        
        # Damaged tower visual
        if self.health < self.max_health:
            damage_color = (int(self.color[0] * 0.7), int(self.color[1] * 0.7), int(self.color[2] * 0.7))
            draw_hexagon(screen, damage_color, (int(self.pos.x), int(self.pos.y)), size, RED, 3)
        else:
            draw_hexagon(screen, self.color, (int(self.pos.x), int(self.pos.y)), size, BLACK, 2)
        
        if sum(self.upgrades.values()) > 0:
            pygame.draw.circle(screen, GOLD, (int(self.pos.x + 12), int(self.pos.y - 12)), 3)
        
        # Draw health bar if damaged
        if self.health < self.max_health:
            bar_width = 20
            bar_height = 3
            bar_x = int(self.pos.x - bar_width // 2)
            bar_y = int(self.pos.y + size + 5)
            
            pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
            health_width = int((self.health / self.max_health) * bar_width)
            pygame.draw.rect(screen, GREEN, (bar_x, bar_y, health_width, bar_height))
        
        if self.target and self.target.alive and self.target.visible:
            pygame.draw.line(screen, self.color, 
                           (int(self.pos.x), int(self.pos.y)),
                           (int(self.target.pos.x), int(self.target.pos.y)), 1)

class Wave:
    def __init__(self, wave_number):
        self.wave_number = wave_number
        self.enemies = []
        self.spawn_timer = 0
        self.spawn_interval = max(12, 40 - wave_number)
        self.enemies_spawned = 0
        self.completed = False
        
        # More aggressive difficulty scaling
        self.difficulty_multiplier = 1.0 + (wave_number - 1) * 0.4 + ((wave_number - 1) ** 1.6) * 0.15
        self.generate_enemies()
    
    def generate_enemies(self):
        w = self.wave_number
        
        # More aggressive enemy scaling
        base_enemies = int(8 + w * 2 + (w ** 1.4) * 0.8)
        
        enemy_composition = []
        
        # Basic enemies (decreasing ratio faster)
        basic_count = max(1, int(base_enemies * 0.3 / (1 + w * 0.15)))
        enemy_composition.extend([EnemyType.BASIC] * basic_count)
        
        # Fast enemies (from wave 1)
        if w >= 1:
            fast_count = int(base_enemies * 0.25 + w * 0.6)
            enemy_composition.extend([EnemyType.FAST] * fast_count)
        
        # Tank enemies (from wave 2)
        if w >= 2:
            tank_count = max(1, int(w * 0.4))
            enemy_composition.extend([EnemyType.TANK] * tank_count)
        
        # Flying enemies (from wave 3)
        if w >= 3:
            flying_count = int(w * 0.5)
            enemy_composition.extend([EnemyType.FLYING] * flying_count)
        
        # Destroyer enemies (from wave 3) - Tower destroyers
        if w >= 3:
            destroyer_count = max(1, int((w - 2) * 0.3))
            enemy_composition.extend([EnemyType.DESTROYER] * destroyer_count)
        
        # Stealth enemies (from wave 4)
        if w >= 4:
            stealth_count = max(1, int((w - 3) * 0.4))
            enemy_composition.extend([EnemyType.STEALTH] * stealth_count)
        
        # Berserker enemies (from wave 5) - Fast tower destroyers
        if w >= 5:
            berserker_count = int((w - 4) * 0.25)
            enemy_composition.extend([EnemyType.BERSERKER] * berserker_count)
        
        # Armored enemies (from wave 6)
        if w >= 6:
            armored_count = int((w - 5) * 0.5)
            enemy_composition.extend([EnemyType.ARMORED] * armored_count)
        
        # Regenerating enemies (from wave 7)
        if w >= 7:
            regen_count = int((w - 6) * 0.3)
            enemy_composition.extend([EnemyType.REGENERATING] * regen_count)
        
        # Swarm enemies (from wave 8)
        if w >= 8:
            swarm_count = int((w - 7) * 1.2)
            enemy_composition.extend([EnemyType.SWARM] * swarm_count)
        
        # Boss enemies (every 4 waves)
        if w % 4 == 0:
            boss_count = 1 + (w // 8)  # More bosses in later waves
            enemy_composition.extend([EnemyType.BOSS] * boss_count)
        
        # Titan enemies (every 5 waves) - Super tough
        if w >= 5 and w % 5 == 0:
            titan_count = 1 + (w // 15)
            enemy_composition.extend([EnemyType.TITAN] * titan_count)
        
        # Demon Lord (every 10 waves) - Ultimate boss
        if w >= 10 and w % 10 == 0:
            demon_count = 1 + (w // 20)
            enemy_composition.extend([EnemyType.DEMON_LORD] * demon_count)
        
        # Mega boss (every 15 waves)
        if w >= 15 and w % 15 == 0:
            enemy_composition.append(EnemyType.MEGA_BOSS)
        
        self.total_enemies = len(enemy_composition)
        self.enemy_queue = enemy_composition
    
    def update(self, path, towers):
        if self.enemies_spawned < self.total_enemies:
            self.spawn_timer += 1
            if self.spawn_timer >= self.spawn_interval:
                enemy_type = self.enemy_queue[self.enemies_spawned]
                enemy = Enemy(enemy_type, path, self.difficulty_multiplier)
                self.enemies.append(enemy)
                self.enemies_spawned += 1
                self.spawn_timer = 0
        
        for enemy in self.enemies[:]:
            enemy.update(towers)
        
        if (self.enemies_spawned >= self.total_enemies and 
            all(not enemy.alive or enemy.reached_end() for enemy in self.enemies)):
            self.completed = True

class TowerDefenseGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Ultimate Tower Defense - Enhanced Edition")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Game state
        self.money = 400  # More starting money due to increased difficulty
        self.lives = 25   # Fewer lives due to tower destruction
        self.score = 0
        self.wave_number = 1
        self.game_over = False
        self.paused = False
        
        # Power-ups and permanent upgrades
        self.powerups = {powerup: 0 for powerup in PowerUpType}
        self.permanent_upgrades = {upgrade: 0 for upgrade in PermanentUpgrade}
        self.global_multipliers = {'damage': 1.0, 'range': 1.0, 'speed': 1.0}
        
        # Active effects
        self.active_effects = {}
        self.interest_timer = 0
        self.notification_timer = 0
        self.notification_text = ""
        
        # Game objects
        self.towers = []
        self.projectiles = []
        self.current_wave = None
        self.wave_active = False
        self.selected_tower_type = TowerType.BASIC
        self.selected_tower = None
        self.shop_page = 0  # 0=towers, 1=powerups, 2=permanent upgrades
        
        self.path = [
            (50, 350), (150, 350), (150, 200), (300, 200),
            (300, 500), (450, 500), (450, 150), (600, 150),
            (600, 450), (750, 450), (750, 250), (900, 250),
            (900, 400), (1050, 400)
        ]
        
        # Tower unlock requirements
        self.tower_unlock_waves = {
            TowerType.BASIC: 1,
            TowerType.RAPID: 1,
            TowerType.HEAVY: 2,
            TowerType.ICE: 3,
            TowerType.LASER: 5,
            TowerType.EXPLOSIVE: 7,
            TowerType.PLASMA: 10,
            TowerType.QUANTUM: 15,
            TowerType.NUCLEAR: 20
        }
        
        # Prices (increased due to tower destruction threat)
        self.tower_costs = {
            TowerType.BASIC: 60,
            TowerType.RAPID: 90,
            TowerType.HEAVY: 150,
            TowerType.ICE: 100,
            TowerType.LASER: 250,
            TowerType.EXPLOSIVE: 380,
            TowerType.PLASMA: 650,
            TowerType.QUANTUM: 1000,
            TowerType.NUCLEAR: 1800
        }
        
        self.powerup_costs = {
            PowerUpType.AIR_STRIKE: 180,
            PowerUpType.FREEZE_ALL: 250,
            PowerUpType.DOUBLE_DAMAGE: 350,
            PowerUpType.MONEY_BOOST: 300,
            PowerUpType.REPAIR_LIVES: 450,
            PowerUpType.TIME_SLOW: 400,
            PowerUpType.LIGHTNING_STORM: 600,
            PowerUpType.NUKE: 1200
        }
        
        self.permanent_costs = {
            PermanentUpgrade.STARTING_MONEY: 600,
            PermanentUpgrade.INTEREST_RATE: 900,
            PermanentUpgrade.TOWER_DISCOUNT: 1200,
            PermanentUpgrade.DAMAGE_MULTIPLIER: 1400,
            PermanentUpgrade.RANGE_MULTIPLIER: 1400,
            PermanentUpgrade.SPEED_MULTIPLIER: 1400,
            PermanentUpgrade.EXTRA_LIVES: 1000,
            PermanentUpgrade.WAVE_SKIP: 2500
        }
        
        self.apply_permanent_upgrades()
    
    def show_notification(self, text, duration=180):
        self.notification_text = text
        self.notification_timer = duration
    
    def is_tower_unlocked(self, tower_type):
        return self.wave_number >= self.tower_unlock_waves[tower_type]
    
    def apply_permanent_upgrades(self):
        # Starting money bonus
        bonus_money = self.permanent_upgrades[PermanentUpgrade.STARTING_MONEY] * 150
        self.money += bonus_money
        
        # Global multipliers
        self.global_multipliers['damage'] = 1.0 + (self.permanent_upgrades[PermanentUpgrade.DAMAGE_MULTIPLIER] * 0.3)
        self.global_multipliers['range'] = 1.0 + (self.permanent_upgrades[PermanentUpgrade.RANGE_MULTIPLIER] * 0.25)
        self.global_multipliers['speed'] = 1.0 + (self.permanent_upgrades[PermanentUpgrade.SPEED_MULTIPLIER] * 0.35)
        
        # Extra lives
        self.lives += self.permanent_upgrades[PermanentUpgrade.EXTRA_LIVES] * 8
    
    def get_tower_cost(self, tower_type):
        base_cost = self.tower_costs[tower_type]
        discount = self.permanent_upgrades[PermanentUpgrade.TOWER_DISCOUNT] * 0.12
        return int(base_cost * (1 - discount))
    
    def get_powerup_cost(self, powerup_type):
        base_cost = self.powerup_costs[powerup_type]
        owned = self.powerups[powerup_type]
        return int(base_cost * (1.6 ** owned))
    
    def get_permanent_cost(self, upgrade_type):
        base_cost = self.permanent_costs[upgrade_type]
        owned = self.permanent_upgrades[upgrade_type]
        return int(base_cost * (2.2 ** owned))
    
    def use_powerup(self, powerup_type):
        if self.powerups[powerup_type] > 0:
            self.powerups[powerup_type] -= 1
            
            if powerup_type == PowerUpType.AIR_STRIKE:
                # Damage all enemies
                if self.current_wave:
                    damage_dealt = 0
                    for enemy in self.current_wave.enemies:
                        if enemy.alive:
                            damage_dealt += min(enemy.health, 250)
                            enemy.take_damage(250)
                    self.show_notification(f"Air Strike: {damage_dealt} damage!")
            
            elif powerup_type == PowerUpType.FREEZE_ALL:
                # Freeze all enemies
                if self.current_wave:
                    frozen_count = 0
                    for enemy in self.current_wave.enemies:
                        if enemy.alive:
                            enemy.freeze(240)
                            frozen_count += 1
                    self.show_notification(f"Froze {frozen_count} enemies!")
            
            elif powerup_type == PowerUpType.DOUBLE_DAMAGE:
                # Double damage for 30 seconds
                self.active_effects['double_damage'] = 1800
                self.show_notification("Double damage activated!")
            
            elif powerup_type == PowerUpType.MONEY_BOOST:
                # Instant money
                boost = 600 + (self.wave_number * 75)
                self.money += boost
                self.show_notification(f"Money boost: +${boost}!")
            
            elif powerup_type == PowerUpType.REPAIR_LIVES:
                # Restore lives
                old_lives = self.lives
                self.lives = min(25 + self.permanent_upgrades[PermanentUpgrade.EXTRA_LIVES] * 8, 
                               self.lives + 15)
                gained = self.lives - old_lives
                self.show_notification(f"Repaired {gained} lives!")
            
            elif powerup_type == PowerUpType.TIME_SLOW:
                # Slow time for 25 seconds
                self.active_effects['time_slow'] = 1500
                self.show_notification("Time slowed!")
            
            elif powerup_type == PowerUpType.LIGHTNING_STORM:
                # Chain lightning damage
                if self.current_wave:
                    damage_dealt = 0
                    for enemy in self.current_wave.enemies[:8]:  # Hit first 8 enemies
                        if enemy.alive:
                            damage_dealt += min(enemy.health, 400)
                            enemy.take_damage(400)
                    self.show_notification(f"Lightning: {damage_dealt} damage!")
            
            elif powerup_type == PowerUpType.NUKE:
                # Massive damage to all enemies
                if self.current_wave:
                    damage_dealt = 0
                    for enemy in self.current_wave.enemies:
                        if enemy.alive:
                            damage_dealt += min(enemy.health, 1500)
                            enemy.take_damage(1500)
                    self.show_notification(f"NUKE: {damage_dealt} damage!")
            
            return True
        return False
    
    def start_wave(self):
        if not self.wave_active:
            self.current_wave = Wave(self.wave_number)
            self.wave_active = True
    
    def update(self):
        if self.game_over or self.paused:
            return
        
        # Update notification
        if self.notification_timer > 0:
            self.notification_timer -= 1
        
        # Update active effects
        for effect in list(self.active_effects.keys()):
            self.active_effects[effect] -= 1
            if self.active_effects[effect] <= 0:
                del self.active_effects[effect]
        
        # Interest system
        if self.permanent_upgrades[PermanentUpgrade.INTEREST_RATE] > 0:
            self.interest_timer += 1
            if self.interest_timer >= 600:  # Every 10 seconds
                interest_rate = 0.025 * self.permanent_upgrades[PermanentUpgrade.INTEREST_RATE]
                interest = int(self.money * interest_rate)
                self.money += interest
                self.interest_timer = 0
        
        # Remove destroyed towers
        self.towers = [tower for tower in self.towers if tower.alive]
        
        # Update wave
        if self.wave_active and self.current_wave:
            self.current_wave.update(self.path, self.towers)
            
            # Check for enemies reaching the end
            for enemy in self.current_wave.enemies[:]:
                if enemy.reached_end() and enemy.alive:
                    damage = {
                        EnemyType.BASIC: 1, EnemyType.FAST: 1, EnemyType.TANK: 2,
                        EnemyType.FLYING: 1, EnemyType.STEALTH: 1, EnemyType.BOSS: 5,
                        EnemyType.ARMORED: 2, EnemyType.REGENERATING: 1,
                        EnemyType.SWARM: 1, EnemyType.MEGA_BOSS: 12,
                        EnemyType.DESTROYER: 3, EnemyType.BERSERKER: 2,
                        EnemyType.TITAN: 8, EnemyType.DEMON_LORD: 15
                    }.get(enemy.type, 1)
                    
                    self.lives -= damage
                    enemy.alive = False
                    if damage > 2:
                        self.show_notification(f"Powerful enemy escaped! -{damage} lives")
                    if self.lives <= 0:
                        self.game_over = True
                elif not enemy.alive and enemy in self.current_wave.enemies:
                    reward_multiplier = 2.0 if 'double_damage' in self.active_effects else 1.0
                    self.money += int(enemy.reward * reward_multiplier)
                    self.score += int(enemy.reward * 10 * reward_multiplier)
                    
                    # Bonus for killing formidable enemies
                    if enemy.type in [EnemyType.DESTROYER, EnemyType.BERSERKER, EnemyType.TITAN, EnemyType.DEMON_LORD]:
                        bonus = int(enemy.reward * 0.5)
                        self.money += bonus
                        self.score += bonus * 20
            
            # Check if wave is completed
            if self.current_wave.completed:
                self.wave_active = False
                # More generous wave completion bonus due to increased difficulty
                bonus = int(75 + (self.wave_number * 35) + ((self.wave_number ** 1.3) * 15))
                self.money += bonus
                
                # Wave milestone rewards
                if self.wave_number % 5 == 0:
                    milestone_bonus = int(self.wave_number * 50)
                    self.money += milestone_bonus
                    self.show_notification(f"Wave {self.wave_number} completed! Bonus: ${bonus + milestone_bonus}")
                else:
                    self.show_notification(f"Wave {self.wave_number} completed! Bonus: ${bonus}")
                
                self.wave_number += 1
        
        # Update towers with global multipliers
        enemies = self.current_wave.enemies if self.current_wave else []
        for tower in self.towers:
            if tower.alive:
                tower.global_multipliers = self.global_multipliers.copy()
                if 'double_damage' in self.active_effects:
                    tower.global_multipliers['damage'] *= 2.0
                tower.update_stats()
                tower.update(enemies)
                projectile = tower.shoot()
                if projectile:
                    self.projectiles.append(projectile)
        
        # Update projectiles (slower if time is slowed)
        speed_factor = 0.4 if 'time_slow' in self.active_effects else 1.0
        if speed_factor < 1.0:
            # Only update some projectiles to simulate slow motion
            for i, projectile in enumerate(self.projectiles):
                if i % 3 == 0:  # Update every third projectile
                    projectile.update()
        else:
            for projectile in self.projectiles[:]:
                projectile.update()
                if not projectile.active:
                    self.projectiles.remove(projectile)
    
    def handle_click(self, pos):
        if self.game_over:
            return
        
        x, y = pos
        
        # Check UI area
        if x > 1100:
            # Shop page buttons
            if 1110 <= x <= 1390:
                if 20 <= y <= 50:
                    if 1110 <= x <= 1200: self.shop_page = 0  # Towers
                    elif 1210 <= x <= 1300: self.shop_page = 1  # Powerups
                    elif 1310 <= x <= 1390: self.shop_page = 2  # Permanent
            
            # Shop items
            if self.shop_page == 0:  # Tower shop
                tower_types = list(TowerType)
                for i, tower_type in enumerate(tower_types):
                    button_y = 80 + i * 30
                    if 1110 <= x <= 1390 and button_y <= y <= button_y + 25:
                        if self.is_tower_unlocked(tower_type):
                            cost = self.get_tower_cost(tower_type)
                            if self.money >= cost:
                                self.selected_tower_type = tower_type
                        break
            
            elif self.shop_page == 1:  # Powerup shop
                powerup_types = list(PowerUpType)
                for i, powerup_type in enumerate(powerup_types):
                    button_y = 80 + i * 30
                    if 1110 <= x <= 1290 and button_y <= y <= button_y + 25:
                        cost = self.get_powerup_cost(powerup_type)
                        if self.money >= cost:
                            self.powerups[powerup_type] += 1
                            self.money -= cost
                        break
                    # Use powerup button
                    elif 1300 <= x <= 1390 and button_y <= y <= button_y + 25:
                        self.use_powerup(powerup_type)
                        break
            
            elif self.shop_page == 2:  # Permanent upgrade shop
                upgrade_types = list(PermanentUpgrade)
                for i, upgrade_type in enumerate(upgrade_types):
                    button_y = 80 + i * 30
                    if 1110 <= x <= 1390 and button_y <= y <= button_y + 25:
                        cost = self.get_permanent_cost(upgrade_type)
                        if self.money >= cost:
                            self.permanent_upgrades[upgrade_type] += 1
                            self.money -= cost
                            self.apply_permanent_upgrades()
                        break
            
            # Start wave button
            if 1110 <= x <= 1390 and 420 <= y <= 450 and not self.wave_active:
                self.start_wave()
            
            # Tower upgrade and repair buttons (when tower selected)
            if self.selected_tower and 1110 <= x <= 1390:
                upgrade_types = list(UpgradeType)
                for i, upgrade_type in enumerate(upgrade_types):
                    button_y = 520 + i * 30
                    if button_y <= y <= button_y + 25:
                        cost = self.selected_tower.get_upgrade_cost(upgrade_type)
                        if self.money >= cost and self.selected_tower.upgrade(upgrade_type):
                            self.money -= cost
                        break
                
                # Repair button
                if 650 <= y <= 675 and self.selected_tower.health < self.selected_tower.max_health:
                    repair_cost = 50
                    if self.money >= repair_cost:
                        self.selected_tower.repair(self.selected_tower.max_health)
                        self.money -= repair_cost
            
            return
        
        # Check if clicking on existing tower
        for tower in self.towers:
            if tower.pos.distance_to(Vector2(x, y)) <= 25:
                self.selected_tower = tower
                return
        
        self.selected_tower = None
        
        # Try to place a tower
        if not self.is_tower_unlocked(self.selected_tower_type):
            unlock_wave = self.tower_unlock_waves[self.selected_tower_type]
            self.show_notification(f"Tower unlocks at wave {unlock_wave}")
            return
        
        cost = self.get_tower_cost(self.selected_tower_type)
        if self.money >= cost:
            # Check if position is valid
            valid_position = True
            
            # Check distance from path
            for path_point in self.path:
                if math.sqrt((x - path_point[0])**2 + (y - path_point[1])**2) < 40:
                    valid_position = False
                    break
            
            # Check distance from other towers
            for tower in self.towers:
                if tower.pos.distance_to(Vector2(x, y)) < 50:
                    valid_position = False
                    break
            
            if valid_position and x < 1100:  # Not in UI area
                new_tower = Tower(self.selected_tower_type, x, y, self.global_multipliers)
                self.towers.append(new_tower)
                self.money -= cost
        else:
            self.show_notification(f"Need ${cost - self.money} more!")
    
    def draw_path(self):
        for i in range(len(self.path) - 1):
            pygame.draw.line(self.screen, BROWN, self.path[i], self.path[i + 1], 15)
            pygame.draw.line(self.screen, YELLOW, self.path[i], self.path[i + 1], 10)
        
        for i, point in enumerate(self.path):
            color = GREEN if i == 0 else (RED if i == len(self.path) - 1 else DARK_GREEN)
            pygame.draw.circle(self.screen, color, point, 10)
            pygame.draw.circle(self.screen, BLACK, point, 10, 2)
    
    def draw_ui(self):
        # UI background
        ui_rect = pygame.Rect(1100, 0, 300, WINDOW_HEIGHT)
        pygame.draw.rect(self.screen, GRAY, ui_rect)
        pygame.draw.rect(self.screen, BLACK, ui_rect, 3)
        
        # Game stats
        stats = [
            f"Money: ${self.money:,}",
            f"Lives: {self.lives}",
            f"Wave: {self.wave_number}",
            f"Score: {self.score:,}"
        ]
        
        for i, stat in enumerate(stats):
            color = GREEN if i == 0 else BLACK
            text = self.font.render(stat, True, color)
            self.screen.blit(text, (1110, 5 + i * 20))
        
        # Notification
        if self.notification_timer > 0:
            notification = self.small_font.render(self.notification_text, True, GOLD)
            self.screen.blit(notification, (1110, 85))
        
        # Shop tabs
        tab_names = ["Towers", "Powers", "Upgrades"]
        tab_colors = [WHITE if i == self.shop_page else LIGHT_BLUE for i in range(3)]
        
        for i, (name, color) in enumerate(zip(tab_names, tab_colors)):
            tab_rect = pygame.Rect(1110 + i * 90, 105, 85, 30)
            pygame.draw.rect(self.screen, color, tab_rect)
            pygame.draw.rect(self.screen, BLACK, tab_rect, 2)
            
            text = self.small_font.render(name, True, BLACK)
            text_rect = text.get_rect(center=tab_rect.center)
            self.screen.blit(text, text_rect)
        
        # Shop content
        if self.shop_page == 0:  # Towers
            self.draw_tower_shop()
        elif self.shop_page == 1:  # Powerups
            self.draw_powerup_shop()
        elif self.shop_page == 2:  # Permanent upgrades
            self.draw_permanent_shop()
        
        # Start wave button
        if not self.wave_active:
            button_rect = pygame.Rect(1110, 420, 280, 30)
            pygame.draw.rect(self.screen, GREEN, button_rect)
            pygame.draw.rect(self.screen, BLACK, button_rect, 2)
            
            bonus = int(75 + (self.wave_number * 35) + ((self.wave_number ** 1.3) * 15))
            text = self.font.render(f"Start Wave {self.wave_number} (+${bonus})", True, BLACK)
            text_rect = text.get_rect(center=button_rect.center)
            self.screen.blit(text, text_rect)
        else:
            remaining = self.current_wave.total_enemies - self.current_wave.enemies_spawned
            alive = sum(1 for e in self.current_wave.enemies if e.alive)
            
            progress_text = self.small_font.render(f"Wave {self.wave_number} Active", True, BLACK)
            remaining_text = self.small_font.render(f"Remaining: {remaining}", True, BLACK)
            alive_text = self.small_font.render(f"Alive: {alive}", True, BLACK)
            
            self.screen.blit(progress_text, (1110, 425))
            self.screen.blit(remaining_text, (1110, 440))
            self.screen.blit(alive_text, (1250, 440))
        
        # Active effects display
        effects_y = 460
        for effect, timer in self.active_effects.items():
            effect_name = effect.replace('_', ' ').title()
            seconds = timer // 60
            effect_text = self.small_font.render(f"{effect_name}: {seconds}s", True, GOLD)
            self.screen.blit(effect_text, (1110, effects_y))
            effects_y += 18
        
        # Tower upgrades (when selected)
        if self.selected_tower:
            self.draw_tower_upgrades()
    
    def draw_tower_shop(self):
        tower_types = list(TowerType)
        tower_names = ["Basic", "Rapid", "Heavy", "Ice", "Laser", "Explosive", "Plasma", "Quantum", "Nuclear"]
        tower_colors = [GREEN, BLUE, PURPLE, LIGHT_BLUE, RED, ORANGE, CYAN, MAGENTA, YELLOW]
        
        y_start = 145
        for i, (tower_type, name, color) in enumerate(zip(tower_types, tower_names, tower_colors)):
            y_pos = y_start + i * 30
            cost = self.get_tower_cost(tower_type)
            unlocked = self.is_tower_unlocked(tower_type)
            affordable = self.money >= cost and unlocked
            
            # Button background
            if not unlocked:
                bg_color = GRAY
                text_color = (64, 64, 64)
            elif tower_type == self.selected_tower_type:
                bg_color = WHITE
                text_color = BLACK
            elif affordable:
                bg_color = LIGHT_BLUE
                text_color = BLACK
            else:
                bg_color = GRAY
                text_color = (64, 64, 64)
            
            button_rect = pygame.Rect(1110, y_pos, 280, 25)
            pygame.draw.rect(self.screen, bg_color, button_rect)
            pygame.draw.rect(self.screen, BLACK, button_rect, 2)
            
            # Tower preview
            if unlocked:
                draw_hexagon(self.screen, color, (1125, y_pos + 12), 8, BLACK, 1)
            else:
                pygame.draw.circle(self.screen, GRAY, (1125, y_pos + 12), 8)
                pygame.draw.line(self.screen, BLACK, (1120, y_pos + 7), (1130, y_pos + 17), 2)
            
            # Text
            if not unlocked:
                unlock_wave = self.tower_unlock_waves[tower_type]
                display_text = f"{name} - Wave {unlock_wave}"
            else:
                display_text = f"{name} - ${cost:,}"
            
            text = self.small_font.render(display_text, True, text_color)
            self.screen.blit(text, (1140, y_pos + 5))
    
    def draw_powerup_shop(self):
        powerup_types = list(PowerUpType)
        powerup_names = ["Air Strike", "Freeze All", "2x Damage", "Money Boost", 
                        "Repair Lives", "Time Slow", "Lightning", "Nuke"]
        
        y_start = 145
        for i, (powerup_type, name) in enumerate(zip(powerup_types, powerup_names)):
            y_pos = y_start + i * 30
            cost = self.get_powerup_cost(powerup_type)
            owned = self.powerups[powerup_type]
            affordable = self.money >= cost
            
            # Buy button
            buy_rect = pygame.Rect(1110, y_pos, 180, 25)
            buy_color = LIGHT_BLUE if affordable else GRAY
            pygame.draw.rect(self.screen, buy_color, buy_rect)
            pygame.draw.rect(self.screen, BLACK, buy_rect, 2)
            
            buy_text = f"Buy {name} (${cost:,})"
            text_color = BLACK if affordable else (64, 64, 64)
            text = self.small_font.render(buy_text, True, text_color)
            self.screen.blit(text, (1115, y_pos + 5))
            
            # Use button
            use_rect = pygame.Rect(1300, y_pos, 90, 25)
            use_color = GREEN if owned > 0 else GRAY
            pygame.draw.rect(self.screen, use_color, use_rect)
            pygame.draw.rect(self.screen, BLACK, use_rect, 2)
            
            use_text = f"Use ({owned})"
            use_text_color = BLACK if owned > 0 else (64, 64, 64)
            text = self.small_font.render(use_text, True, use_text_color)
            text_rect = text.get_rect(center=use_rect.center)
            self.screen.blit(text, text_rect)
    
    def draw_permanent_shop(self):
        upgrade_types = list(PermanentUpgrade)
        upgrade_names = ["Start Money", "Interest", "Tower Discount", "Damage", 
                        "Range", "Fire Rate", "Extra Lives", "Wave Skip"]
        
        y_start = 145
        for i, (upgrade_type, name) in enumerate(zip(upgrade_types, upgrade_names)):
            y_pos = y_start + i * 30
            cost = self.get_permanent_cost(upgrade_type)
            owned = self.permanent_upgrades[upgrade_type]
            affordable = self.money >= cost
            
            # Button
            button_rect = pygame.Rect(1110, y_pos, 280, 25)
            bg_color = LIGHT_BLUE if affordable else GRAY
            pygame.draw.rect(self.screen, bg_color, button_rect)
            pygame.draw.rect(self.screen, BLACK, button_rect, 2)
            
            # Text
            display_text = f"{name} Lv{owned} - ${cost:,}"
            text_color = BLACK if affordable else (64, 64, 64)
            text = self.small_font.render(display_text, True, text_color)
            self.screen.blit(text, (1115, y_pos + 5))
            
            # Level indicators
            for j in range(min(5, owned)):
                indicator_x = 1370 + j * 8
                pygame.draw.circle(self.screen, GOLD, (indicator_x, y_pos + 12), 3)
    
    def draw_tower_upgrades(self):
        upgrade_y = 500
        tower_name = self.selected_tower.type.value.title()
        title_text = self.font.render(f"{tower_name} Tower:", True, BLACK)
        self.screen.blit(title_text, (1110, upgrade_y))
        
        # Tower health display
        health_text = self.small_font.render(
            f"Health: {self.selected_tower.health}/{self.selected_tower.max_health}", 
            True, RED if self.selected_tower.health < self.selected_tower.max_health else BLACK
        )
        self.screen.blit(health_text, (1110, upgrade_y + 18))
        
        upgrade_types = list(UpgradeType)
        upgrade_names = ["Damage", "Range", "Fire Rate", "Special"]
        
        for i, (upgrade_type, name) in enumerate(zip(upgrade_types, upgrade_names)):
            y_pos = 520 + i * 30
            level = self.selected_tower.upgrades[upgrade_type]
            cost = self.selected_tower.get_upgrade_cost(upgrade_type)
            max_level = level >= 5
            
            affordable = self.money >= cost and not max_level and self.selected_tower.alive
            bg_color = LIGHT_BLUE if affordable else GRAY
            text_color = BLACK if affordable else (64, 64, 64)
            
            button_rect = pygame.Rect(1110, y_pos, 280, 25)
            pygame.draw.rect(self.screen, bg_color, button_rect)
            pygame.draw.rect(self.screen, BLACK, button_rect, 2)
            
            if max_level:
                display_text = f"{name}: MAX"
            else:
                display_text = f"{name} Lv{level} - ${cost}"
            
            text = self.small_font.render(display_text, True, text_color)
            self.screen.blit(text, (1115, y_pos + 5))
            
            # Level indicators
            for j in range(5):
                indicator_color = GOLD if j < level else WHITE
                pygame.draw.circle(self.screen, indicator_color, (1350 + j * 12, y_pos + 12), 4)
                pygame.draw.circle(self.screen, BLACK, (1350 + j * 12, y_pos + 12), 4, 1)
        
        # Repair button
        if self.selected_tower.health < self.selected_tower.max_health:
            repair_y = 650
            repair_cost = 50
            affordable = self.money >= repair_cost
            
            repair_rect = pygame.Rect(1110, repair_y, 280, 25)
            bg_color = GREEN if affordable else GRAY
            pygame.draw.rect(self.screen, bg_color, repair_rect)
            pygame.draw.rect(self.screen, BLACK, repair_rect, 2)
            
            repair_text = f"Repair Tower - ${repair_cost}"
            text_color = BLACK if affordable else (64, 64, 64)
            text = self.small_font.render(repair_text, True, text_color)
            text_rect = text.get_rect(center=repair_rect.center)
            self.screen.blit(text, text_rect)
    
    def draw(self):
        self.screen.fill(DARK_GREEN)
        
        # Draw path
        self.draw_path()
        
        # Draw towers
        for tower in self.towers:
            show_range = tower == self.selected_tower
            tower.draw(self.screen, show_range)
        
        # Draw enemies
        if self.current_wave:
            for enemy in self.current_wave.enemies:
                if enemy.alive:
                    enemy.draw(self.screen)
        
        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(self.screen)
        
        # Draw UI
        self.draw_ui()
        
        # Visual effects overlay
        if 'double_damage' in self.active_effects:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.set_alpha(40)
            overlay.fill(RED)
            self.screen.blit(overlay, (0, 0))
        
        if 'time_slow' in self.active_effects:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.set_alpha(30)
            overlay.fill(BLUE)
            self.screen.blit(overlay, (0, 0))
        
        # Pause overlay
        if self.paused and not self.game_over:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            pause_text = pygame.font.Font(None, 48).render("PAUSED", True, WHITE)
            pause_rect = pause_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            self.screen.blit(pause_text, pause_rect)
        
        # Game over screen
        if self.game_over:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.set_alpha(160)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            game_over_text = pygame.font.Font(None, 72).render("GAME OVER", True, WHITE)
            final_score_text = pygame.font.Font(None, 36).render(f"Final Score: {self.score:,}", True, WHITE)
            wave_text = pygame.font.Font(None, 36).render(f"Reached Wave: {self.wave_number}", True, WHITE)
            money_text = pygame.font.Font(None, 36).render(f"Money Left: ${self.money:,}", True, WHITE)
            towers_destroyed = pygame.font.Font(None, 24).render(f"Towers Lost to Enemy Attacks", True, RED)
            restart_text = self.font.render("Press R to restart or Q to quit", True, WHITE)
            
            go_rect = game_over_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 100))
            score_rect = final_score_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 60))
            wave_rect = wave_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 30))
            money_rect = money_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            destroyed_rect = towers_destroyed.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 30))
            restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 70))
            
            self.screen.blit(game_over_text, go_rect)
            self.screen.blit(final_score_text, score_rect)
            self.screen.blit(wave_text, wave_rect)
            self.screen.blit(money_text, money_rect)
            self.screen.blit(towers_destroyed, destroyed_rect)
            self.screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()
    
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.handle_click(event.pos)
            
            if event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_r:
                        self.restart()
                    elif event.key == pygame.K_q:
                        return False
                else:
                    if event.key == pygame.K_SPACE and not self.wave_active:
                        self.start_wave()
                    elif event.key == pygame.K_p:
                        self.paused = not self.paused
                    elif event.key == pygame.K_q:
                        return False
                    elif event.key >= pygame.K_1 and event.key <= pygame.K_9:
                        tower_index = event.key - pygame.K_1
                        tower_types = list(TowerType)
                        if tower_index < len(tower_types):
                            tower_type = tower_types[tower_index]
                            if self.is_tower_unlocked(tower_type):
                                self.selected_tower_type = tower_type
                    # Powerup hotkeys
                    elif event.key == pygame.K_z:
                        self.use_powerup(PowerUpType.AIR_STRIKE)
                    elif event.key == pygame.K_x:
                        self.use_powerup(PowerUpType.FREEZE_ALL)
                    elif event.key == pygame.K_c:
                        self.use_powerup(PowerUpType.DOUBLE_DAMAGE)
                    elif event.key == pygame.K_v:
                        self.use_powerup(PowerUpType.NUKE)
                    elif event.key == pygame.K_t:
                        self.use_powerup(PowerUpType.TIME_SLOW)
        
        return True
    
    def restart(self):
        self.money = 400
        self.lives = 25
        self.score = 0
        self.wave_number = 1
        self.game_over = False
        self.paused = False
        self.towers = []
        self.projectiles = []
        self.current_wave = None
        self.wave_active = False
        self.selected_tower = None
        self.active_effects = {}
        self.interest_timer = 0
        self.notification_timer = 0
        self.notification_text = ""
        
        # Keep permanent upgrades but reset powerups
        self.powerups = {powerup: 0 for powerup in PowerUpType}
        self.apply_permanent_upgrades()
    
    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(60)  # 60 FPS
        
        pygame.quit()

if __name__ == "__main__":
    game = TowerDefenseGame()
    game.run()