import discord
from discord.ext import commands, tasks
from .config import Config
from .youtube_api import YouTubeAPI
from .utils import create_embed

class YouTubeBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        
        # Inicializa componentes
        self.config = Config()
        self.youtube = YouTubeAPI()
        self.temp_configs = {}
        self.setup_channels = {}  # Armazena os canais onde o bot foi configurado
        
        # Carrega os comandos
        self.load_commands()
        
    @tasks.loop(seconds=14400)  # Verifica a cada 4 horas
    async def check_new_videos(self):
        for server_id, config in self.config.get_all_configs().items():
            try:
                # Primeiro tenta obter o vídeo mais recente
                channel_info = self.youtube.get_channel_info(
                    config['youtube_channel_url'],
                    include_shorts=config.get('include_shorts', False)
                )

                # Se não houver vídeo novo ou se o vídeo já foi enviado, tenta obter um vídeo antigo
                if not channel_info or (channel_info and channel_info.get('already_sent', False)):
                    channel_info = self.youtube.get_old_video(
                        config['youtube_channel_url'],
                        include_shorts=config.get('include_shorts', False)
                    )

                if channel_info:  # Se encontrou qualquer vídeo (novo ou antigo)
                    # Obtém o canal do Discord
                    channel = self.get_channel(config['notification_channel'])
                    if channel:
                        # Define o título baseado se é um novo vídeo ou não
                        status = "🎥 Novo Vídeo!" if channel_info.get('is_new_video', False) else "📺 Vídeo Anterior"
                        
                        # Cria o embed bonito
                        embed = discord.Embed(
                            url=channel_info['video_url'],
                            color=discord.Color.red() if channel_info.get('is_new_video', False) else discord.Color.blue()
                        )
                        
                        # Adiciona a thumbnail como imagem principal
                        embed.set_image(url=channel_info['thumbnail_url'])
                        
                        # Adiciona o autor (canal do YouTube) com logo
                        embed.set_author(
                            name=channel_info['channel_name'],
                            url=f"https://www.youtube.com/@{channel_info['channel_name'].replace(' ', '')}",
                            icon_url=channel_info['channel_icon']
                        )
                        
                        # Adiciona o título do vídeo com link
                        embed.add_field(
                            name="",
                            value=f"[{channel_info['video_title']}]({channel_info['video_url']})",
                            inline=False
                        )
                        
                        # Adiciona informações do vídeo
                        embed.add_field(
                            name="",
                            value=f"**{status}** • {channel_info['published_text']}",
                            inline=False
                        )
                        
                        # Adiciona o footer apenas com o ícone
                        embed.set_footer(
                            text="",
                            icon_url="https://www.youtube.com/favicon.ico"
                        )
                        
                        # Envia apenas o embed
                        await channel.send(embed=embed)
                        
            except Exception as e:
                print(f"Erro ao verificar vídeos para o servidor {server_id}: {str(e)}")
        
    def load_commands(self):
        """Carrega todos os comandos do bot"""
        @self.event
        async def on_ready():
            print(f'{self.user} está online!')
            self.check_new_videos.start()
            
        @self.command(name='start')
        async def start(ctx):
            """Inicia o processo de configuração do bot"""
            server_id = str(ctx.guild.id)
            
            # Verifica se o bot já está configurado neste servidor
            if server_id in self.setup_channels:
                setup_channel = self.get_channel(self.setup_channels[server_id])
                if setup_channel and ctx.channel.id != setup_channel.id:
                    await ctx.send(f"❌ O comando `!start` só pode ser usado no canal {setup_channel.mention}")
                    return
            
            # Inicializa a configuração temporária
            self.temp_configs[server_id] = {
                'step': 1,
                'notification_channel': None,
                'youtube_channel_url': None,
                'include_shorts': None
            }
            
            # Armazena o canal onde o comando foi iniciado
            self.setup_channels[server_id] = ctx.channel.id
            
            embed = discord.Embed(
                title="🎮 Configuração do Bot",
                description="Bem-vindo ao assistente de configuração do Bot de Notificações do YouTube!",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="📝 Como Funciona",
                value="Vou te guiar passo a passo na configuração do bot. Em cada etapa, você precisará fornecer as informações solicitadas.",
                inline=False
            )
            
            embed.add_field(
                name="1️⃣ Canal de Notificações",
                value="Primeiro, mencione o canal onde você quer receber as notificações.\nExemplo: `#notificações`",
                inline=False
            )
            
            embed.add_field(
                name="⚠️ Importante",
                value="• Você pode cancelar a configuração a qualquer momento digitando `!cancel`\n• O comando `!start` só pode ser usado neste canal",
                inline=False
            )
            
            embed.set_footer(
                text="",
                icon_url="https://www.youtube.com/favicon.ico"
            )
            
            await ctx.send(embed=embed)
            
        @self.command(name='cancel')
        async def cancel(ctx):
            """Cancela o processo de configuração"""
            server_id = str(ctx.guild.id)
            
            if server_id in self.temp_configs:
                del self.temp_configs[server_id]
                if server_id in self.setup_channels:
                    del self.setup_channels[server_id]
                
                embed = discord.Embed(
                    title="❌ Configuração Cancelada",
                    description="O processo de configuração foi cancelado. Use `!start` para começar novamente.",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
            else:
                await ctx.send("❌ Não há nenhuma configuração em andamento.")
            
        @self.event
        async def on_message(message):
            if message.author.bot:
                return
                
            server_id = str(message.guild.id) if message.guild else None
            
            if server_id and server_id in self.temp_configs:
                config = self.temp_configs[server_id]
                
                if config['step'] == 1:
                    # Verifica se é uma menção de canal
                    if message.channel_mentions:
                        channel = message.channel_mentions[0]
                        config['notification_channel'] = channel.id
                        config['step'] = 2
                        
                        embed = discord.Embed(
                            title="✅ Canal de Notificações Configurado!",
                            description="Ótimo! Agora vamos configurar o canal do YouTube.",
                            color=discord.Color.green()
                        )
                        embed.add_field(
                            name="2️⃣ Canal do YouTube",
                            value="Envie a URL do canal do YouTube que você quer monitorar.\nExemplo: `https://www.youtube.com/@canal`",
                            inline=False
                        )
                        embed.add_field(
                            name="💡 Dica",
                            value="Você pode usar qualquer formato de URL do YouTube:\n• `https://www.youtube.com/@canal`\n• `https://www.youtube.com/c/canal`\n• `https://www.youtube.com/channel/ID`",
                            inline=False
                        )
                        embed.set_footer(
                            text="",
                            icon_url="https://www.youtube.com/favicon.ico"
                        )
                        
                        await message.channel.send(embed=embed)
                    else:
                        await message.channel.send("❌ Por favor, mencione um canal válido usando #.")
                        
                elif config['step'] == 2:
                    # Verifica se é uma URL do YouTube
                    if "youtube.com" in message.content or "youtu.be" in message.content:
                        channel_url = message.content.strip()
                        channel_info = self.youtube.get_channel_info(channel_url)
                        
                        if channel_info:
                            config['youtube_channel_url'] = channel_url
                            config['step'] = 3
                            
                            embed = discord.Embed(
                                title="✅ Canal do YouTube Configurado!",
                                description="Perfeito! Agora vamos escolher o tipo de conteúdo.",
                                color=discord.Color.green()
                            )
                            embed.add_field(
                                name="3️⃣ Tipo de Conteúdo",
                                value="Escolha o tipo de conteúdo que você quer receber:",
                                inline=False
                            )
                            embed.add_field(
                                name="1️⃣ Apenas Vídeos",
                                value="Você receberá notificações apenas de vídeos normais (sem shorts)",
                                inline=True
                            )
                            embed.add_field(
                                name="2️⃣ Vídeos e Shorts",
                                value="Você receberá notificações de vídeos normais e shorts",
                                inline=True
                            )
                            embed.set_footer(
                                text="",
                                icon_url="https://www.youtube.com/favicon.ico"
                            )
                            
                            await message.channel.send(embed=embed)
                        else:
                            await message.channel.send("❌ Não foi possível encontrar o canal do YouTube. Verifique a URL e tente novamente.")
                    else:
                        await message.channel.send("❌ Por favor, envie uma URL válida do YouTube.")
                        
                elif config['step'] == 3:
                    # Verifica a escolha do tipo de conteúdo
                    choice = message.content.strip()
                    if choice in ['1', '2']:
                        config['include_shorts'] = (choice == '2')
                        
                        # Salva a configuração final
                        self.config.save_server_config(server_id, {
                            'notification_channel': config['notification_channel'],
                            'youtube_channel_url': config['youtube_channel_url'],
                            'include_shorts': config['include_shorts']
                        })
                        
                        # Remove a configuração temporária
                        del self.temp_configs[server_id]
                        
                        embed = discord.Embed(
                            title="🎉 Configuração Concluída!",
                            description="O bot foi configurado com sucesso! Agora você receberá notificações de novos vídeos.",
                            color=discord.Color.green()
                        )
                        embed.add_field(
                            name="📢 Canal de Notificações",
                            value=f"<#{config['notification_channel']}>",
                            inline=True
                        )
                        embed.add_field(
                            name="🎥 Canal do YouTube",
                            value=config['youtube_channel_url'],
                            inline=True
                        )
                        embed.add_field(
                            name="📝 Tipo de Conteúdo",
                            value="Vídeos normais e shorts" if config['include_shorts'] else "Apenas vídeos normais",
                            inline=True
                        )
                        embed.add_field(
                            name="⚙️ Comandos Disponíveis",
                            value="• `!start` - Inicia a configuração do bot\n• `!cancel` - Cancela a configuração atual",
                            inline=False
                        )
                        embed.set_footer(
                            text="",
                            icon_url="https://www.youtube.com/favicon.ico"
                        )
                        
                        await message.channel.send(embed=embed)

                        # Faz uma verificação imediata após a configuração
                        try:
                            channel_info = self.youtube.get_channel_info(
                                config['youtube_channel_url'],
                                include_shorts=config['include_shorts']
                            )
                            if channel_info:  # Se encontrou qualquer vídeo (novo ou antigo)
                                # Obtém o canal do Discord
                                channel = self.get_channel(config['notification_channel'])
                                if channel:
                                    # Define o título baseado se é um novo vídeo ou não
                                    status = "🎥 Novo Vídeo!" if channel_info.get('is_new_video', False) else "📺 Vídeo Anterior"
                                    
                                    # Cria o embed bonito
                                    embed = discord.Embed(
                                        url=channel_info['video_url'],
                                        color=discord.Color.red() if channel_info.get('is_new_video', False) else discord.Color.blue()
                                    )
                                    
                                    # Adiciona a thumbnail como imagem principal
                                    embed.set_image(url=channel_info['thumbnail_url'])
                                    
                                    # Adiciona o autor (canal do YouTube) com logo
                                    embed.set_author(
                                        name=channel_info['channel_name'],
                                        url=f"https://www.youtube.com/@{channel_info['channel_name'].replace(' ', '')}",
                                        icon_url=channel_info['channel_icon']
                                    )
                                    
                                    # Adiciona o título do vídeo com link
                                    embed.add_field(
                                        name="",
                                        value=f"[{channel_info['video_title']}]({channel_info['video_url']})",
                                        inline=False
                                    )
                                    
                                    # Adiciona informações do vídeo
                                    embed.add_field(
                                        name="",
                                        value=f"**{status}** • {channel_info['published_text']}",
                                        inline=False
                                    )
                                    
                                    # Adiciona o footer apenas com o ícone
                                    embed.set_footer(
                                        text="",
                                        icon_url="https://www.youtube.com/favicon.ico"
                                    )
                                    
                                    # Envia apenas o embed
                                    await channel.send(embed=embed)
                        except Exception as e:
                            print(f"Erro ao verificar vídeos após configuração: {str(e)}")
                    else:
                        await message.channel.send("❌ Por favor, digite `1` para vídeos normais ou `2` para vídeos normais e shorts.")
            
            await self.process_commands(message) 