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
    LARANJA: int = 0xff5900

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
        'beneficio': "Você pode virar um corvo quando bem entender. 'You don't understand ruby, he turned me into a BIRD!'",
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
"""A Uno é a espinha dorsal do submundo da informação. Num sistema onde o conhecimento é moeda de poder,  a Uno atua como a principal detentora e negociadora de segredos. Sua estrutura é dividida entre funcionários  administrativos, "olhos" e "ouvidos", cada qual com uma função clara na teia de vigilância urbana. Em meio à  liberdade caótica da cidade, a Uno prospera oferecendo informações precisas, vendidas por preço alto — em favores, recursos ou dados. Seu atual líder é **Raviel**.\n
- **Funcionários**: Responsáveis por organizar, catalogar e gerenciar os dados obtidos. Trabalham em escritórios ocultos, muitas vezes sem saber quem são os espiões ou de onde vêm as informações.
- **Olhos**: São os observadores, infiltrados em locais estratégicos, com poderes voltados à percepção, análise e ilusão. São os responsáveis por capturar imagens, cenas e comportamentos.
- **Ouvidos**: Mestres em escuta e infiltração, operam como sombras nos corredores da cidade. Com habilidades de mimetismo e espionagem auditiva, são eles que interceptam conversas, confissões e ameaças."""
    ),
    'image_url': 'https://i.imgur.com/RPuGOvA.png',
    'color': Colors.ROXO,
    'apenas_imagem': True
},

    'Zwei': {
        'title': 'Zwei - Proteção',
        'description': (
"""A Zwei representa o braço protetor da cidade, mesmo num sistema onde a segurança é uma escolha de mercado. Seus membros vestem armaduras pesadas e agem guiados por um ideal de preservação da vida — mesmo quando isso entra em choque com o lucro. Com ações marcadas por coragem e sacrifício, a Zwei é respeitada, mas sua ética altruísta frequentemente causa atritos com o restante da cidade. Sua atual líder é **Tereza**.\n
- **Funcionários**: Trabalham na base de operações, organizando patrulhas, missões de resgate e logística da milícia.
- **Milícia**: Força de combate principal, equipada com armaduras rústicas e poderes defensivos. Atuam em emergências e zonas de risco elevado.
- **Escudo**: Especialistas em contenção e evacuação. Se colocam entre o perigo e os civis, mesmo que isso custe caro."""
    ),
        'image_url': 'https://imgur.com/D5idwnG.png',  # Substitua pelo URL real da imagem
        'color': Colors.AZUL,
        'apenas_imagem': True
    },
    'San': {
        'title': 'San - Transporte',
        'description': (
"""A San é o motor movido a carvão que nunca para. Como a maior transportadora da cidade, sua lógica é simples: lucro sobre trilhos. Com linhas ferroviárias cruzando setores inteiros, a San é a espinha dorsal da logística urbana e industrial. Seus cortes de gastos extremos levaram à criação de forças armadas internas — a temida Equipe de Limpeza. Seu atual líder é **Hermiton**, uma figura difícil de encontrar até para seus subordinados.\n
- **Funcionários**: Administram rotas, vagões e manutenção mínima. Trabalham sob intensa pressão por resultados.
- **Equipe de Limpeza**: Força de combate interna da San, especializada em lidar com "imprevistos", como assaltos, sabotagens e greves.
- **Equipe de Manutenção**: Com poderes voltados à reconstrução e tecnologia, mantém os trilhos operacionais mesmo sob condições adversas."""
    ),
        'image_url': 'https://i.imgur.com/MJvwO8B.png',  # Substitua pelo URL real da imagem
        'color': Colors.AMARELO,
        'apenas_imagem': True
    },
    'Arba\'a': {
        'title': 'Arba\'a - Assasinatos',
        'description': (
"""A Arba’a vive um período de reconstrução após uma queda catastrófica. Antigamente temida como a organização de assassinos mais mortal da cidade, hoje opera nas sombras, tentando retomar seu prestígio. Cada “dedo” da Arba’a representa um estilo único de morte, refletindo a especialização da hierarquia. São cinco grupos principais, conhecidos como a mão da morte. Atualmente, a líder é **Ilya**.\n
- **Funcionários**: Administram contratos, pagamentos e a estrutura decadente da organização.
- **Padrinho & Madrinha**: Líderes da velha guarda. Agem com brutalidade e precisão cirúrgica, mantendo viva a tradição da Arba’a.
- **Polegar**: Especialistas em força bruta — confrontos diretos, mortes viscerais.
- **Indicador**: Mestres das armas de fogo. Precisos e raros numa cidade onde munição é escassa.
- **Meio**: Disciplinados e metódicos. Matam com o corpo, usando artes marciais e anatomia.
- **Anelar**: Sussurram a morte. Agem com extrema sutileza, invisíveis.
- **Mínimo**: Engenheiros da morte indireta. Armadilhas, explosivos e venenos letais e silenciosos."""
    ),
        'image_url': 'https://i.imgur.com/QTf3dbV.png',  # Substitua pelo URL real da imagem
        'color': Colors.VERMELHO,
        'apenas_imagem': True
    },
    'Cinq': {
        'title': 'Cinq - Justiça',
        'description': (
"""A Cinq é a encarnação da lei absoluta em meio ao caos. Mesmo numa sociedade onde a liberdade impera, alguém precisa traçar limites — ou ao menos parecer que o faz. Sua sede imponente e julgamentos públicos tornaram a Cinq uma entidade temida e reverenciada. Suas decisões são definitivas e suas execuções, exemplares. Seu atual líder é **Peter**.\n
- **Funcionários**: Secretários, analistas e operadores jurídicos. Reúnem provas e organizam julgamentos.
- **Juiz**: Autoridades supremas. Julgam com base na tradição e interpretação pessoal da justiça.
- **Executor**: Cumpre as sentenças. Letal e implacável, com poderes voltados à punição e fim."""
    ),
        'image_url': 'https://i.imgur.com/2PoXV2o.png',  # Substitua pelo URL real da imagem
        'color': Colors.AMARELO,
        'apenas_imagem': True
    },
    'Sita': {
        'title': 'Sita - Economia',
        'description': (
"""A Sita controla a cidade por onde realmente importa: o bolso. Detentora do maior mercado e banco local, é nela que o valor das coisas — e das pessoas — é definido. Sua estrutura aristocrática é composta por barões e baronesas que dominam setores como feudos, enquanto o consumidor é apenas um número com carteira. Na Sita, tudo tem um preço. Juros, taxas e cláusulas escondidas são parte do jogo. Sua atual líder é **Rxya**.\n
- **Funcionários**: Operam caixas, estoques e sistemas bancários. São treinados para vender — a qualquer custo.
- **Barão & Baronesa**: Controlam nichos estratégicos da economia, como alimentação, medicina e construção. Ditam preços e políticas internas.
- **Vendedor**: Manipuladores natos, vendem até o que não têm. Sempre com um sorriso... e um contrato."""
    ),
        'image_url': 'https://i.imgur.com/1MjmFs3.png',  # Substitua pelo URL real da imagem
        'color': Colors.VERDE,
        'apenas_imagem': True
    },
    'Sedam': {
        'title': 'Sedam - Armamento',
        'description': (
"""A Sedam é o último resquício do antigo exército — e o único fornecedor legal de pólvora e armas da cidade. Isolada do restante das organizações, raramente se envolve nos conflitos, exceto quando o pagamento justifica. Com estrutura militar e rígida, mantém um monopólio absoluto sobre o armamento. Seu atual líder é **Heinken**.\n
- **Funcionários**: Lidam com a produção, estoque e burocracia de armamentos. Acesso à fábrica é privilégio de poucos.
- **Médico**: Um dos únicos profissionais com acesso real à medicina. Tratam feridos com excelência, muitas vezes gratuitamente — mas a que custo?"""
    ),
        'image_url': 'https://i.imgur.com/OEDAQs7.png',  # Substitua pelo URL real da imagem
        'color': Colors.VERMELHO,
        'apenas_imagem': True
    },
    'Otte': {
'title': 'Otte - Biblioteca',
'description': (
"""A Otte é a guardiã do conhecimento verdadeiro. Em uma cidade dominada por fumaça e ganância, sua biblioteca é um farol de saber. Sobrevive graças a doações misteriosas e benfeitores anônimos, mesmo não sendo lucrativa. Seu atual líder é **Venus**, frequentemente confundido com o lendário professor **Joaquim**.\n
- **Funcionários**: Responsáveis por catalogar, restaurar e proteger documentos raros e preciosos.
- **Pesquisador**: Especialistas em teoria, arcana ou científica. Desenvolvem novas tecnologias e palavras artificiais.
- **Pesquisador de Campo**: Saem da biblioteca em busca de relíquias, dados perdidos e novas formas de saber — mesmo que isso custe caro."""
    ),
        'image_url': 'https://i.imgur.com/vGYPr85.png',  # Substitua pelo URL real da imagem
        'color': Colors.CIANO,
        'apenas_imagem': True
    },
    'Nau': {
        'title': 'Nau - Entretenimento',
        'description': (
"""A Nau colore o cinza da cidade com suas luzes, risos e absurdos. Responsável por toda a produção audiovisual, ela dita o que a cidade vê, ouve e sente. Seu estilo é caótico, extravagante e vicioso. Por trás de cada show, existe uma engrenagem brilhante — e bizarra. Sua figura máxima é o **Palhaço Palhaçada**, símbolo e lenda urbana.\n
- **Funcionários**: Técnicos, roteiristas, câmeras e figurantes. Fazem o show acontecer nos bastidores.
- **Palhaço**: Título e personagem. Qualquer um pode assumir o papel — desde que espalhe o caos divertido."""
    ),
        'image_url': 'https://i.imgur.com/0ctDFBA.png',  # Substitua pelo URL real da imagem
        'color': Colors.BRANCO,
        'apenas_imagem': True
    },
    'Deg': {
        'title': 'Deg - Conselho',
        'description': (
"""A Deg é o que mantém a cidade em ordem — ou pelo menos dá essa impressão. Não dita as regras, mas decide quem fala com quem, quando e sob quais condições. É a peça invisível que move o tabuleiro de poder. Quando há problemas externos, a Deg é sempre a primeira a agir. Sua líder atual é **Yin**.\n
- **Funcionários**: Organizam agendas, registros e reuniões entre as organizações.
- **Diplomata**: Mediadores, negociadores e embaixadores. Com carisma e boa lábia, garantem que a cidade funcione — mais ou menos."""
    ),
        'image_url': 'https://i.imgur.com/VuEh9bu.png',  # Substitua pelo URL real da imagem
        'color': Colors.PRETO,
        'apenas_imagem': True
    },

    #Poderes
            
        'Gelo': {
    'title': 'Palavra: Gelo',
    'description': """Definição: água congelada; sólido cristalino transparente formado por congelamento da água.\n
- **Estágio 0**: Você é exímio em criar, manusear e preservar gelo usando métodos naturais.
- **Estágio 1**: Você pode manipular os atributos do gelo, como temperatura, textura, formato e densidade.
- **Estágio 2**: Você pode gerar gelo, fundi-lo, congelar objetos e até transformar seu corpo parcialmente ou totalmente em gelo.
- **Passiva**: Resistência extrema ao frio e imunidade a congelamento.
- **Estágio 3**: Você pode manipular o conceito de gelo.
- **Modo: Irrestrito**: Você altera o conceito do conceito de gelo temporariamente, podendo aplicar esse conceito a qualquer coisa. Tudo se reverte após o fim.""",
    'image_url': 'https://media.giphy.com/media/KgPmAPOhz7KehtCfOT/giphy.gif',
    'color': Colors.AZUL
},

'Água': {
    'title': 'Palavra: Água',
    'description': """Definição: substância líquida, incolor, inodora e insípida, essencial à vida, composta de hidrogênio e oxigênio.\n
- **Estágio 0**: Você é o melhor em lidar com água: nadar, coletar, purificar ou distribuir.
- **Estágio 1**: Você pode manipular a densidade, fluxo, forma e temperatura da água.
- **Estágio 2**: Você gera água do nada, controla seu estado (líquido, vapor, gelo) e pode se transformar em água.
- **Passiva**: Respiração aquática e hidratação constante.
- **Estágio 3**: Você manipula o conceito de água.
- **Modo: Irrestrito**: Pode aplicar o conceito do conceito de água a qualquer entidade. Reversível após o uso.""",
    'image_url': 'https://media.giphy.com/media/uO8DfiiCAV9GCBjo6f/giphy.gif',
    'color': Colors.CIANO
},

