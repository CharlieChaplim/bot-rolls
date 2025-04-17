import os
import random
import discord
import difflib
from discord.ext import commands
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import ClassVar
from enum import Enum

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIXO = os.getenv('PREFIXO')

@dataclass
class Colors:
    CIANO: int = 0x1ce5ff
    VERDE: int = 0x38ff45
    AMARELO: int = 0xffd000
    ROXO: int = 0xa200ff
    VERMELHO: int = 0x9c0800
    AZUL: int = 0x004cff
    PRETO: int = 0x000000
    BRANCO: int = 0xffffff

@dataclass
class WikiItemConfig:
    apenas_imagem: bool = False  # Indica se o item deve mostrar apenas descrição e imagem


class RaridadesPesos(Enum):
    INSANO: int = 1
    LENDARIO: int = 6
    EPICO: int = 15
    RARO: int = 27
    COMUM: int = 51

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIXO, intents=intents, case_insensitive=True, help_command=None)

# Função para calcular os pesos com base na raridade
def calculate_weights(options_dict):
    # Conta quantos itens existem de cada raridade
    rarity_counts = {}
    for option, data in options_dict.items():
        rarity = data['rarity']
        if rarity not in rarity_counts:
            rarity_counts[rarity] = 0
        rarity_counts[rarity] += 1
    
    # Calcula o peso por item para cada raridade
    rarity_weight_per_item = {}
    for rarity, count in rarity_counts.items():
        rarity_weight_per_item[rarity] = rarity.value / count
    
    # Aplica os pesos calculados a cada item
    for option, data in options_dict.items():
        rarity = data['rarity']
        data['weight'] = rarity_weight_per_item[rarity]
    
    return options_dict

# Define as opções e suas raridades para cada categoria
GROUP_OPTIONS = {
    'Nenhum': {'rarity': RaridadesPesos.COMUM, 'color': Colors.CIANO, 'function': 'Neutro'},

    # Sindicatos
    'O Teatro - Sindicato dos Artistas': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'function': 'Membro'},
    'Forja Viva - Sindicato dos Metalúrgicos': {'rarity': RaridadesPesos.RARO, 'color': Colors.VERDE, 'function': 'Membro'},
    'Olho do Abismo - Sindicato dos Mineiros': {'rarity': RaridadesPesos.COMUM, 'color': Colors.CIANO, 'function': 'Membro'},
    'Aprendizes de Geppetto - Sindicato dos Artesãos': {'rarity': RaridadesPesos.COMUM, 'color': Colors.CIANO, 'function': 'Membro'},
    'Dedos da Criação - Sindicato dos Médicos': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO, 'function': 'Membro'},
    'A Caçada - Sindicato dos Caçadores': {'rarity': RaridadesPesos.RARO, 'color': Colors.VERDE, 'function': 'Membro'},
    'Bússola - Sindicato dos Marinheiros': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'function': 'Membro'},
    'Noite Estrelada - Sindicato da Noite': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO, 'function': 'Membro'},


    # Uno
    'Uno - Investigação (Funcionario)': {'rarity': RaridadesPesos.RARO, 'color': Colors.VERDE, 'function': 'Funcionario'},
    'Uno - Investigação (Olhos)': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO, 'function': 'Olhos'},
    'Uno - Investigação (Ouvidos)': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'function': 'Ouvidos'},
    'Uno - Investigação (Associado)': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'function': 'Associado'},

    # Zwei
    'Zwei - Proteção (Funcionario)': {'rarity': RaridadesPesos.RARO, 'color': Colors.VERDE, 'function': 'Funcionario'},
    'Zwei - Proteção (Milicia)': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'function': 'Milicia'},
    'Zwei - Proteção (Escudo)': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO, 'function': 'Escudo'},
    'Zwei - Proteção (Associado)': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'function': 'Associado'},

    # San
    'San - Transporte (Funcionario)': {'rarity': RaridadesPesos.RARO, 'color': Colors.VERDE, 'function': 'Funcionario'},
    'San - Transporte (Equipe de Limpeza)': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO, 'function': 'Equipe de Limpeza'},
    'San - Transporte (Equipe de Manutenção)': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'function': 'Equipe de Manutenção'},
    'San - Transporte (Associado)': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'function': 'Associado'},

    # Arba'a
    'Arba\'a - Assassinato (Funcionario)': {'rarity': RaridadesPesos.RARO, 'color': Colors.VERDE, 'function': 'Funcionario'},
    'Arba\'a - Assassinato (Padrinho)': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO, 'function': 'Padrinho'},
    'Arba\'a - Assassinato (Madrinha)': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO, 'function': 'Madrinha'},
    'Arba\'a - Assassinato (Dedo: Polegar)': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO, 'function': 'Dedo: Dedão'},
    'Arba\'a - Assassinato (Dedo: Indicador)': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO, 'function': 'Dedo: Indicador'},
    'Arba\'a - Assassinato (Dedo: Meio)': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO, 'function': 'Dedo: Meio'},
    'Arba\'a - Assassinato (Dedo: Anelar)': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO, 'function': 'Dedo: Anelar'},
    'Arba\'a - Assassinato (Dedo: Mínimo)': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO, 'function': 'Dedo: Mindinho'},
    'Arba\'a - Assassinato (Associado)': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'function': 'Associado'},

    # Cinq
    'Cinq - Justiça (Funcionario)': {'rarity': RaridadesPesos.RARO, 'color': Colors.VERDE, 'function': 'Funcionario'},
    'Cinq - Justiça (Juiz)': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO, 'function': 'Juiz'},
    'Cinq - Justiça (Executor)': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'function': 'Executor'},
    'Cinq - Justiça (Associado)': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'function': 'Associado'},

    # Sita
    'Sita - Economia (Funcionario)': {'rarity': RaridadesPesos.RARO, 'color': Colors.VERDE, 'function': 'Funcionario'},
    'Sita - Economia (Barão)': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO, 'function': 'Barão'},
    'Sita - Economia (Baronesa)': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO, 'function': 'Baronesa'},
    'Sita - Economia (Vendedor)': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'function': 'Vendedor'},
    'Sita - Economia (Associado)': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'function': 'Associado'},

    # Sedam
    'Sedam - Armamento (Funcionario)': {'rarity': RaridadesPesos.RARO, 'color': Colors.VERDE, 'function': 'Funcionario'},
    'Sedam - Assassinato (Médico)': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'function': 'Médico'},
    'Sedam - Armamento (Associado)': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'function': 'Associado'},

    # Otte
    'Otte - Biblioteca (Funcionario)': {'rarity': RaridadesPesos.RARO, 'color': Colors.VERDE, 'function': 'Funcionario'},
    'Otte - Biblioteca (Pesquisador)': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO, 'function': 'Pesquisador'},
    'Otte - Biblioteca (Pesquisador de Campo)': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'function': 'Pesquisador de Campo'},
    'Otte - Biblioteca (Associado)': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'function': 'Associado'},

    # Nau
    'Nau - Entretenimento (Funcionario)': {'rarity': RaridadesPesos.RARO, 'color': Colors.VERDE, 'function': 'Funcionario'},
    'Nau - Entretenimento (Palhaço)': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO, 'function': 'Palhaço'},
    'Nau - Entretenimento (Associado)': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'function': 'Associado'},

    # Deg
    'Deg - Conselho (Funcionario)': {'rarity': RaridadesPesos.RARO, 'color': Colors.VERDE, 'function': 'Funcionario'},
    'Deg - Conselho (Diplomata)': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO, 'function': 'Diplomata'},
    'Deg - Conselho (Associado)': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'function': 'Associado'},
}


