import json
import os

class Config:
    def __init__(self):
        self.config_file = 'data/config.json'
        self._load_config()
        
    def _load_config(self):
        """Carrega a configuração do arquivo"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = {}
                os.makedirs('data', exist_ok=True)
                self._save_config()
        except Exception as e:
            print(f"Erro ao carregar configuração: {str(e)}")
            self.config = {}
            
    def _save_config(self):
        """Salva a configuração no arquivo"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f)
        except Exception as e:
            print(f"Erro ao salvar configuração: {str(e)}")
            
    def save_server_config(self, server_id, config):
        """Salva a configuração de um servidor"""
        self.config[server_id] = config
        self._save_config()
        
    def get_server_config(self, server_id):
        """Obtém a configuração de um servidor"""
        return self.config.get(server_id)
        
    def get_all_configs(self):
        """Obtém todas as configurações"""
        return self.config
        
    def update_last_video(self, server_id, video_url):
        """Atualiza a URL do último vídeo de um servidor"""
        if server_id in self.config:
            self.config[server_id]['last_video_url'] = video_url
            self._save_config() 