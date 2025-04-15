# Bot de Rolagens para Discord

Um bot para Discord que permite aos usuários obter famílias, poderes e maldições aleatórias com diferentes raridades e categorias.

## Funcionalidades

- Rolagem para famílias aleatórias (Uzumaki, Uchiha, Kobayashi)
- Rolagem para poderes aleatórios com diferentes categorias (Elementos, Objetos, Animais, Adjetivos, Conceitos abstratos, Verbos)
- Rolagem para maldições aleatórias com diferentes raridades
- Mensagens incorporadas bonitas com código de cores baseado na raridade

## Pré-requisitos

- Python 3.10 ou superior

## Instalação

1. Clone este repositório ou baixe o código fonte

2. Instale as dependências necessárias:

```bash
python -m venv .venv
.venv/scripts/activate
pip install -r requirements.txt
```

## Configuração

1. Crie um arquivo `.env` no diretório raiz do projeto
2. Adicione seu token de bot do Discord ao arquivo `.env`:

```
DISCORD_TOKEN="SEU_TOKEN_DE_BOT_DO_DISCORD"
PREFIXO="!"
```

Você pode usar o arquivo `.env.example` fornecido como modelo.

## Executando o Bot

Execute o bot usando o seguinte comando:

```bash
python bot.py
```

Se tudo estiver configurado corretamente, você deverá ver uma mensagem no console informando que seu bot se conectou ao Discord.

## Uso

O bot responde aos seguintes comandos:

- `!roll grupo` - Rolagem para um grupo aleatório
- `!roll poderes` - Rolagem para um poder aleatório
- `!roll maldicoes` - Rolagem para uma maldição aleatória
- `!wiki <item>` - Consulta informações detalhadas sobre um item específico
- `!help_roll` - Exibe informações de ajuda sobre os comandos

## Licença

Este projeto é de código aberto e disponível sob a [Licença CC0-1.0](https://choosealicense.com/licenses/cc0-1.0/).