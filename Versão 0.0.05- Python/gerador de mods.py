import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 1280, 720
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gerador de Mod")
FONT = pygame.font.SysFont(None, 36)
SMALL_FONT = pygame.font.SysFont(None, 28)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (220, 220, 220)
DARK_GRAY = (50, 50, 50)

clock = pygame.time.Clock()

class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = DARK_GRAY
        self.text = text
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
            self.txt_surface = FONT.render(self.text, True, BLACK)

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, self.rect, 0)
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, BLACK, self.rect, 2)

    def get_text(self):
        return self.text

class Button:
    def __init__(self, x, y, w, h, text, callback):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.callback = callback

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.callback()

    def draw(self, screen):
        pygame.draw.rect(screen, GRAY, self.rect)
        text_surface = FONT.render(self.text, True, BLACK)
        screen.blit(text_surface, (self.rect.centerx - text_surface.get_width() // 2,
                                   self.rect.centery - text_surface.get_height() // 2))

class Checkbox:
    def __init__(self, x, y, label):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.label = label
        self.checked = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.checked = not self.checked

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        if self.checked:
            pygame.draw.line(screen, BLACK, self.rect.topleft, self.rect.bottomright, 2)
            pygame.draw.line(screen, BLACK, self.rect.topright, self.rect.bottomleft, 2)
        label_surface = SMALL_FONT.render(self.label, True, BLACK)
        screen.blit(label_surface, (self.rect.right + 10, self.rect.y - 2))

    def is_checked(self):
        return self.checked

class ColorPicker:
    def __init__(self, x, y, width=200, height=200):
        self.rect = pygame.Rect(x, y, width, height)
        self.surface = pygame.Surface((width, height))
        for i in range(width):
            for j in range(height):
                color = pygame.Color(0)
                color.hsva = (i * 360 / width, 100, 100 - (j * 100 / height), 100)
                self.surface.set_at((i, j), color)
        self.selected_color = (255, 255, 255)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                x, y = event.pos[0] - self.rect.x, event.pos[1] - self.rect.y
                self.selected_color = self.surface.get_at((x, y))[:3]

    def draw(self, screen):
        screen.blit(self.surface, (self.rect.x, self.rect.y))
        pygame.draw.rect(screen, BLACK, self.rect, 2)

    def get_color(self):
        return self.selected_color

# Inicialização
page = 0
mod_name_input = InputBox(100, 100, 300, 40)
creator_input = InputBox(100, 180, 300, 40)
version_input = InputBox(100, 260, 300, 40)
next_button = Button(100, 350, 150, 40, "Próximo", lambda: next_page())

animation_checkbox = Checkbox(100, 100, "Animação Ativada")
pixel_size_input = InputBox(100, 180, 300, 40)
frequency_input = InputBox(100, 260, 300, 40)
next_button2 = Button(100, 350, 150, 40, "Próximo", lambda: next_page())

style_options = ["Clássico", "Moderno", "Retrô"]
current_style = 0
def toggle_style():
    global current_style
    current_style = (current_style + 1) % len(style_options)
style_button = Button(100, 100, 300, 40, style_options[current_style], toggle_style)
color_picker = ColorPicker(100, 180)
color_display_rect = pygame.Rect(320, 180, 80, 80)

colors_chosen = []
add_color_button = Button(100, 400, 180, 40, "Adicionar cor", lambda: add_color())

next_button3 = Button(100, 500, 150, 40, "Finalizar", lambda: print("Finalizado!"))


def next_page():
    global page
    if page < 2:
        page += 1

def add_color():
    color = color_picker.get_color()
    if color not in colors_chosen:
        colors_chosen.append(color)

def draw_page():
    SCREEN.fill(LIGHT_GRAY)
    if page == 0:
        draw_text("Nome do Mod:", 100, 70)
        mod_name_input.draw(SCREEN)
        draw_text("Criador:", 100, 150)
        creator_input.draw(SCREEN)
        draw_text("Versão mínima do jogo:", 100, 230)
        version_input.draw(SCREEN)
        next_button.draw(SCREEN)
    elif page == 1:
        draw_text("Configurações de Animação:", 100, 50)
        animation_checkbox.draw(SCREEN)
        draw_text("Tamanho dos Pixels:", 100, 150)
        pixel_size_input.draw(SCREEN)
        draw_text("Frequência de Atualização:", 100, 230)
        frequency_input.draw(SCREEN)
        next_button2.draw(SCREEN)
    elif page == 2:
        draw_text("Estilo do Mod:", 100, 70)
        style_button.text = style_options[current_style]
        style_button.draw(SCREEN)
        draw_text("Escolha uma cor:", 100, 150)
        color_picker.draw(SCREEN)
        pygame.draw.rect(SCREEN, color_picker.get_color(), color_display_rect)
        pygame.draw.rect(SCREEN, BLACK, color_display_rect, 2)
        add_color_button.draw(SCREEN)
        draw_text("Cores adicionadas:", 500, 70)
        for i, color in enumerate(colors_chosen):
            pygame.draw.rect(SCREEN, color, (500 + (i * 60), 100, 50, 50))
            pygame.draw.rect(SCREEN, BLACK, (500 + (i * 60), 100, 50, 50), 2)
        next_button3.draw(SCREEN)

def draw_text(text, x, y):
    surface = FONT.render(text, True, BLACK)
    SCREEN.blit(surface, (x, y))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if page == 0:
            mod_name_input.handle_event(event)
            creator_input.handle_event(event)
            version_input.handle_event(event)
            next_button.handle_event(event)
        elif page == 1:
            animation_checkbox.handle_event(event)
            pixel_size_input.handle_event(event)
            frequency_input.handle_event(event)
            next_button2.handle_event(event)
        elif page == 2:
            style_button.handle_event(event)
            color_picker.handle_event(event)
            add_color_button.handle_event(event)
            next_button3.handle_event(event)

    draw_page()
    pygame.display.flip()
    clock.tick(60)
