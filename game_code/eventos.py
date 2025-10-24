# eventos.py
import requests
import json
from datetime import datetime, timedelta
import pygame

class Evento:
    def __init__(self, nome, data_inicio, hora_inicio, data_final, hora_final, tipo="normal", id=None):
        self.nome = nome
        self.data_inicio = data_inicio
        self.hora_inicio = hora_inicio
        self.data_final = data_final
        self.hora_final = hora_final
        self.tipo = tipo  # pontos_duplos, bonus_click, etc.
        self.id = id or nome.lower().replace(" ", "_")
        self.ativo = False
        
    def verificar_ativo(self):
        """Verifica se o evento está ativo no momento atual"""
        try:
            agora = datetime.now()
            
            # Combina data e hora de início
            inicio_str = f"{self.data_inicio} {self.hora_inicio}"
            inicio = datetime.strptime(inicio_str, "%d/%m/%Y %H:%M")
            
            # Combina data e hora final
            final_str = f"{self.data_final} {self.hora_final}"
            final = datetime.strptime(final_str, "%d/%m/%Y %H:%M")
            
            self.ativo = inicio <= agora <= final
            return self.ativo
            
        except Exception as e:
            print(f"Erro ao verificar evento {self.nome}: {e}")
            self.ativo = False
            return False
    
    def get_tempo_restante(self):
        """Retorna o tempo restante para o evento terminar"""
        if not self.ativo:
            return "Evento inativo"
            
        try:
            final_str = f"{self.data_final} {self.hora_final}"
            final = datetime.strptime(final_str, "%d/%m/%Y %H:%M")
            agora = datetime.now()
            
            if agora > final:
                return "Evento finalizado"
                
            diferenca = final - agora
            dias = diferenca.days
            horas = diferenca.seconds // 3600
            minutos = (diferenca.seconds % 3600) // 60
            
            if dias > 0:
                return f"{dias}d {horas}h {minutos}m"
            elif horas > 0:
                return f"{horas}h {minutos}m"
            else:
                return f"{minutos}m"
                
        except Exception as e:
            return "Erro no cálculo"
    
    def get_icone(self):
        """Retorna ícone baseado no tipo do evento"""
        icones = {
            "pontos_duplos": "⚡",
            "bonus_click": "🎯",
            "velocidade_trabalhador": "🏃",
            "preco_reduzido": "💸",
            "evento_raro": "🌟",
            "natal": "🎄",
            "ano_novo": "🎆",
            "halloween": "🎃"
        }
        return icones.get(self.tipo, "🎉")
    
    def get_descricao(self):
        """Retorna descrição baseada no tipo do evento"""
        descricoes = {
            "pontos_duplos": "Ganhe o DOBRO de pontos por clique!",
            "bonus_click": "Bônus extra em cada clique!",
            "velocidade_trabalhador": "Trabalhadores 2x mais rápidos!",
            "preco_reduzido": "Upgrades com 50% de desconto!",
            "evento_raro": "Evento especial raro ativo!",
            "natal": "Evento especial de Natal!",
            "ano_novo": "Celebre o Ano Novo!",
            "halloween": "Evento assustador do Halloween!"
        }
        return descricoes.get(self.tipo, "Evento especial ativo!")
    
    def aplicar_efeito_pontos(self, pontos_base):
        """Aplica efeitos de multiplicador de pontos"""
        if not self.ativo:
            return pontos_base
            
        multiplicadores = {
            "pontos_duplos": 2.0,
            "bonus_click": 1.5,
            "evento_raro": 3.0,
            "natal": 2.5,
            "ano_novo": 2.0,
            "halloween": 1.8
        }
        
        multiplicador = multiplicadores.get(self.tipo, 1.0)
        return int(pontos_base * multiplicador)
    
    def aplicar_efeito_trabalhador(self, velocidade_base):
        """Aplica efeitos de velocidade dos trabalhadores"""
        if not self.ativo:
            return velocidade_base
            
        if self.tipo == "velocidade_trabalhador":
            return velocidade_base * 2.0
            
        return velocidade_base
    
    def aplicar_desconto_upgrades(self, preco_base):
        """Aplica descontos nos preços dos upgrades"""
        if not self.ativo:
            return preco_base
            
        if self.tipo == "preco_reduzido":
            return preco_base * 0.5
            
        return preco_base

