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
        """A Uno é a espinha dorsal do submundo da informação. Num sistema onde o conhecimento é moeda de poder, 
        a Uno atua como a principal detentora e negociadora de segredos. Sua estrutura é dividida entre funcionários 
        administrativos, "olhos" e "ouvidos", cada qual com uma função clara na teia de vigilância urbana. Em meio à 
        liberdade caótica da cidade, a Uno prospera oferecendo informações precisas, vendidas por preço alto — em favores, 
        recursos ou dados. Seu atual líder é **Raviel**.\n
        - **Funcionários**: Responsáveis por organizar, catalogar e gerenciar os dados obtidos. Trabalham em escritórios ocultos, 
        muitas vezes sem saber quem são os espiões ou de onde vêm as informações.
        - **Olhos**: São os observadores, infiltrados em locais estratégicos, com poderes voltados à percepção, análise e ilusão. 
        São os responsáveis por capturar imagens, cenas e comportamentos.
        - **Ouvidos**: Mestres em escuta e infiltração, operam como sombras nos corredores da cidade. Com habilidades de mimetismo 
        e espionagem auditiva, são eles que interceptam conversas, confissões e ameaças."""
    ),
    'image_url': 'https://i.imgur.com/RPuGOvA.png',
    'color': Colors.ROXO,
    'apenas_imagem': True
},

    'Zwei': {
        'title': 'Zwei - Proteção',
        'description': (
        """A Zwei representa o braço protetor da cidade, mesmo num sistema onde a segurança é uma escolha de mercado. 
        Seus membros vestem armaduras pesadas e agem guiados por um ideal de preservação da vida — mesmo quando isso entra em choque com o lucro. 
        Com ações marcadas por coragem e sacrifício, a Zwei é respeitada, mas sua ética altruísta frequentemente causa atritos com o restante da cidade. 
        Sua atual líder é **Tereza**.\n
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
        """A San é o motor movido a carvão que nunca para. Como a maior transportadora da cidade, sua lógica é simples: lucro sobre trilhos. 
        Com linhas ferroviárias cruzando setores inteiros, a San é a espinha dorsal da logística urbana e industrial. 
        Seus cortes de gastos extremos levaram à criação de forças armadas internas — a temida Equipe de Limpeza. 
        Seu atual líder é **Hermiton**, uma figura difícil de encontrar até para seus subordinados.\n
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
        """A Arba’a vive um período de reconstrução após uma queda catastrófica. Antigamente temida como a organização de assassinos mais mortal da cidade, 
        hoje opera nas sombras, tentando retomar seu prestígio. Cada “dedo” da Arba’a representa um estilo único de morte, refletindo a especialização da hierarquia. 
        São cinco grupos principais, conhecidos como a mão da morte. Atualmente, a líder é **Ilya**.\n
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
        """A Cinq é a encarnação da lei absoluta em meio ao caos. Mesmo numa sociedade onde a liberdade impera, alguém precisa traçar limites — 
        ou ao menos parecer que o faz. Sua sede imponente e julgamentos públicos tornaram a Cinq uma entidade temida e reverenciada. 
        Suas decisões são definitivas e suas execuções, exemplares. Seu atual líder é **Peter**.\n
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
        """A Sita controla a cidade por onde realmente importa: o bolso. Detentora do maior mercado e banco local, é nela que o valor das coisas — e das pessoas — é definido. 
        Sua estrutura aristocrática é composta por barões e baronesas que dominam setores como feudos, enquanto o consumidor é apenas um número com carteira. 
        Na Sita, tudo tem um preço. Juros, taxas e cláusulas escondidas são parte do jogo. Sua atual líder é **Rxya**.\n
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
        """A Sedam é o último resquício do antigo exército — e o único fornecedor legal de pólvora e armas da cidade. 
        Isolada do restante das organizações, raramente se envolve nos conflitos, exceto quando o pagamento justifica. 
        Com estrutura militar e rígida, mantém um monopólio absoluto sobre o armamento. Seu atual líder é **Heinken**.\n
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
        """A Otte é a guardiã do conhecimento verdadeiro. Em uma cidade dominada por fumaça e ganância, sua biblioteca é um farol de saber. 
        Sobrevive graças a doações misteriosas e benfeitores anônimos, mesmo não sendo lucrativa. 
        Seu atual líder é **Venus**, frequentemente confundido com o lendário professor **Joaquim**.\n
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
        """A Nau colore o cinza da cidade com suas luzes, risos e absurdos. Responsável por toda a produção audiovisual, ela dita o que a cidade vê, ouve e sente. 
        Seu estilo é caótico, extravagante e vicioso. Por trás de cada show, existe uma engrenagem brilhante — e bizarra. 
        Sua figura máxima é o **Palhaço Palhaçada**, símbolo e lenda urbana.\n
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
        """A Deg é o que mantém a cidade em ordem — ou pelo menos dá essa impressão. Não dita as regras, mas decide quem fala com quem, quando e sob quais condições. 
        É a peça invisível que move o tabuleiro de poder. Quando há problemas externos, a Deg é sempre a primeira a agir. 
        Sua líder atual é **Yin**.\n
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