'Fumaça': {
    'title': 'Palavra: Fumaça',
    'description': """Definição: conjunto de gases e partículas em suspensão resultantes da combustão incompleta de uma substância.\n
- **Estágio 0**: Você é o melhor em criar, manipular ou ocultar-se com fumaça de forma natural.
- **Estágio 1**: Pode alterar densidade, cor, toxicidade e formato da fumaça.
- **Estágio 2**: Geração espontânea de fumaça, alteração de estado (fumaça -> sólido, etc.), e transformação corporal parcial em fumaça.
- **Passiva**: Imunidade à asfixia e visão através de fumaça.
- **Estágio 3**: Manipulação do conceito de fumaça.
- **Modo: Irrestrito**: Altera o conceito do conceito de fumaça por um tempo limitado.""",
    'image_url': 'https://media.giphy.com/media/QExFHkdN4KxcAAXzXA/giphy.gif',
    'color': Colors.BRANCO
},

'Areia': {
    'title': 'Palavra: Areia',
    'description': """Definição: material granular composto por pequenas partículas de rochas e minerais.\n
- **Estágio 0**: Mestre na manipulação e construção com areia.
- **Estágio 1**: Altere granulação, densidade, forma e peso da areia.
- **Estágio 2**: Gere areia, solidifique ou disperse, e transforme seu corpo em areia.
- **Passiva**: Resistência à abrasão e sentidos adaptados a ambientes áridos.
- **Estágio 3**: Você pode manipular o conceito de areia.
- **Modo: Irrestrito**: Modifica temporariamente o conceito do conceito de areia.""",
    'image_url': 'https://media.giphy.com/media/TlOO64fRmfZ9eFY7LN/giphy.gif',
    'color': Colors.AMARELO
},

'Raio': {
    'title': 'Palavra: Raio',
    'description': """Definição: descarga elétrica de grande intensidade que ocorre entre nuvens ou entre a nuvem e o solo.\n
- **Estágio 0**: Você é especialista em eletricidade e suas aplicações naturais.
- **Estágio 1**: Controle sobre intensidade, direção, cor e velocidade de descargas elétricas.
- **Estágio 2**: Geração espontânea de raios, condução elétrica, transformação corporal em raio.
- **Passiva**: Imunidade a choques e percepção elétrica aumentada.
- **Estágio 3**: Manipulação do conceito de raio.
- **Modo: Irrestrito**: Muda o conceito do conceito de raio por tempo limitado.""",
    'image_url': 'https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExM3JyeXF4eHpqN3RyYThlN3I4MGloeGZuNjIyanB6NnI3NnRleDE3MSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/hieAMams78x69gsm7H/giphy.gif',
    'color': Colors.AMARELO
},

'Madeira': {
    'title': 'Palavra: Madeira',
    'description': """Definição: tecido vegetal que forma o caule, os galhos e os ramos das árvores.\n
- **Estágio 0**: Você é o maior especialista em trabalhar com madeira de forma natural.
- **Estágio 1**: Manipula densidade, resistência, flexibilidade e crescimento da madeira.
- **Estágio 2**: Gera madeira, acelera crescimento de plantas lenhosas, transforma-se em madeira.
- **Passiva**: Resistência a impactos e comunicação com plantas.
- **Estágio 3**: Manipula o conceito de madeira.
- **Modo: Irrestrito**: Pode redefinir o que é madeira ao alterar o conceito do conceito.""",
    'image_url': 'https://media.giphy.com/media/WMquvCccxifj6AsflV/giphy.gif',
    'color': Colors.VERDE
},

'Cristal': {
    'title': 'Palavra: Cristal',
    'description': """Definição: substância sólida com estrutura ordenada de átomos, formando formas geométricas.\n
- **Estágio 0**: Mestre em criação, corte e estudo de cristais naturais.
- **Estágio 1**: Controle sobre cor, dureza, forma e propriedades ópticas dos cristais.
- **Estágio 2**: Geração de cristais, fusão e alteração de forma, transformação corporal parcial em cristal.
- **Passiva**: Pele endurecida e reflexos prismáticos.
- **Estágio 3**: Manipulação do conceito de cristal.
- **Modo: Irrestrito**: Pode alterar temporariamente o conceito do conceito de cristal.""",
    'image_url': 'https://media.giphy.com/media/X8H8SUFQj9lhyfVXPU/giphy.gif',
    'color': Colors.AZUL
},

'Rosa': {
    'title': 'Palavra: Rosa',
    'description': """Definição: flor com pétalas delicadas e geralmente perfumadas; símbolo de beleza e amor.\n
- **Estágio 0**: Especialista em cultivar, podar e compreender rosas e seus significados.
- **Estágio 1**: Altera cor, perfume, tamanho e resistência de rosas.
- **Estágio 2**: Geração de rosas com efeitos variados (curativos, venenosos, cortantes), transformação parcial em pétalas.
- **Passiva**: Atração natural e resistência a venenos.
- **Estágio 3**: Manipulação do conceito de rosa.
- **Modo: Irrestrito**: Pode alterar o conceito do conceito de rosa por um tempo limitado.""",
    'image_url': 'https://media.giphy.com/media/a39Rm8sAZlttcvi30e/giphy.gif',
    'color': Colors.VERMELHO
},

'Ferro': {
    'title': 'Palavra: Ferro',
    'description': """Definição: elemento metálico maleável, magnético, utilizado em construção e fabricação.\n
- **Estágio 0**: Você é um mestre ferreiro e entende todos os usos do ferro.
- **Estágio 1**: Pode alterar maleabilidade, magnetismo e formato do ferro.
- **Estágio 2**: Geração e manipulação de ferro, fusão e transformação corporal metálica.
- **Passiva**: Corpo parcialmente magnético e extremamente resistente.
- **Estágio 3**: Manipula o conceito de ferro.
- **Modo: Irrestrito**: Pode alterar o conceito do conceito de ferro durante o irrestrito.""",
    'image_url': 'https://media.giphy.com/media/dHzKQtRHhgUcrnnUF2/giphy.gif',
    'color': Colors.PRETO
},

'Mel': {
    'title': 'Palavra: Mel',
    'description': """Definição: substância doce produzida pelas abelhas a partir do néctar das flores.\n
- **Estágio 0**: Você é o maior apicultor vivo.
- **Estágio 1**: Manipula sabor, viscosidade, cor e propriedades medicinais do mel.
- **Estágio 2**: Geração espontânea de mel, controle de abelhas, transformação parcial em mel.
- **Passiva**: Imunidade a toxinas e empatia com insetos.
- **Estágio 3**: Manipulação do conceito de mel.
- **Modo: Irrestrito**: Pode alterar o conceito do conceito de mel durante o uso irrestrito.
Ps: Em minha defesa, não existem muito manipuladores de mel.""",
    'image_url': 'https://media.giphy.com/media/aeyDY7P0UZpTmnUfDS/giphy.gif',
    'color': Colors.AMARELO
},
'Vidro': {
    'title': 'Palavra: Vidro',
    'description': """Definição: substância sólida, geralmente transparente e frágil, obtida pela fusão de areia com outros materiais.\n
- **Estágio 0**: Você é um mestre vidreiro, capaz de moldar, cortar e manipular vidro como ninguém.
- **Estágio 1**: Manipula transparência, resistência, cor e forma do vidro.
- **Estágio 2**: Geração de vidro, fusão e manipulação de estado (quebrado/integral), transformação parcial em vidro.
- **Passiva**: Resistência a cortes e reflexos aumentados.
- **Estágio 3**: Manipulação do conceito de vidro.
- **Modo: Irrestrito**: Pode redefinir o conceito do conceito de vidro temporariamente.""",
    'image_url': 'https://media.giphy.com/media/RY5Hb7sZ3EpA0KMPA0/giphy.gif',
    'color': Colors.BRANCO
},

'Gasolina': {
    'title': 'Palavra: Gasolina',
    'description': """Definição: combustível líquido derivado do petróleo, inflamável e volátil.\n
- **Estágio 0**: Você é o melhor em lidar com combustíveis e suas aplicações.
- **Estágio 1**: Manipula inflamabilidade, densidade, cor e pureza da gasolina.
- **Estágio 2**: Geração de gasolina, ignição controlada, transformação parcial em líquido inflamável.
- **Passiva**: Resistência a vapores tóxicos e combustão interna.
- **Estágio 3**: Manipula o conceito de gasolina.
- **Modo: Irrestrito**: Pode alterar temporariamente o conceito do conceito de gasolina.""",
    'image_url': 'https://media.giphy.com/media/Dyoz6ivICdXPWv7t3v/giphy.gif',
    'color': Colors.AMARELO
},

'Pólvora': {
    'title': 'Palavra: Pólvora',
    'description': """Definição: mistura explosiva usada como propelente ou em explosivos.\n
- **Estágio 0**: Especialista em explosivos e munições artesanais.
- **Estágio 1**: Manipula potência, tempo de detonação, densidade e efeito da pólvora.
- **Estágio 2**: Geração espontânea de pólvora, ignição e transformação parcial em material explosivo.
- **Passiva**: Corpo adaptado a explosões e resistência acústica.
- **Estágio 3**: Manipulação do conceito de pólvora.
- **Modo: Irrestrito**: Pode alterar o conceito do conceito de pólvora temporariamente.""",
    'image_url': 'https://media.giphy.com/media/bMBtBdzuZ2Rai1dCkR/giphy.gif',
    'color': Colors.PRETO
},

'Vácuo': {
    'title': 'Palavra: Vácuo',
    'description': """Definição: espaço completamente desprovido de matéria; ausência total de ar.\n
- **Estágio 0**: Você é um mestre em criar ambientes selados e sistemas de vácuo naturais.
- **Estágio 1**: Manipula pressão, ausência de som, ausência de matéria em pequenas áreas.
- **Estágio 2**: Geração de bolsões de vácuo, remoção instantânea de ar e transformação parcial em entidade etérea.
- **Passiva**: Imunidade ao sufocamento e sentidos adaptados ao silêncio absoluto.
- **Estágio 3**: Manipulação do conceito de vácuo.
- **Modo: Irrestrito**: Pode alterar o conceito do conceito de vácuo por tempo limitado.""",
    'image_url': 'https://media.giphy.com/media/C3qoXiDBfTiWpXFSLc/giphy.gif',
    'color': Colors.PRETO
},

'Sangue': {
    'title': 'Palavra: Sangue',
    'description': """Definição: fluido vital que circula pelo corpo, transportando oxigênio e nutrientes.\n
- **Estágio 0**: Você é o maior especialista em medicina, ferimentos e circulação.
- **Estágio 1**: Manipula viscosidade, cor, coagulação e fluxo do sangue (inclusive de outros).
- **Estágio 2**: Geração de sangue, controle absoluto sobre sangue alheio, transformação parcial em sangue.
- **Passiva**: Regeneração acelerada e leitura de sinais vitais.
- **Estágio 3**: Manipulação do conceito de sangue.
- **Modo: Irrestrito**: Pode alterar o conceito do conceito de sangue temporariamente.""",
    'image_url': 'https://media.giphy.com/media/iOndVObklMVDGMD1oQ/giphy.gif',
    'color': Colors.VERMELHO
},

'Fogo': {
    'title': 'Palavra: Fogo',
    'description': """Definição: fenômeno que consiste no desprendimento de calor e luz produzidos pela combustão de um corpo; lume.\n
- **Estágio 0**: Você é o melhor em lidar com fogo de forma natural — acendê-lo, mantê-lo, controlá-lo em rituais ou práticas comuns.
- **Estágio 1**: Você manipula os atributos do fogo, como temperatura, cor, tamanho e comportamento.
- **Estágio 2**: Pode gerar fogo espontaneamente, extingui-lo à vontade e transformar seu corpo em chama.
- **Passiva**: Resistência extrema ao calor e imunidade a queimaduras.
- **Estágio 3**: Manipula o conceito de fogo.
- **Modo: Irrestrito**: Altera temporariamente o conceito do conceito de fogo, redefinindo o que significa arder ou queimar.""",
    'image_url': 'https://media.giphy.com/media/976R2DTMMg43pAfNg0/giphy.gif',
    'color': Colors.VERMELHO
},
'Relógio': {
    'title': 'Palavra: Relógio',
    'description': """Definição: instrumento usado para medir e indicar o tempo.\n
- **Estágio 0**: Você é um mestre relojoeiro — entende e monta qualquer tipo de relógio com perfeição.
- **Estágio 1**: Manipula os atributos de relógios, como velocidade dos ponteiros, precisão, estilo e mecânica.
- **Estágio 2**: Geração de relógios, fusão com mecanismos, transformar partes do corpo em engrenagens funcionais.
- **Passiva**: No estágio 2, você pode sentir o "ritmo" de tudo — como se tudo tivesse um tique-taque sutil.
- **Estágio 3**: Manipula o conceito de relógio (ex: transformar qualquer objeto em um marcador de tempo).
- **Modo: Irrestrito**: Pode redefinir o conceito do conceito de relógio temporariamente.""",
    'image_url': 'https://media.giphy.com/media/oQ7LgyBapZl9avnkmn/giphy.gif',
    'color': Colors.AMARELO
},

