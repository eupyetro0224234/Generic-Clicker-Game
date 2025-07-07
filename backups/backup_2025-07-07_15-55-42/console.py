import pygame

console_instance = None

def open_console(screen, width, height):
    global console_instance
    if console_instance is None:
        console_instance = Console(screen, width, height)
    console_instance.visible = True
    return console_instance

class Console:
    def __init__(self, screen, width, height):
        # seu código aqui (como já está)
        self.screen = screen
        self.width = width
        self.height = height
        self.font = pygame.font.SysFont("Consolas", 24)
        self.lines = ["Console ativado!", "Digite comandos..."]
        self.visible = True
        self.input_text = ""
        self.max_lines = 6

    def handle_event(self, event):
        # seu código...

    def execute_command(self, command):
        # seu código...

    def draw(self):
        # seu código...
