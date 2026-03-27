import pygame, pytz
from datetime import datetime
from game_assets.game_assets_packed import load_image

class StatisticsMenu:
    def __init__(self, screen, window_width, window_height, game_reference=None):
        self.screen = screen
        self.width = window_width
        self.height = window_height
        self.game = game_reference

        self.bg_color = (255, 182, 193)
        self.text_color = (47, 24, 63)
        self.option_height = 50
        self.option_radius = 20
        self.padding_x = 20
        self.padding_y = 15
        self.spacing_x = 15
        self.spacing_y = 12
        self.options_per_row = 2

        self.content_margin = 60

        self.visible = False

        self.title_font = pygame.font.SysFont(None, 38)
        self.font = pygame.font.SysFont(None, 28)
        self.emoji_font = pygame.font.SysFont("segoeuiemoji", 24)

        self.hovered_option = None
        self.button_rects = []

        self.close_button_rect = pygame.Rect(self.width - 80, 15, 40, 40)

        try:
            self.close_image = load_image("close.png")
            self.close_image = pygame.transform.smoothscale(self.close_image, (40, 40))
        except Exception:
            self.close_image = None

        self.scroll_y = 0
        self.scroll_speed = 30
        self.max_scroll = 0
        self.scrollbar_width = 12
        self.scrollbar_rect = None
        self.is_scrolling = False
        self.scroll_drag_start = 0

        self.first_join_date = None

        self._stat_shadow = {}
        self._stat_scale  = {}

    def _content_x(self):
        return self.content_margin

    def _content_width(self):
        return self.width - 2 * self.content_margin

    def _animate(self, key, is_hovered):
        alpha = self._stat_shadow.get(key, 0)
        alpha = min(40, alpha + 6) if is_hovered else max(0, alpha - 6)
        self._stat_shadow[key] = alpha

        scale = self._stat_scale.get(key, 1.0)
        target = 1.03 if is_hovered else 1.0
        scale += (target - scale) * 0.2
        if abs(scale - target) < 0.001:
            scale = target
        self._stat_scale[key] = scale

        return alpha, scale

    def get_first_join_date(self):
        if not self.game:
            return "Não disponível"
        if hasattr(self.game, 'first_join_date') and self.game.first_join_date:
            return self.game.first_join_date
        if hasattr(self.game, 'score_manager'):
            try:
                data = self.game.score_manager.load_data()
                if data and 'first_join_date' in data and data['first_join_date']:
                    return data['first_join_date']
            except Exception:
                pass
        try:
            tz_brasilia = pytz.timezone('America/Sao_Paulo')
            first_join = datetime.now(tz_brasilia).strftime("%d/%m/%Y - %H:%M")
            if hasattr(self.game, 'first_join_date'):
                self.game.first_join_date = first_join
                if hasattr(self.game, 'save_game_data'):
                    self.game.save_game_data()
            return first_join
        except Exception:
            return "Não disponível"

    def format_number(self, number):
        try:
            if isinstance(number, str):
                number = float(number.replace('.', '').replace(',', ''))
            return f"{int(number):,}".replace(",", ".")
        except (ValueError, TypeError):
            return "0"

    def get_statistics_data(self):
        if not self.game:
            return self.get_default_statistics()
        try:
            total_score = getattr(self.game, 'score', 0)
            max_score = getattr(self.game, 'max_score', 0)
            total_score_earned = getattr(self.game, 'total_score_earned', 0)
            normal_clicks = 0
            mini_event_clicks = 0
            if hasattr(self.game, 'tracker'):
                normal_clicks = getattr(self.game.tracker, 'normal_clicks', 0)
                mini_event_clicks = getattr(self.game.tracker, 'mini_event_clicks', 0)
            total_clicks = normal_clicks + mini_event_clicks
            unlocked_achievements = 0
            total_achievements = 0
            if hasattr(self.game, 'tracker'):
                unlocked_achievements = len(getattr(self.game.tracker, 'unlocked', {}))
                total_achievements = len([a for a in getattr(self.game.tracker, 'achievements', []) if a.id != "console"])
            total_play_time = 0
            formatted_time = "00:00:00"
            if hasattr(self.game, 'get_total_play_time'):
                total_play_time = self.game.get_total_play_time()
                if hasattr(self.game, 'format_time'):
                    formatted_time = self.game.format_time(total_play_time)
            purchased_upgrades = 0
            if hasattr(self.game, 'upgrade_menu') and hasattr(self.game.upgrade_menu, 'purchased'):
                purchased_upgrades = sum(self.game.upgrade_menu.purchased.values())
            eventos_participados = 0
            if hasattr(self.game, 'eventos_participados'):
                eventos_participados = sum(self.game.eventos_participados.values())
            mini_eventos_sessao = 0
            if hasattr(self.game, 'get_mini_events_session_total'):
                mini_eventos_sessao = self.game.get_mini_events_session_total()
            mini_event1_total = getattr(self.game, 'mini_event1_total', 0)
            mini_event2_total = getattr(self.game, 'mini_event2_total', 0)
            mini_eventos_total = mini_event1_total + mini_event2_total
            streak_data = getattr(self.game, 'streak_data', {})
            current_streak = streak_data.get('current_streak', 0)
            max_streak = streak_data.get('max_streak', 0)
            if not self.first_join_date:
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
                "Primeira Entrada": self.first_join_date if self.first_join_date else "Não disponível",
                "Sequência Atual": f"{current_streak} dias",
                "Maior Sequência": f"{max_streak} dias"
            }
        except Exception:
            return self.get_default_statistics()

    def get_default_statistics(self):
        return {
            "Pontuação Atual": 0,
            "Pontuação Máxima": 0,
            "Pontuação Total": 0,
            "Cliques Totais": 0,
            "Conquistas Desbloqueadas": "0/0",
            "Tempo de Jogo": "00:00:00",
            "Upgrades Comprados": 0,
            "Eventos Participados": 0,
            "Mini Eventos Sessão": 0,
            "Mini Eventos Totais": 0,
            "Primeira Entrada": "Não disponível",
            "Sequência Atual": "0 dias",
            "Maior Sequência": "0 dias"
        }

    def draw_section_title(self, title, x, y):
        box_width  = self._content_width()
        box_height = 45
        box_rect   = pygame.Rect(x, y - self.scroll_y, box_width, box_height)
        if box_rect.bottom < 0 or box_rect.top > self.height:
            return y + box_height + 10
        azul_claro = (200, 190, 255, 230)
        pygame.draw.rect(self.screen, azul_claro, box_rect, border_radius=self.option_radius)
        pygame.draw.rect(self.screen, (150, 150, 150), box_rect, width=2, border_radius=self.option_radius)
        title_surf = self.title_font.render(title, True, self.text_color)
        title_rect = title_surf.get_rect(center=box_rect.center)
        self.screen.blit(title_surf, title_rect)
        return y + box_height + 10

    def draw_stat_option(self, key, value, x, y, width):
        mouse_pos        = pygame.mouse.get_pos()
        container_height = self.option_height
        container_rect   = pygame.Rect(x, y - self.scroll_y, width, container_height)

        if container_rect.bottom < 0 or container_rect.top > self.height:
            return y + container_height + self.spacing_y

        is_hovered = container_rect.collidepoint(mouse_pos)
        alpha, scale = self._animate(key, is_hovered)

        card = pygame.Surface((width, container_height), pygame.SRCALPHA)
        blend = alpha / 40.0
        color = (int(255 - blend * 10), int(255 - blend * 10), int(255 - blend * 5))
        pygame.draw.rect(card, color,           (0, 0, width, container_height), border_radius=self.option_radius)
        pygame.draw.rect(card, (150, 150, 150), (0, 0, width, container_height), width=2, border_radius=self.option_radius)

        if isinstance(value, (int, float)) and key not in ["Conquistas Desbloqueadas", "Tempo de Jogo", "Primeira Entrada", "Sequência Atual", "Maior Sequência"]:
            display_value = self.format_number(value)
        else:
            display_value = str(value)

        text_surf = self.font.render(key, True, self.text_color)
        card.blit(text_surf, text_surf.get_rect(midleft=(18, container_height // 2)))

        value_surf = self.font.render(display_value, True, self.text_color)
        card.blit(value_surf, value_surf.get_rect(midright=(width - 18, container_height // 2)))

        sw = int(width * scale)
        sh = int(container_height * scale)
        scaled = pygame.transform.smoothscale(card, (sw, sh))
        cx = x + width // 2
        cy = container_rect.centery
        dx = cx - sw // 2
        dy = cy - sh // 2

        if alpha > 0:
            pad = int(3 * scale)
            shadow = pygame.Surface((sw + pad * 2, sh + pad * 2), pygame.SRCALPHA)
            pygame.draw.rect(shadow, (0, 0, 0, alpha),
                             (0, 0, sw + pad * 2, sh + pad * 2),
                             border_radius=int(self.option_radius * scale))
            self.screen.blit(shadow, (dx - pad, dy - pad))

        self.screen.blit(scaled, (dx, dy))
        return y + container_height + self.spacing_y

    def draw_scrollbar(self):
        if self.max_scroll <= 0:
            return
        scroll_area_x    = self.width - self.scrollbar_width - 5
        scroll_area_rect = pygame.Rect(scroll_area_x, 80, self.scrollbar_width, self.height - 100)
        visible_ratio    = self.height / (self.max_scroll + self.height)
        thumb_height     = max(30, visible_ratio * (self.height - 100))
        scroll_ratio     = self.scroll_y / self.max_scroll
        thumb_y          = 80 + scroll_ratio * ((self.height - 100) - thumb_height)
        self.scrollbar_rect = pygame.Rect(scroll_area_x, thumb_y, self.scrollbar_width, thumb_height)
        pygame.draw.rect(self.screen, (200, 200, 200, 150), scroll_area_rect, border_radius=6)
        pygame.draw.rect(self.screen, (100, 100, 100, 200), self.scrollbar_rect, border_radius=6)
        pygame.draw.rect(self.screen, (70, 70, 70), self.scrollbar_rect, 1, border_radius=6)

    def calculate_content_height(self):
        section_h    = 45 + 10
        row_h        = self.option_height + self.spacing_y
        total_height = 90
        total_height += section_h
        total_height += row_h * 3
        total_height += 35
        total_height += section_h
        total_height += row_h * 8
        total_height += 35
        total_height += section_h
        total_height += row_h * 2
        total_height += 20
        self.max_scroll = max(0, total_height - self.height)
        return total_height

    def draw_close_button(self):
        if self.close_image:
            image_rect = self.close_image.get_rect(center=self.close_button_rect.center)
            self.screen.blit(self.close_image, image_rect)
        else:
            pygame.draw.rect(self.screen, (255, 100, 100), self.close_button_rect, border_radius=8)
            center_x, center_y = self.close_button_rect.center
            line_length = 15
            pygame.draw.line(self.screen, (255, 255, 255),
                             (center_x - line_length, center_y - line_length),
                             (center_x + line_length, center_y + line_length), 2)
            pygame.draw.line(self.screen, (255, 255, 255),
                             (center_x - line_length, center_y + line_length),
                             (center_x + line_length, center_y - line_length), 2)

    def draw(self):
        if not self.visible:
            return
        self.button_rects = []
        self.screen.fill(self.bg_color)
        self.calculate_content_height()
        self.scroll_y = max(0, min(self.scroll_y, self.max_scroll))

        x           = self._content_x()
        stat_width  = self._content_width()

        title_font = pygame.font.SysFont(None, 44)
        title_surf = title_font.render("Estatísticas", True, self.text_color)
        title_rect = title_surf.get_rect(center=(self.width // 2, 35))
        self.screen.blit(title_surf, title_rect)

        y = 85
        stats_data = self.get_statistics_data()

        y = self.draw_section_title("Pontuação", x, y)
        y = self.draw_stat_option("Pontuação Atual",  stats_data.get("Pontuação Atual",  0), x, y, stat_width)
        y = self.draw_stat_option("Pontuação Máxima", stats_data.get("Pontuação Máxima", 0), x, y, stat_width)
        y = self.draw_stat_option("Pontuação Total",  stats_data.get("Pontuação Total",  0), x, y, stat_width)
        y += 35
        y = self.draw_section_title("Progresso Geral", x, y)
        y = self.draw_stat_option("Cliques Totais",            stats_data.get("Cliques Totais",            0),              x, y, stat_width)
        y = self.draw_stat_option("Conquistas Desbloqueadas",  stats_data.get("Conquistas Desbloqueadas",  "0/0"),          x, y, stat_width)
        y = self.draw_stat_option("Tempo de Jogo",             stats_data.get("Tempo de Jogo",             "00:00:00"),     x, y, stat_width)
        y = self.draw_stat_option("Upgrades Comprados",        stats_data.get("Upgrades Comprados",        0),              x, y, stat_width)
        y = self.draw_stat_option("Eventos Participados",      stats_data.get("Eventos Participados",      0),              x, y, stat_width)
        y = self.draw_stat_option("Primeira Entrada",          stats_data.get("Primeira Entrada",          "Não disponível"), x, y, stat_width)
        y = self.draw_stat_option("Sequência Atual",           stats_data.get("Sequência Atual",           "0 dias"),       x, y, stat_width)
        y = self.draw_stat_option("Maior Sequência",           stats_data.get("Maior Sequência",           "0 dias"),       x, y, stat_width)
        y += 35
        y = self.draw_section_title("Mini Eventos", x, y)
        y = self.draw_stat_option("Mini Eventos Sessão", stats_data.get("Mini Eventos Sessão", 0), x, y, stat_width)
        y = self.draw_stat_option("Mini Eventos Totais", stats_data.get("Mini Eventos Totais", 0), x, y, stat_width)

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
                mouse_y            = event.pos[1]
                scroll_area_height = self.height - 100
                thumb_height       = self.scrollbar_rect.height
                min_y              = 80
                max_y              = min_y + scroll_area_height - thumb_height
                new_thumb_y        = max(min_y, min(max_y, mouse_y - self.scroll_drag_start))
                scroll_ratio       = (new_thumb_y - min_y) / (scroll_area_height - thumb_height)
                self.scroll_y      = int(scroll_ratio * self.max_scroll)
                return True
        return False

    def show(self):
        self.visible = True
        self.scroll_y = 0
        if not self.first_join_date:
            self.first_join_date = self.get_first_join_date()

    def hide(self):
        self.visible  = False
        self.scroll_y = 0

    def toggle(self):
        if self.visible:
            self.hide()
        else:
            self.show()

    def set_game_reference(self, game):
        self.game = game
        self.first_join_date = self.get_first_join_date()