'Zweihander': {
    'title': 'Palavra: Zweihander',
    'description': """Definição: espada longa de duas mãos, típica de soldados pesados medievais.\n
- **Estágio 0**: Você é um mestre em combate com espadas grandes, força, técnica e equilíbrio incomparáveis.
- **Estágio 1**: Manipula peso, corte, resistência e forma de espadas do tipo Zweihander.
- **Estágio 2**: Geração de grandes espadas, fusão com sua estrutura, transformação parcial em lâmina viva.
- **Passiva**: A cada golpe, você acumula força em ataques consecutivos.
- **Estágio 3**: Manipulação do conceito de Zweihander — qualquer coisa pode se tornar uma "espada de duas mãos".
- **Modo: Irrestrito**: Pode alterar o conceito do conceito de Zweihander temporariamente.""",
    'image_url': 'https://media.giphy.com/media/4nuY9RykmXfyFu0MAb/giphy.gif',
    'color': Colors.PRETO
},

'Café': {
    'title': 'Palavra: Café',
    'description': """Definição: bebida feita a partir dos grãos torrados do cafeeiro, estimulante e aromática.\n
- **Estágio 0**: Você é um barista lendário — domina sabores, texturas e efeitos do café.
- **Estágio 1**: Manipula aroma, temperatura, concentração e tipo de café (expresso, coado, gelado).
- **Estágio 2**: Geração de café com efeitos variados, manipulação de estado (líquido/vapor), transformação parcial.
- **Passiva**: Energia constante, foco elevado e resistência a sono e cansaço.
- **Estágio 3**: Manipula o conceito de café — fazer com que algo “seja café”.
- **Modo: Irrestrito**: Pode alterar temporariamente o conceito do conceito de café.""",
    'image_url': 'https://media.giphy.com/media/gL0Ii1XoEwZVXLwRNU/giphy.gif',
    'color': Colors.PRETO
},

'Vela': {
    'title': 'Palavra: Vela',
    'description': """Definição: objeto geralmente de cera com um pavio, usado para iluminação.\n
- **Estágio 0**: Você é expert em fabricação, manuseio e uso ritualístico de velas.
- **Estágio 1**: Manipula cor, duração, formato e tipo de chama da vela (sem controlar o fogo em si).
- **Estágio 2**: Geração de velas, fusão com cera, transformação parcial em vela viva (sem se queimar).
- **Passiva**: Sua presença traz foco e clareza para quem estiver por perto.
- **Estágio 3**: Manipula o conceito de vela — iluminar com presença, guiar, marcar o tempo.
- **Modo: Irrestrito**: Pode alterar temporariamente o conceito do conceito de vela.""",
    'image_url': 'https://media.giphy.com/media/5LAFmPCO6jQrOVyyzE/giphy.gif',
    'color': Colors.AMARELO
},
'Papel': {
    'title': 'Palavra: Papel',
    'description': """Definição: material feito de fibras vegetais usado para escrita, impressão ou embalagem.\n
- **Estágio 0**: Você é um mestre na arte do papel — origami, caligrafia, encadernação, tudo com perfeição.
- **Estágio 1**: Manipula textura, espessura, resistência e tipo do papel.
- **Estágio 2**: Geração de papel com propriedades especiais, transformação parcial em papel, manipulação de estado (amassado, rasgado, liso).
- **Passiva**: Você pode registrar qualquer coisa com precisão apenas tocando o papel.
- **Estágio 3**: Manipula o conceito de papel — qualquer superfície pode ser transformada em papel.
- **Modo: Irrestrito**: Pode alterar temporariamente o conceito do conceito de papel.""",
    'image_url': 'https://media.giphy.com/media/rLlJnn6AJyyUv3tGfh/giphy.gif',
    'color': Colors.BRANCO
},

'Tinta': {
    'title': 'Palavra: Tinta',
    'description': """Definição: líquido colorido usado para escrever, desenhar ou imprimir.\n
- **Estágio 0**: Você domina todas as formas de pintura, escrita e arte com tinta.
- **Estágio 1**: Manipula cor, viscosidade, secagem e permanência da tinta.
- **Estágio 2**: Geração de tinta viva, escrita que se move, transformação parcial em fluido artístico.
- **Passiva**: Toda sua tinta expressa mais do que palavras — sentimentos, intenções e memórias.
- **Estágio 3**: Manipula o conceito de tinta — aquilo que expressa, imprime ou marca.
- **Modo: Irrestrito**: Pode alterar temporariamente o conceito do conceito de tinta.""",
    'image_url': 'https://media.giphy.com/media/WmZRtNuYgRT58q8HXQ/giphy.gif',
    'color': Colors.PRETO
},

'Trompete': {
    'title': 'Palavra: Trompete',
    'description': """Definição: instrumento musical de sopro, metálico, com som vibrante e poderoso.\n
- **Estágio 0**: Você é um músico virtuoso no trompete, domina técnica, melodia e improviso.
- **Estágio 1**: Manipula tom, alcance, reverberação e intensidade do som do trompete.
- **Estágio 2**: Geração de trompetes etéreos, som sólido, fusão com o instrumento, transformação parcial.
- **Passiva**: Seu som alcança corações — capaz de inspirar ou silenciar multidões.
- **Estágio 3**: Manipula o conceito de trompete — tudo pode soar como um.
- **Modo: Irrestrito**: Pode alterar temporariamente o conceito do conceito de trompete.""",
    'image_url': 'https://media.giphy.com/media/lo3nttF60Jz0aSaPWm/giphy.gif',
    'color': Colors.AMARELO
},

'Porta': {
    'title': 'Palavra: Porta',
    'description': """Definição: estrutura móvel usada para fechar ou permitir a passagem entre espaços.\n
- **Estágio 0**: Você é o melhor em construir, trancar, destrancar e entender portas de todos os tipos.
- **Estágio 1**: Manipula tamanho, forma, abertura, som e material das portas.
- **Estágio 2**: Geração de portas que conectam lugares (sem teletransporte), fusão com portas, transformação parcial.
- **Passiva**: Pode sentir o que há do outro lado de qualquer passagem.
- **Estágio 3**: Manipula o conceito de porta — qualquer coisa pode se tornar ou funcionar como uma.
- **Modo: Irrestrito**: Pode alterar temporariamente o conceito do conceito de porta.""",
    'image_url': 'https://media.giphy.com/media/CLb5jItiMVn3l4oMqM/giphy.gif',
    'color': Colors.VERDE
},

'Lixo': {
    'title': 'Palavra: Lixo',
    'description': """Definição: tudo aquilo considerado inútil ou descartável.\n
- **Estágio 0**: Você é mestre em reciclagem, aproveitamento e reaproveitamento de resíduos.
- **Estágio 1**: Manipula odor, densidade, toxicidade e utilidade aparente do lixo.
- **Estágio 2**: Geração de lixo mutável, fusão com descarte, transformação parcial em massa de resíduo.
- **Passiva**: Nada em você é desperdiçado, tudo se transforma.
- **Estágio 3**: Manipula o conceito de lixo — aquilo que é inútil pode se tornar essencial.
- **Modo: Irrestrito**: Pode alterar temporariamente o conceito do conceito de lixo.""",
    'image_url': 'https://media.giphy.com/media/tg3MTEgoLAudbHngwy/giphy.gif',
    'color': Colors.PRETO
},

'Argila': {
    'title': 'Palavra: Argila',
    'description': """Definição: material terroso, moldável quando úmido, usado em cerâmica e escultura.\n
- **Estágio 0**: Você é um escultor sem igual, moldando argila com perfeição intuitiva.
- **Estágio 1**: Manipula dureza, secagem, plasticidade e tipo da argila.
- **Estágio 2**: Geração de argila viva, moldagem instantânea, transformação parcial.
- **Passiva**: Seu corpo pode absorver impactos como barro e voltar à forma original.
- **Estágio 3**: Manipula o conceito de argila — tudo pode ser modelado.
- **Modo: Irrestrito**: Pode alterar temporariamente o conceito do conceito de argila.""",
    'image_url': 'https://media.giphy.com/media/vBAey1iswzGFDm0M5H/giphy.gif',
    'color': Colors.VERMELHO
},

'Lâmina': {
    'title': 'Palavra: Lâmina',
    'description': """Definição: parte cortante de instrumentos como facas e espadas.\n
- **Estágio 0**: Você é um mestre forjador e lutador com lâminas de todo tipo.
- **Estágio 1**: Manipula fio, forma, flexibilidade e composição da lâmina.
- **Estágio 2**: Geração de lâminas, fusão ao corpo, transformação parcial em corte puro.
- **Passiva**: Seus movimentos são afiados — corta o ar e até intenções.
- **Estágio 3**: Manipula o conceito de lâmina — tudo pode cortar.
- **Modo: Irrestrito**: Pode alterar temporariamente o conceito do conceito de lâmina.""",
    'image_url': 'https://media.giphy.com/media/WnBFuRbKaRybITfMVA/giphy.gif',
    'color': Colors.BRANCO
},

'Prego': {
    'title': 'Palavra: Prego',
    'description': """Definição: peça metálica usada para unir objetos, geralmente batida com martelo.\n
- **Estágio 0**: Você é um mestre construtor — precisão absoluta em unir, fixar e montar estruturas.
- **Estágio 1**: Manipula tamanho, resistência, aderência e direção de pregos.
- **Estágio 2**: Geração de pregos, controle de impacto, transformação parcial em metal penetrante.
- **Passiva**: Você fixa ideias e pessoas com sua presença firme.
- **Estágio 3**: Manipula o conceito de prego — o que fixa, une ou atravessa.
- **Modo: Irrestrito**: Pode alterar temporariamente o conceito do conceito de prego.""",
    'image_url': 'https://media.giphy.com/media/TKYBJZqpuW61PuHlti/giphy.gif',
    'color': Colors.BRANCO
},

'Bússola': {
    'title': 'Palavra: Bússola',
    'description': """Definição: instrumento que indica a direção geográfica, geralmente apontando para o norte.\n
- **Estágio 0**: Você é um navegador imbatível, sempre encontra seu caminho.
- **Estágio 1**: Manipula direção, precisão, escala e função de bússolas.
- **Estágio 2**: Geração de bússolas intuitivas, transformação parcial em entidade que aponta o caminho.
- **Passiva**: Você sempre sabe onde está e para onde precisa ir.
- **Estágio 3**: Manipula o conceito de bússola — qualquer coisa pode guiar ou orientar.
- **Modo: Irrestrito**: Pode alterar temporariamente o conceito do conceito de bússola.""",
    'image_url': 'https://media.giphy.com/media/gudk45NVu34tHvuCpV/giphy.gif',
    'color': Colors.BRANCO
},

'Carta': {
    'title': 'Palavra: Carta',
    'description': """Definição: mensagem escrita em papel, enviada de uma pessoa para outra.\n
- **Estágio 0**: Você escreve e interpreta cartas com precisão e impacto emocional inigualáveis.
- **Estágio 1**: Manipula forma, estilo, conteúdo e entrega de cartas.
- **Estágio 2**: Geração de cartas com efeitos únicos, transformação parcial em portador de mensagens.
- **Passiva**: Toda mensagem sua chega exatamente onde deve, mesmo sem endereço.
- **Estágio 3**: Manipula o conceito de carta — o que comunica entre distâncias.
- **Modo: Irrestrito**: Pode alterar temporariamente o conceito do conceito de carta.""",
    'image_url': 'https://media.giphy.com/media/sFpYJdaptGYXcklTqv/giphy.gif',
    'color': Colors.BRANCO
},

'Machadinha': {
    'title': 'Palavra: Machadinha',
    'description': """Definição: Machado que se maneja com uma só mão.\n
- **Estágio 0**: Você é um lutador e desbravador de elite com a Machadinha.
- **Estágio 1**: Manipula peso, resistência, fio e alcance da Machadinha.
- **Estágio 2**: Geração de Machadinhas rústicas, corte brutal, fusão com o corpo, transformação parcial.
- **Passiva**: Seus ataques abrem caminho mesmo em situações impossíveis.
- **Estágio 3**: Manipula o conceito de Machadinha — força para romper obstáculos.
- **Modo: Irrestrito**: Pode alterar temporariamente o conceito do conceito de Machadinha.""",
    'image_url': 'https://media.giphy.com/media/JSbDiS2mjXkn345b2B/giphy.gif',
    'color': Colors.PRETO
},