class GerenciadorEventos:
    def __init__(self):
        self.eventos = []
        self.url_json = "https://raw.githack.com/eupyetro0224234/Generic-Clicker-Game/main/github_assets/eventos.json"
        self.ultima_verificacao = None
        self.intervalo_verificacao = 300000  # 5 minutos em milissegundos
        
    def carregar_eventos(self):
        """Carrega eventos do JSON do GitHub"""
        try:
            response = requests.get(self.url_json, timeout=10)
            response.raise_for_status()
            
            dados = response.json()
            self.eventos.clear()
            
            for evento_data in dados.get("eventos", []):
                evento = Evento(
                    nome=evento_data.get("nome", ""),
                    data_inicio=evento_data.get("data_inicio", ""),
                    hora_inicio=evento_data.get("hora_inicio", ""),
                    data_final=evento_data.get("data_final", ""),
                    hora_final=evento_data.get("hora_final", ""),
                    tipo=evento_data.get("tipo", "normal"),
                    id=evento_data.get("id")
                )
                self.eventos.append(evento)
            
            print(f"Carregados {len(self.eventos)} eventos do GitHub")
            self.ultima_verificacao = pygame.time.get_ticks()
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"Erro ao carregar eventos do GitHub: {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar JSON: {e}")
            return False
    
    def atualizar_eventos(self):
        """Atualiza o status dos eventos periodicamente"""
        current_time = pygame.time.get_ticks()
        
        if (self.ultima_verificacao is None or 
            current_time - self.ultima_verificacao > self.intervalo_verificacao):
            self.carregar_eventos()
        
        eventos_ativos = []
        for evento in self.eventos:
            if evento.verificar_ativo():
                eventos_ativos.append(evento)
        
        return eventos_ativos
    
    def get_eventos_ativos(self):
        """Retorna lista de eventos ativos"""
        return [evento for evento in self.eventos if evento.ativo]
    
    def get_eventos_por_tipo(self, tipo):
        """Retorna eventos ativos de um tipo específico"""
        return [evento for evento in self.eventos if evento.ativo and evento.tipo == tipo]
    
    def get_proximo_evento(self):
        """Retorna o próximo evento a começar"""
        try:
            agora = datetime.now()
            eventos_futuros = []
            
            for evento in self.eventos:
                inicio_str = f"{evento.data_inicio} {evento.hora_inicio}"
                inicio = datetime.strptime(inicio_str, "%d/%m/%Y %H:%M")
                
                if inicio > agora:
                    eventos_futuros.append((evento, inicio))
            
            if eventos_futuros:
                eventos_futuros.sort(key=lambda x: x[1])
                return eventos_futuros[0][0]
                
            return None
            
        except Exception as e:
            print(f"Erro ao buscar próximo evento: {e}")
            return None
    
    def aplicar_efeitos_pontos(self, pontos_base):
        """Aplica todos os efeitos ativos de multiplicação de pontos"""
        pontos_finais = pontos_base
        eventos_ativos = self.get_eventos_ativos()
        
        for evento in eventos_ativos:
            pontos_finais = evento.aplicar_efeito_pontos(pontos_finais)
        
        return pontos_finais
    
    def aplicar_efeitos_trabalhador(self, velocidade_base):
        """Aplica todos os efeitos ativos de velocidade dos trabalhadores"""
        velocidade_final = velocidade_base
        eventos_ativos = self.get_eventos_ativos()
        
        for evento in eventos_ativos:
            velocidade_final = evento.aplicar_efeito_trabalhador(velocidade_final)
        
        return velocidade_final
    
    def aplicar_descontos_upgrades(self, preco_base):
        """Aplica todos os descontos ativos nos upgrades"""
        preco_final = preco_base
        eventos_ativos = self.get_eventos_ativos()
        
        for evento in eventos_ativos:
            preco_final = evento.aplicar_desconto_upgrades(preco_final)
        
        return preco_final

# Exemplo de uso e teste
if __name__ == "__main__":
    gerenciador = GerenciadorEventos()
    
    if gerenciador.carregar_eventos():
        eventos_ativos = gerenciador.atualizar_eventos()
        
        print("\n=== EVENTOS ATIVOS ===")
        for evento in eventos_ativos:
            print(f"{evento.get_icone()} {evento.nome}")
            print(f"   Tipo: {evento.tipo}")
            print(f"   Descrição: {evento.get_descricao()}")
            print(f"   Tempo restante: {evento.get_tempo_restante()}")
            
            # Teste de efeitos
            pontos_test = 100
            pontos_finais = evento.aplicar_efeito_pontos(pontos_test)
            print(f"   Efeito: {pontos_test} → {pontos_finais} pontos")
            print()
        
        print("\n=== TODOS OS EVENTOS ===")
        for evento in gerenciador.eventos:
            status = "ATIVO" if evento.ativo else "INATIVO"
            print(f"{evento.get_icone()} {evento.nome} - {status}")
            print(f"   Tipo: {evento.tipo}")
            if evento.ativo:
                print(f"   Tempo restante: {evento.get_tempo_restante()}")
            print()