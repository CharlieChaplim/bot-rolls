import os
import random
import discord
import difflib
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIXO = os.getenv('PREFIXO')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIXO, intents=intents, case_insensitive=True, help_command=None)

# Define as opções e suas raridades para cada categoria
FAMILY_OPTIONS = {
    'Uzumaki': {'rarity': 'Raro', 'weight': 30, 'color': 0xFF0000},  # Vermelho
    'Uchiha': {'rarity': 'Lendário', 'weight': 20, 'color': 0x000080},  # Azul Marinho
    'Kobayashi': {'rarity': 'Comum', 'weight': 70, 'color': 0x008000}  # Verde
}

POWERS_OPTIONS = {
    # Elementos
    'Fogo': {'rarity': 'Mítico', 'weight': 10, 'color': 0xa200ff, 'category': 'Elementos'},
    'Gelo': {'rarity': 'Mítico', 'weight': 10, 'color': 0xa200ff, 'category': 'Elementos'},
    'Água': {'rarity': 'Lendário', 'weight': 5, 'color': 0xffd000, 'category': 'Elementos'},
    'Fumaça': {'rarity': 'Raro', 'weight': 30, 'color': 0x38ff45, 'category': 'Elementos'},
    'Areia': {'rarity': 'Lendário', 'weight': 5, 'color': 0xffd000, 'category': 'Elementos'},
    'Raio': {'rarity': 'Mítico', 'weight': 10, 'color': 0xa200ff, 'category': 'Elementos'},
    'Madeira': {'rarity': 'Comum', 'weight': 55, 'color': 0x1ce5ff, 'category': 'Elementos'},
    'Cristal': {'rarity': 'Comum', 'weight': 55, 'color': 0x1ce5ff, 'category': 'Elementos'},
    'Rosa': {'rarity': 'Raro', 'weight': 30, 'color': 0x38ff45, 'category': 'Elementos'},
    'Ferro': {'rarity': 'Raro', 'weight': 30, 'color': 0x38ff45, 'category': 'Elementos'},
    'Mel': {'rarity': 'Mítico', 'weight': 10, 'color': 0xa200ff, 'category': 'Elementos'},
    'Vidro': {'rarity': 'Raro', 'weight': 30, 'color': 0x38ff45, 'category': 'Elementos'},
    'Gasolina': {'rarity': 'Raro', 'weight': 30, 'color': 0x38ff45, 'category': 'Elementos'},
    'Pólvora': {'rarity': 'Mítico', 'weight': 10, 'color': 0xa200ff, 'category': 'Elementos'},
    'Vácuo': {'rarity': 'Mítico', 'weight': 10, 'color': 0xa200ff, 'category': 'Elementos'},
    'Sangue': {'rarity': 'Lendário', 'weight': 5, 'color': 0xffd000, 'category': 'Elementos'},

    # Objetos
    'Relógio': {'rarity': 'Raro', 'weight': 30, 'color': 0x38ff45, 'category': 'Objetos'},
    'Zweihander': {'rarity': 'Raro', 'weight': 30, 'color': 0x38ff45, 'category': 'Objetos'},
    'Café': {'rarity': 'Comum', 'weight': 55, 'color': 0x1ce5ff, 'category': 'Objetos'},
    'Vela': {'rarity': 'Mítico', 'weight': 10, 'color': 0xa200ff, 'category': 'Objetos'},
    'Papel': {'rarity': 'Mítico', 'weight': 10, 'color': 0xa200ff, 'category': 'Objetos'},
    'Tinta': {'rarity': 'Lendário', 'weight': 5, 'color': 0xffd000, 'category': 'Objetos'},
    'Trompete': {'rarity': 'Raro', 'weight': 30, 'color': 0x38ff45, 'category': 'Objetos'},
    'Porta': {'rarity': 'Mítico', 'weight': 10, 'color': 0xa200ff, 'category': 'Objetos'},
    'Lixo': {'rarity': 'Raro', 'weight': 30, 'color': 0x38ff45, 'category': 'Objetos'},
    'Argila': {'rarity': 'Raro', 'weight': 30, 'color': 0x38ff45, 'category': 'Objetos'},
    'Lâmina': {'rarity': 'Lendário', 'weight': 5, 'color': 0xffd000, 'category': 'Objetos'},
    'Prego': {'rarity': 'Comum', 'weight': 55, 'color': 0x1ce5ff, 'category': 'Objetos'},
    'Bússola': {'rarity': 'Raro', 'weight': 30, 'color': 0x38ff45, 'category': 'Objetos'},
    'Carta': {'rarity': 'Comum', 'weight': 55, 'color': 0x1ce5ff, 'category': 'Objetos'},
    'Machete': {'rarity': 'Raro', 'weight': 30, 'color': 0x38ff45, 'category': 'Objetos'},
    'Sino': {'rarity': 'Raro', 'weight': 30, 'color': 0x38ff45, 'category': 'Objetos'},

    # Animais
    'Canino': {'rarity': 'Comum', 'weight': 55, 'color': 0x1ce5ff, 'category': 'Animais'},
    'Raposa': {'rarity': 'Comum', 'weight': 55, 'color': 0x1ce5ff, 'category': 'Animais'},
    'Inseto': {'rarity': 'Lendário', 'weight': 5, 'color': 0xffd000, 'category': 'Animais'},
    'Peixe': {'rarity': 'Raro', 'weight': 30, 'color': 0x38ff45, 'category': 'Animais'},
    'Anfíbio': {'rarity': 'Comum', 'weight': 55, 'color': 0x1ce5ff, 'category': 'Animais'},
    'Ave': {'rarity': 'Raro', 'weight': 30, 'color': 0x38ff45, 'category': 'Animais'},
    'Réptil': {'rarity': 'Mítico', 'weight': 10, 'color': 0xa200ff, 'category': 'Animais'},
    'Touro/Vaca': {'rarity': 'Lendário', 'weight': 5, 'color': 0xffd000, 'category': 'Animais'},
    'Equino': {'rarity': 'Mítico', 'weight': 10, 'color': 0xa200ff, 'category': 'Animais'},
    'Aracnídeo': {'rarity': 'Mítico', 'weight': 10, 'color': 0xa200ff, 'category': 'Animais'},
    'Canguru': {'rarity': 'Comum', 'weight': 55, 'color': 0x1ce5ff, 'category': 'Animais'},
    'Dragão': {'rarity': 'Lendário', 'weight': 5, 'color': 0xffd000, 'category': 'Animais'},
    'Leprechaum': {'rarity': 'Lendário', 'weight': 5, 'color': 0xffd000, 'category': 'Animais'},  # Criatura mágica

    # Adjetivos
    'Sorte': {'rarity': 'Lendário', 'weight': 5, 'color': 0xffd000, 'category': 'Adjetivos'},
    'Beleza': {'rarity': 'Mítico', 'weight': 10, 'color': 0xa200ff, 'category': 'Adjetivos'},
    'Rapidez': {'rarity': 'Mítico', 'weight': 10, 'color': 0xa200ff, 'category': 'Adjetivos'},
    'Força': {'rarity': 'Raro', 'weight': 30, 'color': 0x38ff45, 'category': 'Adjetivos'},
    'Carisma': {'rarity': 'Lendário', 'weight': 5, 'color': 0xffd000, 'category': 'Adjetivos'},
    'Inteligência': {'rarity': 'Lendário', 'weight': 5, 'color': 0xffd000, 'category': 'Adjetivos'},
    'Dureza': {'rarity': 'Raro', 'weight': 30, 'color': 0x38ff45, 'category': 'Adjetivos'},
    'Resistência': {'rarity': 'Mítico', 'weight': 10, 'color': 0xa200ff, 'category': 'Adjetivos'},
    'Nostalgia': {'rarity': 'Comum', 'weight': 55, 'color': 0x1ce5ff, 'category': 'Adjetivos'},
    'Liso': {'rarity': 'Comum', 'weight': 55, 'color': 0x1ce5ff, 'category': 'Adjetivos'},
    'Preto': {'rarity': 'Raro', 'weight': 30, 'color': 0x38ff45, 'category': 'Adjetivos'},
    'Tamanho': {'rarity': 'Mítico', 'weight': 10, 'color': 0xa200ff, 'category': 'Adjetivos'},

    # Abstratos
    'Felicidade': {'rarity': 'Raro', 'weight': 30, 'color': 0x38ff45, 'category': 'Abstratos'},
    'Dor': {'rarity': 'Lendário', 'weight': 5, 'color': 0xffd000, 'category': 'Abstratos'},
    'Som': {'rarity': 'Mítico', 'weight': 10, 'color': 0xa200ff, 'category': 'Abstratos'},
    'Eletromagnetismo': {'rarity': 'Lendário', 'weight': 5, 'color': 0xffd000, 'category': 'Abstratos'},
    'Gravidade': {'rarity': 'Mítico', 'weight': 10, 'color': 0xa200ff, 'category': 'Abstratos'},
    'Tempo (Musical)': {'rarity': 'Mítico', 'weight': 10, 'color': 0xa200ff, 'category': 'Abstratos'},
    'Atrito': {'rarity': 'Lendário', 'weight': 5, 'color': 0xffd000, 'category': 'Abstratos'},
    'Sonho': {'rarity': 'Raro', 'weight': 30, 'color': 0x38ff45, 'category': 'Abstratos'},
    'Lag': {'rarity': 'Mítico', 'weight': 10, 'color': 0xa200ff, 'category': 'Abstratos'},
    'Ressonância': {'rarity': 'Lendário', 'weight': 5, 'color': 0xffd000, 'category': 'Abstratos'},
    'Retorno': {'rarity': 'Mítico', 'weight': 10, 'color': 0xa200ff, 'category': 'Abstratos'},
    'Soma': {'rarity': 'Mítico', 'weight': 10, 'color': 0xa200ff, 'category': 'Abstratos'},
    'Monarca': {'rarity': 'Lendário', 'weight': 5, 'color': 0xffd000, 'category': 'Abstratos'},  # Conceito abstrato

    # Verbos
    'Golpear': {'rarity': 'Comum', 'weight': 55, 'color': 0x1ce5ff, 'category': 'Verbos'},
    'Produzir': {'rarity': 'Raro', 'weight': 30, 'color': 0x38ff45, 'category': 'Verbos'},
    'Cultivar': {'rarity': 'Raro', 'weight': 30, 'color': 0x38ff45, 'category': 'Verbos'},
    'Roubar': {'rarity': 'Lendário', 'weight': 5, 'color': 0xffd000, 'category': 'Verbos'},
    'Curar': {'rarity': 'Lendário', 'weight': 5, 'color': 0xffd000, 'category': 'Verbos'},
    'Brutalizar': {'rarity': 'Comum', 'weight': 55, 'color': 0x1ce5ff, 'category': 'Verbos'},
    'Dançar': {'rarity': 'Raro', 'weight': 30, 'color': 0x38ff45, 'category': 'Verbos'},
    'Planejar': {'rarity': 'Raro', 'weight': 30, 'color': 0x38ff45, 'category': 'Verbos'},
    'Acertar': {'rarity': 'Mítico', 'weight': 10, 'color': 0xa200ff, 'category': 'Verbos'},
    'Apodrecer': {'rarity': 'Lendário', 'weight': 5, 'color': 0xffd000, 'category': 'Verbos'},
    'Iluminar': {'rarity': 'Raro', 'weight': 30, 'color': 0x38ff45, 'category': 'Verbos'},
    'Teleportar': {'rarity': 'Mítico', 'weight': 10, 'color': 0xa200ff, 'category': 'Verbos'},
    'Caçar': {'rarity': 'Raro', 'weight': 30, 'color': 0x38ff45, 'category': 'Verbos'},
    'Cirurgia': {'rarity': 'Mítico', 'weight': 10, 'color': 0xa200ff, 'category': 'Verbos'},
    'Cantar': {'rarity': 'Comum', 'weight': 55, 'color': 0x1ce5ff, 'category': 'Verbos'},
    'Impulsionar': {'rarity': 'Mítico', 'weight': 10, 'color': 0xa200ff, 'category': 'Verbos'},
}



