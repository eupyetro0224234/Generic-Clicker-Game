import os
import json
import pygame

class ConfigManager:
    def __init__(self, folder_name=".assests", filename="config.json"):
        localappdata = os.getenv("LOCALAPPDATA")
        if not localappdata:
            raise EnvironmentError("Variável LOCALAPPDATA não encontrada no sistema.")
        
        self.folder_path = os.path.join(localappdata, folder_name)
        os.makedirs(self.folder_path, exist_ok=True)
        self.file_path = os.path.join(self.folder_path, filename)
        
        self.default_config = {
            "configurações gerais": {
                "clicks sobem com o botão direito": True,
                "clicks sobem com o botão esquerdo": True,
                "clicks sobem com o click botão de rolagem do mouse": True,
                "clicks sobem com a rolagem do mouse": True
            },
            "mods e texturas": {
                "ativar mods": False,
                "ativar texturas": False
            }
        }
        
        self.config = {}
        self.load_config()
    
    def load_config(self):
        if not os.path.isfile(self.file_path):
            self.config = self.default_config
            self.save_config()
        else:
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
            except Exception:
                self.config = self.default_config
                self.save_config()

    def save_config(self):
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print("Erro ao salvar config:", e)

    def get_option(self, section, option):
        return self.config.get(section, {}).get(option, None)

    def set_option(self, section, option, value):
        if section in self.config and option in self.config[section]:
            self.config[section][option] = value
            self.save_config()

class ConfigMenu:
    def __init__(self, screen, width, height, config_manager):
        self.screen = screen
        self.width = width
        self.height = height
        self.config_manager = config_manager
        
        self.bg_color = (220, 230, 255)
        self.font_title = pygame.font.SysFont(None, 36)
        self.font_option = pygame.font.SysFont(None, 28)
        self.text_color = (30, 30, 60)
        self.box_color = (200, 220, 255)
        self.box_border = (150, 180, 230)
        
        self.margin = 20
        self.spacing = 12
        self.option_height = 32
        
        self.visible = False
        
        # Prepara retângulos clicáveis para as opções
        self.option_rects = []
        self.update_option_rects()

    def update_option_rects(self):
        self.option_rects = []
        y = self.margin + 60  # espaço para título
        for section in self.config_manager.config:
            y += self.option_height  # espaço para o título da seção
            for option in self.config_manager.config[section]:
                rect = pygame.Rect(
                    self.margin + 30,
                    y,
                    self.width - 2 * self.margin - 60,
                    self.option_height
                )
                self.option_rects.append((section, option, rect))
                y += self.option_height + self.spacing

    def draw(self):
        if not self.visible:
            return
        
        self.screen.fill(self.bg_color)
        
        y = self.margin
        # Título
        title_surf = self.font_title.render("Configurações", True, self.text_color)
        self.screen.blit(title_surf, (self.margin, y))
        y += 60
        
        for section in self.config_manager.config:
            # Nome da seção
            section_surf = self.font_option.render(section.capitalize(), True, self.text_color)
            self.screen.blit(section_surf, (self.margin + 10, y))
            y += self.option_height
            
            for option in self.config_manager.config[section]:
                value = self.config_manager.get_option(section, option)
                option_text = f"{option} : {'Sim' if value else 'Não'}"
                
                # Busca retângulo para desenhar fundo
                rect = None
                for s, o, r in self.option_rects:
                    if s == section and o == option:
                        rect = r
                        break
                if rect:
                    pygame.draw.rect(self.screen, self.box_color, rect, border_radius=8)
                    pygame.draw.rect(self.screen, self.box_border, rect, 2, border_radius=8)
                    
                    option_surf = self.font_option.render(option_text, True, self.text_color)
                    option_rect = option_surf.get_rect(center=rect.center)
                    self.screen.blit(option_surf, option_rect)

                y += self.option_height + self.spacing
    
    def handle_event(self, event):
        if not self.visible:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.visible = False
                return True
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            for section, option, rect in self.option_rects:
                if rect.collidepoint(mx, my):
                    current = self.config_manager.get_option(section, option)
                    self.config_manager.set_option(section, option, not current)
                    return True
        
        return False
