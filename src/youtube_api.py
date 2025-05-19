from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
from datetime import datetime, timedelta
import json

class YouTubeAPI:
    def __init__(self):
        self.api_key = os.getenv('YOUTUBE_API_KEY')
        if not self.api_key:
            raise ValueError("YouTube API key não encontrada. Configure a variável YOUTUBE_API_KEY no arquivo .env")
            
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        self.cache_file = 'data/youtube_cache.json'
        self._load_cache()
        
    def _load_cache(self):
        """Carrega o cache de vídeos do arquivo"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    self.video_cache = json.load(f)
            else:
                self.video_cache = {}
                os.makedirs('data', exist_ok=True)
                self._save_cache()
        except Exception as e:
            print(f"Erro ao carregar cache: {str(e)}")
            self.video_cache = {}
            
    def _save_cache(self):
        """Salva o cache de vídeos no arquivo"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.video_cache, f)
        except Exception as e:
            print(f"Erro ao salvar cache: {str(e)}")
            
    def get_channel_info(self, channel_url, include_shorts=False):
        """Obtém informações do canal e do último vídeo usando a API do YouTube"""
        try:
            # Extrai o ID do canal da URL
            channel_id = self._extract_channel_id(channel_url)
            if not channel_id:
                print(f"Não foi possível extrair o ID do canal da URL: {channel_url}")
                return None

            # Obtém informações do canal
            channel_response = self.youtube.channels().list(
                part='snippet,contentDetails',
                id=channel_id
            ).execute()

            if not channel_response['items']:
                print(f"Canal não encontrado: {channel_id}")
                return None

            channel = channel_response['items'][0]
            channel_name = channel['snippet']['title']
            channel_icon = channel['snippet']['thumbnails']['default']['url']
            uploads_playlist_id = channel['contentDetails']['relatedPlaylists']['uploads']

            # Obtém os vídeos do canal
            playlist_response = self.youtube.playlistItems().list(
                part='snippet',
                playlistId=uploads_playlist_id,
                maxResults=50
            ).execute()

            if not playlist_response['items']:
                print(f"Nenhum vídeo encontrado para o canal: {channel_name}")
                return None

            # Procura o primeiro vídeo que não seja shorts (se include_shorts for False)
            video = None
            for item in playlist_response['items']:
                video_title = item['snippet']['title']
                video_description = item['snippet'].get('description', '')
                
                if include_shorts or ('#shorts' not in video_title.lower() and '#shorts' not in video_description.lower()):
                    video = item
                    break

            if not video:
                print(f"Nenhum vídeo encontrado que atenda aos critérios para o canal: {channel_name}")
                return None

            # Obtém detalhes do vídeo
            video_id = video['snippet']['resourceId']['videoId']
            video_title = video['snippet']['title']
            published_at = video['snippet']['publishedAt']
            thumbnail_url = video['snippet']['thumbnails']['high']['url']

            # Verifica se o vídeo já foi enviado
            if channel_id in self.video_cache and self.video_cache[channel_id] == video_id:
                print(f"Vídeo já foi enviado anteriormente: {video_title}")
                return {'already_sent': True}

            # Atualiza o cache com o novo vídeo
            self.video_cache[channel_id] = video_id
            self._save_cache()

            # Formata a data de publicação
            published_date = datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%SZ')
            now = datetime.utcnow()
            time_diff = now - published_date

            if time_diff.days > 0:
                published_text = f"Publicado há {time_diff.days} dias"
            elif time_diff.seconds >= 3600:
                hours = time_diff.seconds // 3600
                published_text = f"Publicado há {hours} horas"
            else:
                minutes = time_diff.seconds // 60
                published_text = f"Publicado há {minutes} minutos"

            # Verifica se é um novo vídeo (menos de 5 minutos)
            is_new_video = time_diff.seconds < 300

            return {
                'video_url': f'https://www.youtube.com/watch?v={video_id}',
                'video_title': video_title,
                'thumbnail_url': thumbnail_url,
                'channel_name': channel_name,
                'channel_icon': channel_icon,
                'published_text': published_text,
                'is_new_video': is_new_video
            }

        except HttpError as e:
            print(f"Erro na API do YouTube: {str(e)}")
            return None
        except Exception as e:
            print(f"Erro ao obter informações do canal: {str(e)}")
            return None

    def get_old_video(self, channel_url, include_shorts=False):
        """Obtém um vídeo antigo que ainda não foi enviado"""
        try:
            # Extrai o ID do canal da URL
            channel_id = self._extract_channel_id(channel_url)
            if not channel_id:
                print(f"Não foi possível extrair o ID do canal da URL: {channel_url}")
                return None

            # Obtém informações do canal
            channel_response = self.youtube.channels().list(
                part='snippet,contentDetails',
                id=channel_id
            ).execute()

            if not channel_response['items']:
                print(f"Canal não encontrado: {channel_id}")
                return None

            channel = channel_response['items'][0]
            channel_name = channel['snippet']['title']
            channel_icon = channel['snippet']['thumbnails']['default']['url']
            uploads_playlist_id = channel['contentDetails']['relatedPlaylists']['uploads']

            # Obtém mais vídeos do canal (página 2)
            playlist_response = self.youtube.playlistItems().list(
                part='snippet',
                playlistId=uploads_playlist_id,
                maxResults=50,
                pageToken=self._get_next_page_token(uploads_playlist_id)
            ).execute()

            if not playlist_response['items']:
                print(f"Nenhum vídeo antigo encontrado para o canal: {channel_name}")
                return None

            # Procura um vídeo antigo que não seja shorts (se include_shorts for False)
            video = None
            for item in playlist_response['items']:
                video_id = item['snippet']['resourceId']['videoId']
                video_title = item['snippet']['title']
                video_description = item['snippet'].get('description', '')
                
                # Verifica se o vídeo já foi enviado
                if channel_id in self.video_cache and self.video_cache[channel_id] == video_id:
                    continue
                
                if include_shorts or ('#shorts' not in video_title.lower() and '#shorts' not in video_description.lower()):
                    video = item
                    break

            if not video:
                print(f"Nenhum vídeo antigo encontrado que atenda aos critérios para o canal: {channel_name}")
                return None

            # Obtém detalhes do vídeo
            video_id = video['snippet']['resourceId']['videoId']
            video_title = video['snippet']['title']
            published_at = video['snippet']['publishedAt']
            thumbnail_url = video['snippet']['thumbnails']['high']['url']

            # Atualiza o cache com o vídeo antigo
            self.video_cache[channel_id] = video_id
            self._save_cache()

            # Formata a data de publicação
            published_date = datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%SZ')
            now = datetime.utcnow()
            time_diff = now - published_date

            if time_diff.days > 0:
                published_text = f"Publicado há {time_diff.days} dias"
            elif time_diff.seconds >= 3600:
                hours = time_diff.seconds // 3600
                published_text = f"Publicado há {hours} horas"
            else:
                minutes = time_diff.seconds // 60
                published_text = f"Publicado há {minutes} minutos"

            return {
                'video_url': f'https://www.youtube.com/watch?v={video_id}',
                'video_title': video_title,
                'thumbnail_url': thumbnail_url,
                'channel_name': channel_name,
                'channel_icon': channel_icon,
                'published_text': published_text,
                'is_new_video': False
            }

        except HttpError as e:
            print(f"Erro na API do YouTube: {str(e)}")
            return None
        except Exception as e:
            print(f"Erro ao obter vídeo antigo: {str(e)}")
            return None

    def _get_next_page_token(self, playlist_id):
        """Obtém o token da próxima página de vídeos"""
        try:
            response = self.youtube.playlistItems().list(
                part='snippet',
                playlistId=playlist_id,
                maxResults=1
            ).execute()
            return response.get('nextPageToken')
        except Exception as e:
            print(f"Erro ao obter token da próxima página: {str(e)}")
            return None

    def _extract_channel_id(self, url):
        """Extrai o ID do canal da URL"""
        try:
            # Se a URL contém @, precisamos primeiro obter o ID do canal
            if '@' in url:
                username = url.split('@')[1].split('/')[0]
                # Faz uma requisição para obter o ID do canal
                response = self.youtube.search().list(
                    part='snippet',
                    q=username,
                    type='channel',
                    maxResults=1
                ).execute()
                
                if response['items']:
                    return response['items'][0]['id']['channelId']
                return None
                
            # Se a URL contém /channel/, extrai o ID diretamente
            if '/channel/' in url:
                return url.split('/channel/')[1].split('/')[0]
                
            # Se a URL contém /c/ ou /user/, precisamos fazer uma busca
            if '/c/' in url or '/user/' in url:
                username = url.split('/')[-1]
                response = self.youtube.search().list(
                    part='snippet',
                    q=username,
                    type='channel',
                    maxResults=1
                ).execute()
                
                if response['items']:
                    return response['items'][0]['id']['channelId']
                    
            return None
            
        except Exception as e:
            print(f"Erro ao extrair ID do canal: {str(e)}")
            return None 