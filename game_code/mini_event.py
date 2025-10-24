import pygame
import random
import os
import sys

def resource_path(relative_path):
    """Retorna o caminho absoluto de um recurso, mesmo dentro do executável PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class MiniEvent:
    def __init__(self, screen, width, height, event_type="normal"):
        """
        Evento unificado que pode ser normal (tipo 1) ou raro (tipo 2)
        
        Args:
            event_type: "normal" ou "rare"
        """
        self.screen = screen
        self.width = width
        self.height = height
        self.event_type = event_type
        
        # Configurações baseadas no tipo
        if self.event_type == "rare":
            # Configurações do evento raro (MiniEvent2)
            self.image_name = "mini-event2.png"
            self.sound_name = "mini-event-sound.mp3"
            self.size = 60
            self.base_color = (0, 100, 255)  # Azul
            self.text_label = "ME2"
            self.clicks_needed = self._get_weighted_clicks()
            self.clicks_done = 0
            
            # Duração baseada na dificuldade
            if self.clicks_needed <= 10:
                self.time_to_live = 10000  # 10 segundos
            else:
                self.time_to_live = 15000  # 15 segundos
                
            self.reward_multiplier = 2  # dobro do normal
            self.upgrade_chance = 0.05  # 5%
            
        else:
            # Configurações do evento normal (MiniEvent original)
            self.image_name = "mini-event.png"
            self.sound_name = "mini-event-sound.mp3"
            self.size = 50
            self.base_color = (255, 0, 0)  # Vermelho
            self.text_label = "EVENTO"
            self.clicks_needed = 1
            self.clicks_done = 0
            
            self.time_to_live = 10000  # 10 segundos
            self.reward_multiplier = 1
            self.upgrade_chance = 0.05

        # ✅ Caminho correto do asset
        self.image_path = resource_path(os.path.join("game_assets", self.image_name))
        self.sound_path = resource_path(os.path.join("game_assets", self.sound_name))

        try:
            self.image = pygame.image.load(self.image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.size, self.size))
        except Exception as e:
            # Fallback: cria uma superfície colorida
            self.image = pygame.Surface((self.size, self.size))
            self.image.fill(self.base_color)
            font = pygame.font.SysFont(None, 20)
            text = font.render(self.text_label, True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.size//2, self.size//2))
            self.image.blit(text, text_rect)

        # ✅ Carregar áudio
        try:
            self.sound = pygame.mixer.Sound(self.sound_path)
            self.sound_playing = False
            self.sound_channel = None
        except Exception as e:
            print(f"Erro ao carregar áudio do mini-evento ({self.event_type}): {e}")
            self.sound = None
            self.sound_playing = False
            self.sound_channel = None

        # Posição aleatória
        self.x = random.randint(0, self.width - self.size)
        self.y = random.randint(0, self.height - self.size)
        self.spawn_time = pygame.time.get_ticks()
        self.visible = True
        self.font = pygame.font.SysFont(None, 24)
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
        self.pos = (self.x, self.y)

    def _get_weighted_clicks(self):
        """Para eventos raros: retorna cliques necessários com viés para valores altos"""
        num = int(random.triangular(1, 50, 45))
        return max(1, min(50, num))

    def update(self):
        """Atualiza o tempo de vida do evento e controla o áudio."""
        if not self.visible:
            if self.sound_playing and self.sound_channel:
                self.sound_channel.stop()
                self.sound_playing = False
            return

        if not self.sound_playing and self.sound:
            try:
                self.sound_channel = self.sound.play(loops=-1)
                self.sound_playing = True
            except Exception as e:
                print(f"Erro ao tocar áudio do mini-evento: {e}")
                self.sound_playing = False

        current_time = pygame.time.get_ticks()
        if current_time - self.spawn_time >= self.time_to_live:
            if self.sound_playing and self.sound_channel:
                self.sound_channel.stop()
                self.sound_playing = False
            self.visible = False

    def draw(self):
        """Desenha o evento e informações relevantes."""
        if not self.visible:
            return

        self.screen.blit(self.image, (self.x, self.y))

        elapsed_time = pygame.time.get_ticks() - self.spawn_time
        time_left = max(0, self.time_to_live - elapsed_time) // 1000

        # Define a cor do texto
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
        """Detecta clique e aplica recompensa. Retorna (novo_score, upgrade_obtido, pontos_ganhos)"""
        if not self.visible:
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

                    pontos_ganhos = random.randint(6, 10) * 1000 * self.reward_multiplier
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

                pontos_ganhos = random.randint(6, 10) * 1000 * self.reward_multiplier
                novo_score = score + pontos_ganhos
                return novo_score, False, pontos_ganhos

        return score, False, 0

    def handle_worker_click(self):
        """Chamado por trabalhadores para simular clique automático."""
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
        """Para o som forçadamente."""
        if self.sound_playing and self.sound_channel:
            self.sound_channel.stop()
            self.sound_playing = False

    def is_rare(self):
        """Retorna True se este é um evento raro."""
        return self.event_type == "rare"
