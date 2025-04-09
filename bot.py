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


class RaridadesPesos(Enum):
    LENDARIO: int = 8
    EPICO: int = 17
    RARO: int = 27
    COMUM: int = 48

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
    'San - Transporte (Associado)': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'function': 'Associado'},

    # Arba'a
    'Arba\'a - Assassinato (Funcionario)': {'rarity': RaridadesPesos.RARO, 'color': Colors.VERDE, 'function': 'Funcionario'},
    'Arba\'a - Assassinato (Padrinho)': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO, 'function': 'Padrinho'},
    'Arba\'a - Assassinato (Madrinha)': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO, 'function': 'Madrinha'},
    'Arba\'a - Assassinato (Associado)': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'function': 'Associado'},

    # Cinq
    'Cinq - Justiça (Funcionario)': {'rarity': RaridadesPesos.RARO, 'color': Colors.VERDE, 'function': 'Funcionario'},
    'Cinq - Justiça (Juiz)': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO, 'function': 'Juiz'},
    'Cinq - Justiça (Associado)': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'function': 'Associado'},

    # Sita
    'Sita - Economia (Funcionario)': {'rarity': RaridadesPesos.RARO, 'color': Colors.VERDE, 'function': 'Funcionario'},
    'Sita - Economia (Barão)': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO, 'function': 'Barão'},
    'Sita - Economia (Baronesa)': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO, 'function': 'Baronesa'},
    'Sita - Economia (Vendedor)': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'function': 'Vendedor'},
    'Sita - Economia (Associado)': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'function': 'Associado'},

    # Sedam
    'Sedam - Armamento (Funcionario)': {'rarity': RaridadesPesos.RARO, 'color': Colors.VERDE, 'function': 'Funcionario'},
    'Sedam - Armamento (Dedo: Dedão)': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO, 'function': 'Dedo: Dedão'},
    'Sedam - Armamento (Dedo: Indicador)': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO, 'function': 'Dedo: Indicador'},
    'Sedam - Armamento (Dedo: Meio)': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO, 'function': 'Dedo: Meio'},
    'Sedam - Armamento (Dedo: Anelar)': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO, 'function': 'Dedo: Anelar'},
    'Sedam - Armamento (Dedo: Mindinho)': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO, 'function': 'Dedo: Mindinho'},
    'Sedam - Armamento (Associado)': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'function': 'Associado'},

    # Otte
    'Otte - Biblioteca (Funcionario)': {'rarity': RaridadesPesos.RARO, 'color': Colors.VERDE, 'function': 'Funcionario'},
    'Otte - Biblioteca (Pesquisador)': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'function': 'Pesquisador'},
    'Otte - Biblioteca (Professor)': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO, 'function': 'Professor'},
    'Otte - Biblioteca (Associado)': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'function': 'Associado'},

    # Nau
    'Nau - Entretenimento (Funcionario)': {'rarity': RaridadesPesos.RARO, 'color': Colors.VERDE, 'function': 'Funcionario'},
    'Nau - Entretenimento (Palhaço)': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO, 'function': 'Palhaço'},
    'Nau - Entretenimento (Associado)': {'rarity': RaridadesPesos.EPICO, 'color': Colors.ROXO, 'function': 'Associado'},

    # Deg
    'Deg - Conselho (Funcionario)': {'rarity': RaridadesPesos.RARO, 'color': Colors.VERDE, 'function': 'Funcionario'},
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
    'Maldição 1': {'rarity': RaridadesPesos.COMUM, 'color': Colors.CIANO},  # Cinza
    'Maldição 2': {'rarity': RaridadesPesos.COMUM, 'color': Colors.CIANO},  # Roxo
    'Maldição 3': {'rarity': RaridadesPesos.LENDARIO, 'color': Colors.AMARELO}  # Preto
}

# Dicionário para mapear opções de comando para seus respectivos dicionários de opções
OPTION_CATEGORIES = {
    'grupo': GROUP_OPTIONS,
    'poderes': POWERS_OPTIONS,
    'maldicoes': CURSES_OPTIONS
}

# Lista de todos os comandos disponíveis para sugestões
AVAILABLE_COMMANDS = ['roll', 'help_roll']

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
    
    embed.set_footer(text=f"Solicitado por {ctx.author.display_name}")
    
    await ctx.send(embed=embed)

# Executa o bot
if __name__ == '__main__':
    bot.run(TOKEN)