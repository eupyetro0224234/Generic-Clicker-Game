import pygame, random, io
from game_assets.game_assets_packed import load_image, load_sound as packed_load_sound

class MiniEvent:
    def __init__(self, screen, width, height, event_type="normal"):
        self.screen = screen
        self.width = width
        self.height = height
        self.event_type = event_type
        
        if self.event_type == "rare":
            self.image_name = "mini-event2.png"
            self.sound_name = "mini-event-sound.mp3"
            self.size = 60
            self.base_color = (0, 100, 255)
            self.text_label = "ME2"
            self.clicks_needed = self._get_weighted_clicks()
            self.clicks_done = 0
            
            if self.clicks_needed <= 10:
                self.time_to_live = 10000
            else:
                self.time_to_live = 15000
                
            self.reward_multiplier = 2
            self.upgrade_chance = 0.05
            
        else:
            self.image_name = "mini-event.png"
            self.sound_name = "mini-event-sound.mp3"
            self.size = 50
            self.base_color = (255, 0, 0)
            self.text_label = "EVENTO"
            self.clicks_needed = 1
            self.clicks_done = 0
            
            self.time_to_live = 10000
            self.reward_multiplier = 1
            self.upgrade_chance = 0.05

        try:
            self.image = load_image(self.image_name)
            self.image = pygame.transform.scale(self.image, (self.size, self.size))
        except Exception:
            self.image = pygame.Surface((self.size, self.size))
            self.image.fill(self.base_color)
            font = pygame.font.SysFont(None, 20)
            text = font.render(self.text_label, True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.size//2, self.size//2))
            self.image.blit(text, text_rect)

        self.volume = 1.0
        self.sound_playing = False
        self.sound_channel = None
        
        try:
            self.sound = packed_load_sound(self.sound_name)
            self.sound.set_volume(self.volume)
        except Exception:
            self.sound = None

        self.x = random.randint(0, self.width - self.size)
        self.y = random.randint(0, self.height - self.size)
        self.spawn_time = pygame.time.get_ticks()
        self.visible = True
        self.font = pygame.font.SysFont(None, 24)
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
        self.pos = (self.x, self.y)

    def set_volume(self, volume):
        self.volume = max(0.0, min(1.0, volume))
        if self.sound:
            try:
                self.sound.set_volume(self.volume)
                if self.sound_playing and self.sound_channel:
                    self.sound_channel.set_volume(self.volume)
            except Exception:
                pass

    def _get_weighted_clicks(self):
        num = int(random.triangular(1, 50, 45))
        return max(1, min(50, num))

    def _get_max_reward(self, score):
        if score <= 0:
            return 1

        if score < 1000:
            return max(1, score)

        if score <= 5000:
            return (score // 1000) * 1000

        if score < 10000:
            return max(1, int(score * 0.5))

        if score < 50000:
            return max(1, score // 2)

        extra = (score - 50000) // 50000
        divisor = 3 + extra
        return max(1, score // divisor)

    def _get_normal_event_reward(self, score):
        max_reward = self._get_max_reward(score)
        if max_reward <= 1:
            return 1
        return random.randint(1, max_reward)

    def _get_rare_event_reward(self, score):
        max_reward = self._get_max_reward(score)
        if max_reward <= 1:
            return 1
        return random.randint(1, max_reward)

    def update(self):
        if not self.visible:
            if self.sound_playing and self.sound_channel:
                self.sound_channel.stop()
                self.sound_playing = False
            return

        if not self.sound_playing and self.sound:
            try:
                self.sound_channel = self.sound.play(loops=-1)
                if self.sound_channel:
                    self.sound_channel.set_volume(self.volume)
                self.sound_playing = True
            except Exception:
                self.sound_playing = False

        current_time = pygame.time.get_ticks()
        if current_time - self.spawn_time >= self.time_to_live:
            if self.sound_playing and self.sound_channel:
                self.sound_channel.stop()
                self.sound_playing = False
            self.visible = False

    def draw(self):
        if not self.visible:
            return

        self.screen.blit(self.image, (self.x, self.y))

        elapsed_time = pygame.time.get_ticks() - self.spawn_time
        time_left = max(0, self.time_to_live - elapsed_time) // 1000
        text_color = (255, 255, 255) if self.event_type == "rare" else (0, 0, 0)

        if self.event_type == "rare":
            progress_text = self.font.render(f"{self.clicks_done}/{self.clicks_needed}", True, text_color)
            time_text = self.font.render(f"{time_left}s", True, text_color)
            progress_rect = progress_text.get_rect(center=(self.x + self.size//2, self.y + self.size//2 - 8))
            time_rect = time_text.get_rect(center=(self.x + self.size//2, self.y + self.size//2 + 8))
            self.screen.blit(progress_text, progress_rect)
            self.screen.blit(time_text, time_rect)
        else:
            time_text = self.font.render(f"{time_left}s", True, text_color)
            time_rect = time_text.get_rect(center=(self.x + self.size//2, self.y + self.size//2))
            self.screen.blit(time_text, time_rect)

    def handle_click(self, pos, score, upgrade_menu):
        if not self.visible:
            return score, False, 0

        mouse_buttons = pygame.mouse.get_pressed()
        
        if self.event_type == "normal":
            if not mouse_buttons[0]:
                return score, False, 0

        if self.rect.collidepoint(pos):
            if self.event_type == "rare":
                self.clicks_done += 1
                if self.clicks_done >= self.clicks_needed:
                    if self.sound_playing and self.sound_channel:
                        self.sound_channel.stop()
                        self.sound_playing = False
                    self.visible = False

                    if random.random() < self.upgrade_chance:
                        if hasattr(upgrade_menu, "purchase_random_upgrade"):
                            upgrade_menu.purchase_random_upgrade()
                        return score, True, 0

                    if random.random() < 0.01:
                        pontos_ganhos = score
                    else:
                        pontos_ganhos = self._get_rare_event_reward(score)

                    novo_score = score + pontos_ganhos
                    return novo_score, False, pontos_ganhos
                else:
                    return score, False, 0
                    
            else:
                if self.sound_playing and self.sound_channel:
                    self.sound_channel.stop()
                    self.sound_playing = False
                self.visible = False

                if random.random() < self.upgrade_chance:
                    if hasattr(upgrade_menu, "purchase_random_upgrade"):
                        upgrade_menu.purchase_random_upgrade()
                    return score, True, 0

                if random.random() < 0.01:
                    pontos_ganhos = score
                else:
                    pontos_ganhos = self._get_normal_event_reward(score)

                novo_score = score + pontos_ganhos
                return novo_score, False, pontos_ganhos

        return score, False, 0

    def handle_worker_click(self):
        if not self.visible:
            return False

        if self.event_type == "rare":
            self.clicks_done += 1
            if self.clicks_done >= self.clicks_needed:
                if self.sound_playing and self.sound_channel:
                    self.sound_channel.stop()
                    self.sound_playing = False
                self.visible = False
                return True
            return False
        else:
            if self.sound_playing and self.sound_channel:
                self.sound_channel.stop()
                self.sound_playing = False
            self.visible = False
            return True

    def force_stop_sound(self):
        if self.sound_playing and self.sound_channel:
            self.sound_channel.stop()
            self.sound_playing = False

    def is_rare(self):
        return self.event_type == "rare"