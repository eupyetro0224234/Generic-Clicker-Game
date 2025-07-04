import pygame
import os
import urllib.request
from controles import ControlsMenu
from config import FullSettingsMenu

class ConfigMenu:
    def __init__(self, screen, window_width, window_height, loading_callback=None):
        self.screen = screen
        self.font = pygame.font.SysFont(None, 24)
        self.bg_color = (180, 210, 255)
        self.option_color = (255, 255, 255)
        self.option_border = (200, 220, 250)
        self.text_color = (40, 40, 60)

        self.option_height = 38
        self.option_radius = 10
        self.padding_x = 6
        self.spacing = 5

        self.is_open = False
        self.animation_progress = 0.0
        self.animation_speed = 0.12
        self.fade_speed = 10  # velocidade do fade in/out da tela

        localappdata = os.getenv("LOCALAPPDATA")
        self.assets_folder = os.path.join(localappdata, ".assests")
        os.makedirs(self.assets_folder, exist_ok=True)

        self.icon_url = "https://i.postimg.cc/hGf3VRqY/image-removebg-preview-5.png"
        self.icon_path = os.path.join(self.assets_folder, "config_icon.png")

        if not os.path.isfile(self.icon_path):
            try:
                if loading_callback:
                    loading_callback(10, "Baixando ícone de configurações...")
                urllib.request.urlretrieve(self.icon_url, self.icon_path)
            except Exception as e:
                print("Erro ao baixar ícone de configurações:", e)

        self.icon_image = None
        try:
            self.icon_image = pygame.image.load(self.icon_path).convert_alpha()
            self.icon_image = pygame.transform.smoothscale(self.icon_image, (42, 42))
        except Exception as e:
            print("Erro ao carregar ícone:", e)

        self.icon_rect = self.icon_image.get_rect() if self.icon_image else pygame.Rect(0, 0, 48, 48)
        self.icon_rect.topright = (window_width - 6, 6)

        # Adicionei opção "Sair" no final da lista
        self.options = ["Configurações", "Controles", "Sair"]
        self.max_height = len(self.options) * (self.option_height + self.spacing)

        self.controls_menu = ControlsMenu(screen, window_width, window_height)
        self.settings_menu = FullSettingsMenu(screen, window_width, window_height)

        # Estado para confirmação de saída
        self.confirm_exit = False

        # Para fade out/in da tela ao sair
        self.fading = False
        self.fade_alpha = 255  # Começa em 255 para fade in
        self.fade_surface = pygame.Surface((window_width, window_height))
        self.fade_surface.fill((0, 0, 0))
        self.fade_surface.set_alpha(self.fade_alpha)

    def draw_icon(self):
        if self.icon_image:
            self.screen.blit(self.icon_image, self.icon_rect)
        else:
            pygame.draw.rect(self.screen, (70, 130, 180), self.icon_rect)

    def update_animation(self):
        if self.is_open and self.fade_alpha > 0:
            # Fade in
            self.fade_alpha = max(0, self.fade_alpha - self.fade_speed)
            self.fade_surface.set_alpha(self.fade_alpha)
        elif not self.is_open and self.fade_alpha < 255:
            # Fade out da abertura (se fechar sem sair)
            self.fade_alpha = min(255, self.fade_alpha + self.fade_speed)
            self.fade_surface.set_alpha(self.fade_alpha)

        if self.is_open:
            self.animation_progress = min(1.0, self.animation_progress + self.animation_speed)
        else:
            self.animation_progress = max(0.0, self.animation_progress - self.animation_speed)

    def draw_menu(self):
        self.update_animation()
        if self.animation_progress <= 0:
            return

        width = 190
        vertical_padding = 6
        full_height = len(self.options) * (self.option_height + self.spacing) - self.spacing + vertical_padding * 2
        height = int(full_height * self.animation_progress)

        margin_right = 4
        x = self.screen.get_width() - width - margin_right
        y = self.icon_rect.bottom + 6

        menu_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(menu_surface, self.bg_color, (0, 0, width, height), border_radius=12)

        for i, option in enumerate(self.options):
            oy = vertical_padding + i * (self.option_height + self.spacing)
            if oy + self.option_height > height:
                break

            option_rect = pygame.Rect(
                self.padding_x,
                oy,
                width - self.padding_x * 2,
                self.option_height
            )
            pygame.draw.rect(menu_surface, self.option_color, option_rect, border_radius=self.option_radius)
            pygame.draw.rect(menu_surface, self.option_border, option_rect, width=1, border_radius=self.option_radius)

            text_surf = self.font.render(option, True, self.text_color)
            text_rect = text_surf.get_rect(center=option_rect.center)
            menu_surface.blit(text_surf, text_rect)

        self.screen.blit(menu_surface, (x, y))

        # Se estiver confirmando saída, desenhar janela modal simples
        if self.confirm_exit:
            self.draw_confirm_exit()

        # Desenhar fade in/out da abertura do menu
        if self.is_open and self.fade_alpha > 0:
            self.screen.blit(self.fade_surface, (0, 0))

    def draw_confirm_exit(self):
        # Tela escurecida
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        w, h = 300, 140
        x = (self.screen.get_width() - w) // 2
        y = (self.screen.get_height() - h) // 2
        rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(self.screen, (255, 255, 255), rect, border_radius=12)
        pygame.draw.rect(self.screen, (0, 0, 0), rect, width=2, border_radius=12)

        msg_surf = self.font.render("Tem certeza que deseja sair?", True, (40, 40, 40))
        msg_rect = msg_surf.get_rect(center=(x + w // 2, y + 40))
        self.screen.blit(msg_surf, msg_rect)

        # Botões Sim e Não
        btn_w, btn_h = 80, 35
        btn_spacing = 40
        btn_y = y + h - 55

        btn_sim_rect = pygame.Rect(x + w // 2 - btn_w - btn_spacing//2, btn_y, btn_w, btn_h)
        btn_nao_rect = pygame.Rect(x + w // 2 + btn_spacing//2, btn_y, btn_w, btn_h)

        pygame.draw.rect(self.screen, (100, 200, 100), btn_sim_rect, border_radius=8)
        pygame.draw.rect(self.screen, (200, 100, 100), btn_nao_rect, border_radius=8)

        sim_text = self.font.render("Sim", True, (255, 255, 255))
        nao_text = self.font.render("Não", True, (255, 255, 255))

        self.screen.blit(sim_text, sim_text.get_rect(center=btn_sim_rect.center))
        self.screen.blit(nao_text, nao_text.get_rect(center=btn_nao_rect.center))

        # Guardar para detectar clique depois
        self.btn_sim_rect = btn_sim_rect
        self.btn_nao_rect = btn_nao_rect

    def draw(self):
        self.draw_menu()
        if self.controls_menu.visible:
            self.controls_menu.draw()
        if self.settings_menu.visible:
            self.settings_menu.draw()

    def handle_event(self, event):
        # Se estiver no modal de confirmação, trata somente ele
        if self.confirm_exit:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.btn_sim_rect.collidepoint(event.pos):
                    self.fading = True  # inicia fade out e sair
                    self.confirm_exit = False
                elif self.btn_nao_rect.collidepoint(event.pos):
                    self.confirm_exit = False
                return True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.confirm_exit = False
                    return True
            return False

        # Primeiro deixa o submenu (configurações/controles) tentar tratar o evento
        if self.settings_menu.visible:
            if self.settings_menu.handle_event(event):
                return True
        if self.controls_menu.visible:
            if self.controls_menu.handle_event(event):
                return True

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.fading:
                # Durante fade, bloqueia eventos
                return True

            if self.icon_rect.collidepoint(event.pos):
                self.is_open = not self.is_open
                return True

            if self.is_open:
                width = 190
                vertical_padding = 6
                full_height = len(self.options) * (self.option_height + self.spacing) - self.spacing + vertical_padding * 2
                height = int(full_height * self.animation_progress)
                margin_right = 4
                x = self.screen.get_width() - width - margin_right
                y = self.icon_rect.bottom + 6
                rect = pygame.Rect(x, y, width, height)

                if rect.collidepoint(event.pos):
                    relative_y = event.pos[1] - y - vertical_padding
                    index = relative_y // (self.option_height + self.spacing)
                    if 0 <= index < len(self.options):
                        selected = self.options[index]
                        if selected == "Controles":
                            self.controls_menu.visible = not self.controls_menu.visible
                            self.settings_menu.visible = False
                        elif selected == "Configurações":
                            self.settings_menu.visible = not self.settings_menu.visible
                            self.controls_menu.visible = False
                        elif selected == "Sair":
                            # Pergunta confirmação antes de sair
                            self.confirm_exit = True
                    return True
                else:
                    # Clique fora do menu principal fecha ele (não fecha submenus)
                    self.is_open = False
                    return True

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.fading:
                    return True  # bloqueia escape durante fade
                if self.confirm_exit:
                    self.confirm_exit = False
                    return True
                if self.settings_menu.visible:
                    self.settings_menu.visible = False
                    return True
                if self.controls_menu.visible:
                    self.controls_menu.visible = False
                    return True
                if self.is_open:
                    self.is_open = False
                    return True

        return False

    def update_fade(self):
        # Atualiza fade out da saída e fecha o jogo quando termina
        if self.fading:
            self.fade_alpha += self.fade_speed
            if self.fade_alpha >= 255:
                pygame.quit()
                sys.exit()
            else:
                self.fade_surface.set_alpha(self.fade_alpha)
                self.screen.blit(self.fade_surface, (0, 0))
                pygame.display.flip()
