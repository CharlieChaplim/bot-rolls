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
    'Machete': {'rarity': RaridadesPesos.RARO, 'color': Colors.VERDE, 'category': 'Objetos'},
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
    
    # Verifica se o item deve mostrar apenas descrição e imagem usando a propriedade 'apenas_imagem'
    # Para adicionar novos itens que mostram apenas imagem, basta definir 'apenas_imagem': True no dicionário
    if item_info.get('apenas_imagem', False):
        embed.set_image(url=item_info['image_url'])
    else:
        # Para outros itens, mostra benefício e malefício
        embed.add_field(name="Benefício", value=item_info['beneficio'], inline=False)
        
    
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