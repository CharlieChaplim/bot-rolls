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

# Definição dos pesos totais por raridade
RARITY_WEIGHTS = {
    'Mítico': 17,
    'Lendário': 8,
    'Raro': 27,
    'Comum': 48,
}

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
        if rarity in RARITY_WEIGHTS and count > 0:
            rarity_weight_per_item[rarity] = RARITY_WEIGHTS[rarity] / count
        else:
            # Valor padrão caso a raridade não esteja definida
            rarity_weight_per_item[rarity] = 1
    
    # Aplica os pesos calculados a cada item
    for option, data in options_dict.items():
        rarity = data['rarity']
        data['weight'] = rarity_weight_per_item[rarity]
    
    return options_dict

# Define as opções e suas raridades para cada categoria
GROUP_OPTIONS = {
    'Nenhum': {'rarity': 'Comum', 'color': 0x1ce5ff, 'function': 'Neutro'},

    # Uno
    'Uno - Investigação (Funcionario)': {'rarity': 'Raro', 'color': 0x38ff45, 'function': 'Funcionario'},
    'Uno - Investigação (Olhos)': {'rarity': 'Lendário', 'color': 0xffd000, 'function': 'Olhos'},
    'Uno - Investigação (Ouvidos)': {'rarity': 'Mítico', 'color': 0xa200ff, 'function': 'Ouvidos'},
    'Uno - Investigação (Associado)': {'rarity': 'Mítico', 'color': 0xa200ff, 'function': 'Associado'},

    # Zwei
    'Zwei - Proteção (Funcionario)': {'rarity': 'Raro', 'color': 0x38ff45, 'function': 'Funcionario'},
    'Zwei - Proteção (Milicia)': {'rarity': 'Mítico', 'color': 0xa200ff, 'function': 'Milicia'},
    'Zwei - Proteção (Escudo)': {'rarity': 'Lendário', 'color': 0xffd000, 'function': 'Escudo'},
    'Zwei - Proteção (Associado)': {'rarity': 'Mítico', 'color': 0xa200ff, 'function': 'Associado'},

    # San
    'San - Transporte (Funcionario)': {'rarity': 'Raro', 'color': 0x38ff45, 'function': 'Funcionario'},
    'San - Transporte (Equipe de Limpeza)': {'rarity': 'Lendário', 'color': 0xffd000, 'function': 'Equipe de Limpeza'},
    'San - Transporte (Associado)': {'rarity': 'Mítico', 'color': 0xa200ff, 'function': 'Associado'},

    # Arba'a
    'Arba\'a - Assassinato (Funcionario)': {'rarity': 'Raro', 'color': 0x38ff45, 'function': 'Funcionario'},
    'Arba\'a - Assassinato (Padrinho)': {'rarity': 'Lendário', 'color': 0xffd000, 'function': 'Padrinho'},
    'Arba\'a - Assassinato (Madrinha)': {'rarity': 'Lendário', 'color': 0xffd000, 'function': 'Madrinha'},
    'Arba\'a - Assassinato (Associado)': {'rarity': 'Mítico', 'color': 0xa200ff, 'function': 'Associado'},

    # Cinq
    'Cinq - Justiça (Funcionario)': {'rarity': 'Raro', 'color': 0x38ff45, 'function': 'Funcionario'},
    'Cinq - Justiça (Juiz)': {'rarity': 'Lendário', 'color': 0xffd000, 'function': 'Juiz'},
    'Cinq - Justiça (Associado)': {'rarity': 'Mítico', 'color': 0xa200ff, 'function': 'Associado'},

    # Sita
    'Sita - Economia (Funcionario)': {'rarity': 'Raro', 'color': 0x38ff45, 'function': 'Funcionario'},
    'Sita - Economia (Barão)': {'rarity': 'Lendário', 'color': 0xffd000, 'function': 'Barão'},
    'Sita - Economia (Baronesa)': {'rarity': 'Lendário', 'color': 0xffd000, 'function': 'Baronesa'},
    'Sita - Economia (Vendedor)': {'rarity': 'Mítico', 'color': 0xa200ff, 'function': 'Vendedor'},
    'Sita - Economia (Associado)': {'rarity': 'Mítico', 'color': 0xa200ff, 'function': 'Associado'},

    # Sedam
    'Sedam - Armamento (Funcionario)': {'rarity': 'Raro', 'color': 0x38ff45, 'function': 'Funcionario'},
    'Sedam - Armamento (Dedo: Dedão)': {'rarity': 'Lendário', 'color': 0xffd000, 'function': 'Dedo: Dedão'},
    'Sedam - Armamento (Dedo: Indicador)': {'rarity': 'Lendário', 'color': 0xffd000, 'function': 'Dedo: Indicador'},
    'Sedam - Armamento (Dedo: Meio)': {'rarity': 'Lendário', 'color': 0xffd000, 'function': 'Dedo: Meio'},
    'Sedam - Armamento (Dedo: Anelar)': {'rarity': 'Lendário', 'color': 0xffd000, 'function': 'Dedo: Anelar'},
    'Sedam - Armamento (Dedo: Mindinho)': {'rarity': 'Lendário', 'color': 0xffd000, 'function': 'Dedo: Mindinho'},
    'Sedam - Armamento (Associado)': {'rarity': 'Mítico', 'color': 0xa200ff, 'function': 'Associado'},

    # Otte
    'Otte - Biblioteca (Funcionario)': {'rarity': 'Raro', 'color': 0x38ff45, 'function': 'Funcionario'},
    'Otte - Biblioteca (Pesquisador)': {'rarity': 'Mítico', 'color': 0xa200ff, 'function': 'Pesquisador'},
    'Otte - Biblioteca (Professor)': {'rarity': 'Lendário', 'color': 0xffd000, 'function': 'Professor'},
    'Otte - Biblioteca (Associado)': {'rarity': 'Mítico', 'color': 0xa200ff, 'function': 'Associado'},

    # Nau
    'Nau - Entretenimento (Funcionario)': {'rarity': 'Raro', 'color': 0x38ff45, 'function': 'Funcionario'},
    'Nau - Entretenimento (Palhaço)': {'rarity': 'Lendário', 'color': 0xffd000, 'function': 'Palhaço'},
    'Nau - Entretenimento (Associado)': {'rarity': 'Mítico', 'color': 0xa200ff, 'function': 'Associado'},

    # Deg
    'Deg - Conselho (Funcionario)': {'rarity': 'Raro', 'color': 0x38ff45, 'function': 'Funcionario'},
    'Deg - Conselho (Associado)': {'rarity': 'Mítico', 'color': 0xa200ff, 'function': 'Associado'},
}