POWERS_OPTIONS = {
    # Elementos
    'Fogo': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'category': 'Elementos'},
    'Gelo': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'category': 'Elementos'},
    'Água': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO, 'category': 'Elementos'},
    'Fumaça': {'rarity': RaridadesPesos.RARO, 'color': Colors.VERDE, 'category': 'Elementos'},
    'Areia': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO, 'category': 'Elementos'},
    'Raio': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'category': 'Elementos'},
    'Madeira': {'rarity': RaridadesPesos.COMUM, 'color': Colors.CIANO, 'category': 'Elementos'},
    'Cristal': {'rarity': RaridadesPesos.COMUM, 'color': Colors.CIANO, 'category': 'Elementos'},
    'Rosa': {'rarity': RaridadesPesos.RARO, 'color': Colors.VERDE, 'category': 'Elementos'},
    'Ferro': {'rarity': RaridadesPesos.RARO, 'color': Colors.VERDE, 'category': 'Elementos'},
    'Mel': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'category': 'Elementos'},
    'Vidro': {'rarity': RaridadesPesos.RARO, 'color': Colors.VERDE, 'category': 'Elementos'},
    'Gasolina': {'rarity': RaridadesPesos.RARO, 'color': Colors.VERDE, 'category': 'Elementos'},
    'Pólvora': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'category': 'Elementos'},
    'Vácuo': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'category': 'Elementos'},
    'Sangue': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO, 'category': 'Elementos'},

    # Objetos
    'Relógio': {'rarity': RaridadesPesos.RARO, 'color': Colors.VERDE, 'category': 'Objetos'},
    'Zweihander': {'rarity': RaridadesPesos.RARO, 'color': Colors.VERDE, 'category': 'Objetos'},
    'Café': {'rarity': RaridadesPesos.COMUM, 'color': Colors.CIANO, 'category': 'Objetos'},
    'Vela': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'category': 'Objetos'},
    'Papel': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'category': 'Objetos'},
    'Tinta': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO, 'category': 'Objetos'},
    'Trompete': {'rarity': RaridadesPesos.RARO, 'color': Colors.VERDE, 'category': 'Objetos'},
    'Porta': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'category': 'Objetos'},
    'Lixo': {'rarity': RaridadesPesos.RARO, 'color': Colors.VERDE, 'category': 'Objetos'},
    'Argila': {'rarity': RaridadesPesos.RARO, 'color': Colors.VERDE, 'category': 'Objetos'},
    'Lâmina': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO, 'category': 'Objetos'},
    'Prego': {'rarity': RaridadesPesos.COMUM, 'color': Colors.CIANO, 'category': 'Objetos'},
    'Bússola': {'rarity': RaridadesPesos.RARO, 'color': Colors.VERDE, 'category': 'Objetos'},
    'Carta': {'rarity': RaridadesPesos.COMUM, 'color': Colors.CIANO, 'category': 'Objetos'},
    'Machadinha': {'rarity': RaridadesPesos.RARO, 'color': Colors.VERDE, 'category': 'Objetos'},
    'Sino': {'rarity': RaridadesPesos.RARO, 'color': Colors.VERDE, 'category': 'Objetos'},

    # Animais
    'Canino': {'rarity': RaridadesPesos.COMUM, 'color': Colors.CIANO, 'category': 'Animais'},
    'Raposa': {'rarity': RaridadesPesos.COMUM, 'color': Colors.CIANO, 'category': 'Animais'},
    'Inseto': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO, 'category': 'Animais'},
    'Peixe': {'rarity': RaridadesPesos.RARO, 'color': Colors.VERDE, 'category': 'Animais'},
    'Anfíbio': {'rarity': RaridadesPesos.COMUM, 'color': Colors.CIANO, 'category': 'Animais'},
    'Ave': {'rarity': RaridadesPesos.RARO, 'color': Colors.VERDE, 'category': 'Animais'},
    'Réptil': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'category': 'Animais'},
    'Touro/Vaca': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO, 'category': 'Animais'},
    'Equino': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'category': 'Animais'},
    'Aracnídeo': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'category': 'Animais'},
    'Canguru': {'rarity': RaridadesPesos.COMUM, 'color': Colors.CIANO, 'category': 'Animais'},
    'Dragão': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO, 'category': 'Animais'},
    'Leprechaum': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO, 'category': 'Animais'},  # Criatura mágica

    # Adjetivos
    'Sorte': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO, 'category': 'Adjetivos'},
    'Beleza': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'category': 'Adjetivos'},
    'Rapidez': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'category': 'Adjetivos'},
    'Força': {'rarity': RaridadesPesos.RARO, 'color': Colors.VERDE, 'category': 'Adjetivos'},
    'Carisma': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO, 'category': 'Adjetivos'},
    'Inteligência': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO, 'category': 'Adjetivos'},
    'Dureza': {'rarity': RaridadesPesos.RARO, 'color': Colors.VERDE, 'category': 'Adjetivos'},
    'Resistência': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'category': 'Adjetivos'},
    'Nostalgia': {'rarity': RaridadesPesos.COMUM, 'color': Colors.CIANO, 'category': 'Adjetivos'},
    'Liso': {'rarity': RaridadesPesos.COMUM, 'color': Colors.CIANO, 'category': 'Adjetivos'},
    'Preto': {'rarity': RaridadesPesos.RARO, 'color': Colors.VERDE, 'category': 'Adjetivos'},
    'Tamanho': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'category': 'Adjetivos'},

    # Abstratos
    'Felicidade': {'rarity': RaridadesPesos.RARO, 'color': Colors.VERDE, 'category': 'Abstratos'},
    'Dor': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO, 'category': 'Abstratos'},
    'Som': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'category': 'Abstratos'},
    'Eletromagnetismo': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO, 'category': 'Abstratos'},
    'Gravidade': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'category': 'Abstratos'},
    'Tempo (Musical)': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'category': 'Abstratos'},
    'Atrito': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO, 'category': 'Abstratos'},
    'Sonho': {'rarity': RaridadesPesos.RARO, 'color': Colors.VERDE, 'category': 'Abstratos'},
    'Lag': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'category': 'Abstratos'},
    'Ressonância': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO, 'category': 'Abstratos'},
    'Retorno': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'category': 'Abstratos'},
    'Soma': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'category': 'Abstratos'},
    'Monarca': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO, 'category': 'Abstratos'},  # Conceito abstrato

    # Verbos
    'Golpear': {'rarity': RaridadesPesos.COMUM, 'color': Colors.CIANO, 'category': 'Verbos'},
    'Produzir': {'rarity': RaridadesPesos.RARO, 'color': Colors.VERDE, 'category': 'Verbos'},
    'Cultivar': {'rarity': RaridadesPesos.RARO, 'color': Colors.VERDE, 'category': 'Verbos'},
    'Roubar': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO, 'category': 'Verbos'},
    'Curar': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO, 'category': 'Verbos'},
    'Brutalizar': {'rarity': RaridadesPesos.COMUM, 'color': Colors.CIANO, 'category': 'Verbos'},
    'Dançar': {'rarity': RaridadesPesos.RARO, 'color': Colors.VERDE, 'category': 'Verbos'},
    'Planejar': {'rarity': RaridadesPesos.RARO, 'color': Colors.VERDE, 'category': 'Verbos'},
    'Acertar': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'category': 'Verbos'},
    'Apodrecer': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO, 'category': 'Verbos'},
    'Iluminar': {'rarity': RaridadesPesos.RARO, 'color': Colors.VERDE, 'category': 'Verbos'},
    'Teleportar': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'category': 'Verbos'},
    'Caçar': {'rarity': RaridadesPesos.RARO, 'color': Colors.VERDE, 'category': 'Verbos'},
    'Cirurgia': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'category': 'Verbos'},
    'Cantar': {'rarity': RaridadesPesos.COMUM, 'color': Colors.CIANO, 'category': 'Verbos'},
    'Impulsionar': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'category': 'Verbos'},
}



CURSES_OPTIONS = {
    'Nenhuma': {'rarity': RaridadesPesos.COMUM, 'color': Colors.CIANO}, 
    'Maldição da Gula': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO},
    'Maldição do Não Mais Humano': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO},
    'Maldição do Corpo': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO},
    'Maldição do Poder': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO},
    'Maldição dos Corvos': {'rarity': RaridadesPesos.INSANO, 'color': Colors.VERMELHO},
    'Maldição da Tsukuyomi': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO},
    'Maldição do Rei': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO},
    'Maldição do Gêmeo Maligno': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO},
}

# Dicionário para mapear opções de comando para seus respectivos dicionários de opções
OPTION_CATEGORIES = {
    'grupo': GROUP_OPTIONS,
    'poderes': POWERS_OPTIONS,
    'maldicoes': CURSES_OPTIONS
}

