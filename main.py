"""
TubeBot de Notificação do YouTube
Desenvolvido por Prolldevs - https://developers.prollabe.com
"""

import os
from dotenv import load_dotenv
from src.bot import YouTubeBot

def main():
    # Carrega as variáveis de ambiente
    load_dotenv()
    
    # Inicializa o bot
    bot = YouTubeBot()
    
    # Inicia o bot
    bot.run(os.getenv('DISCORD_TOKEN'))

if __name__ == "__main__":
    main() 