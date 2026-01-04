import pygame, pytz, sys, os
from datetime import datetime

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class StatisticsMenu:
    def __init__(self, screen, window_width, window_height, game_reference=None):
        self.screen = screen
        self.width = window_width
        self.height = window_height
        self.game = game_reference

        self.bg_color = (255, 182, 193)
        self.text_color = (47, 24, 63)
        self.option_height = 60
        self.option_radius = 15
        self.padding_x = 20
        self.padding_y = 20
        self.spacing_x = 20
        self.spacing_y = 20
        self.options_per_row = 2

        self.visible = False

        self.title_font = pygame.font.SysFont(None, 42)
        self.font = pygame.font.SysFont(None, 32)
        self.emoji_font = pygame.font.SysFont("segoeuiemoji", 28)
        
        self.hovered_option = None
        self.button_rects = []
        
        # Botão de fechar igual ao do primeiro código
        self.close_button_rect = pygame.Rect(self.width - 80, 15, 40, 40)
        try:
            close_image_path = resource_path("game_assets/close.png")
            if not os.path.exists(close_image_path):
                close_image_path = os.path.join("..", "game_assets", "close.png")
            self.close_image = pygame.image.load(close_image_path).convert_alpha()
            # Tamanho reduzido para 40x40 pixels
            target_size = (40, 40)
            self.close_image = pygame.transform.smoothscale(self.close_image, target_size)
        except Exception:
            self.close_image = None

        self.scroll_y = 0
        self.scroll_speed = 30
        self.max_scroll = 0
        self.scrollbar_width = 12
        self.scrollbar_rect = None
        self.is_scrolling = False
        self.scroll_drag_start = 0

        self.first_join_date = self.get_first_join_date()

    def get_first_join_date(self):
        if not self.game:
            return "Não disponível"
            
        if hasattr(self.game, 'score_manager'):
            try:
                data = self.game.score_manager.load_data()
                if data and len(data) > 15:
                    return data[15]
                
                tz_brasilia = pytz.timezone('America/Sao_Paulo')
                first_join = datetime.now(tz_brasilia).strftime("%d/%m/%Y - %H:%M")
                return first_join
            except:
                pass
        
        return "Não disponível"

    def format_number(self, number):
        """Formata números para exibição com separadores de milhar"""
        try:
            if isinstance(number, str):
                number = float(number.replace('.', '').replace(',', ''))
            return f"{int(number):,}".replace(",", ".")
        except (ValueError, TypeError):
            return "0"

    def get_statistics_data(self):
        """Obtém dados reais das estatísticas do jogo"""
        if not self.game:
            return self.get_default_statistics()
            
        try:
            # Pontuações
            total_score = self.game.score
            max_score = getattr(self.game, 'max_score', 0)
            total_score_earned = getattr(self.game, 'total_score_earned', 0)
            
            # Cliques - garantindo que sejam números válidos
            normal_clicks = getattr(self.game.tracker, 'normal_clicks', 0)
            mini_event_clicks = getattr(self.game.tracker, 'mini_event_clicks', 0)
            total_clicks = normal_clicks + mini_event_clicks
            
            # Conquistas
            unlocked_achievements = len(getattr(self.game.tracker, 'unlocked', {}))
            total_achievements = len(getattr(self.game.tracker, 'achievements', {}))
            
            # Tempo de jogo
            total_play_time = self.game.get_total_play_time()
            formatted_time = self.game.format_time(total_play_time) if hasattr(self.game, 'format_time') else "00:00:00"
            
            # Upgrades
            purchased_upgrades = 0
            if hasattr(self.game, 'upgrade_menu') and hasattr(self.game.upgrade_menu, 'purchased'):
                purchased_upgrades = sum(self.game.upgrade_menu.purchased.values())
            
            # Eventos
            eventos_participados = sum(getattr(self.game, 'eventos_participados', {}).values())
            
            # Mini eventos
            mini_eventos_sessao = self.game.get_mini_events_session_total() if hasattr(self.game, 'get_mini_events_session_total') else 0
            # Mini eventos totais (nunca resetam, como os clicks totais)
            mini_event1_total = getattr(self.game, 'mini_event1_total', 0)
            mini_event2_total = getattr(self.game, 'mini_event2_total', 0)
            mini_eventos_total = mini_event1_total + mini_event2_total
            
            # Sequência
            streak_data = getattr(self.game, 'streak_data', {})
            current_streak = streak_data.get('current_streak', 0)
            max_streak = streak_data.get('max_streak', 0)
            
            # Primeira entrada
            if self.first_join_date == "Não disponível":
                self.first_join_date = self.get_first_join_date()
            
            return {
                "Pontuação Atual": total_score,
                "Pontuação Máxima": max_score,
                "Pontuação Total": total_score_earned,
                "Cliques Totais": total_clicks,
                "Conquistas Desbloqueadas": f"{unlocked_achievements}/{total_achievements}",
                "Tempo de Jogo": formatted_time,
                "Upgrades Comprados": purchased_upgrades,
                "Eventos Participados": eventos_participados,
                "Mini Eventos Sessão": mini_eventos_sessao,
                "Mini Eventos Totais": mini_eventos_total,
                "Primeira Entrada": self.first_join_date,
                "Sequência Atual": f"{current_streak} dias",
                "Maior Sequência": f"{max_streak} dias"
            }
        except Exception as e:
            print(f"Erro ao obter estatísticas: {e}")
            return self.get_default_statistics()

    def get_default_statistics(self):
        """Retorna estatísticas padrão caso haja erro"""
        return {
            "Pontuação Atual": "0",
            "Pontuação Máxima": "0",
            "Pontuação Total": "0",
            "Cliques Totais": "0",
            "Conquistas Desbloqueadas": "0/0",
            "Tempo de Jogo": "00:00:00",
            "Upgrades Comprados": "0",
            "Eventos Participados": "0",
            "Mini Eventos Sessão": "0",
            "Mini Eventos Totais": "0",
            "Primeira Entrada": "Não disponível",
            "Sequência Atual": "0 dias",
            "Maior Sequência": "0 dias"
        }

    def draw_section_title(self, title, x, y):
        box_width = self.width - 2 * x - self.scrollbar_width - 10
        box_height = self.option_height
        box_rect = pygame.Rect(x, y - self.scroll_y, box_width, box_height)

        if box_rect.bottom < 0 or box_rect.top > self.height:
            return y + box_height + self.spacing_y

        azul_claro = (200, 190, 255, 230)
        pygame.draw.rect(self.screen, azul_claro, box_rect, border_radius=self.option_radius)
        pygame.draw.rect(self.screen, (150, 150, 150), box_rect, width=2, border_radius=self.option_radius)

        title_surf = self.title_font.render(title, True, self.text_color)
        title_rect = title_surf.get_rect(center=box_rect.center)
        self.screen.blit(title_surf, title_rect)

        return y + box_height + self.spacing_y

    def draw_stat_option(self, key, value, x, y, width):
        container_height = self.option_height
        container_rect = pygame.Rect(x, y - self.scroll_y, width, container_height)
        
        if container_rect.bottom < 0 or container_rect.top > self.height:
            return y + container_height + self.spacing_y

        shadow_surface = pygame.Surface((width + 6, container_height + 6), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 20), (0, 0, width + 6, container_height + 6), border_radius=15)
        self.screen.blit(shadow_surface, (x - 3, y - self.scroll_y - 3))
        
        color = (220, 235, 255)
        pygame.draw.rect(self.screen, color, container_rect, border_radius=self.option_radius)
        pygame.draw.rect(self.screen, (150, 150, 150), container_rect, width=2, border_radius=self.option_radius)
        
        text_surf = self.font.render(key, True, self.text_color)
        text_rect = text_surf.get_rect(midleft=(x + 20, y - self.scroll_y + container_height // 2))
        self.screen.blit(text_surf, text_rect)
        
        # Formata o valor corretamente
        if isinstance(value, (int, float)) and key not in ["Conquistas Desbloqueadas", "Tempo de Jogo", "Primeira Entrada", "Sequência Atual", "Maior Sequência"]:
            display_value = self.format_number(value)
        else:
            display_value = str(value)
            
        value_surf = self.font.render(display_value, True, self.text_color)
        value_rect = value_surf.get_rect(midright=(x + width - 20, y - self.scroll_y + container_height // 2))
        self.screen.blit(value_surf, value_rect)
        
        return y + container_height + self.spacing_y

    def draw_scrollbar(self):
        if self.max_scroll <= 0:
            return
            
        scroll_area_x = self.width - self.scrollbar_width - 5
        scroll_area_rect = pygame.Rect(scroll_area_x, 80, self.scrollbar_width, self.height - 100)
        
        visible_ratio = self.height / (self.max_scroll + self.height)
        thumb_height = max(30, visible_ratio * (self.height - 100))
        
        scroll_ratio = self.scroll_y / self.max_scroll
        thumb_y = 80 + scroll_ratio * ((self.height - 100) - thumb_height)
        
        self.scrollbar_rect = pygame.Rect(scroll_area_x, thumb_y, self.scrollbar_width, thumb_height)
        
        pygame.draw.rect(self.screen, (200, 200, 200, 150), scroll_area_rect, border_radius=6)
        
        pygame.draw.rect(self.screen, (100, 100, 100, 200), self.scrollbar_rect, border_radius=6)
        pygame.draw.rect(self.screen, (70, 70, 70), self.scrollbar_rect, 1, border_radius=6)

    def calculate_content_height(self):
        stats_data = self.get_statistics_data()
        
        total_height = 90
        
        total_height += self.option_height + self.spacing_y
        total_height += (self.option_height + self.spacing_y) * 2
        total_height += 40
        
        total_height += self.option_height + self.spacing_y
        total_height += (self.option_height + self.spacing_y) * 8
        total_height += 40
        
        total_height += self.option_height + self.spacing_y
        total_height += (self.option_height + self.spacing_y) * 3
        
        total_height += 20
        
        self.max_scroll = max(0, total_height - self.height)
        return total_height

    def draw_close_button(self):
        """Desenha o botão de fechar igual ao do primeiro código"""
        if self.close_image:
            image_rect = self.close_image.get_rect(center=self.close_button_rect.center)
            self.screen.blit(self.close_image, image_rect)
        else:
            # Fallback se a imagem não carregar
            pygame.draw.rect(self.screen, (255, 100, 100), self.close_button_rect, border_radius=6)
            center_x, center_y = self.close_button_rect.center
            line_length = 15
            pygame.draw.line(self.screen, (255, 255, 255), (center_x - line_length, center_y - line_length),
                            (center_x + line_length, center_y + line_length), 2)
            pygame.draw.line(self.screen, (255, 255, 255), (center_x - line_length, center_y + line_length),
                            (center_x + line_length, center_y - line_length), 2)

    def draw(self):
        if not self.visible:
            return

        self.button_rects = []

        self.screen.fill(self.bg_color)

        self.calculate_content_height()
        
        self.scroll_y = max(0, min(self.scroll_y, self.max_scroll))

        x = self.padding_x
        y = self.padding_y

        title_font = pygame.font.SysFont(None, 48)
        title_surf = title_font.render("Estatísticas", True, self.text_color)
        title_rect = title_surf.get_rect(center=(self.width // 2, 35))
        self.screen.blit(title_surf, title_rect)

        y = 90

        stats_data = self.get_statistics_data()

        slider_width = self.width - 2 * x - self.scrollbar_width - 10

        y = self.draw_section_title("Pontuação", x, y)
        y = self.draw_stat_option("Pontuação Atual", stats_data.get("Pontuação Atual", "0"), x, y, slider_width)
        y = self.draw_stat_option("Pontuação Máxima", stats_data.get("Pontuação Máxima", "0"), x, y, slider_width)
        y = self.draw_stat_option("Pontuação Total", stats_data.get("Pontuação Total", "0"), x, y, slider_width)

        y += 40

        y = self.draw_section_title("Progresso Geral", x, y)
        y = self.draw_stat_option("Cliques Totais", stats_data.get("Cliques Totais", "0"), x, y, slider_width)
        y = self.draw_stat_option("Conquistas Desbloqueadas", stats_data.get("Conquistas Desbloqueadas", "0/0"), x, y, slider_width)
        y = self.draw_stat_option("Tempo de Jogo", stats_data.get("Tempo de Jogo", "00:00:00"), x, y, slider_width)
        y = self.draw_stat_option("Upgrades Comprados", stats_data.get("Upgrades Comprados", "0"), x, y, slider_width)
        y = self.draw_stat_option("Eventos Participados", stats_data.get("Eventos Participados", "0"), x, y, slider_width)
        y = self.draw_stat_option("Primeira Entrada", stats_data.get("Primeira Entrada", "Não disponível"), x, y, slider_width)
        y = self.draw_stat_option("Sequência Atual", stats_data.get("Sequência Atual", "0 dias"), x, y, slider_width)
        y = self.draw_stat_option("Maior Sequência", stats_data.get("Maior Sequência", "0 dias"), x, y, slider_width)

        y += 40

        # CORRIGIDO: Agora mostra 2 estatísticas apenas
        y = self.draw_section_title("Mini Eventos", x, y)
        y = self.draw_stat_option("Mini Eventos Sessão", stats_data.get("Mini Eventos Sessão", "0"), x, y, slider_width)
        y = self.draw_stat_option("Mini Eventos Totais", stats_data.get("Mini Eventos Totais", "0"), x, y, slider_width)

        if self.max_scroll > 0:
            self.draw_scrollbar()

        self.draw_close_button()

    def handle_event(self, event):
        if not self.visible:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.visible = False
                return True
            elif event.key == pygame.K_UP:
                self.scroll_y = max(0, self.scroll_y - self.scroll_speed)
                return True
            elif event.key == pygame.K_DOWN:
                self.scroll_y = min(self.max_scroll, self.scroll_y + self.scroll_speed)
                return True
            elif event.key == pygame.K_PAGEUP:
                self.scroll_y = max(0, self.scroll_y - self.height // 2)
                return True
            elif event.key == pygame.K_PAGEDOWN:
                self.scroll_y = min(self.max_scroll, self.scroll_y + self.height // 2)
                return True
            elif event.key == pygame.K_HOME:
                self.scroll_y = 0
                return True
            elif event.key == pygame.K_END:
                self.scroll_y = self.max_scroll
                return True
            return True

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            
            # Verificar clique no botão de fechar (apenas botão esquerdo)
            if event.button == 1 and self.close_button_rect.collidepoint(mouse_pos):
                self.visible = False
                return True

            if self.scrollbar_rect and self.scrollbar_rect.collidepoint(mouse_pos):
                self.is_scrolling = True
                self.scroll_drag_start = mouse_pos[1] - self.scrollbar_rect.y
                return True

            if event.button == 4:
                self.scroll_y = max(0, self.scroll_y - self.scroll_speed * 2)
                return True
            elif event.button == 5:
                self.scroll_y = min(self.max_scroll, self.scroll_y + self.scroll_speed * 2)
                return True

            return True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.is_scrolling = False
                return True

        elif event.type == pygame.MOUSEMOTION:
            if self.is_scrolling and self.scrollbar_rect:
                mouse_y = event.pos[1]
                scroll_area_height = self.height - 100
                thumb_height = self.scrollbar_rect.height
                
                min_y = 80
                max_y = min_y + scroll_area_height - thumb_height
                
                new_thumb_y = max(min_y, min(max_y, mouse_y - self.scroll_drag_start))
                
                scroll_ratio = (new_thumb_y - min_y) / (scroll_area_height - thumb_height)
                self.scroll_y = int(scroll_ratio * self.max_scroll)
                return True

        return False

    def show(self):
        self.visible = True
        self.scroll_y = 0

    def hide(self):
        self.visible = False
        self.scroll_y = 0

    def toggle(self):
        if self.visible:
            self.hide()
        else:
            self.show()

    def set_game_reference(self, game):
        self.game = game
        self.first_join_date = self.get_first_join_date()