# Dicionário com informações detalhadas para o comando wiki
WIKI_INFO = {
    'Maldição dos Corvos': {
        'title': 'Maldição dos Corvos',
        'description': 'Você não tem nenhum malefício?',
        'beneficio': 'Você pode virar um corvo quando bem entender. "You don\'t understand ruby, he turned me into a BIRD!"',
        'maleficio': 'Nenhum.',
        'color': Colors.VERMELHO
    },
    'Maldição da Gula': {
        'title': 'Maldição da Gula',
        'description': 'Sua fome não conhece limites — a ponto de levar restaurantes inteiros à falência. No entanto, essa voracidade vem acompanhada de uma vitalidade fora do comum.',
        'beneficio': 'Seu modo irrestrito dura sempre 15 minutos, sem necessidade de rolagem.',
        'maleficio': 'Você constantemente sente fome.',
        'color': Colors.AMARELO
    },
    'Maldição do Não Mais Humano': {
        'title': 'Maldição do Não Mais Humano',
        'description': 'Palavras ligadas à transformação cobram um preço alto: sua humanidade. Você nunca mais será completamente humano — uma criatura híbrida, sempre dividida.',
        'beneficio': 'Em troca, sua vida se estende consideravelmente, vivendo até cinco vezes mais que uma pessoa comum.',
        'maleficio': 'Você nunca será completamente humano.',
        'color': Colors.AMARELO
    },
    'Maldição do Corpo': {
        'title': 'Maldição do Corpo',
        'description': 'Seu corpo é frágil, quebradiço, talvez até doente. Mas seu poder é desproporcionalmente devastador — como se o universo compensasse sua condição com força pura.',
        'beneficio': 'Seus ataques e habilidades baseados em palavra são significativamente mais fortes do que o normal.',
        'maleficio': 'Seu corpo é muito fragil e doente.',
        'color': Colors.AMARELO
    },
    'Maldição do Poder': {
        'title': 'Maldição do Poder',
        'description': 'Seu poder é medíocre, quase inútil. Mas seu corpo? Inquebrável.',
        'beneficio': 'Sua força física, resistência e habilidades corporais ultrapassam os limites humanos.',
        'maleficio': 'Sua palavra tem um efeito reverso indesejado (Como sorte virar azar).',
        'color': Colors.AMARELO
    },
    'Maldição da Tsukuyomi': {
        'title': 'Maldição da Tsukuyomi',
        'description': 'Você é constantemente observado... Talvez você se quer esteja vivo... Se acha vivo?',
        'beneficio': 'Corvos te seguem por toda cidade, lhe dando informações sem filtro do que você quer ouvir, afinal, você pertence aos corvos e não o contrário!',
        'maleficio': 'Você pertence aos corvos e não o contrário! Logo, a cada 3 loots, um será dos corvos.',
        'color': Colors.AMARELO
    },
    'Maldição do Rei': {
        'title': 'Maldição do Rei',
        'description': 'Sempre procurando por mais, negligenciando seus súditos e reinos... Dia após dia, sua luta é incessante e você? Acaba como um esqueleto.',
        'beneficio': 'Imortalidade!',
        'maleficio': 'Só que como um esqueleto.',
        'color': Colors.AMARELO
    },
    'Maldição do Gêmeo Maligno': {
        'title': 'Maldição do Gêmeo Maligno',
        'description': 'Dentro de você... Sim, ele sempre esteve dentro de você! Você só não notou ainda, seu gêmeo maligno é você mesmo com transtorno de personalidade!',
        'beneficio': 'Uma segunda palavra, que só poderá ser usada pelo irmão "gêmeo".',
        'maleficio': 'Seu gêmeo necessáriamente tem de ser seu oposto, como se você for bom, ele tem de ser mau.',
        'color': Colors.AMARELO
    },

    #Organizações

'Uno': {
    'title': 'Uno - Investigação',
    'description': (
        'A Uno é a espinha dorsal do submundo da informação. Num sistema onde o conhecimento é moeda de poder, '
        'a Uno atua como a principal detentora e negociadora de segredos. Sua estrutura é dividida entre funcionários '
        'administrativos, "olhos" e "ouvidos", cada qual com uma função clara na teia de vigilância urbana. Em meio à '
        'liberdade caótica da cidade, a Uno prospera oferecendo informações precisas, vendidas por preço alto — em favores, '
        'recursos ou dados. Seu atual líder é **Raviel**.\n\n'
        '- **Funcionários**: Responsáveis por organizar, catalogar e gerenciar os dados obtidos. Trabalham em escritórios ocultos, '
        'muitas vezes sem saber quem são os espiões ou de onde vêm as informações.\n'
        '- **Olhos**: São os observadores, infiltrados em locais estratégicos, com poderes voltados à percepção, análise e ilusão. '
        'São os responsáveis por capturar imagens, cenas e comportamentos.\n'
        '- **Ouvidos**: Mestres em escuta e infiltração, operam como sombras nos corredores da cidade. Com habilidades de mimetismo '
        'e espionagem auditiva, são eles que interceptam conversas, confissões e ameaças.'
    ),
    'image_url': 'https://media.discordapp.net/attachments/952277039686226071/1358936664998805774/Uno.png?ex=67ff8b24&is=67fe39a4&hm=179221145ef0ad71422468ff48f76a5ca4de6b7afdab03615dd03178a56f72a0&=&format=webp&quality=lossless',
    'color': Colors.ROXO,
    'apenas_imagem': True
},

    'Zwei': {
        'title': 'Zwei - Proteção',
        'description': (
        'A Zwei representa o braço protetor da cidade, mesmo num sistema onde a segurança é uma escolha de mercado. '
        'Seus membros vestem armaduras pesadas e agem guiados por um ideal de preservação da vida — mesmo quando isso entra em choque com o lucro. '
        'Com ações marcadas por coragem e sacrifício, a Zwei é respeitada, mas sua ética altruísta frequentemente causa atritos com o restante da cidade. '
        'Sua atual líder é **Tereza**.\n\n'
        '- **Funcionários**: Trabalham na base de operações, organizando patrulhas, missões de resgate e logística da milícia.\n'
        '- **Milícia**: Força de combate principal, equipada com armaduras rústicas e poderes defensivos. Atuam em emergências e zonas de risco elevado.\n'
        '- **Escudo**: Especialistas em contenção e evacuação. Se colocam entre o perigo e os civis, mesmo que isso custe caro.'
    ),
        'image_url': 'https://media.discordapp.net/attachments/952277039686226071/1358939975713947699/Zwei.png?ex=67ff8e3a&is=67fe3cba&hm=75ce4fdbf89bbd9f2c10161aab63d7aefbe6dce9dcffa5b3574b86faf77189ed&=&format=webp&quality=lossless',  # Substitua pelo URL real da imagem
        'color': Colors.AZUL,
        'apenas_imagem': True
    },
    'San': {
        'title': 'San - Transporte',
        'description': (
        'A San é o motor movido a carvão que nunca para. Como a maior transportadora da cidade, sua lógica é simples: lucro sobre trilhos. '
        'Com linhas ferroviárias cruzando setores inteiros, a San é a espinha dorsal da logística urbana e industrial. '
        'Seus cortes de gastos extremos levaram à criação de forças armadas internas — a temida Equipe de Limpeza. '
        'Seu atual líder é **Hermiton**, uma figura difícil de encontrar até para seus subordinados.\n\n'
        '- **Funcionários**: Administram rotas, vagões e manutenção mínima. Trabalham sob intensa pressão por resultados.\n'
        '- **Equipe de Limpeza**: Força de combate interna da San, especializada em lidar com "imprevistos", como assaltos, sabotagens e greves.\n'
        '- **Equipe de Manutenção**: Com poderes voltados à reconstrução e tecnologia, mantém os trilhos operacionais mesmo sob condições adversas.'
    ),
        'image_url': 'https://media.discordapp.net/attachments/952277039686226071/1358943537265250565/San.png?ex=67ff918b&is=67fe400b&hm=d4654afb1e87a9de58b3ad8c943a5a62b9cd629b0de54c5a8b8cf410e4ec98df&=&format=webp&quality=lossless',  # Substitua pelo URL real da imagem
        'color': Colors.AMARELO,
        'apenas_imagem': True
    },
    'Arba\'a': {
        'title': 'Arba\'a - Assasinatos',
        'description': (
        'A Arba’a vive um período de reconstrução após uma queda catastrófica. Antigamente temida como a organização de assassinos mais mortal da cidade, '
        'hoje opera nas sombras, tentando retomar seu prestígio. Cada “dedo” da Arba’a representa um estilo único de morte, refletindo a especialização da hierarquia. '
        'São cinco grupos principais, conhecidos como a mão da morte. Atualmente, a líder é **Ilya**.\n\n'
        '- **Funcionários**: Administram contratos, pagamentos e a estrutura decadente da organização.\n'
        '- **Padrinho & Madrinha**: Líderes da velha guarda. Agem com brutalidade e precisão cirúrgica, mantendo viva a tradição da Arba’a.\n'
        '- **Polegar**: Especialistas em força bruta — confrontos diretos, mortes viscerais.\n'
        '- **Indicador**: Mestres das armas de fogo. Precisos e raros numa cidade onde munição é escassa.\n'
        '- **Meio**: Disciplinados e metódicos. Matam com o corpo, usando artes marciais e anatomia.\n'
        '- **Anelar**: Sussurram a morte. Agem com extrema sutileza, invisíveis.\n'
        '- **Mínimo**: Engenheiros da morte indireta. Armadilhas, explosivos e venenos letais e silenciosos.'
    ),
        'image_url': 'https://media.discordapp.net/attachments/952277039686226071/1358944794549682327/Arbaa.png?ex=67ff92b6&is=67fe4136&hm=4d109d7c73151c190667ade61902e13ac51fe71b01855f538926b3012184cdfa&=&format=webp&quality=lossless',  # Substitua pelo URL real da imagem
        'color': Colors.VERMELHO,
        'apenas_imagem': True
    },
    'Cinq': {
        'title': 'Cinq - Justiça',
        'description': (
        'A Cinq é a encarnação da lei absoluta em meio ao caos. Mesmo numa sociedade onde a liberdade impera, alguém precisa traçar limites — '
        'ou ao menos parecer que o faz. Sua sede imponente e julgamentos públicos tornaram a Cinq uma entidade temida e reverenciada. '
        'Suas decisões são definitivas e suas execuções, exemplares. Seu atual líder é **Peter**.\n\n'
        '- **Funcionários**: Secretários, analistas e operadores jurídicos. Reúnem provas e organizam julgamentos.\n'
        '- **Juiz**: Autoridades supremas. Julgam com base na tradição e interpretação pessoal da justiça.\n'
        '- **Executor**: Cumpre as sentenças. Letal e implacável, com poderes voltados à punição e fim.'
    ),
        'image_url': 'https://media.discordapp.net/attachments/952277039686226071/1358946120352403506/Cinq.png?ex=67ff93f3&is=67fe4273&hm=34dcecf488b80e95d8ceba7e7f063d4b66f70f733ba372efcbcef4b2b4559b12&=&format=webp&quality=lossless',  # Substitua pelo URL real da imagem
        'color': Colors.AMARELO,
        'apenas_imagem': True
    },
    'Sita': {
        'title': 'Sita - Economia',
        'description': (
        'A Sita controla a cidade por onde realmente importa: o bolso. Detentora do maior mercado e banco local, é nela que o valor das coisas — e das pessoas — é definido. '
        'Sua estrutura aristocrática é composta por barões e baronesas que dominam setores como feudos, enquanto o consumidor é apenas um número com carteira. '
        'Na Sita, tudo tem um preço. Juros, taxas e cláusulas escondidas são parte do jogo. Sua atual líder é **Rxya**.\n\n'
        '- **Funcionários**: Operam caixas, estoques e sistemas bancários. São treinados para vender — a qualquer custo.\n'
        '- **Barão & Baronesa**: Controlam nichos estratégicos da economia, como alimentação, medicina e construção. Ditam preços e políticas internas.\n'
        '- **Vendedor**: Manipuladores natos, vendem até o que não têm. Sempre com um sorriso... e um contrato.'
    ),
        'image_url': 'https://media.discordapp.net/attachments/952277039686226071/1358948276413665561/Sita.png?ex=67ff95f5&is=67fe4475&hm=93a87ad1010d4a03aaf281280ab578a7b819a36bbc1746a1d7f6d6aaa580efe4&=&format=webp&quality=lossless',  # Substitua pelo URL real da imagem
        'color': Colors.VERDE,
        'apenas_imagem': True
    },
    'Sedam': {
        'title': 'Sedam - Armamento',
        'description': (
        'A Sedam é o último resquício do antigo exército — e o único fornecedor legal de pólvora e armas da cidade. '
        'Isolada do restante das organizações, raramente se envolve nos conflitos, exceto quando o pagamento justifica. '
        'Com estrutura militar e rígida, mantém um monopólio absoluto sobre o armamento. Seu atual líder é **Heinken**.\n\n'
        '- **Funcionários**: Lidam com a produção, estoque e burocracia de armamentos. Acesso à fábrica é privilégio de poucos.\n'
        '- **Médico**: Um dos únicos profissionais com acesso real à medicina. Tratam feridos com excelência, muitas vezes gratuitamente — mas a que custo?'
    ),
        'image_url': 'https://media.discordapp.net/attachments/952277039686226071/1358949528866394232/Sedam.png?ex=67ff971f&is=67fe459f&hm=290085547b927bbc1436f5a15565bbff175ffed4bae9f2ba860d267bf140e837&=&format=webp&quality=lossless',  # Substitua pelo URL real da imagem
        'color': Colors.VERMELHO,
        'apenas_imagem': True
    },
    'Otte': {
        'title': 'Otte - Biblioteca',
        'description': (
        'A Otte é a guardiã do conhecimento verdadeiro. Em uma cidade dominada por fumaça e ganância, sua biblioteca é um farol de saber. '
        'Sobrevive graças a doações misteriosas e benfeitores anônimos, mesmo não sendo lucrativa. '
        'Seu atual líder é **Venus**, frequentemente confundido com o lendário professor **Joaquim**.\n\n'
        '- **Funcionários**: Responsáveis por catalogar, restaurar e proteger documentos raros e preciosos.\n'
        '- **Pesquisador**: Especialistas em teoria, arcana ou científica. Desenvolvem novas tecnologias e palavras artificiais.\n'
        '- **Pesquisador de Campo**: Saem da biblioteca em busca de relíquias, dados perdidos e novas formas de saber — mesmo que isso custe caro.'
    ),
        'image_url': 'https://media.discordapp.net/attachments/952277039686226071/1358950660053270658/Otte.png?ex=67ff982d&is=67fe46ad&hm=92caf8c002635632b83333b2d1eb52d14e678827f41d8632c7dddddb6a7d43bb&=&format=webp&quality=lossless',  # Substitua pelo URL real da imagem
        'color': Colors.CIANO,
        'apenas_imagem': True
    },
    'Nau': {
        'title': 'Nau - Entretenimento',
        'description': (
        'A Nau colore o cinza da cidade com suas luzes, risos e absurdos. Responsável por toda a produção audiovisual, ela dita o que a cidade vê, ouve e sente. '
        'Seu estilo é caótico, extravagante e vicioso. Por trás de cada show, existe uma engrenagem brilhante — e bizarra. '
        'Sua figura máxima é o **Palhaço Palhaçada**, símbolo e lenda urbana.\n\n'
        '- **Funcionários**: Técnicos, roteiristas, câmeras e figurantes. Fazem o show acontecer nos bastidores.\n'
        '- **Palhaço**: Título e personagem. Qualquer um pode assumir o papel — desde que espalhe o caos divertido.'
    ),
        'image_url': 'https://media.discordapp.net/attachments/952277039686226071/1358951715537420580/Nau.png?ex=67ff9929&is=67fe47a9&hm=1f39349346bb4a2b2d0e2fd7c7d7969cd3dd2a7cc581e5e6ea63d68a7c90dfb5&=&format=webp&quality=lossless',  # Substitua pelo URL real da imagem
        'color': Colors.BRANCO,
        'apenas_imagem': True
    },
    'Deg': {
        'title': 'Deg - Conselho',
        'description': (
        'A Deg é o que mantém a cidade em ordem — ou pelo menos dá essa impressão. Não dita as regras, mas decide quem fala com quem, quando e sob quais condições. '
        'É a peça invisível que move o tabuleiro de poder. Quando há problemas externos, a Deg é sempre a primeira a agir. '
        'Sua líder atual é **Yin**.\n\n'
        '- **Funcionários**: Organizam agendas, registros e reuniões entre as organizações.\n'
        '- **Diplomata**: Mediadores, negociadores e embaixadores. Com carisma e boa lábia, garantem que a cidade funcione — mais ou menos.'
    ),
        'image_url': 'https://media.discordapp.net/attachments/952277039686226071/1358952504876077207/Deg.png?ex=67ff99e5&is=67fe4865&hm=408511970b160732df0e078ea645a61e7f5c8527281e21fd6a9c948290b093c8&=&format=webp&quality=lossless',  # Substitua pelo URL real da imagem
        'color': Colors.PRETO,
        'apenas_imagem': True
    },

    #Poderes

        'Gelo': {
    'title': 'Palavra: Gelo',
    'description': 'Definição: água congelada; sólido cristalino transparente formado por congelamento da água.\n\n'
'- **Estágio 0**: Você é exímio em criar, manusear e preservar gelo usando métodos naturais.\n'
'- **Estágio 1**: Você pode manipular os atributos do gelo, como temperatura, textura, formato e densidade.\n'
'- **Estágio 2**: Você pode gerar gelo, fundi-lo, congelar objetos e até transformar seu corpo parcialmente ou totalmente em gelo.\n'
'- **Passiva**: Resistência extrema ao frio e imunidade a congelamento.\n'
'- **Estágio 3**: Você pode manipular o conceito de gelo.\n'
'- **Modo: Irrestrito**: Você altera o conceito do conceito de gelo temporariamente, podendo aplicar esse conceito a qualquer coisa. Tudo se reverte após o fim.',
    'image_url': 'https://media.discordapp.net/attachments/1277763265379958794/1362435262361112839/ice-quirk.gif?ex=68026237&is=680110b7&hm=7a7982451b5801e6b5c4b9e8a227bc59a082956ae65e64e0652d76d91412fc32&=',
    'color': Colors.AZUL
},

'Água': {
    'title': 'Palavra: Água',
    'description': 'Definição: substância líquida, incolor, inodora e insípida, essencial à vida, composta de hidrogênio e oxigênio.\n\n'
'- **Estágio 0**: Você é o melhor em lidar com água: nadar, coletar, purificar ou distribuir.\n'
'- **Estágio 1**: Você pode manipular a densidade, fluxo, forma e temperatura da água.\n'
'- **Estágio 2**: Você gera água do nada, controla seu estado (líquido, vapor, gelo) e pode se transformar em água.\n'
'- **Passiva**: Respiração aquática e hidratação constante.\n'
'- **Estágio 3**: Você manipula o conceito de água.\n'
'- **Modo: Irrestrito**: Pode aplicar o conceito do conceito de água a qualquer entidade. Reversível após o uso.',
    'image_url': 'https://media.discordapp.net/attachments/1277763265379958794/1362443475588481174/water-dance.gif?ex=680269dd&is=6801185d&hm=9b35a7d59ef3e6e3fbc17f02f197f221ceae54118bd8da48819d30eb6ed3e96c&=',
    'color': Colors.CIANO
},

'Fumaça': {
    'title': 'Palavra: Fumaça',
    'description': 'Definição: conjunto de gases e partículas em suspensão resultantes da combustão incompleta de uma substância.\n\n'
'- **Estágio 0**: Você é o melhor em criar, manipular ou ocultar-se com fumaça de forma natural.\n'
'- **Estágio 1**: Pode alterar densidade, cor, toxicidade e formato da fumaça.\n'
'- **Estágio 2**: Geração espontânea de fumaça, alteração de estado (fumaça -> sólido, etc.), e transformação corporal parcial em fumaça.\n'
'- **Passiva**: Imunidade à asfixia e visão através de fumaça.\n'
'- **Estágio 3**: Manipulação do conceito de fumaça.\n'
'- **Modo: Irrestrito**: Altera o conceito do conceito de fumaça por um tempo limitado.',
    'image_url': 'https://media.discordapp.net/attachments/1277763265379958794/1362443475211259974/rikuo-anime.gif?ex=680269dd&is=6801185d&hm=88c9bd4e248d89296510fd67c9cce8766e458d3b1bb2fc3f1609e4b81376f290&=',
    'color': Colors.BRANCO
},

'Areia': {
    'title': 'Palavra: Areia',
    'description': 'Definição: material granular composto por pequenas partículas de rochas e minerais.\n\n'
'- **Estágio 0**: Mestre na manipulação e construção com areia.\n'
'- **Estágio 1**: Altere granulação, densidade, forma e peso da areia.\n'
'- **Estágio 2**: Gere areia, solidifique ou disperse, e transforme seu corpo em areia.\n'
'- **Passiva**: Resistência à abrasão e sentidos adaptados a ambientes áridos.\n'
'- **Estágio 3**: Você pode manipular o conceito de areia.\n'
'- **Modo: Irrestrito**: Modifica temporariamente o conceito do conceito de areia.',
    'image_url': 'https://media.discordapp.net/attachments/1277763265379958794/1362443476532465694/dissolving-power-rangers.gif?ex=680269dd&is=6801185d&hm=eab1e4ef7004bf6e2e5559ef50c21152ccd6d46d7262cee4535b7343281f90ec&=',
    'color': Colors.AMARELO
},

'Raio': {
    'title': 'Palavra: Raio',
    'description': 'Definição: descarga elétrica de grande intensidade que ocorre entre nuvens ou entre a nuvem e o solo.\n\n'
'- **Estágio 0**: Você é especialista em eletricidade e suas aplicações naturais.\n'
'- **Estágio 1**: Controle sobre intensidade, direção, cor e velocidade de descargas elétricas.\n'
'- **Estágio 2**: Geração espontânea de raios, condução elétrica, transformação corporal em raio.\n'
'- **Passiva**: Imunidade a choques e percepção elétrica aumentada.\n'
'- **Estágio 3**: Manipulação do conceito de raio.\n'
'- **Modo: Irrestrito**: Muda o conceito do conceito de raio por tempo limitado.',
    'image_url': 'https://media.discordapp.net/attachments/1277763265379958794/1362417119521935460/c6cbf2eb314aa301a74d155a5632fbad.gif?ex=68025151&is=6800ffd1&hm=ab6893e80ddc53553e8bd0d68334da17edd0717cb40fb7147f31521b4fd14d9c&=',
    'color': Colors.AMARELO
},

'Madeira': {
    'title': 'Palavra: Madeira',
    'description': 'Definição: tecido vegetal que forma o caule, os galhos e os ramos das árvores.\n\n'
'- **Estágio 0**: Você é o maior especialista em trabalhar com madeira de forma natural.\n'
'- **Estágio 1**: Manipula densidade, resistência, flexibilidade e crescimento da madeira.\n'
'- **Estágio 2**: Gera madeira, acelera crescimento de plantas lenhosas, transforma-se em madeira.\n'
'- **Passiva**: Resistência a impactos e comunicação com plantas.\n'
'- **Estágio 3**: Manipula o conceito de madeira.\n'
'- **Modo: Irrestrito**: Pode redefinir o que é madeira ao alterar o conceito do conceito.',
    'image_url': 'https://tenor.com/view/yamato-naruto-jutsu-wood-house-gif-18241232',
    'color': Colors.VERDE
},

'Cristal': {
    'title': 'Palavra: Cristal',
    'description': 'Definição: substância sólida com estrutura ordenada de átomos, formando formas geométricas.\n\n'
'- **Estágio 0**: Mestre em criação, corte e estudo de cristais naturais.\n'
'- **Estágio 1**: Controle sobre cor, dureza, forma e propriedades ópticas dos cristais.\n'
'- **Estágio 2**: Geração de cristais, fusão e alteração de forma, transformação corporal parcial em cristal.\n'
'- **Passiva**: Pele endurecida e reflexos prismáticos.\n'
'- **Estágio 3**: Manipulação do conceito de cristal.\n'
'- **Modo: Irrestrito**: Pode alterar temporariamente o conceito do conceito de cristal.',
    'image_url': 'https://media.discordapp.net/attachments/1277763265379958794/1362443476049989652/yamato-naruto.gif?ex=680269dd&is=6801185d&hm=9d3c37bc1809a2fdc079ea0c5f3dcd2d13466a625bac07e9983b939e40f579ad&=',
    'color': Colors.AZUL
},

'Rosa': {
    'title': 'Palavra: Rosa',
    'description': 'Definição: flor com pétalas delicadas e geralmente perfumadas; símbolo de beleza e amor.\n\n'
'- **Estágio 0**: Especialista em cultivar, podar e compreender rosas e seus significados.\n'
'- **Estágio 1**: Altera cor, perfume, tamanho e resistência de rosas.\n'
'- **Estágio 2**: Geração de rosas com efeitos variados (curativos, venenosos, cortantes), transformação parcial em pétalas.\n'
'- **Passiva**: Atração natural e resistência a venenos.\n'
'- **Estágio 3**: Manipulação do conceito de rosa.\n'
'- **Modo: Irrestrito**: Pode alterar o conceito do conceito de rosa por um tempo limitado.',
    'image_url': 'https://media.discordapp.net/attachments/1277763265379958794/1362443846935384216/black-clover-black-clover-movie.gif?ex=68026a36&is=680118b6&hm=635859429b9314f519c95a40dc92a18f959d6f6914bac5a8741b4ce27614415e&=',
    'color': Colors.VERMELHO
},

'Ferro': {
    'title': 'Palavra: Ferro',
    'description': 'Definição: elemento metálico maleável, magnético, utilizado em construção e fabricação.\n\n'
'- **Estágio 0**: Você é um mestre ferreiro e entende todos os usos do ferro.\n'
'- **Estágio 1**: Pode alterar maleabilidade, magnetismo e formato do ferro.\n'
'- **Estágio 2**: Geração e manipulação de ferro, fusão e transformação corporal metálica.\n'
'- **Passiva**: Corpo parcialmente magnético e extremamente resistente.\n'
'- **Estágio 3**: Manipula o conceito de ferro.\n'
'- **Modo: Irrestrito**: Pode alterar o conceito do conceito de ferro durante o irrestrito.',
    'image_url': 'https://media.discordapp.net/attachments/1277763265379958794/1362443847342489881/gajeel-gajeel-redfox.gif?ex=68026a36&is=680118b6&hm=1251647fe05bbf34cc5a20def6dcdde611f7f49489c1a32d9d350ca54a21f64c&=',
    'color': Colors.PRETO
},

'Mel': {
    'title': 'Palavra: Mel',
    'description': 'Definição: substância doce produzida pelas abelhas a partir do néctar das flores.\n\n'
'- **Estágio 0**: Você é o maior apicultor vivo.\n'
'- **Estágio 1**: Manipula sabor, viscosidade, cor e propriedades medicinais do mel.\n'
'- **Estágio 2**: Geração espontânea de mel, controle de abelhas, transformação parcial em mel.\n'
'- **Passiva**: Imunidade a toxinas e empatia com insetos.\n'
'- **Estágio 3**: Manipulação do conceito de mel.\n'
'- **Modo: Irrestrito**: Pode alterar o conceito do conceito de mel durante o uso irrestrito.\n'
'Ps: Em minha defesa, não existem muito manipuladores de mel.',
    'image_url': 'https://media.discordapp.net/attachments/1277763265379958794/1362443847946338627/helluva-boss-beelzebub-helluva-boss.gif?ex=68026a36&is=680118b6&hm=8100ddb1d0b33dd59d2f3188046760e9fee33f3ff6143edcd5cd68cce5c4db77&=',
    'color': Colors.AMARELO
},
'Vidro': {
    'title': 'Palavra: Vidro',
    'description': 'Definição: substância sólida, geralmente transparente e frágil, obtida pela fusão de areia com outros materiais.\n\n'
'- **Estágio 0**: Você é um mestre vidreiro, capaz de moldar, cortar e manipular vidro como ninguém.\n'
'- **Estágio 1**: Manipula transparência, resistência, cor e forma do vidro.\n'
'- **Estágio 2**: Geração de vidro, fusão e manipulação de estado (quebrado/integral), transformação parcial em vidro.\n'
'- **Passiva**: Resistência a cortes e reflexos aumentados.\n'
'- **Estágio 3**: Manipulação do conceito de vidro.\n'
'- **Modo: Irrestrito**: Pode redefinir o conceito do conceito de vidro temporariamente.',
    'image_url': 'https://media.discordapp.net/attachments/1277763265379958794/1362444302432731229/marika-break.gif?ex=68026aa2&is=68011922&hm=f5d2ebcae82e74c52ba10630d9f8b2ffbb76ab9ff0bad123afbab2400175aafc&=',
    'color': Colors.BRANCO
},

'Gasolina': {
    'title': 'Palavra: Gasolina',
    'description': 'Definição: combustível líquido derivado do petróleo, inflamável e volátil.\n\n'
'- **Estágio 0**: Você é o melhor em lidar com combustíveis e suas aplicações.\n'
'- **Estágio 1**: Manipula inflamabilidade, densidade, cor e pureza da gasolina.\n'
'- **Estágio 2**: Geração de gasolina, ignição controlada, transformação parcial em líquido inflamável.\n'
'- **Passiva**: Resistência a vapores tóxicos e combustão interna.\n'
'- **Estágio 3**: Manipula o conceito de gasolina.\n'
'- **Modo: Irrestrito**: Pode alterar temporariamente o conceito do conceito de gasolina.',
    'image_url': 'https://media.discordapp.net/attachments/1277763265379958794/1362444301971226624/rokka-no-yuusha-fire-breathing.gif?ex=68026aa2&is=68011922&hm=a174835d15656e60a67976829a72bd0e69e128c7cc5e8c66359ce2b36b1d71e1&=',
    'color': Colors.AMARELO
},

'Pólvora': {
    'title': 'Palavra: Pólvora',
    'description': 'Definição: mistura explosiva usada como propelente ou em explosivos.\n\n'
'- **Estágio 0**: Especialista em explosivos e munições artesanais.\n'
'- **Estágio 1**: Manipula potência, tempo de detonação, densidade e efeito da pólvora.\n'
'- **Estágio 2**: Geração espontânea de pólvora, ignição e transformação parcial em material explosivo.\n'
'- **Passiva**: Corpo adaptado a explosões e resistência acústica.\n'
'- **Estágio 3**: Manipulação do conceito de pólvora.\n'
'- **Modo: Irrestrito**: Pode alterar o conceito do conceito de pólvora temporariamente.',
    'image_url': 'hhttps://media.discordapp.net/attachments/1277763265379958794/1362444301342212216/youjo-senki-the-saga-of-tanya-the-evil.gif?ex=68026aa2&is=68011922&hm=ec95dbc7685c6bf5f729f1ea2e3ddcc361421f6c531c2a28fd257de0d3247e70&=',
    'color': Colors.PRETO
},

'Vácuo': {
    'title': 'Palavra: Vácuo',
    'description': 'Definição: espaço completamente desprovido de matéria; ausência total de ar.\n\n'
'- **Estágio 0**: Você é um mestre em criar ambientes selados e sistemas de vácuo naturais.\n'
'- **Estágio 1**: Manipula pressão, ausência de som, ausência de matéria em pequenas áreas.\n'
'- **Estágio 2**: Geração de bolsões de vácuo, remoção instantânea de ar e transformação parcial em entidade etérea.\n'
'- **Passiva**: Imunidade ao sufocamento e sentidos adaptados ao silêncio absoluto.\n'
'- **Estágio 3**: Manipulação do conceito de vácuo.\n'
'- **Modo: Irrestrito**: Pode alterar o conceito do conceito de vácuo por tempo limitado.',
    'image_url': 'https://media.discordapp.net/attachments/1277763265379958794/1362444303510540398/akira-implosion.gif?ex=68026aa2&is=68011922&hm=e80f2275750c79c6b12dd183b81bb4a45195dc622eeaca31a30e91df1f55a3f3&=',
    'color': Colors.PRETO
},

'Sangue': {
    'title': 'Palavra: Sangue',
    'description': 'Definição: fluido vital que circula pelo corpo, transportando oxigênio e nutrientes.\n\n'
'- **Estágio 0**: Você é o maior especialista em medicina, ferimentos e circulação.\n'
'- **Estágio 1**: Manipula viscosidade, cor, coagulação e fluxo do sangue (inclusive de outros).\n'
'- **Estágio 2**: Geração de sangue, controle absoluto sobre sangue alheio, transformação parcial em sangue.\n'
'- **Passiva**: Regeneração acelerada e leitura de sinais vitais.\n'
'- **Estágio 3**: Manipulação do conceito de sangue.\n'
'- **Modo: Irrestrito**: Pode alterar o conceito do conceito de sangue temporariamente.',
    'image_url': 'https://media.discordapp.net/attachments/1277763265379958794/1362444300503220234/zapp-renfro-blood-manipulation.gif?ex=68026aa2&is=68011922&hm=48c603ce059c7fc316e3216c7ca53e258868ef813e72032e1afc808453917189&=',
    'color': Colors.VERMELHO
},

'Fogo': {
    'title': 'Palavra: Fogo',
    'description': 'Definição: fenômeno que consiste no desprendimento de calor e luz produzidos pela combustão de um corpo; lume.\n\n'
'- **Estágio 0**: Você é o melhor em lidar com fogo de forma natural — acendê-lo, mantê-lo, controlá-lo em rituais ou práticas comuns.\n'
'- **Estágio 1**: Você manipula os atributos do fogo, como temperatura, cor, tamanho e comportamento.\n'
'- **Estágio 2**: Pode gerar fogo espontaneamente, extingui-lo à vontade e transformar seu corpo em chama.\n'
'- **Passiva**: Resistência extrema ao calor e imunidade a queimaduras.\n'
'- **Estágio 3**: Manipula o conceito de fogo.\n'
'- **Modo: Irrestrito**: Altera temporariamente o conceito do conceito de fogo, redefinindo o que significa arder ou queimar.',
    'image_url': 'https://media.discordapp.net/attachments/1277763265379958794/1362444302898430332/benimaru-shinmon-enn-enn-no-shouboutai.gif?ex=68026aa2&is=68011922&hm=8ebd407bfbb684f14a5a1f281bb1f8c41b80736c3efb01efe1a95362c1103ee1&=',
    'color': Colors.VERMELHO
},
'Relógio': {
    'title': 'Palavra: Relógio',
    'description': 'Definição: instrumento usado para medir e indicar o tempo.\n\n'
'- **Estágio 0**: Você é um mestre relojoeiro — entende e monta qualquer tipo de relógio com perfeição.\n'
'- **Estágio 1**: Manipula os atributos de relógios, como velocidade dos ponteiros, precisão, estilo e mecânica.\n'
'- **Estágio 2**: Geração de relógios, fusão com mecanismos, transformar partes do corpo em engrenagens funcionais.\n'
'- **Passiva**: No estágio 2, você pode sentir o "ritmo" de tudo — como se tudo tivesse um tique-taque sutil.\n'
'- **Estágio 3**: Manipula o conceito de relógio (ex: transformar qualquer objeto em um marcador de tempo).\n'
'- **Modo: Irrestrito**: Pode redefinir o conceito do conceito de relógio temporariamente.',
    'image_url': 'https://media.discordapp.net/attachments/1277763265379958794/1362448705189576915/date-a-live-kurumi.gif?ex=68026ebc&is=68011d3c&hm=c6444a5b54390c817ad7658ebc316cc70ab8f9b1d79d8b3613256e1a52c679be&=',
    'color': Colors.AMARELO
},

'Zweihander': {
    'title': 'Palavra: Zweihander',
    'description': 'Definição: espada longa de duas mãos, típica de soldados pesados medievais.\n\n'
'- **Estágio 0**: Você é um mestre em combate com espadas grandes, força, técnica e equilíbrio incomparáveis.\n'
'- **Estágio 1**: Manipula peso, corte, resistência e forma de espadas do tipo Zweihander.\n'
'- **Estágio 2**: Geração de grandes espadas, fusão com sua estrutura, transformação parcial em lâmina viva.\n'
'- **Passiva**: A cada golpe, você acumula força em ataques consecutivos.\n'
'- **Estágio 3**: Manipulação do conceito de Zweihander — qualquer coisa pode se tornar uma "espada de duas mãos".\n'
'- **Modo: Irrestrito**: Pode alterar o conceito do conceito de Zweihander temporariamente.',
    'image_url': 'https://media.discordapp.net/attachments/1277763265379958794/1362448704681939009/zweihander-dark-souls.gif?ex=68026ebc&is=68011d3c&hm=347803aab6ed9f92ed50a793a5d5d4c769cc42ef95a5ffac530bf8cfc3d12eb0&=',
    'color': Colors.PRETO
},

'Café': {
    'title': 'Palavra: Café',
    'description': 'Definição: bebida feita a partir dos grãos torrados do cafeeiro, estimulante e aromática.\n\n'
'- **Estágio 0**: Você é um barista lendário — domina sabores, texturas e efeitos do café.\n'
'- **Estágio 1**: Manipula aroma, temperatura, concentração e tipo de café (expresso, coado, gelado).\n'
'- **Estágio 2**: Geração de café com efeitos variados, manipulação de estado (líquido/vapor), transformação parcial.\n'
'- **Passiva**: Energia constante, foco elevado e resistência a sono e cansaço.\n'
'- **Estágio 3**: Manipula o conceito de café — fazer com que algo “seja café”.\n'
'- **Modo: Irrestrito**: Pode alterar temporariamente o conceito do conceito de café.',
    'image_url': 'https://media.discordapp.net/attachments/1277763265379958794/1362448704274956288/coffee-overflow.gif?ex=68026ebc&is=68011d3c&hm=a3cdef0eeb7cfaabe8c63458f190f22a8482bb485fbae50a4c332526c5e4a7c7&=',
    'color': Colors.PRETO
},

'Vela': {
    'title': 'Palavra: Vela',
    'description': 'Definição: objeto geralmente de cera com um pavio, usado para iluminação.\n\n'
'- **Estágio 0**: Você é expert em fabricação, manuseio e uso ritualístico de velas.\n'
'- **Estágio 1**: Manipula cor, duração, formato e tipo de chama da vela (sem controlar o fogo em si).\n'
'- **Estágio 2**: Geração de velas, fusão com cera, transformação parcial em vela viva (sem se queimar).\n'
'- **Passiva**: Sua presença traz foco e clareza para quem estiver por perto.\n'
'- **Estágio 3**: Manipula o conceito de vela — iluminar com presença, guiar, marcar o tempo.\n'
'- **Modo: Irrestrito**: Pode alterar temporariamente o conceito do conceito de vela.',
    'image_url': 'https://media.discordapp.net/attachments/1277763265379958794/1362448703843205130/mr-3-one-piece-mr-3.gif?ex=68026ebc&is=68011d3c&hm=86364981a6e2194f09326a5e20bdd8db96ef503d0eadd36fd585ead603170777&=',
    'color': Colors.AMARELO
},
'Papel': {
    'title': 'Palavra: Papel',
    'description': 'Definição: material feito de fibras vegetais usado para escrita, impressão ou embalagem.\n\n'
'- **Estágio 0**: Você é um mestre na arte do papel — origami, caligrafia, encadernação, tudo com perfeição.\n'
'- **Estágio 1**: Manipula textura, espessura, resistência e tipo do papel.\n'
'- **Estágio 2**: Geração de papel com propriedades especiais, transformação parcial em papel, manipulação de estado (amassado, rasgado, liso).\n'
'- **Passiva**: Você pode registrar qualquer coisa com precisão apenas tocando o papel.\n'
'- **Estágio 3**: Manipula o conceito de papel — qualquer superfície pode ser transformada em papel.\n'
'- **Modo: Irrestrito**: Pode alterar temporariamente o conceito do conceito de papel.',
    'image_url': 'https://media.discordapp.net/attachments/1277763265379958794/1362448703339761746/sml-jeffy.gif?ex=68026ebb&is=68011d3b&hm=274b08007ca352c775861c11821318d1aff940c580e598f6e3218f38421dd926&=',
    'color': Colors.BRANCO
},

'Tinta': {
    'title': 'Palavra: Tinta',
    'description': 'Definição: líquido colorido usado para escrever, desenhar ou imprimir.\n\n'
'- **Estágio 0**: Você domina todas as formas de pintura, escrita e arte com tinta.\n'
'- **Estágio 1**: Manipula cor, viscosidade, secagem e permanência da tinta.\n'
'- **Estágio 2**: Geração de tinta viva, escrita que se move, transformação parcial em fluido artístico.\n'
'- **Passiva**: Toda sua tinta expressa mais do que palavras — sentimentos, intenções e memórias.\n'
'- **Estágio 3**: Manipula o conceito de tinta — aquilo que expressa, imprime ou marca.\n'
'- **Modo: Irrestrito**: Pode alterar temporariamente o conceito do conceito de tinta.',
    'image_url': 'https://media.discordapp.net/attachments/1277763265379958794/1362448702945493172/gabbiehanna-thegabbieshow.gif?ex=68026ebb&is=68011d3b&hm=545f55b2de8d1564b4eb38615923ee69e706d1c2007626523793d32c12301a10&=',
    'color': Colors.PRETO
},

'Trompete': {
    'title': 'Palavra: Trompete',
    'description': 'Definição: instrumento musical de sopro, metálico, com som vibrante e poderoso.\n\n'
'- **Estágio 0**: Você é um músico virtuoso no trompete, domina técnica, melodia e improviso.\n'
'- **Estágio 1**: Manipula tom, alcance, reverberação e intensidade do som do trompete.\n'
'- **Estágio 2**: Geração de trompetes etéreos, som sólido, fusão com o instrumento, transformação parcial.\n'
'- **Passiva**: Seu som alcança corações — capaz de inspirar ou silenciar multidões.\n'
'- **Estágio 3**: Manipula o conceito de trompete — tudo pode soar como um.\n'
'- **Modo: Irrestrito**: Pode alterar temporariamente o conceito do conceito de trompete.',
    'image_url': 'https://media.discordapp.net/attachments/1277763265379958794/1362448702605885480/nichijou-silly.gif?ex=68026ebb&is=68011d3b&hm=e9cc512cf418263c3f741f11d97b8e0c49998f9bd7dd8884143db85c058f9202&=',
    'color': Colors.AMARELO
},

'Porta': {
    'title': 'Palavra: Porta',
    'description': 'Definição: estrutura móvel usada para fechar ou permitir a passagem entre espaços.\n\n'
'- **Estágio 0**: Você é o melhor em construir, trancar, destrancar e entender portas de todos os tipos.\n'
'- **Estágio 1**: Manipula tamanho, forma, abertura, som e material das portas.\n'
'- **Estágio 2**: Geração de portas que conectam lugares (sem teletransporte), fusão com portas, transformação parcial.\n'
'- **Passiva**: Pode sentir o que há do outro lado de qualquer passagem.\n'
'- **Estágio 3**: Manipula o conceito de porta — qualquer coisa pode se tornar ou funcionar como uma.\n'
'- **Modo: Irrestrito**: Pode alterar temporariamente o conceito do conceito de porta.',
    'image_url': 'https://media.discordapp.net/attachments/1277763265379958794/1362448705562738768/welcome-to-the-game-lucas.gif?ex=68026ebc&is=68011d3c&hm=ed3b0d29a06faac6e71fb18c8d4235ed20899adfe0db0484ffe91247099f7dca&=',
    'color': Colors.VERDE
},

'Lixo': {
    'title': 'Palavra: Lixo',
    'description': 'Definição: tudo aquilo considerado inútil ou descartável.\n\n'
'- **Estágio 0**: Você é mestre em reciclagem, aproveitamento e reaproveitamento de resíduos.\n'
'- **Estágio 1**: Manipula odor, densidade, toxicidade e utilidade aparente do lixo.\n'
'- **Estágio 2**: Geração de lixo mutável, fusão com descarte, transformação parcial em massa de resíduo.\n'
'- **Passiva**: Nada em você é desperdiçado, tudo se transforma.\n'
'- **Estágio 3**: Manipula o conceito de lixo — aquilo que é inútil pode se tornar essencial.\n'
'- **Modo: Irrestrito**: Pode alterar temporariamente o conceito do conceito de lixo.',
    'image_url': 'https://media.discordapp.net/attachments/1277763265379958794/1362448882247663636/goodbye-im-out.gif?ex=68026ee6&is=68011d66&hm=20d6b62cb2d2ba15afd8fbdff9dea11f6f2a4bb44e71bbac6f523677d9614ca3&=',
    'color': Colors.PRETO
},

'Argila': {
    'title': 'Palavra: Argila',
    'description': 'Definição: material terroso, moldável quando úmido, usado em cerâmica e escultura.\n\n'
'- **Estágio 0**: Você é um escultor sem igual, moldando argila com perfeição intuitiva.\n'
'- **Estágio 1**: Manipula dureza, secagem, plasticidade e tipo da argila.\n'
'- **Estágio 2**: Geração de argila viva, moldagem instantânea, transformação parcial.\n'
'- **Passiva**: Seu corpo pode absorver impactos como barro e voltar à forma original.\n'
'- **Estágio 3**: Manipula o conceito de argila — tudo pode ser modelado.\n'
'- **Modo: Irrestrito**: Pode alterar temporariamente o conceito do conceito de argila.',
    'image_url': 'https://media.discordapp.net/attachments/1277763265379958794/1362449077576663231/clay-mud.gif?ex=68026f15&is=68011d95&hm=8d68c4569280be6341051368b7ccec0052b4c55ae9ca154edd7e52f855a3bad2&=',
    'color': Colors.VERMELHO
},

'Lâmina': {
    'title': 'Palavra: Lâmina',
    'description': 'Definição: parte cortante de instrumentos como facas e espadas.\n\n'
'- **Estágio 0**: Você é um mestre forjador e lutador com lâminas de todo tipo.\n'
'- **Estágio 1**: Manipula fio, forma, flexibilidade e composição da lâmina.\n'
'- **Estágio 2**: Geração de lâminas, fusão ao corpo, transformação parcial em corte puro.\n'
'- **Passiva**: Seus movimentos são afiados — corta o ar e até intenções.\n'
'- **Estágio 3**: Manipula o conceito de lâmina — tudo pode cortar.\n'
'- **Modo: Irrestrito**: Pode alterar temporariamente o conceito do conceito de lâmina.',
    'image_url': 'https://static.wikia.nocookie.net/powerlisting/images/6/65/Shirou_Emiya_%28TYPE-MOON%29_Tracing.gif',
    'color': Colors.BRANCO
},

'Prego': {
    'title': 'Palavra: Prego',
    'description': 'Definição: peça metálica usada para unir objetos, geralmente batida com martelo.\n\n'
'- **Estágio 0**: Você é um mestre construtor — precisão absoluta em unir, fixar e montar estruturas.\n'
'- **Estágio 1**: Manipula tamanho, resistência, aderência e direção de pregos.\n'
'- **Estágio 2**: Geração de pregos, controle de impacto, transformação parcial em metal penetrante.\n'
'- **Passiva**: Você fixa ideias e pessoas com sua presença firme.\n'
'- **Estágio 3**: Manipula o conceito de prego — o que fixa, une ou atravessa.\n'
'- **Modo: Irrestrito**: Pode alterar temporariamente o conceito do conceito de prego.',
    'image_url': 'https://media.discordapp.net/attachments/1277763265379958794/1362448881727832205/souichi-tsujii-junji-ito.gif?ex=68026ee6&is=68011d66&hm=356d1701d552b9351f1d81c71651fe353a520a411338d0369772234787af12d9&=',
    'color': Colors.BRANCO
},

'Bússola': {
    'title': 'Palavra: Bússola',
    'description': 'Definição: instrumento que indica a direção geográfica, geralmente apontando para o norte.\n\n'
'- **Estágio 0**: Você é um navegador imbatível, sempre encontra seu caminho.\n'
'- **Estágio 1**: Manipula direção, precisão, escala e função de bússolas.\n'
'- **Estágio 2**: Geração de bússolas intuitivas, transformação parcial em entidade que aponta o caminho.\n'
'- **Passiva**: Você sempre sabe onde está e para onde precisa ir.\n'
'- **Estágio 3**: Manipula o conceito de bússola — qualquer coisa pode guiar ou orientar.\n'
'- **Modo: Irrestrito**: Pode alterar temporariamente o conceito do conceito de bússola.',
    'image_url': 'https://media.discordapp.net/attachments/1277763265379958794/1362448884466450482/compass.gif?ex=68026ee7&is=68011d67&hm=8d7252a20085c7523d10bb2c2f66c119cbc2dda232598c6ad823db9e8e7fe43a&=',
    'color': Colors.BRANCO
},

'Carta': {
    'title': 'Palavra: Carta',
    'description': 'Definição: mensagem escrita em papel, enviada de uma pessoa para outra.\n\n'
'- **Estágio 0**: Você escreve e interpreta cartas com precisão e impacto emocional inigualáveis.\n'
'- **Estágio 1**: Manipula forma, estilo, conteúdo e entrega de cartas.\n'
'- **Estágio 2**: Geração de cartas com efeitos únicos, transformação parcial em portador de mensagens.\n'
'- **Passiva**: Toda mensagem sua chega exatamente onde deve, mesmo sem endereço.\n'
'- **Estágio 3**: Manipula o conceito de carta — o que comunica entre distâncias.\n'
'- **Modo: Irrestrito**: Pode alterar temporariamente o conceito do conceito de carta.',
    'image_url': 'https://media.discordapp.net/attachments/1277763265379958794/1362448884017791136/banned.gif?ex=68026ee7&is=68011d67&hm=7b2a75f547b6c6a3bf3deb3b362b2c702add6c36dba014cbf477a661a52d1a0c&=',
    'color': Colors.BRANCO
},

'Machadinha': {
    'title': 'Palavra: Machadinha',
    'description': 'Definição: Machado que se maneja com uma só mão.\n\n'
'- **Estágio 0**: Você é um lutador e desbravador de elite com a Machadinha.\n'
'- **Estágio 1**: Manipula peso, resistência, fio e alcance da Machadinha.\n'
'- **Estágio 2**: Geração de Machadinhas rústicas, corte brutal, fusão com o corpo, transformação parcial.\n'
'- **Passiva**: Seus ataques abrem caminho mesmo em situações impossíveis.\n'
'- **Estágio 3**: Manipula o conceito de Machadinha — força para romper obstáculos.\n'
'- **Modo: Irrestrito**: Pode alterar temporariamente o conceito do conceito de Machadinha.',
    'image_url': 'https://media.discordapp.net/attachments/1277763265379958794/1362448883233456188/anime.gif?ex=68026ee6&is=68011d66&hm=b04a10394035c45f3c3c917eeb2765c984d6c2c0f51b71259d378af7cacae086&=',
    'color': Colors.PRETO
},

'Sino': {
    'title': 'Palavra: Sino',
    'description': 'Definição: objeto metálico que emite som ao ser percutido, geralmente usado como sinalizador.\n\n'
'- **Estágio 0**: Você é mestre em sinos, seus toques ressoam de forma única e precisa.\n'
'- **Estágio 1**: Manipula tom, volume, eco e alcance dos sinos.\n'
'- **Estágio 2**: Geração de sinos com efeitos especiais, fusão com ressonância, transformação parcial.\n'
'- **Passiva**: Seus sons atravessam barreiras, ecoando até na alma.\n'
'- **Estágio 3**: Manipula o conceito de sino — o que anuncia, chama ou desperta.\n'
'- **Modo: Irrestrito**: Pode alterar temporariamente o conceito do conceito de sino.',
    'image_url': 'https://media.discordapp.net/attachments/1277763265379958794/1362448882835128370/one-piece-luffy.gif?ex=68026ee6&is=68011d66&hm=52c8c18e7c34396640303f5e5486c81dd7d4b9d75b3f3f790db0d1cd560e0100&=',
    'color': Colors.AMARELO
},
'Canino': {
    'title': 'Palavra: Canino',
    'description': 'Definição: mamíferos da família dos cães, conhecidos por seu faro aguçado, sociabilidade e instintos de matilha.\n\n'
'- **Estágio 0**: Você compreende e interage com cães e animais caninos melhor do que qualquer um.\n'
'- **Estágio 1**: Pode manipular atributos de caninos — Tanto seus quanto de um canino.\n'
'- **Estágio 2**: Pode transformar-se parcial ou totalmente em um canino.\n'
'- **Passiva**: Caninos se alinham naturalmente a você. Seus sentidos são reforçados.\n'
'- **Estágio 3**: Manipula o conceito de canino — instintos, lealdade, matilha e comportamento podem se manifestar em qualquer coisa.\n'
'- **Modo: Irrestrito**: Altera temporariamente o conceito do conceito de canino.',
    'image_url': 'https://media.discordapp.net/attachments/1277763265379958794/1362450665993011200/stephanie-dora-stephanie-dola.gif?ex=6802708f&is=68011f0f&hm=1acdfc89790d0b4ff918c9545e5396ac8ae489937a6644965c7fd296409ab7d1&=',
    'color': Colors.VERMELHO
},

'Raposa': {
    'title': 'Palavra: Raposa',
    'description': 'Definição: mamífero ágil e astuto, geralmente solitário, conhecido por sua inteligência e adaptação.\n\n'
'- **Estágio 0**: Você entende perfeitamente o comportamento e padrões das raposas.\n'
'- **Estágio 1**: Manipula atributos de raposas — Tanto seus quanto de uma raposa.\n'
'- **Estágio 2**: Pode transformar-se parcial ou totalmente em uma raposa.\n'
'- **Passiva**: Você naturalmente confunde sensores e percebe armadilhas intuitivamente.\n'
'- **Estágio 3**: Manipula o conceito de raposa — astúcia, camuflagem e independência tomam forma onde quiser.\n'
'- **Modo: Irrestrito**: Altera temporariamente o conceito do conceito de raposa.',
    'image_url': 'https://media.discordapp.net/attachments/1277763265379958794/1362450665330446640/kawaii-fox-girl-love.gif?ex=6802708f&is=68011f0f&hm=f86a95238e4c61f778b7a322203ed9840cfbf4f0bd6bc833776e8da8b95318ab&=',
    'color': Colors.AMARELO
},

'Inseto': {
    'title': 'Palavra: Inseto',
    'description': 'Definição: grupo de artrópodes com corpo segmentado, exoesqueleto e seis patas, altamente adaptáveis.\n\n'
'- **Estágio 0**: Você entende o comportamento, ciclo de vida e comunicação dos insetos.\n'
'- **Estágio 1**: Manipula atributos dos insetos — Tanto seus quanto de um inseto.\n'
'- **Estágio 2**: Pode se transformar em um inseto ou forma híbrida, alem de poder passar por uma metamorfose, vulgo, modo de defesa.\n'
'- **Passiva**: Insetos não o atacam e podem ser convocados instintivamente.\n'
'- **Estágio 3**: Manipula o conceito de inseto — enxame, multiplicidade e adaptação se tornam forças amplas.\n'
'- **Modo: Irrestrito**: Altera temporariamente o conceito do conceito de inseto.',
    'image_url': 'https://media.discordapp.net/attachments/1277763265379958794/1362450664780857364/jogo-insect.gif?ex=6802708f&is=68011f0f&hm=db90d459157a1af113a502fca18a9338d45e098fd08904142ce993e6eb1cc1a6&=',
    'color': Colors.VERDE
},

'Peixe': {
    'title': 'Palavra: Peixe',
    'description': 'Definição: vertebrados aquáticos que respiram por guelras, possuem nadadeiras e vivem em ecossistemas aquáticos.\n\n'
'- **Estágio 0**: Você entende peixes, seus sentidos e funcionamento subaquático com perfeição.\n'
'- **Estágio 1**: Manipula atributos de peixes — Tanto seus quanto de um peixe.\n'
'- **Estágio 2**: Pode se transformar em peixe ou forma híbrida.\n'
'- **Passiva**: Você respira embaixo d’água e nada com facilidade sobrenatural.\n'
'- **Estágio 3**: Manipula o conceito de peixe — fluidez, invisibilidade e adaptação a ambientes extremos.\n'
'- **Modo: Irrestrito**: Altera temporariamente o conceito do conceito de peixe.',
    'image_url': 'https://media.discordapp.net/attachments/1277763265379958794/1362450669633798429/merman-mermaid.gif?ex=68027090&is=68011f10&hm=29b183c5417f9ec5e0bff67967afe46580aae2a2f36cc1097fb28d3e40532340&=',
    'color': Colors.CIANO
},

'Anfíbio': {
    'title': 'Palavra: Anfíbio',
    'description': 'Definição: vertebrados de vida dupla, como sapos e salamandras, que vivem em terra e na água.\n\n'
'- **Estágio 0**: Você entende totalmente o comportamento e funções dos anfíbios.\n'
'- **Estágio 1**: Manipula atributos de anfíbios — Tanto seus quanto de um anfíbio.\n'
'- **Estágio 2**: Pode se transformar em um anfíbio ou forma mista.\n'
'- **Passiva**: Sua pele regula naturalmente a temperatura e umidade do ambiente.\n'
'- **Estágio 3**: Manipula o conceito de anfíbio — transição, adaptação e dualidade se manifestam em seres e ambientes.\n'
'- **Modo: Irrestrito**: Altera temporariamente o conceito do conceito de anfíbio.',
    'image_url': 'https://media.discordapp.net/attachments/1277763265379958794/1362450669193134130/clover-studios-fourleafclover.gif?ex=68027090&is=68011f10&hm=d823fc984fd7dd0753257f14cf3315831ec4f73baeaf061602fa994e616fc143&=',
    'color': Colors.VERDE
},

'Ave': {
    'title': 'Palavra: Ave',
    'description': 'Definição: vertebrados com penas, bico, ossos pneumáticos e, geralmente, capacidade de voar.\n\n'
'- **Estágio 0**: Você entende a comunicação e hábitos migratórios e territoriais das aves.\n'
'- **Estágio 1**: Manipula atributos de aves — Tanto seus quanto de uma ave.\n'
'- **Estágio 2**: Pode se transformar em uma ave ou forma alada.\n'
'- **Passiva**: Você pode flutuar levemente e possui senso de orientação excepcional.\n'
'- **Estágio 3**: Manipula o conceito de ave — liberdade, altura e observação se espalham por onde quiser.\n'
'- **Modo: Irrestrito**: Altera temporariamente o conceito do conceito de ave.',
    'image_url': 'https://media.discordapp.net/attachments/1277763265379958794/1362450668471849210/one-piece-one-piece-pell.gif?ex=68027090&is=68011f10&hm=38b41b13d90b60f89e09f05132335aec7c900e9128cab82fe491cff7211e7ec3&=',
    'color': Colors.CIANO
},

'Réptil': {
    'title': 'Palavra: Réptil',
    'description': 'Definição: animais vertebrados de sangue frio com escamas, como cobras, lagartos e jacarés.\n\n'
'- **Estágio 0**: Você entende com perfeição o comportamento, fisiologia e adaptação de répteis.\n'
'- **Estágio 1**: Manipula atributos de répteis — Tanto seus quanto de um réptil.\n'
'- **Estágio 2**: Pode se transformar em um réptil ou forma híbrida.\n'
'- **Passiva**: Você se adapta ao ambiente termicamente e se move silenciosamente.\n'
'- **Estágio 3**: Manipula o conceito de réptil — sangue frio, paciência e força latente se impõem.\n'
'- **Modo: Irrestrito**: Altera temporariamente o conceito do conceito de réptil.',
    'image_url': 'https://media.discordapp.net/attachments/1277763265379958794/1362450667553165554/cuca-crocodile.gif?ex=68027090&is=68011f10&hm=4bba783ca6c6472b2309b858b0d40445db1e9a313106f49d8ab9acbd7a1698f1&=',
    'color': Colors.VERDE
},

'Touro/Vaca': {
    'title': 'Palavra: Touro/Vaca',
    'description': 'Definição: grandes mamíferos herbívoros domesticados, conhecidos por sua força e persistência.\n\n'
'- **Estágio 0**: Você entende profundamente o comportamento de bovinos e os acalma com facilidade.\n'
'- **Estágio 1**: Manipula atributos desses animais — Tanto seus quanto de um Touro/Vaca.\n'
'- **Estágio 2**: Pode se transformar em um touro, vaca ou forma híbrida.\n'
'- **Passiva**: Você é extremamente resistente a empurrões, cargas e controle emocional.\n'
'- **Estágio 3**: Manipula o conceito de bovino — força bruta, calma e resiliência podem ser aplicadas onde desejar.\n'
'- **Modo: Irrestrito**: Altera temporariamente o conceito do conceito de touro/vaca.',
    'image_url': 'https://media.discordapp.net/attachments/1277763265379958794/1362450666785603777/looney-tunes.gif?ex=68027090&is=68011f10&hm=853900f8e57f27405b9ba92c5dc74da5f6dd68dba73819638239a745c9ae221a&=',
    'color': Colors.VERMELHO
},




    'Pobrs': {
        'title': 'Pobrs',
        'description': (
        'Você quer levar sua esposa e seus 8 filhos pra comer fora mas não tem dinheiro pra sair nem da favela? Não tema, o Pobrs é a solução!'
        'Lancheria acessível, podrão delícia com gordura velha e todo tipo de marca de refrigerante, de álcool só glacial.\n\n'
           ),
        'image_url': 'https://media.discordapp.net/attachments/1361048544596988256/1361048563727204392/cd06f1f8ad33c9202d01e2ec785f6aff.png?ex=68014b40&is=67fff9c0&hm=a8016e407a13f9c5fb563d81f4ffc9e24bbb979cd3ea1796cf05e9a85f43410f&=&format=webp&quality=lossless',  # Substitua pelo URL real da imagem
        'color': Colors.PRETO,
        'apenas_imagem': True
    },
}