'Sino': {
    'title': 'Palavra: Sino',
    'description': """Definição: objeto metálico que emite som ao ser percutido, geralmente usado como sinalizador.\n
- **Estágio 0**: Você é mestre em sinos, seus toques ressoam de forma única e precisa.
- **Estágio 1**: Manipula tom, volume, eco e alcance dos sinos.
- **Estágio 2**: Geração de sinos com efeitos especiais, fusão com ressonância, transformação parcial.
- **Passiva**: Seus sons atravessam barreiras, ecoando até na alma.
- **Estágio 3**: Manipula o conceito de sino — o que anuncia, chama ou desperta.
'- **Modo: Irrestrito**: Pode alterar temporariamente o conceito do conceito de sino.""",
    'image_url': 'https://media.giphy.com/media/TO5ytGkq1ILaJijhO1/giphy.gif',
    'color': Colors.AMARELO
},
'Canino': {
    'title': 'Palavra: Canino',
    'description': """Definição: mamíferos da família dos cães, conhecidos por seu faro aguçado, sociabilidade e instintos de matilha.\n
- **Estágio 0**: Você compreende e interage com cães e animais caninos melhor do que qualquer um.
- **Estágio 1**: Pode manipular atributos de caninos — Tanto seus quanto de um canino.
- **Estágio 2**: Pode transformar-se parcial ou totalmente em um canino.
- **Passiva**: Caninos se alinham naturalmente a você. Seus sentidos são reforçados.
- **Estágio 3**: Manipula o conceito de canino — instintos, lealdade, matilha e comportamento podem se manifestar em qualquer coisa.
- **Modo: Irrestrito**: Altera temporariamente o conceito do conceito de canino.""",
    'image_url': 'https://media.giphy.com/media/KG3nMwDURDZEumbpoc/giphy.gif',
    'color': Colors.VERMELHO
},

'Raposa': {
    'title': 'Palavra: Raposa',
    'description': """Definição: mamífero ágil e astuto, geralmente solitário, conhecido por sua inteligência e adaptação.\n
- **Estágio 0**: Você entende perfeitamente o comportamento e padrões das raposas.
- **Estágio 1**: Manipula atributos de raposas — Tanto seus quanto de uma raposa.
- **Estágio 2**: Pode transformar-se parcial ou totalmente em uma raposa.
- **Passiva**: Você naturalmente confunde sensores e percebe armadilhas intuitivamente.
- **Estágio 3**: Manipula o conceito de raposa — astúcia, camuflagem e independência tomam forma onde quiser.
- **Modo: Irrestrito**: Altera temporariamente o conceito do conceito de raposa.""",
    'image_url': 'https://media.giphy.com/media/IA7ZxyxHTVc3PJuyZu/giphy.gif',
    'color': Colors.AMARELO
},

'Inseto': {
    'title': 'Palavra: Inseto',
    'description': """Definição: grupo de artrópodes com corpo segmentado, exoesqueleto e seis patas, altamente adaptáveis.\n
- **Estágio 0**: Você entende o comportamento, ciclo de vida e comunicação dos insetos.
- **Estágio 1**: Manipula atributos dos insetos — Tanto seus quanto de um inseto.
- **Estágio 2**: Pode se transformar em um inseto ou forma híbrida, alem de poder passar por uma metamorfose, vulgo, modo de defesa.
- **Passiva**: Insetos não o atacam e podem ser convocados instintivamente.
- **Estágio 3**: Manipula o conceito de inseto — enxame, multiplicidade e adaptação se tornam forças amplas.
- **Modo: Irrestrito**: Altera temporariamente o conceito do conceito de inseto.""",
    'image_url': 'https://media.giphy.com/media/EtKKuba00Yupmb5twe/giphy.gif',
    'color': Colors.VERDE
},

'Peixe': {
    'title': 'Palavra: Peixe',
    'description': """Definição: vertebrados aquáticos que respiram por guelras, possuem nadadeiras e vivem em ecossistemas aquáticos.\n
- **Estágio 0**: Você entende peixes, seus sentidos e funcionamento subaquático com perfeição.
- **Estágio 1**: Manipula atributos de peixes — Tanto seus quanto de um peixe.
- **Estágio 2**: Pode se transformar em peixe ou forma híbrida.
- **Passiva**: Você respira embaixo d’água e nada com facilidade sobrenatural.
- **Estágio 3**: Manipula o conceito de peixe — fluidez, invisibilidade e adaptação a ambientes extremos.
- **Modo: Irrestrito**: Altera temporariamente o conceito do conceito de peixe.""",
    'image_url': 'https://media.giphy.com/media/ffOkYx96k4epFWPbpa/giphy.gif',
    'color': Colors.CIANO
},

'Anfíbio': {
    'title': 'Palavra: Anfíbio',
    'description': """Definição: vertebrados de vida dupla, como sapos e salamandras, que vivem em terra e na água.\n
- **Estágio 0**: Você entende totalmente o comportamento e funções dos anfíbios.
- **Estágio 1**: Manipula atributos de anfíbios — Tanto seus quanto de um anfíbio.
- **Estágio 2**: Pode se transformar em um anfíbio ou forma mista.
- **Passiva**: Sua pele regula naturalmente a temperatura e umidade do ambiente.
- **Estágio 3**: Manipula o conceito de anfíbio — transição, adaptação e dualidade se manifestam em seres e ambientes.
- **Modo: Irrestrito**: Altera temporariamente o conceito do conceito de anfíbio.""",
    'image_url': 'https://media.giphy.com/media/etgyNelyBcrKZYwsIH/giphy.gif',
    'color': Colors.VERDE
},

'Ave': {
    'title': 'Palavra: Ave',
    'description': """Definição: vertebrados com penas, bico, ossos pneumáticos e, geralmente, capacidade de voar.\n
- **Estágio 0**: Você entende a comunicação e hábitos migratórios e territoriais das aves.
- **Estágio 1**: Manipula atributos de aves — Tanto seus quanto de uma ave.
- **Estágio 2**: Pode se transformar em uma ave ou forma alada.
- **Passiva**: Você pode flutuar levemente e possui senso de orientação excepcional.
- **Estágio 3**: Manipula o conceito de ave — liberdade, altura e observação se espalham por onde quiser.
- **Modo: Irrestrito**: Altera temporariamente o conceito do conceito de ave.""",
    'image_url': 'https://media.giphy.com/media/bMo2AaDUi3DUVjDJh2/giphy.gif',
    'color': Colors.CIANO
},

'Réptil': {
    'title': 'Palavra: Réptil',
    'description': """Definição: animais vertebrados de sangue frio com escamas, como cobras, lagartos e jacarés.\n
- **Estágio 0**: Você entende com perfeição o comportamento, fisiologia e adaptação de répteis.
- **Estágio 1**: Manipula atributos de répteis — Tanto seus quanto de um réptil.
- **Estágio 2**: Pode se transformar em um réptil ou forma híbrida.
- **Passiva**: Você se adapta ao ambiente termicamente e se move silenciosamente.
- **Estágio 3**: Manipula o conceito de réptil — sangue frio, paciência e força latente se impõem.
- **Modo: Irrestrito**: Altera temporariamente o conceito do conceito de réptil.""",
    'image_url': 'https://media.giphy.com/media/uGlZkm11rfMGYY8wXz/giphy.gif',
    'color': Colors.VERDE
},

'Touro/Vaca': {
    'title': 'Palavra: Touro/Vaca',
    'description': """Definição: grandes mamíferos herbívoros domesticados, conhecidos por sua força e persistência.\n
- **Estágio 0**: Você entende profundamente o comportamento de bovinos e os acalma com facilidade.
- **Estágio 1**: Manipula atributos desses animais — Tanto seus quanto de um Touro/Vaca.
- **Estágio 2**: Pode se transformar em um touro, vaca ou forma híbrida.
- **Passiva**: Você é extremamente resistente a empurrões, cargas e controle emocional.
- **Estágio 3**: Manipula o conceito de bovino — força bruta, calma e resiliência podem ser aplicadas onde desejar.
- **Modo: Irrestrito**: Altera temporariamente o conceito do conceito de touro/vaca.""",
    'image_url': 'https://media.giphy.com/media/DBbEeUM6JBgOZy2DLN/giphy.gif',
    'color': Colors.VERMELHO
},
'Equino': {
    'title': 'Palavra: Equino',
    'description': """Definição: mamíferos herbívoros como cavalos, jumentos e zebras, conhecidos por sua velocidade, resistência e relação com humanos.

- **Estágio 0**: Você entende profundamente o comportamento de equinos e consegue domá-los com maestria.
- **Estágio 1**: Manipula atributos desses animais — Tanto seus quanto de um Equino.
- **Estágio 2**: Pode se transformar em um equino ou forma híbrida.
- **Passiva**: Você nunca se cansa em longas jornadas e sabe exatamente para onde está indo.
- **Estágio 3**: Manipula o conceito de equino — liberdade, vigor e lealdade podem ser aplicadas a qualquer coisa.
- **Modo: Irrestrito**: Altera temporariamente o conceito do conceito de equino.""",
    'image_url': 'https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHVjNTdkdGgxOXl3OGpicGsycGF4dnpkaHRqZXgwOGMxZ2M5ODZkYSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/VTHRL99gV7Jdwh2mNd/giphy.gif',
    'color': Colors.BRANCO
},

'Aracnídeo': {
    'title': 'Palavra: Aracnídeo',
    'description': """Definição: animais invertebrados como aranhas e escorpiões, com oito patas, exoesqueleto e habilidades como tecelagem ou veneno.

- **Estágio 0**: Você entende os padrões e comportamentos de aracnídeos como ninguém.
- **Estágio 1**: Manipula atributos desses animais — Tanto seus quanto de um Aracnídeo.
- **Estágio 2**: Pode se transformar em um aracnídeo ou forma híbrida.
- **Passiva**: Você pode aderir a superfícies e seus reflexos são extremamente rápidos.
- **Estágio 3**: Manipula o conceito de aracnídeo — armadilha, paciência e veneno podem ser aplicados ao mundo.
- **Modo: Irrestrito**: Altera temporariamente o conceito do conceito de aracnídeo.""",
    'image_url': 'https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExZGE4NjJpMDd2Nzg2Y3E2dG8ydjQ3bDR6cmRhanltb3M0NG10dmpwNyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/Rv8hOwoLyz4XBAnMcx/giphy.gif',
    'color': Colors.ROXO
},

'Canguru': {
    'title': 'Palavra: Canguru',
    'description': """Definição: mamífero marsupial saltador da Austrália, conhecido por suas pernas poderosas, cauda rígida e cuidado com os filhotes.

- **Estágio 0**: Você entende o comportamento dos cangurus e sua dinâmica de grupo.
- **Estágio 1**: Manipula atributos desses animais — Tanto seus quanto de um Canguru.
- **Estágio 2**: Pode se transformar em um canguru ou forma híbrida.
- **Passiva**: Você possui equilíbrio absoluto e propulsão aprimorada nas pernas.
- **Estágio 3**: Manipula o conceito de canguru — proteção, mobilidade e salto aplicáveis a qualquer meio.
- **Modo: Irrestrito**: Altera temporariamente o conceito do conceito de canguru.""",
    'image_url': 'https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExczNhNzNwY3loNmZnN2N6ZDlkczR2MTQ1dnh5cmJjcXlnd2RwZW1sciZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/v9Dsle3klBhZdd8Z70/giphy.gif',
    'color': Colors.LARANJA
},

'Dragão': {
    'title': 'Palavra: Dragão',
    'description': """Definição: criatura mitológica associada a poder, sabedoria, voo e fogo. Dragões variam culturalmente entre guardiões e ameaças.

- **Estágio 0**: Você entende todos os mitos e simbologias envolvendo dragões.
- **Estágio 1**: Manipula atributos desses seres — Tanto seus quanto de um Dragão.
- **Estágio 2**: Pode se transformar em um dragão ou forma híbrida.
- **Passiva**: Sua presença impõe respeito, e você emana poder místico.
- **Estágio 3**: Manipula o conceito de dragão — imponência, proteção e catástrofe ganham forma onde quiser.
- **Modo: Irrestrito**: Altera temporariamente o conceito do conceito de dragão.""",
    'image_url': 'https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExcXB5bHExMWk0ZnUxNnJyMHhmeTAwd3I2aWxrdWl3d2hoOWZlNTA2byZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/VvBbaJmJbEKV63czaq/giphy.gif',
    'color': Colors.AMARELO
},