POWERS_OPTIONS = {
    # Elementos
    'Fogo': {'rarity': 'Mítico', 'color': 0xa200ff, 'category': 'Elementos'},
    'Gelo': {'rarity': 'Mítico', 'color': 0xa200ff, 'category': 'Elementos'},
    'Água': {'rarity': 'Lendário', 'color': 0xffd000, 'category': 'Elementos'},
    'Fumaça': {'rarity': 'Raro', 'color': 0x38ff45, 'category': 'Elementos'},
    'Areia': {'rarity': 'Lendário', 'color': 0xffd000, 'category': 'Elementos'},
    'Raio': {'rarity': 'Mítico', 'color': 0xa200ff, 'category': 'Elementos'},
    'Madeira': {'rarity': 'Comum', 'color': 0x1ce5ff, 'category': 'Elementos'},
    'Cristal': {'rarity': 'Comum', 'color': 0x1ce5ff, 'category': 'Elementos'},
    'Rosa': {'rarity': 'Raro', 'color': 0x38ff45, 'category': 'Elementos'},
    'Ferro': {'rarity': 'Raro', 'color': 0x38ff45, 'category': 'Elementos'},
    'Mel': {'rarity': 'Mítico', 'color': 0xa200ff, 'category': 'Elementos'},
    'Vidro': {'rarity': 'Raro', 'color': 0x38ff45, 'category': 'Elementos'},
    'Gasolina': {'rarity': 'Raro', 'color': 0x38ff45, 'category': 'Elementos'},
    'Pólvora': {'rarity': 'Mítico', 'color': 0xa200ff, 'category': 'Elementos'},
    'Vácuo': {'rarity': 'Mítico', 'color': 0xa200ff, 'category': 'Elementos'},
    'Sangue': {'rarity': 'Lendário', 'color': 0xffd000, 'category': 'Elementos'},

    # Objetos
    'Relógio': {'rarity': 'Raro', 'color': 0x38ff45, 'category': 'Objetos'},
    'Zweihander': {'rarity': 'Raro', 'color': 0x38ff45, 'category': 'Objetos'},
    'Café': {'rarity': 'Comum', 'color': 0x1ce5ff, 'category': 'Objetos'},
    'Vela': {'rarity': 'Mítico', 'color': 0xa200ff, 'category': 'Objetos'},
    'Papel': {'rarity': 'Mítico', 'color': 0xa200ff, 'category': 'Objetos'},
    'Tinta': {'rarity': 'Lendário', 'color': 0xffd000, 'category': 'Objetos'},
    'Trompete': {'rarity': 'Raro', 'color': 0x38ff45, 'category': 'Objetos'},
    'Porta': {'rarity': 'Mítico', 'color': 0xa200ff, 'category': 'Objetos'},
    'Lixo': {'rarity': 'Raro', 'color': 0x38ff45, 'category': 'Objetos'},
    'Argila': {'rarity': 'Raro', 'color': 0x38ff45, 'category': 'Objetos'},
    'Lâmina': {'rarity': 'Lendário', 'color': 0xffd000, 'category': 'Objetos'},
    'Prego': {'rarity': 'Comum', 'color': 0x1ce5ff, 'category': 'Objetos'},
    'Bússola': {'rarity': 'Raro', 'color': 0x38ff45, 'category': 'Objetos'},
    'Carta': {'rarity': 'Comum', 'color': 0x1ce5ff, 'category': 'Objetos'},
    'Machete': {'rarity': 'Raro', 'color': 0x38ff45, 'category': 'Objetos'},
    'Sino': {'rarity': 'Raro', 'color': 0x38ff45, 'category': 'Objetos'},

    # Animais
    'Canino': {'rarity': 'Comum', 'color': 0x1ce5ff, 'category': 'Animais'},
    'Raposa': {'rarity': 'Comum', 'color': 0x1ce5ff, 'category': 'Animais'},
    'Inseto': {'rarity': 'Lendário', 'color': 0xffd000, 'category': 'Animais'},
    'Peixe': {'rarity': 'Raro', 'color': 0x38ff45, 'category': 'Animais'},
    'Anfíbio': {'rarity': 'Comum', 'color': 0x1ce5ff, 'category': 'Animais'},
    'Ave': {'rarity': 'Raro', 'color': 0x38ff45, 'category': 'Animais'},
    'Réptil': {'rarity': 'Mítico', 'color': 0xa200ff, 'category': 'Animais'},
    'Touro/Vaca': {'rarity': 'Lendário', 'color': 0xffd000, 'category': 'Animais'},
    'Equino': {'rarity': 'Mítico', 'color': 0xa200ff, 'category': 'Animais'},
    'Aracnídeo': {'rarity': 'Mítico', 'color': 0xa200ff, 'category': 'Animais'},
    'Canguru': {'rarity': 'Comum', 'color': 0x1ce5ff, 'category': 'Animais'},
    'Dragão': {'rarity': 'Lendário', 'color': 0xffd000, 'category': 'Animais'},
    'Leprechaum': {'rarity': 'Lendário', 'color': 0xffd000, 'category': 'Animais'},  # Criatura mágica

    # Adjetivos
    'Sorte': {'rarity': 'Lendário', 'color': 0xffd000, 'category': 'Adjetivos'},
    'Beleza': {'rarity': 'Mítico', 'color': 0xa200ff, 'category': 'Adjetivos'},
    'Rapidez': {'rarity': 'Mítico', 'color': 0xa200ff, 'category': 'Adjetivos'},
    'Força': {'rarity': 'Raro', 'color': 0x38ff45, 'category': 'Adjetivos'},
    'Carisma': {'rarity': 'Lendário', 'color': 0xffd000, 'category': 'Adjetivos'},
    'Inteligência': {'rarity': 'Lendário', 'color': 0xffd000, 'category': 'Adjetivos'},
    'Dureza': {'rarity': 'Raro', 'color': 0x38ff45, 'category': 'Adjetivos'},
    'Resistência': {'rarity': 'Mítico', 'color': 0xa200ff, 'category': 'Adjetivos'},
    'Nostalgia': {'rarity': 'Comum', 'color': 0x1ce5ff, 'category': 'Adjetivos'},
    'Liso': {'rarity': 'Comum', 'color': 0x1ce5ff, 'category': 'Adjetivos'},
    'Preto': {'rarity': 'Raro', 'color': 0x38ff45, 'category': 'Adjetivos'},
    'Tamanho': {'rarity': 'Mítico', 'color': 0xa200ff, 'category': 'Adjetivos'},

    # Abstratos
    'Felicidade': {'rarity': 'Raro', 'color': 0x38ff45, 'category': 'Abstratos'},
    'Dor': {'rarity': 'Lendário', 'color': 0xffd000, 'category': 'Abstratos'},
    'Som': {'rarity': 'Mítico', 'color': 0xa200ff, 'category': 'Abstratos'},
    'Eletromagnetismo': {'rarity': 'Lendário', 'color': 0xffd000, 'category': 'Abstratos'},
    'Gravidade': {'rarity': 'Mítico', 'color': 0xa200ff, 'category': 'Abstratos'},
    'Tempo (Musical)': {'rarity': 'Mítico', 'color': 0xa200ff, 'category': 'Abstratos'},
    'Atrito': {'rarity': 'Lendário', 'color': 0xffd000, 'category': 'Abstratos'},
    'Sonho': {'rarity': 'Raro', 'color': 0x38ff45, 'category': 'Abstratos'},
    'Lag': {'rarity': 'Mítico', 'color': 0xa200ff, 'category': 'Abstratos'},
    'Ressonância': {'rarity': 'Lendário', 'color': 0xffd000, 'category': 'Abstratos'},
    'Retorno': {'rarity': 'Mítico', 'color': 0xa200ff, 'category': 'Abstratos'},
    'Soma': {'rarity': 'Mítico', 'color': 0xa200ff, 'category': 'Abstratos'},
    'Monarca': {'rarity': 'Lendário', 'color': 0xffd000, 'category': 'Abstratos'},  # Conceito abstrato

    # Verbos
    'Golpear': {'rarity': 'Comum', 'color': 0x1ce5ff, 'category': 'Verbos'},
    'Produzir': {'rarity': 'Raro', 'color': 0x38ff45, 'category': 'Verbos'},
    'Cultivar': {'rarity': 'Raro', 'color': 0x38ff45, 'category': 'Verbos'},
    'Roubar': {'rarity': 'Lendário', 'color': 0xffd000, 'category': 'Verbos'},
    'Curar': {'rarity': 'Lendário', 'color': 0xffd000, 'category': 'Verbos'},
    'Brutalizar': {'rarity': 'Comum', 'color': 0x1ce5ff, 'category': 'Verbos'},
    'Dançar': {'rarity': 'Raro', 'color': 0x38ff45, 'category': 'Verbos'},
    'Planejar': {'rarity': 'Raro', 'color': 0x38ff45, 'category': 'Verbos'},
    'Acertar': {'rarity': 'Mítico', 'color': 0xa200ff, 'category': 'Verbos'},
    'Apodrecer': {'rarity': 'Lendário', 'color': 0xffd000, 'category': 'Verbos'},
    'Iluminar': {'rarity': 'Raro', 'color': 0x38ff45, 'category': 'Verbos'},
    'Teleportar': {'rarity': 'Mítico', 'color': 0xa200ff, 'category': 'Verbos'},
    'Caçar': {'rarity': 'Raro', 'color': 0x38ff45, 'category': 'Verbos'},
    'Cirurgia': {'rarity': 'Mítico', 'color': 0xa200ff, 'category': 'Verbos'},
    'Cantar': {'rarity': 'Comum', 'color': 0x1ce5ff, 'category': 'Verbos'},
    'Impulsionar': {'rarity': 'Mítico', 'color': 0xa200ff, 'category': 'Verbos'},
}



CURSES_OPTIONS = {
    'Maldição 1': {'rarity': 'Comum', 'color': 0x808080},  # Cinza
    'Maldição 2': {'rarity': 'Incomum', 'color': 0x800080},  # Roxo
    'Maldição 3': {'rarity': 'Lendário', 'color': 0x000000}  # Preto
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
    
    embed.add_field(name="Raridade", value=result_data['rarity'], inline=False)
    
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