# Lista de todos os comandos disponíveis para sugestões
AVAILABLE_COMMANDS = ['roll', 'help_roll', 'wiki']

@bot.event
async def on_ready():
    print(f'{bot.user.name} conectou-se ao Discord!')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        # Obtém o comando que o usuário tentou usar
        command_name = ctx.message.content.split()[0][1:]
        
        # Encontra o comando mais próximo usando difflib
        closest_matches = difflib.get_close_matches(command_name, AVAILABLE_COMMANDS, n=1, cutoff=0.5)
        
        if closest_matches:
            await ctx.send(f'Você quis dizer `!{closest_matches[0]}`?')
        else:
            await ctx.send('Comando não encontrado. Use `!help_roll` para ver os comandos disponíveis.')

@bot.command(name='roll')
async def roll(ctx, option=None):
    """Rola para uma opção aleatória com base na categoria especificada."""
    if not option:
        await ctx.send('Por favor, especifique uma categoria para rolar: `!roll <opção>` (grupo, poderes, maldicoes)')
        return
    
    option = option.lower()
    
    if option not in OPTION_CATEGORIES:
        await ctx.send('Categoria inválida. Categorias disponíveis: grupo, poderes, maldicoes')
        return
    
    # Obtém o dicionário de opções e calcula os pesos automaticamente
    options_dict = calculate_weights(OPTION_CATEGORIES[option])
    
    # Obtém as opções e seus pesos calculados
    options = list(options_dict.keys())
    weights = [options_dict[opt]['weight'] for opt in options]
    
    # Seleciona aleatoriamente uma opção com base nos pesos
    result = random.choices(options, weights=weights, k=1)[0]
    result_data = options_dict[result]
    
    # Cria um embed para o resultado
    embed = discord.Embed(
        title=f"Resultado do Roll: {option.capitalize()}",
        description=f"Você rolou: **{result}**",
        color=result_data['color']
    )
    
    embed.add_field(name="Raridade", value=result_data['rarity'].name.capitalize(), inline=False)
    
    # Adiciona o campo de categoria para poderes ou função para grupo
    if option == 'poderes' and 'category' in result_data:
        embed.add_field(name="Categoria", value=result_data['category'], inline=False)
    elif option == 'grupo' and 'function' in result_data:
        embed.add_field(name="Função", value=result_data['function'], inline=False)
    
    embed.set_footer(text=f"Solicitado por {ctx.author.display_name}")
    
    await ctx.send(embed=embed)

