import pygame
import urllib.request
import json
from datetime import datetime

class EventoManager:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.evento_ativo = None
        self.font_titulo = pygame.font.SysFont(None, 48)
        self.font_texto = pygame.font.SysFont(None, 28)
        self.bg_color = (255, 255, 255)
        self.border_color = (0, 120, 255)
        self.text_color = (20, 20, 20)
        self.link_json = "https://raw.githubusercontent.com/eupyetro0224234/Generic-Clicker-Game/refs/heads/main/eventos.json"
        self.verificado = False

    def verificar_eventos(self):
        if self.verificado:
            return
        try:
            response = urllib.request.urlopen(self.link_json, timeout=5)
            data = json.loads(response.read().decode())

            hoje = datetime.now().date()
            for evento in data:
                inicio = datetime.strptime(evento["data_inicio"], "%Y-%m-%d").date()
                fim = datetime.strptime(evento["data_fim"], "%Y-%m-%d").date()

                if inicio <= hoje <= fim:
                    self.evento_ativo = {
                        "titulo": evento["titulo"],
                        "mensagem": evento["mensagem"]
                    }
                    break
        except Exception as e:
            print("Erro ao verificar eventos:", e)
        self.verificado = True

    def draw(self):
        if not self.evento_ativo:
            return

        pygame.draw.rect(self.screen, self.bg_color, (100, 100, self.width - 200, 150), border_radius=16)
        pygame.draw.rect(self.screen, self.border_color, (100, 100, self.width - 200, 150), 4, border_radius=16)

        titulo_surf = self.font_titulo.render(self.evento_ativo["titulo"], True, self.text_color)
        msg_surf = self.font_texto.render(self.evento_ativo["mensagem"], True, self.text_color)

        self.screen.blit(titulo_surf, (self.width // 2 - titulo_surf.get_width() // 2, 120))
        self.screen.blit(msg_surf, (self.width // 2 - msg_surf.get_width() // 2, 180))