CURSES_OPTIONS = {
    'Maldição 1': {'rarity': 'Comum', 'weight': 55, 'color': 0x808080},  # Cinza
    'Maldição 2': {'rarity': 'Incomum', 'weight': 30, 'color': 0x800080},  # Roxo
    'Maldição 3': {'rarity': 'Lendário', 'weight': 20, 'color': 0x000000}  # Preto
}

# Dicionário para mapear opções de comando para seus respectivos dicionários de opções
OPTION_CATEGORIES = {
    'familia': FAMILY_OPTIONS,
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
        await ctx.send('Por favor, especifique uma categoria para rolar: `!roll <opção>` (familia, poderes, maldicoes)')
        return
    
    option = option.lower()
    
    if option not in OPTION_CATEGORIES:
        await ctx.send('Categoria inválida. Categorias disponíveis: familia, poderes, maldicoes')
        return
    
    options_dict = OPTION_CATEGORIES[option]
    
    # Obtém as opções e seus pesos
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
    
    embed.add_field(name="Raridade", value=result_data['rarity'], inline=False)
    
    # Adiciona o campo de categoria apenas para poderes
    if option == 'poderes' and 'category' in result_data:
        embed.add_field(name="Categoria", value=result_data['category'], inline=False)
    
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
        value="`familia` - Role para uma família (Uzumaki, Uchiha, Kobayashi)\n"
              "`poderes` - Role para um poder (Gelo, Fogo, Trovão)\n"
              "`maldicoes` - Role para uma maldição (Maldição 1, Maldição 2, Maldição 3)",
        inline=False
    )
    
    embed.set_footer(text=f"Solicitado por {ctx.author.display_name}")
    
    await ctx.send(embed=embed)

# Executa o bot
if __name__ == '__main__':
    bot.run(TOKEN)