'Leprechaum': {
    'title': 'Palavra: Leprechaum',
    'description': """Definição: criatura do folclore irlandês, pequena e travessa, associada à sorte, ouro e truques mágicos.

- **Estágio 0**: Você entende profundamente as histórias, truques e lógica dos leprechauns.
- **Estágio 1**: Manipula atributos desses seres — Tanto seus quanto de um Leprechaum.
- **Estágio 2**: Pode se transformar em um leprechaum ou forma híbrida.
- **Passiva**: Você sempre tem uma saída engenhosa e tende a atrair fortuna aleatória.
- **Estágio 3**: Manipula o conceito de leprechaum — sorte, truques e pequenos milagres moldam a realidade.
- **Modo: Irrestrito**: Altera temporariamente o conceito do conceito de leprechaum.""",
    'image_url': 'https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExdGNybGJ1ZDAwMHZ1dnA0azByZXRwcjN6Zm1neXB3OGhxeWVrNXloNSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/kdHd6QGFWG7I7wK7c9/giphy.gif',
    'color': Colors.VERDE
},

'Tigre': {
    'title': 'Palavra: Tigre',
    'description': """Definição: grande felino carnívoro, caçador solitário e furtivo, conhecido por sua força, velocidade e inteligência.

- **Estágio 0**: Você entende os hábitos de caça, território e hierarquia de tigres.
- **Estágio 1**: Manipula atributos desses animais — Tanto seus quanto de um Tigre.
- **Estágio 2**: Pode se transformar em um tigre ou forma híbrida.
- **Passiva**: Você pode desaparecer na selva urbana e atacar com precisão letal.
- **Estágio 3**: Manipula o conceito de tigre — domínio, predador absoluto e silêncio ganham forma em qualquer contexto.
- **Modo: Irrestrito**: Altera temporariamente o conceito do conceito de tigre.""",
    'image_url': 'https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExd2d5cm9jeTMyY2lxZGE2dW9wbXkwazl2Y2cwcjB4aXZpcDdoOHhvOSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/LsMU2qxRALq9Cd1sKm/giphy.gif',
    'color': Colors.LARANJA
},
'Sorte': {
    'title': 'Palavra: Sorte',
    'description': """Definição: circunstância favorável atribuída ao acaso; boa fortuna.

- **Estágio 0**: Você é absurdamente sortudo em tudo que envolva probabilidade comum.
- **Estágio 1**: Manipula atributos da sorte em objetos, pessoas ou situações.
- **Estágio 2**: Pode gerar ou remover estados de sorte, atraindo ou afastando eventos improváveis.
- **Passiva**: Situações improváveis tendem a favorecer você naturalmente.
- **Estágio 3**: Manipula o conceito de sorte — o destino pode ser moldado ao seu favor.
- **Modo: Irrestrito**: Altera temporariamente o conceito do conceito de sorte.""",
    'image_url': 'https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExaGt4enlsODFva3RsZTFha2kwMXhlczhmNjRmdzIzam14c25lbjdhdSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/jJqzoRLfplqRt9Rf35/giphy.gif',
    'color': Colors.AMARELO
},

'Beleza': {
    'title': 'Palavra: Beleza',
    'description': """Definição: qualidade do que é belo ou agradável aos sentidos ou ao espírito.

- **Estágio 0**: Você é capaz de realçar a beleza de tudo ao seu redor com naturalidade.
- **Estágio 1**: Manipula atributos da beleza em si mesmo ou em qualquer coisa.
- **Estágio 2**: Pode transformar ou distorcer estados de beleza — tornar algo belo ou horrendo.
- **Passiva**: Sua presença atrai admiração e fascínio constante.
- **Estágio 3**: Manipula o conceito de beleza — redefinindo o que é belo no mundo.
- **Modo: Irrestrito**: Altera temporariamente o conceito do conceito de beleza.""",
    'image_url': 'https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExdWR0bzB2bWxwODlkZzljamdkZ3EwNTN5a2c5OHA0M28yNGZxdmh3ZSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/gquyZDQ8WDwnyvHS1L/giphy.gif',
    'color': Colors.CIANO
},

'Rapidez': {
    'title': 'Palavra: Rapidez',
    'description': """Definição: qualidade de quem ou do que é rápido; velocidade de execução.

- **Estágio 0**: Você é o ser humano mais veloz em reação e execução de tarefas físicas.
- **Estágio 1**: Manipula atributos de velocidade em si ou em objetos.
- **Estágio 2**: Pode alterar o estado de rapidez — tornar algo extremamente rápido ou lento.
- **Passiva**: Você reage instintivamente antes de qualquer perigo se manifestar.
- **Estágio 3**: Manipula o conceito de rapidez — acelerando tudo ao seu redor em sentido amplo.
- **Modo: Irrestrito**: Altera temporariamente o conceito do conceito de rapidez.""",
    'image_url': 'https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExMnk3bm1maGJ2bDdsN2ZhdHdneXY5b3o0dGs1ajIxMzNwd3MzMjllZiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/KNApDbo5JqhfleFdrm/giphy.gif',
    'color': Colors.BRANCO
},

'Força': {
    'title': 'Palavra: Força',
    'description': """Definição: capacidade de exercer poder físico ou impacto; vigor.

- **Estágio 0**: Você possui a maior força física humana registrada.
- **Estágio 1**: Manipula atributos da força física em objetos ou corpos.
- **Estágio 2**: Pode transformar algo em forte ou fraco, afetando sua resistência ou impacto.
- **Passiva**: Seus golpes e ações sempre têm mais potência do que o normal.
- **Estágio 3**: Manipula o conceito de força — inclusive força de vontade ou simbólica.
- **Modo: Irrestrito**: Altera temporariamente o conceito do conceito de força.""",
    'image_url': 'https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExenpkNHdrbXR3NHh2ZDVkYml0NjA0ZzRxN3MwNTc4d3F0bWNsaWNxYyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/M8H7PlrNQewj0tPbNj/giphy.gif',
    'color': Colors.VERMELHO
},

'Carisma': {
    'title': 'Palavra: Carisma',
    'description': """Definição: qualidade de atrair, encantar e influenciar outras pessoas.

- **Estágio 0**: Você convence e encanta naturalmente quem estiver por perto.
- **Estágio 1**: Manipula atributos de carisma — ampliando ou reduzindo sua influência.
- **Estágio 2**: Pode aplicar ou remover carisma de outros, tornando-os líderes ou ignorados.
- **Passiva**: Seus pedidos soam como ordens naturais, quase irresistíveis.
- **Estágio 3**: Manipula o conceito de carisma — moldando autoridade, influência e encantamento no mundo.
- **Modo: Irrestrito**: Altera temporariamente o conceito do conceito de carisma.""",
    'image_url': 'https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExNjZ4MzBmc2x5bHN4amwwaWZ2NDF2cm1vZXc1bG9zb2pmeDk1MmZlYyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/CuJwtMF5EslC1zFnyY/giphy.gif',
    'color': Colors.ROXO
},

'Inteligência': {
    'title': 'Palavra: Inteligência',
    'description': """Definição: capacidade de aprender, compreender e aplicar conhecimentos.

- **Estágio 0**: Você é o ser humano mais intelectualmente habilidoso da atualidade.
- **Estágio 1**: Manipula atributos de inteligência em si e em outros.
- **Estágio 2**: Pode criar ou remover estados de inteligência — gênio ou tolice absoluta.
- **Passiva**: Você compreende rapidamente qualquer conceito que entre em contato.
- **Estágio 3**: Manipula o conceito de inteligência — aplicando sabedoria a contextos abstratos.
- **Modo: Irrestrito**: Altera temporariamente o conceito do conceito de inteligência.""",
    'image_url': 'https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExcHdpOW5vaTAwOWgzNjk4ejhncnVrZjZlcTlpODY2eXBsNTZxYXRuYyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/RoH7oWSHHRsXxmSYbb/giphy.gif',
    'color': Colors.AZUL
},

'Dureza': {
    'title': 'Palavra: Dureza',
    'description': """Definição: qualidade de ser duro, resistente a deformações ou impactos.

- **Estágio 0**: Você entende como tornar qualquer material ou postura mais resistente.
- **Estágio 1**: Manipula atributos de dureza em superfícies e corpos.
- **Estágio 2**: Pode tornar qualquer coisa rígida ou frágil em nível estrutural.
- **Passiva**: Seu corpo é naturalmente mais difícil de romper, dobrar ou quebrar.
- **Estágio 3**: Manipula o conceito de dureza — tornando ideias, relações ou leis inquebráveis.
- **Modo: Irrestrito**: Altera temporariamente o conceito do conceito de dureza.""",
    'image_url': 'https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHFwcDIwZ2duYjFnOWg1OGZ3b2xyMHUxaWlhMnAxejdvaHkxdXpseCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/CCXb3l9RBCaRVHFWOw/giphy.gif',
    'color': Colors.PRETO
},

'Resistência': {
    'title': 'Palavra: Resistência',
    'description': """Definição: capacidade de suportar esforço, dor ou pressão por tempo prolongado.

- **Estágio 0**: Você pode suportar situações físicas e mentais por longos períodos.
- **Estágio 1**: Manipula atributos de resistência em si e em outros.
- **Estágio 2**: Pode gerar ou remover estados de resistência — exaustão ou perseverança extrema.
- **Passiva**: Sua energia vital parece não se esgotar em batalhas longas.
- **Estágio 3**: Manipula o conceito de resistência — oposição, durabilidade e persistência onde quiser.
- **Modo: Irrestrito**: Altera temporariamente o conceito do conceito de resistência.""",
    'image_url': 'https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExcDJienNiM25veXU4aTFqbTh0Nzc4ZnI0czE2cmh1M2RlbHMyZ2FidSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/CEkrWgkg1LYfw73Aqs/giphy.gif',
    'color': Colors.PRETO
},

'Nostalgia': {
    'title': 'Palavra: Nostalgia',
    'description': """Definição: sentimento de saudade idealizada de tempos passados.

- **Estágio 0**: Você é mestre em evocar sentimentos nostálgicos em si e nos outros.
- **Estágio 1**: Manipula atributos nostálgicos — sensações, imagens, atmosferas.
- **Estágio 2**: Pode mergulhar lugares e pessoas em estados nostálgicos ou apagá-los.
- **Passiva**: Sua presença evoca memórias afetivas mesmo em desconhecidos.
- **Estágio 3**: Manipula o conceito de nostalgia — tempo, memória e afeto tornam-se moldáveis.
- **Modo: Irrestrito**: Altera temporariamente o conceito do conceito de nostalgia.""",
    'image_url': 'https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExdm94NTJ5b2hjams2dGRyZ3Y5Ym1xemR3dzRwbWN0dXFmd29idmsyZyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/kv1c5up59MS2B3i3vJ/giphy.gif',
    'color': Colors.AMARELO
},

'Liso': {
    'title': 'Palavra: Liso',
    'description': """Definição: superfície sem rugosidade, atrito ou textura; escorregadia.

- **Estágio 0**: Você entende e identifica todas as formas de suavidade e atrito.
- **Estágio 1**: Manipula atributos de lisura — em objetos, superfícies ou até pele.
- **Estágio 2**: Pode alterar o estado liso — tornar algo impossível de agarrar ou absurdamente escorregadio.
- **Passiva**: Você escapa com facilidade de agarrões, prisões ou amarras.
- **Estágio 3**: Manipula o conceito de liso — tanto literal quanto metafórico, como “escapar” de situações.
- **Modo: Irrestrito**: Altera temporariamente o conceito do conceito de liso.""",
    'image_url': 'https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExbHQ1Y2wzMHJzMmk3djJobTVwcHV0djlybzh3ZXR0c2ZzNjNobTk0MyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/m1xBBvKcngel8qoCDm/giphy.gif',
    'color': Colors.BRANCO
},

'Preto': {
    'title': 'Palavra: Preto',
    'description': """Definição: ausência de luz ou cor; tom mais escuro do espectro visível.

- **Estágio 0**: Você entende o uso e impacto da cor preta em todas as formas.
- **Estágio 1**: Manipula atributos relacionados ao preto — cor, densidade, profundidade.
- **Estágio 2**: Pode transformar estados — escurecer completamente ou absorver luz e cor.
- **Passiva**: Você pode desaparecer facilmente em ambientes escuros.
- **Estágio 3**: Manipula o conceito de preto — ausência, mistério, sombra e silêncio.
- **Modo: Irrestrito**: Altera temporariamente o conceito do conceito de preto.""",
    'image_url': 'https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExMHplaGo2aXkxOWwxc3JhdXZ4anJzejZlMGNpMXNhM3lxbTRsOW80aiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/n4JSH7Z560gYdxSy7Q/giphy.gif',
    'color': Colors.PRETO
},

