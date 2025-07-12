import os
import json
import pygame

class RestoreDataMenu:
    def __init__(self, config_menu, score_manager, get_score_callback, set_score_callback, achievement_tracker, upgrade_menu):
        self.config_menu = config_menu
        self.screen = config_menu.screen
        self.width = 420
        self.height = 50
        self.font = pygame.font.SysFont(None, 26)
        self.bg_color = (200, 100, 100, 220)
        self.text_color = (255, 255, 255)
        self.option_rect = None
        self.visible = False
        
        self.score_manager = score_manager
        self.get_score = get_score_callback
        self.set_score = set_score_callback
        self.tracker = achievement_tracker
        self.upgrade_menu = upgrade_menu
        
        # Para mostrar confirmação simples
        self.confirming = False
        self.confirm_text = ""
        self.confirm_result = None

    def draw(self):
        if not self.config_menu.is_open:
            self.visible = False
            return

        if self.visible:
            # Desenha um botão simples abaixo do menu
            x = self.config_menu.window_width - self.width - 6
            y = self.config_menu.icon_rect.bottom + 8 + self.config_menu.option_height * 5 + 20
            rect = pygame.Rect(x, y, self.width, self.height)
            self.option_rect = rect
            
            pygame.draw.rect(self.screen, self.bg_color, rect, border_radius=12)
            txt_surf = self.font.render("Restaurar dados do backup", True, self.text_color)
            txt_rect = txt_surf.get_rect(center=rect.center)
            self.screen.blit(txt_surf, txt_rect)

        # Se estiver confirmando, mostra caixa de diálogo simples
        if self.confirming:
            self.draw_confirmation()

    def draw_confirmation(self):
        w, h = 400, 150
        x = self.config_menu.window_width // 2 - w // 2
        y = self.config_menu.window_height // 2 - h // 2
        bg_rect = pygame.Rect(x, y, w, h)

        pygame.draw.rect(self.screen, (50, 50, 50), bg_rect, border_radius=16)
        pygame.draw.rect(self.screen, (200, 200, 200), bg_rect, 3, border_radius=16)

        lines = ["Tem certeza que deseja restaurar os dados?"]
        lines.append("Isto substituirá seu progresso atual.")
        lines.append("Pressione Y para confirmar ou N para cancelar.")

        font = pygame.font.SysFont(None, 22)
        for i, line in enumerate(lines):
            surf = font.render(line, True, (255, 255, 255))
            self.screen.blit(surf, (x + 20, y + 20 + i*30))

    def handle_event(self, event):
        if self.confirming:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    self.confirm_result = True
                    self.confirming = False
                    self.restore_data()
                    self.visible = False
                    self.config_menu.is_open = False
                    return True
                elif event.key == pygame.K_n or event.key == pygame.K_ESCAPE:
                    self.confirm_result = False
                    self.confirming = False
                    return True
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.visible:
            if self.option_rect and self.option_rect.collidepoint(event.pos):
                self.confirming = True
                return True

        return False

    def restore_data(self):
        backup_path = os.path.join(self.score_manager.folder_path, "old.json")
        if not os.path.isfile(backup_path):
            print("[RestoreDataMenu] Backup old.json não encontrado.")
            return

        try:
            with open(backup_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            print("[RestoreDataMenu] Restaurando dados do backup...")

            # Atualiza score
            self.set_score(data.get("score", 0))

            # Atualiza controles visíveis
            if hasattr(self.config_menu.controls_menu, 'visible'):
                self.config_menu.controls_menu.visible = data.get("controls_visible", False)

            # Atualiza conquistas
            unlocked = data.get("achievements", [])
            if self.tracker:
                self.tracker.unlocked = set(unlocked)
                # Marca conquistas desbloqueadas
                for ach in self.tracker.achievements:
                    ach.unlocked = ach.id in self.tracker.unlocked

            # Atualiza upgrades
            if self.upgrade_menu:
                self.upgrade_menu.load_upgrades(data.get("upgrades", {}))

            # Atualiza mini_event_click_count
            if self.tracker:
                self.tracker.mini_event_clicks = data.get("mini_event_click_count", 0)

            # Salva imediatamente o score.dat atualizado
            self.score_manager.save_data(
                self.get_score(),
                self.config_menu.controls_menu.visible,
                list(self.tracker.unlocked) if self.tracker else [],
                self.upgrade_menu.purchased if self.upgrade_menu else {},
                self.tracker.mini_event_clicks if self.tracker else 0
            )

            # Apaga backup
            os.remove(backup_path)
            print("[RestoreDataMenu] Backup old.json removido após restauração.")

        except Exception as e:
            print(f"[RestoreDataMenu] Erro ao restaurar dados: {e}")
