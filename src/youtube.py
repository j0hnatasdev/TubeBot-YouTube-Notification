import requests
import re
import json
from datetime import datetime
from urllib.parse import urlparse, parse_qs

class YouTubeScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
        
    def get_channel_info(self, channel_url):
        """Obtém informações do canal do YouTube"""
        try:
            print(f"Processando URL: {channel_url}")
            
            # Normaliza a URL do canal para a aba de vídeos
            if '@' in channel_url:
                username = channel_url.split('@')[1].split('/')[0]
                channel_url = f"https://www.youtube.com/@{username}/videos"
            elif not channel_url.endswith('/videos'):
                channel_url = f"{channel_url}/videos"
                
            print(f"URL normalizada: {channel_url}")
            
            # Faz a requisição inicial
            response = requests.get(channel_url, headers=self.headers)
            response.raise_for_status()
            
            # Procura pelo ID do canal
            channel_id_match = re.search(r'"channelId":"([^"]+)"', response.text)
            if not channel_id_match:
                print("Não foi possível encontrar o ID do canal")
                return None
                
            channel_id = channel_id_match.group(1)
            print(f"ID do canal encontrado: {channel_id}")
            
            # Faz uma requisição para a API não oficial
            api_url = f"https://www.youtube.com/channel/{channel_id}/videos"
            response = requests.get(api_url, headers=self.headers)
            response.raise_for_status()
            
            # Procura pelo vídeo mais recente
            video_id_match = re.search(r'"videoId":"([^"]+)"', response.text)
            if not video_id_match:
                print("Não foi possível encontrar o ID do vídeo")
                return None
                
            video_id = video_id_match.group(1)
            print(f"ID do vídeo encontrado: {video_id}")
            
            # Obtém informações do vídeo
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            video_response = requests.get(video_url, headers=self.headers)
            video_response.raise_for_status()
            
            # Extrai informações do vídeo
            title_match = re.search(r'"title":"([^"]+)"', video_response.text)
            channel_name_match = re.search(r'"channelName":"([^"]+)"', video_response.text)
            
            if not title_match or not channel_name_match:
                print("Não foi possível extrair título ou nome do canal")
                return None
                
            video_title = title_match.group(1).replace('\\u0026', '&')
            channel_name = channel_name_match.group(1)
            thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
            
            print(f"Vídeo encontrado: {video_title}")
            
            return {
                'video_url': video_url,
                'video_title': video_title,
                'thumbnail_url': thumbnail_url,
                'channel_name': channel_name,
                'published_text': "Publicado agora mesmo"
            }
            
        except Exception as e:
            print(f"Erro ao obter informações do canal: {str(e)}")
            return None
            
    def _extract_channel_id(self, url):
        """Extrai o ID do canal da URL"""
        try:
            # Tenta obter o ID do canal diretamente da URL
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            # Procura pelo ID do canal no HTML
            channel_id_match = re.search(r'"channelId":"([^"]+)"', response.text)
            if channel_id_match:
                return channel_id_match.group(1)
                
            # Se não encontrar, tenta extrair do formato @username
            username_match = re.search(r'@([^/]+)', url)
            if username_match:
                username = username_match.group(1)
                # Faz uma requisição para obter o ID do canal
                response = requests.get(f"https://www.youtube.com/@{username}", headers=self.headers)
                response.raise_for_status()
                channel_id_match = re.search(r'"channelId":"([^"]+)"', response.text)
                if channel_id_match:
                    return channel_id_match.group(1)
                    
            return None
        except Exception as e:
            print(f"Erro ao extrair ID do canal: {str(e)}")
            return None 