'Tamanho': {
    'title': 'Palavra: Tamanho',
    'description': """Definição: dimensão física ou escala de algo.

- **Estágio 0**: Você tem noção precisa de proporções e escalas de tudo ao seu redor.
- **Estágio 1**: Manipula atributos de tamanho em si ou em objetos/pessoas.
- **Estágio 2**: Pode alterar estados — expandir ou reduzir o tamanho real ou simbólico de algo.
- **Passiva**: Você pode se adaptar facilmente a qualquer escala sem desconforto.
- **Estágio 3**: Manipula o conceito de tamanho — importância, influência ou escala podem ser moldadas.
- **Modo: Irrestrito**: Altera temporariamente o conceito do conceito de tamanho.""",
    'image_url': 'https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExeXd0ZG1meDFpdDUyYWltc3BtMm9wYjF3aHR4NTBwZ29hZGRoMjBheCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/qwTMT2AgUuHwFreZXW/giphy.gif',
    'color': Colors.AZUL
},
'Felicidade': {
    'title': 'Palavra: Felicidade',
    'description': """Definição: estado de espírito pleno de satisfação, contentamento ou alegria.\n\n
- **Estágio 0**: Você compreende profundamente o que traz felicidade aos outros, podendo induzir momentos de alegria com gestos simples.
- **Estágio 1**: Pode manipular os atributos da felicidade, como sua intensidade, duração e foco (felicidade por comida, companhia, etc).
- **Estágio 2**: Pode gerar felicidade em pessoas, objetos ou locais e alternar seu estado (feliz ↔ neutro), podendo até tornar-se uma "presença feliz".
- **Passiva**: Sua presença inspira emoções positivas e bem-estar.
- **Estágio 3**: Manipula o conceito de felicidade em si, podendo alterá-lo ou aplicá-lo a ideias, memórias ou sensações.
- **Modo: Irrestrito**: Altera temporariamente o que é felicidade no mundo ao seu redor.""",
    'image_url': 'https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExM3k0a2xvZmw2MGJ5bXFua3UxMHl3aDMxNmttd3l5NTF2ejN4dWVsZyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/C7IKtEWlrYnkucUH08/giphy.gif',
    'color': Colors.AMARELO
},

'Dor': {
    'title': 'Palavra: Dor',
    'description': """Definição: sensação desagradável provocada por fatores físicos ou emocionais.\n
- **Estágio 0**: Você compreende e reconhece todos os tipos de dor, sendo imune a traumas menores.
- **Estágio 1**: Manipula atributos da dor — intensidade, tipo (corte, queimação), duração e localização.
- **Estágio 2**: Pode induzir, transferir ou absorver dor, e assumir uma forma de "encarnação da dor".
- **Passiva**: Você resiste a todos os tipos de dor, física ou emocional.
- **Estágio 3**: Manipula o conceito de dor, aplicando-a em ideias, símbolos ou até lugares.
- **Modo: Irrestrito**: Altera temporariamente o conceito de dor em todas as suas formas.""",
    'image_url': 'https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExN3d6eHRnanRjdGFobzlvOXVidzZwb3ZzdjM3eTNmbzhoejB6OTEwOCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/rHtFaKfQdCp4cYSKwK/giphy.gif',
    'color': Colors.VERMELHO
},

'Som': {
    'title': 'Palavra: Som',
    'description': """Definição: vibrações que se propagam por um meio e podem ser percebidas pela audição.\n
- **Estágio 0**: Você possui percepção sonora extremamente aguçada e entende perfeitamente harmonia, frequência e timbre.
- **Estágio 1**: Manipula atributos do som — volume, direção, frequência, duração e timbre.
- **Estágio 2**: Pode gerar, silenciar ou moldar sons, tornando-se fonte sonora viva.
- **Passiva**: Imune a distorções sonoras e hipersensível a alterações acústicas.
- **Estágio 3**: Manipula o conceito de som — tornando pensamentos audíveis, ruídos visíveis ou aplicando som a coisas que normalmente não soam.
- **Modo: Irrestrito**: Altera o conceito do conceito de som por tempo limitado.""",
    'image_url': 'https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExaTB5OWZ5ZDdtbW41OHMzMW1hbWFnejFhMXVpc2Rranl2bnVrc2Z5byZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/07iJVhWFQDdgzGsMR5/giphy.gif',
    'color': Colors.CIANO
},
'Eletromagnetismo': {
    'title': 'Palavra: Eletromagnetismo',
    'description': """Definição: interação física que ocorre entre partículas com carga elétrica, unificando eletricidade e magnetismo.\n
- **Estágio 0**: Você entende perfeitamente os fenômenos elétricos e magnéticos, podendo prever seus efeitos com precisão.
- **Estágio 1**: Manipula atributos eletromagnéticos — polaridade, intensidade, frequência e campo.
- **Estágio 2**: Pode gerar campos eletromagnéticos, anulá-los ou incorporar propriedades eletromagnéticas ao seu corpo.
- **Passiva**: Seus movimentos e decisões não são afetados por ondas eletromagnéticas ou campos magnéticos.
- **Estágio 3**: Manipula o conceito de eletromagnetismo, interferindo com comunicações, gravidade ou movimento.
- **Modo: Irrestrito**: Reescreve temporariamente o que significa eletromagnetismo.""",
    'image_url': 'https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExdTBtbmZuenVpdHFycWpuNXhmM3VpaWMxOXp3eGF1ZWYzOXFsOXNuaSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/4pAkj09i8BFhEoEvAE/giphy.gif',
    'color': Colors.AZUL
},

'Gravidade': {
    'title': 'Palavra: Gravidade',
    'description': """Definição: força que atrai corpos com massa uns aos outros; peso.\n
- **Estágio 0**: Você compreende e calcula a gravidade com precisão, reconhecendo suas variações com facilidade.
- **Estágio 1**: Manipula atributos gravitacionais — direção, intensidade e alcance.
- **Estágio 2**: Pode criar, remover ou inverter gravidade localmente e assumir forma gravitacional.
- **Passiva**: Sua movimentação ignora efeitos negativos da gravidade.
- **Estágio 3**: Manipula o conceito de gravidade — aplicando-a a ideias, vontades ou sentimentos.
- **Modo: Irrestrito**: Temporariamente Altera o que é a gravidade no mundo ao redor.""",
    'image_url': 'https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExcTV0NjNjNDhqemNid3YxcmdkNGp4bW96MGRreDhoNWpwdjlvMWRkaCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/SwRqAiPZBdQSBggrpl/giphy.gif',
    'color': Colors.ROXO
},

'Tempo (Musical)': {
    'title': 'Palavra: Tempo (Musical)',
    'description': """Definição: velocidade ou andamento com que uma música deve ser executada.\n
- **Estágio 0**: Você sente e domina perfeitamente qualquer andamento musical.
- **Estágio 1**: Manipula atributos do tempo musical — aceleração, pausa, marcação rítmica e pulso.
- **Estágio 2**: Pode aplicar andamentos musicais ao ambiente e ao seu corpo, ritmando ações e movimentos.
- **Passiva**: Seu corpo sempre age em sincronia com o ritmo mais eficiente para cada ação.
- **Estágio 3**: Manipula o conceito de tempo musical — tornando tudo ao seu redor regido por uma batida.
- **Modo: Irrestrito**: Você Altera o próprio conceito de ritmo e tempo aplicado à existência.""",
    'image_url': 'https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExbnhsNW9yZ3M5bG44NTdmM3M2OHZhdDVrNzExZjFubDBkOGZwcjN6ayZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/dvaiiZfVLPLUaysZ2m/giphy.gif',
    'color': Colors.LARANJA
},

'Atrito': {
    'title': 'Palavra: Atrito',
    'description': """Definição: força que resiste ao movimento relativo entre superfícies em contato.\n
- **Estágio 0**: Você entende a física do atrito em qualquer superfície, com precisão absoluta.
- **Estágio 1**: Manipula atributos do atrito — aumentando, reduzindo ou redirecionando seu efeito.
- **Estágio 2**: Pode gerar atrito em pleno ar, remover atrito do chão, ou incorporar atrito ao seu corpo ou objetos.
- **Passiva**: Seus movimentos são otimizados, com total controle de aderência e deslizamento.
- **Estágio 3**: Manipula o conceito de atrito, aplicando resistência ou fluidez a qualquer coisa.
- **Modo: Irrestrito**: Reescreve temporariamente a existência e aplicação do atrito.""",
    'image_url': 'https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExdGQxOGN5azJ0YW42ZzdpbmU2MXdjOGhyMzdxZGZtcGR6eXp5NjNjNyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/8WOINgtcKYJqXGBk1I/giphy.gif',
    'color': Colors.PRETO
},

'Sonho': {
    'title': 'Palavra: Sonho',
    'description': """Definição: conjunto de imagens, ideias e sensações vividas durante o sono ou um ideal imaginado.\n
- **Estágio 0**: Você entende simbolismos e significados ocultos nos sonhos alheios com facilidade.
- **Estágio 1**: Manipula atributos de sonhos — intensidade, lucidez, duração e tema.
- **Estágio 2**: Pode invadir ou criar sonhos em outros, ou entrar em um estado de sonho ativo.
- **Passiva**: Você recupera energia enquanto sonha e raramente dorme involuntariamente.
- **Estágio 3**: Manipula o conceito de sonho — tornando ilusões reais ou aplicando sonho a estados acordados.
- **Modo: Irrestrito**: Altera temporariamente o que é sonho e o que é realidade.""",
    'image_url': 'https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExZXowM2NiYTVqOWk5aGN1bHFvM2M5MTE5cXRobnJlaDlwMXV3cTV1ZyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/gq607lYNzeZQcIWR13/giphy.gif',
    'color': Colors.CIANO
},

'Lag': {
    'title': 'Palavra: Lag',
    'description': """Definição: atraso ou lentidão entre uma ação e sua consequência, especialmente em sistemas digitais.\n
- **Estágio 0**: Você sente qualquer tipo de descompasso, falha de tempo ou resposta atrasada com precisão.
- **Estágio 1**: Manipula atributos do lag — atraso, duração, intervalo e alcance.
- **Estágio 2**: Pode aplicar atrasos a ações, palavras, ou movimentos seus e dos outros.
- **Passiva**: Você nunca sofre com atrasos mentais ou reflexos.
- **Estágio 3**: Manipula o conceito de lag — atrasando até sentimentos, decisões ou lógica.
- **Modo: Irrestrito**: Altera temporariamente o que é atraso e como o mundo responde a ações.""",
    'image_url': 'https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExdjJ4dmxndTkxdHp1c2c3aGFlbGpoeTFieXVzbnJ1OXNuOTVjc296eCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/FA49CIMkO9SfGDQqJQ/giphy.gif',
    'color': Colors.ROXO
},

'Ressonância': {
    'title': 'Palavra: Ressonância',
    'description': """Definição: reforço de vibração natural de um sistema quando exposto a uma frequência correspondente.\n
- **Estágio 0**: Você detecta facilmente ressonâncias naturais em qualquer ambiente ou objeto.
- **Estágio 1**: Manipula atributos de ressonância — frequência, intensidade, harmonia e tempo.
- **Estágio 2**: Pode forçar ressonância entre corpos ou sentimentos, ou tornar-se fonte de eco e amplificação.
- **Passiva**: Seu corpo vibra de forma harmônica, resistindo a forças destrutivas.
- **Estágio 3**: Manipula o conceito de ressonância — sincronizando ideias, emoções ou eventos.
- **Modo: Irrestrito**: Altera temporariamente o que significa vibrar em sintonia.""",
    'image_url': 'https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExMnUycDl0ZmVwM2Y2dXZjejFxaW05dGd3ZTBjeWY2ano1YjY0cmJtciZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/nUCMxWhvxzM9vdMIpP/giphy.gif',
    'color': Colors.AZUL
},

'Retorno': {
    'title': 'Palavra: Retorno',
    'description': """Definição: ação de voltar a um ponto de origem ou retribuição.\n
- **Estágio 0**: Você compreende ciclos, consequências e reações como ninguém.
- **Estágio 1**: Manipula atributos de retorno — tempo, força, alvo e forma.
- **Estágio 2**: Pode devolver ataques, repetir ações ou fazer objetos voltarem ao estado anterior.
- **Passiva**: Seus erros e danos sempre voltam com menor impacto.
- **Estágio 3**: Manipula o conceito de retorno — fazendo ideias, eventos ou sentimentos retornarem.
- **Modo: Irrestrito**: Reescreve temporariamente a lógica do que pode ou não voltar.""",
    'image_url': 'https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExMWNmbWZjdXZta2k5MTlnYnFwZzNyZmN6dnQxM3F4NWNlemZvYzZ4NCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/4AQNzWqau56rp9RGbn/giphy.gif',
    'color': Colors.VERDE
},

