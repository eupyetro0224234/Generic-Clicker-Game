from controles import ControlsMenu
from config import FullSettingsMenu

class SubMenus:
    def __init__(self, screen, window_width, window_height):
        self.controls_menu = ControlsMenu(screen, window_width, window_height)
        self.settings_menu = FullSettingsMenu(screen, window_width, window_height)

    def draw(self):
        if self.controls_menu.visible:
            self.controls_menu.draw()
        if self.settings_menu.visible:
            self.settings_menu.draw()

    def handle_event(self, event):
        if self.settings_menu.visible:
            if self.settings_menu.handle_event(event):
                return True
        if self.controls_menu.visible:
            if self.controls_menu.handle_event(event):
                return True
        return False

    def toggle_menu(self, menu_name):
        if menu_name == "Controles":
            self.controls_menu.visible = not self.controls_menu.visible
            if self.controls_menu.visible:
                self.settings_menu.visible = False
        elif menu_name == "Configurações":
            self.settings_menu.visible = not self.settings_menu.visible
            if self.settings_menu.visible:
                self.controls_menu.visible = False
        else:
            # Se precisar lidar com outras opções depois
            pass
