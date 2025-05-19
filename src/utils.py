import discord

def create_embed(title, description="", color=discord.Color.blue(), url=None):
    """Cria um embed do Discord com configurações padrão"""
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        url=url
    )
    return embed 