'Soma': {
    'title': 'Palavra: Soma',
    'description': """Definição: resultado da adição de dois ou mais elementos.\n\n
- **Estágio 0**: Você calcula e combina elementos intuitivamente, com maestria.
- **Estágio 1**: Manipula atributos da soma — quantidade, ordem, tipo e valor dos somados.
- **Estágio 2**: Pode somar conceitos, objetos ou efeitos, criando resultados híbridos ou acumulativos.
- **Passiva**: Suas ações tendem a acumular efeitos positivos.
- **Estágio 3**: Manipula o conceito de soma — unindo ideias, histórias ou probabilidades.
- **Modo: Irrestrito**: Altera o que é somar — combinando até opostos.""",
    'image_url': 'https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExY3U2NjExdzd5N3dxaWw5aHFyc3ZlN3ByZzY5cXdxZ2RhcmZldXRmdSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/FL46di7XoaRIqIg57G/giphy.gif',
    'color': Colors.AMARELO
},

'Monarca': {
    'title': 'Palavra: Monarca',
    'description': """Definição: soberano absoluto de um reino ou estado; rei ou rainha.\n
- **Estágio 0**: Você compreende profundamente dinâmicas de liderança e hierarquia.
- **Estágio 1**: Manipula atributos de um monarca — autoridade, respeito, ordem e presença.
- **Estágio 2**: Pode emanar influência dominante, forçar obediência ou se tornar a representação viva de um trono.
- **Passiva**: Sua presença impõe respeito natural e evita conflitos diretos.
- **Estágio 3**: Manipula o conceito de monarca — aplicando domínio e soberania em qualquer situação.
- **Modo: Irrestrito**: Altera temporariamente o que é reinar — fazendo de você o centro absoluto.""",
    'image_url': 'https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExdzIzeWE1YmR0Nnlzd2swemNmOHUzeG5rY3MwN3hraGlxam55NzRnbSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/UmJxWvFPXeSEzE2QHL/giphy.gif',
    'color': Colors.PRETO
},
'Golpear': {
    'title': 'Palavra: Golpear',
    'description': """Definição: atingir com um golpe; bater ou agredir com força.

- **Estágio 0**: Você domina todas as formas conhecidas de golpes físicos, desde técnicas marciais até improvisações.
- **Estágio 1**: Manipula os atributos de um golpe — intensidade, direção, área de impacto, entre outros.
- **Estágio 2**: Pode aplicar o estado de "golpeado" em alvos sem contato direto, estendendo a ideia de golpe para múltiplos meios.
- **Passiva**: Seus golpes ignoram resistência comum e são mais difíceis de prever ou bloquear.
- **Estágio 3**: Manipula o conceito de golpe — tudo que for afetado por você pode ser tratado como um golpe, inclusive palavras, ideias e emoções.
- **Modo: Irrestrito**: Altera temporariamente o que é considerado um golpe no mundo, desde uma olhada até a ausência de ação.""",
    'image_url': 'https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExc3Axc2toY2d4NGNienR4YnB0ZnIxeG8wYmVua3lhOGpuOGluazdieiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/RFXHXXfI9YIZTQAJLK/giphy.gif',
    'color': Colors.VERMELHO
},

'Produzir': {
    'title': 'Palavra: Produzir',
    'description': """Definição: criar, gerar ou fabricar algo a partir de matéria, energia ou ideias.

- **Estágio 0**: Você tem eficiência máxima ao criar coisas manualmente, como alimentos, itens ou arte.
- **Estágio 1**: Manipula os atributos do processo de produção — velocidade, escala, complexidade.
- **Estágio 2**: Pode produzir elementos complexos do nada ou alterar a origem de algo produzido.
- **Passiva**: O que você cria é sempre funcional e difícil de replicar por outros.
- **Estágio 3**: Manipula o conceito de produção — fazer com que qualquer coisa surja, mesmo sem lógica aparente.
- **Modo: Irrestrito**: Durante o irrestrito, tudo ao seu redor passa a gerar versões de si mesmo em cadeia, em um ciclo que para após o efeito.""",
    'image_url': 'https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExMjIwanAyd3MxYXE3OTNrazRuazF0ODVqNGJxNnozeWVwcDVuemNscyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/ZkEKlEjKl7yEqx8J2N/giphy.gif',
    'color': Colors.AMARELO
},

'Cultivar': {
    'title': 'Palavra: Cultivar',
    'description': """Definição: cuidar de algo para que cresça ou se desenvolva — geralmente plantas, mas também ideias, relações, etc.

- **Estágio 0**: Você entende profundamente os ciclos de crescimento de seres vivos e ideias.
- **Estágio 1**: Manipula o crescimento — acelera, desacelera ou condiciona o cultivo de qualquer coisa.
- **Estágio 2**: Pode criar campos de cultivo de ideias, emoções ou matéria orgânica.
- **Passiva**: Tudo que você planta ou inicia tem um desenvolvimento constante e sustentável.
- **Estágio 3**: Manipula o conceito de cultivar — fazer com que qualquer coisa evolua com cuidado e intenção.
- **Modo: Irrestrito**: Tudo ao seu redor entra em estado de crescimento rápido e controlado por você.""",
    'image_url': 'https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExNDR0NXptZ3B3MHI0Z2hnb3AxaTVjbzVuYXlyZnhtNmF0bnMyNGlrdyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/P3TAfhCOdtuEgQQdK2/giphy.gif',
    'color': Colors.VERDE
},

'Roubar': {
    'title': 'Palavra: Roubar',
    'description': """Definição: tomar algo que pertence a outro sem permissão.

- **Estágio 0**: Você é um mestre em furtos, entendendo o momento, valor e consequência de cada roubo.
- **Estágio 1**: Manipula atributos de roubo — o que, quando e quanto se perde ou se transfere.
- **Estágio 2**: Pode roubar coisas intangíveis como sorte, conhecimento ou tempo de alguém.
- **Passiva**: O que você rouba não pode ser facilmente recuperado e se adapta bem a você.
- **Estágio 3**: Manipula o conceito de roubo — tomar de qualquer forma, mesmo sem contato direto ou intenção perceptível.
- **Modo: Irrestrito**: O universo passa a permitir que você tome aquilo que "não deveria ser tomado", inclusive conceitos como destino ou propósito.""",
    'image_url': 'https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExemptdHJjZHJkaWNqdHRodWJ2dHRzb2FnaWw5cTl5ZDNnOHQ5OXVrOCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/Gq1V5eUAxwTWyTRI24/giphy.gif',
    'color': Colors.ROXO
},

'Curar': {
    'title': 'Palavra: Curar',
    'description': """Definição: restaurar a saúde, reparar danos ou aliviar dores.

- **Estágio 0**: Você tem a melhor compreensão possível de processos de cura naturais e medicinais.
- **Estágio 1**: Manipula a velocidade e qualidade da cura, além de aplicar cura seletiva.
- **Estágio 2**: Pode curar traumas mentais, espirituais ou mesmo entidades não-biológicas.
- **Passiva**: Sua presença acelera a recuperação de aliados e ambientes.
- **Estágio 3**: Manipula o conceito de cura — fazendo com que qualquer coisa volte ao seu estado "ideal".
- **Modo: Irrestrito**: Você pode reverter eventos ao estado anterior ao "dano", curando até o tempo.""",
    'image_url': 'https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExY2FtdWxxY2IzOWIycXI4aW92aWh0enR1dDNjODdnbDF0YnpibHk0MyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/XQ5JzhnZ665ZjXOaB7/giphy.gif',
    'color': Colors.AZUL
},
'Brutalizar': {
    'title': 'Palavra: Brutalizar',
    'description': """Definição: agir com extrema violência, crueldade ou força desenfreada.

- **Estágio 0**: Você compreende profundamente as manifestações mais intensas de agressão e força bruta.
- **Estágio 1**: Manipula os atributos de ações violentas — intensidade, impacto, alcance emocional.
- **Estágio 2**: Pode brutalizar o ambiente ou conceitos, fazendo com que qualquer coisa seja corrompida pela violência.
- **Passiva**: Seus ataques e ações têm um efeito psicológico desmoralizante.
- **Estágio 3**: Manipula o conceito de brutalidade — tudo que você toca ou influencia se torna brutal.
- **Modo: Irrestrito**: Você transforma a realidade em um estado de brutalidade latente, onde tudo colapsa para a violência.""",
    'image_url': 'https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExdDM3eWFrMmt4bHJudGZoeWx3aG4zMGFwamNpd25ncG9zMHUxeGI4YiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/59Z2Kj0sN712PrKK5K/giphy.gif',
    'color': Colors.VERMELHO
},

'Dançar': {
    'title': 'Palavra: Dançar',
    'description': """Definição: mover-se ritmicamente ao som de música ou impulsos internos.

- **Estágio 0**: Você é o dançarino mais talentoso, com controle total sobre ritmo, fluidez e expressão.
- **Estágio 1**: Manipula atributos da dança — velocidade, graça, impacto no ambiente e até nos outros.
- **Estágio 2**: Pode forçar o ambiente ou pessoas a seguirem o seu "ritmo" e transformá-lo em dança literal ou simbólica.
- **Passiva**: Seu corpo flui com uma leveza sobrenatural e atrai atenção.
- **Estágio 3**: Manipula o conceito de dançar — tudo pode entrar em harmonia ou fluxo com sua intenção.
- **Modo: Irrestrito**: O mundo ao redor dança com você, regido por sua vontade e seu compasso.""",
    'image_url': 'https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExOWkzdnBnOGJ3NTY1aDVwd3Vlc2d0c283NDF6cGYyeWpoMXVpMnBoMiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/cf3hHIgtnMPMtqRGBK/giphy.gif',
    'color': Colors.CIANO
},

'Planejar': {
    'title': 'Palavra: Planejar',
    'description': """Definição: organizar mentalmente ou estruturar ações futuras com objetivos claros.

- **Estágio 0**: Você é o melhor estrategista e sempre tem planos detalhados para cada situação.
- **Estágio 1**: Manipula os atributos de um plano — duração, precisão, adaptabilidade.
- **Estágio 2**: Pode tornar planos realidade parcial mesmo antes de executá-los.
- **Passiva**: Seus planos são quase inevitáveis de se realizarem.
- **Estágio 3**: Manipula o conceito de planejamento — você define o destino das coisas antes que aconteçam.
- **Modo: Irrestrito**: Toda a realidade passa a se moldar de acordo com o seu plano mestre.""",
    'image_url': 'https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExZWFsN3ZiMjVjcjc2MHg2dHcxMjZ5ZzZueWRiZTZiZG5ybXJodnl6ZiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/XcabYJnOhiked32EZz/giphy.gif',
    'color': Colors.PRETO
},

'Acertar': {
    'title': 'Palavra: Acertar',
    'description': """Definição: atingir o alvo com precisão ou fazer algo corretamente.

- **Estágio 0**: Você raramente erra qualquer coisa que tente, com uma taxa de acerto quase perfeita.
- **Estágio 1**: Manipula os atributos de acerto — alcance, precisão, inevitabilidade.
- **Estágio 2**: Pode "acertar" conceitos, como acertar uma ideia, uma escolha ou um sentimento.
- **Passiva**: Seus acertos afetam mais do que o esperado, com consequências em cadeia.
- **Estágio 3**: Manipula o conceito de acerto — tudo que você faz tende a resultar corretamente.
- **Modo: Irrestrito**: Durante o irrestrito, tudo o que você fizer será o acerto ideal, não importa como.""",
    'image_url': 'https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExMHF6NWtwZ3BmaDJhc2h3bHIwMWlhc3QzYXpndHE2dnc2eXgxeWg1diZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/GLQuTzY81a4PIbTgOO/giphy.gif',
    'color': Colors.AZUL
},

'Apodrecer': {
    'title': 'Palavra: Apodrecer',
    'description': """Definição: decompor-se ou deteriorar-se gradualmente, física ou simbolicamente.

- **Estágio 0**: Você compreende com perfeição o processo de decadência e putrefação.
- **Estágio 1**: Manipula atributos de decomposição — velocidade, profundidade, alvo.
- **Estágio 2**: Pode apodrecer objetos imateriais como memórias, estruturas sociais ou ideias.
- **Passiva**: Tudo que você negligencia tende a se deteriorar naturalmente.
- **Estágio 3**: Manipula o conceito de apodrecer — tornando tudo suscetível à entropia.
- **Modo: Irrestrito**: O tempo e a estabilidade das coisas ao seu redor entram em colapso, apodrecendo por existência.""",
    'image_url': 'https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExcHM4cnI5aHk3dnNhbnl2b2F1aHJxbWF3dmtpbmZjNzN5bnM1YTQxMSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/2yGcHhmjk4PQliNOAx/giphy.gif',
    'color': Colors.ROXO
},