@bot.command(name='wiki')
async def wiki(ctx, *, item=None):
    """Exibe informações detalhadas sobre um item específico."""
    if not item:
        await ctx.send('Por favor, especifique um item para consultar: `!wiki <nome do item>`')
        return
    
    # Procura o item no dicionário WIKI_INFO
    # Primeiro tenta uma correspondência exata
    if item in WIKI_INFO:
        item_info = WIKI_INFO[item]
    else:
        # Se não encontrar, tenta encontrar uma correspondência parcial
        possible_matches = [key for key in WIKI_INFO.keys() if item.lower() in key.lower()]
        
        if len(possible_matches) == 1:
            # Se encontrar apenas uma correspondência parcial, usa ela
            item_info = WIKI_INFO[possible_matches[0]]
        elif len(possible_matches) > 1:
            # Se encontrar múltiplas correspondências, mostra as opções
            matches_text = '\n'.join([f'`{match}`' for match in possible_matches])
            await ctx.send(f'Encontrei múltiplas correspondências para "{item}". Por favor, seja mais específico:\n{matches_text}')
            return
        else:
            # Se não encontrar nenhuma correspondência
            await ctx.send(f'Não encontrei informações sobre "{item}". Verifique a ortografia ou tente outro item.')
            return
    
    # Cria um embed com as informações do item
    embed = discord.Embed(
        title=item_info['title'],
        description=item_info['description'],
        color=item_info['color']
    )
    
    # Verifica se o item tem uma URL de imagem ou GIF e a exibe
    if 'image_url' in item_info:
        image_url = item_info['image_url']
        # Converte URLs do Tenor para URLs diretas de GIF
        if 'tenor.com/view/' in image_url and not image_url.endswith('.gif'):
            # Adiciona .gif ao final da URL para obter a URL direta do GIF
            image_url = f"https://media.tenor.com/images/{image_url.split('/')[-1].split('-')[0]}/tenor.gif"
        # Verifica se é uma URL do wikia que pode estar com problemas
        elif 'static.wikia.nocookie.net' in image_url:
            # Remove parâmetros de URL que podem causar problemas
            if '?' in image_url:
                image_url = image_url.split('?')[0]
        embed.set_image(url=image_url)
    
    # Verifica se o item deve mostrar apenas descrição e imagem usando a propriedade 'apenas_imagem'
    # Para adicionar novos itens que mostram apenas imagem, basta definir 'apenas_imagem': True no dicionário
    if not item_info.get('apenas_imagem', False):
        # Para itens que não são apenas imagem, mostra benefício e malefício se existirem
        if 'beneficio' in item_info:
            embed.add_field(name="Benefício", value=item_info['beneficio'], inline=False)
        if 'maleficio' in item_info:
            embed.add_field(name="Malefício", value=item_info['maleficio'], inline=False)
    
    embed.set_footer(text=f"Solicitado por {ctx.author.display_name}")
    
    await ctx.send(embed=embed)

@bot.command(name='help_roll')
async def help_roll(ctx):
    """Exibe informações de ajuda para o comando roll."""
    embed = discord.Embed(
        title="Ajuda do Comando Roll",
        description="Use o comando roll para obter uma opção aleatória de diferentes categorias.",
        color=0x3498db
    )
    
    embed.add_field(
        name="Uso",
        value="`!roll <categoria>`",
        inline=False
    )
    
    embed.add_field(
        name="Categorias Disponíveis",
        value="`grupo` - Role para um grupo (Uzumaki, Uchiha, Kobayashi)\n"
              "`poderes` - Role para um poder (Gelo, Fogo, Trovão)\n"
              "`maldicoes` - Role para uma maldição (Maldição 1, Maldição 2, Maldição 3)",
        inline=False
    )
    
    embed.add_field(
        name="Outros Comandos",
        value="`!wiki <item>` - Consulta informações detalhadas sobre um item específico",
        inline=False
    )
    
    embed.set_footer(text=f"Solicitado por {ctx.author.display_name}")
    
    await ctx.send(embed=embed)

# Executa o bot
if __name__ == '__main__':
    bot.run(TOKEN)