'Iluminar': {
    'title': 'Palavra: Iluminar',
    'description': """Definição: tornar algo visível, claro ou compreensível através da luz ou conhecimento.

- **Estágio 0**: Você é excelente em fazer os outros entenderem algo, revelar e trazer clareza.
- **Estágio 1**: Manipula a luz ou entendimento — foco, intensidade, alcance.
- **Estágio 2**: Pode tornar ideias e verdades visíveis ou "iluminar" lugares que não existem.
- **Passiva**: Sua presença tende a revelar o que está escondido.
- **Estágio 3**: Manipula o conceito de iluminação — tudo pode ser clareado, exposto ou elevado.
- **Modo: Irrestrito**: Toda escuridão, dúvida ou mistério desaparece temporariamente diante da sua luz.""",
    'image_url': 'https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExNXNraHV1M28xbzN5anNsOXZkcmptcjN2am5pcGY0b3NvaHNqa2M3bSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/m0B8R1QqNuCfViycll/giphy.gif',
    'color': Colors.AMARELO
},

'Teleportar': {
    'title': 'Palavra: Teleportar',
    'description': """Definição: mover-se instantaneamente de um ponto a outro.

- **Estágio 0**: Você conhece e calcula deslocamentos com perfeição.
- **Estágio 1**: Manipula atributos do teleporte — alcance, destino, quantidade.
- **Estágio 2**: Pode teletransportar ideias, emoções ou até momentos no tempo.
- **Passiva**: Seus movimentos são imprevisíveis e quase instantâneos.
- **Estágio 3**: Manipula o conceito de presença — estar onde quiser, mesmo sem movimento.
- **Modo: Irrestrito**: O espaço deixa de ser uma limitação, você e tudo ao seu redor podem surgir em qualquer lugar.""",
    'image_url': 'https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExNWRhdGl0MnRqc2Jyd3E0aTMyaWExZm5qaG51ZW1sczVjaGk3cWdieCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/HJuhEMfP9lPzT0ulDr/giphy.gif',
    'color': Colors.CIANO
},

'Caçar': {
    'title': 'Palavra: Caçar',
    'description': """Definição: perseguir algo com o objetivo de capturar ou eliminar.

- **Estágio 0**: Você é o maior rastreador, estrategista e perseguidor natural.
- **Estágio 1**: Manipula atributos da caçada — foco, resistência, sigilo.
- **Estágio 2**: Pode caçar conceitos, emoções ou até destinos.
- **Passiva**: Tudo que você persegue tende a ser inevitavelmente alcançado.
- **Estágio 3**: Manipula o conceito de caça — todo o universo passa a ver algo como sua presa.
- **Modo: Irrestrito**: Sua presa não tem escapatória, independentemente de onde ou o que seja.""",
    'image_url': 'https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExNGx4dmRtcHEzYnJqN2tsZmZmeHV5N3Z3N3Mwb3g5NTlnYnlqbWpiOSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/iwl3TiUU6LTrML6ooW/giphy.gif',
    'color': Colors.VERMELHO
},

'Cirurgia': {
    'title': 'Palavra: Cirurgia',
    'description': """Definição: procedimento técnico e preciso para modificar corpos, sistemas ou estruturas.

- **Estágio 0**: Você domina anatomia, procedimentos médicos e reparos corporais.
- **Estágio 1**: Manipula atributos de uma cirurgia — precisão, tipo de intervenção, tempo.
- **Estágio 2**: Pode operar estruturas não físicas, como emoções, ideias ou relações.
- **Passiva**: Suas intervenções são sempre minimamente invasivas e eficazes.
- **Estágio 3**: Manipula o conceito de cirurgia — pode modificar qualquer coisa com precisão absoluta.
- **Modo: Irrestrito**: Você "opera" o mundo, removendo, implantando ou corrigindo até leis universais.""",
    'image_url': 'https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExZ2djZGMydzhrajY0NTZyN3owaTU5bm0zb3dwemMxY294MjBvYWpzbyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/1BuP7iRMql5xZhFs3G/giphy.gif',
    'color': Colors.BRANCO
},

'Cantar': {
    'title': 'Palavra: Cantar',
    'description': """Definição: emitir som com ritmo e melodia, geralmente com a voz.

- **Estágio 0**: Você é o cantor mais expressivo, afinado e impactante.
- **Estágio 1**: Manipula os atributos da voz — alcance, emoção, efeitos.
- **Estágio 2**: Pode cantar para afetar diretamente a realidade, curar, controlar ou alterar.
- **Passiva**: Sua voz tem efeito emocional real nas pessoas ao redor.
- **Estágio 3**: Manipula o conceito de canto — o universo ressoa com sua melodia.
- **Modo: Irrestrito**: Cada nota que você emite altera o mundo em um nível conceitual.""",
    'image_url': 'https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExNnVkMjdwYWRydjd6Y2xmaWF5ZzY5OWR0ajNtdXFwOTg0MXc4Z3VxeiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/Zor8Z7RQso67MhpX42/giphy.gif',
    'color': Colors.CIANO
},

'Impulsionar': {
    'title': 'Palavra: Impulsionar',
    'description': """Definição: dar impulso ou força para algo avançar ou crescer.

- **Estágio 0**: Você entende o momento e a força certa para acelerar pessoas, ideias ou ações.
- **Estágio 1**: Manipula o impulso — velocidade, direção, impacto.
- **Estágio 2**: Pode impulsionar o tempo, conceitos ou emoções.
- **Passiva**: Você naturalmente acelera processos e ideias ao seu redor.
- **Estágio 3**: Manipula o conceito de impulso — tudo que você toca ganha um novo movimento inevitável.
- **Modo: Irrestrito**: Tudo se torna propulsionado ao extremo, como uma explosão de progresso em tudo que você deseja.""",
    'image_url': 'https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExb3J3M3k4bm83cnJoYmM3cHp6cGR1NHU1YmdnYXFzd3I4eHFyZDJ3eiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/2G72eLZIuxjJUMUtLH/giphy.gif',
    'color': Colors.LARANJA
},

# Casos: Arquivos

"Arquivo: Vermelho Silencioso": {
  "title": "Arquivo: Vermelho Silencioso",
  "description": (
    """Dizem que entre os campos mortos do interior, onde o trigo cresce mais dourado do que deveria, vive um espectro de capuz vermelho — uma jovem sem nome, sem Palavra, sem voz. \n
Chamam-na de **Aura**. Não por luz, mas por vazio. Não brilha, não guia. Só caminha. \n
Foi arrancada de sua família pela Igreja por seus cabelos loiros e olhos verdes — traços ditos "apropriados" para o serviço divino. Criada para obedecer, alimentada por dogmas e violência. Mas tudo mudou no dia do **banquete no campo**.\n
Ali, ela e a **Deusa do Trigo** dividiram uma refeição proibida: uma freira, sua "avó". E após o último pedaço, Aura uivou ao sol... e jamais falou outra vez. \n
Roubaram sua Palavra. Roubaram sua infância. Mas ela ficou com algo: **ódio e aço.** \n
- **Arma**: *Cutelo de Trincheira “Credo”* — um serrote rústico e brutal feito de metal litúrgico. Serrando carne ou cortando ar, faz um som grotesco que ecoa como uma missa maldita.
- **Estilo de combate**: Silenciosa, brutal, instintiva. Conhece o corpo humano como quem conhece o próprio trauma. Mata sem hesitar.
- **Comportamento**: Nunca fala. Nunca sorri. Sua presença causa calafrios em padres e silêncio em igrejas.
- **Status atual**: Vagando. Sem propósito, sem salvação. Em busca apenas de vingança contra a estrutura que a moldou e que agora deseja esquecer sua existência. \n
Alguns dizem que ela ainda busca por algo no trigo. Outros, que deseja apenas lembrar ao mundo o gosto do sangue de sua origem."""
  ),
  'image_url': 'https://imgur.com/SJ5hjgW.png',
    'color': Colors.VERMELHO
},

"Arquivo: Gula Púrpura": {
  "title": "Arquivo: Gula Púrpura",
  "description": (
    """Na cidade de Kato, onde os cheiros se misturam ao vapor e a fome espreita mesmo nos saciados, vive **Rize**, a Dama da Gula. Ou como alguns a chamam, a **Fome que Ri**.\n
Seu passado é um enigma contado em sussurros: uma garota criada em meio aos descartes de banquetes, onde aprendeu que a fome é tanto maldição quanto poder. Nunca teve um lar. Mas sempre teve apetite. \n
Quando sua Palavra (Voracidade) despertou, foi como uma febre. Começou a provar o que ninguém ousava: vidro moído, pedra quente, mentiras. Descobriu que tudo pode ser engolido — até vontades. \n
**Rize não sente fome. Ela é a fome.**\n
Dizem que seus olhos brilham ao ver fraquezas, que seu riso pode cortar apetite de quem ouve. E que uma vez convidado à sua mesa, não se sai o mesmo. Nem inteiro.\n
- **Arma**: *Punhos Nus* — musculatura refinada, dedos afiados e articulações reforçadas. Rize cozinha com as mãos. E luta do mesmo jeito. Cada soco seu reorganiza o mundo como um prato indesejado.
- **Estilo de combate**: Selvagem, elegante, implacável. Não guarda postura — ela dita o ritmo. Cada ataque é como mastigar algo resistente: decidido, ritmado, instintivo.
- **Comportamento**: Descontraída, sedutora, insuportavelmente confiante. Sempre rindo, sempre avaliando. Seu olhar pesa como um garfo prestes a decidir o que vale ser devorado.
- **Status atual**: Considerada uma das três damas de Kato. Anda sozinha, mas sua presença enche os becos de sussurros e estômagos de medo. Alguns dizem que ela não luta por causa, nem por glória — apenas por **sabor**.\n
Rize não quer destruir nada. Mas se algo cair no prato, ela não desperdiça."""
  ),
  'image_url': 'https://imgur.com/a/u7UOtTg.png',
  'color': Colors.ROXO
},

"Arquivo: Sabedoria Celeste": {
  "title": "Arquivo: Sabedoria Celeste",
  "description": (
    """Na cidade de Kato, onde até as mentiras se ajoelham diante do saber, habita **Nyxaria**, a Grande Sábia. Ou como os mais íntimos chamam, com ternura e temor: **a que consome a si mesma para alimentar o mundo**.\n
Vestida como uma freira, com cabelos claros e um único olho de pérola reluzente, **Nyxaria não luta. Ela vive por um fio.** Seus órgãos, corroídos pela própria Palavra, já não cumprem seu papel. Cada passo é uma dança com a morte. Cada gesto, um milagre sustentado por pura intenção.\n
Sua Palavra é **Autofagia** — e ela a aceita com resignação. Seu corpo se destrói, mas em troca, ela compreende. Entende pensamentos que não foram ditos. Traduz sonhos em verdades. Desvenda almas pela forma como respiram. Cada pedaço que ela perde, é devolvido em sabedoria aos outros. \n
**Nyxaria é o preço da iluminação.**\n
Criada nas bordas do mundo, longe da fé e perto do desespero, foi descoberta pela Igreja não como uma ameaça — mas como uma relíquia viva. **Eles a mantêm como um segredo frágil e precioso**, trancada entre janelas fechadas e promessas falsas. Não a veneram. Não a libertam. Apenas a exibem, quando convém.\n
- **Arma**: *Nenhuma*. Sua força não reside em mãos ou espadas, mas em palavras que não precisam ser ditas. Quando muito, seus olhos bastam.
- **Estilo de combate**: *Inexistente*. Nyxaria não combate. Ela guia. Ela observa. E às vezes, quando o mundo precisa, **ela chora — e as lágrimas caem como veredictos**.
- **Comportamento**: Gentil, compassiva, serena. Mas nunca fraca. Sob sua delicadeza há um estoicismo indomável. Ela sabe que morrerá pouco a pouco — e ainda assim, escolhe oferecer tudo o que lhe resta a quem mais precisa. Não por fé. Mas por escolha.
- **Status atual**: Uma das três damas de Kato. Preservada pela Igreja, mas não pertencente a ela. Reverenciada por quem a conhece, temida por quem entende o que ela carrega. Dizem que, se Nyxaria um dia deixar de existir, a cidade de Kato perderá seu coração — e o céu, sua bússola.\n
Nyxaria não deseja redenção. Nem poder. Ela apenas quer que ninguém mais precise se consumir como ela para ser ouvido."""
  ),
  'image_url': 'https://imgur.com/a/jnQ6p4q.png',
  'color': Colors.PEROLA
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


@bot.command(name='test_embed')
async def test_embed(ctx):
    """Testa a criação de um embed."""
    embed = discord.Embed(
        title='Teste de Embed',
        description='Este é um teste de embed para ver como ele é exibido.',
        color=Colors.VERDE,
    )
    
    #embed.set_image(url="https://c.tenor.com/tOWeRGLqcQkAAAAC/tenor.gif")
    embed.set_image(url="https://i.imgur.com/0UtTwt2.gif")
    # https://c.tenor.com/ {URL} /tenor.gif
    return await ctx.send(embed=embed)

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