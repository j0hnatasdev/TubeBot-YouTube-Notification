# TubeBot de Notificação do YouTube

Este bot monitora canais do YouTube e envia notificações no Discord quando novos vídeos são publicados.

## Desenvolvido por
[Prolldevs](https://developers.prollabe.com) - Soluções em Desenvolvimento

## Estrutura do Projeto

```
.
├── data/               # Diretório para armazenar configurações
├── src/               # Código fonte do bot
│   ├── __init__.py    # Inicializador do pacote
│   ├── bot.py         # Classe principal do bot
│   ├── config.py      # Gerenciamento de configurações
│   ├── youtube.py     # Scraping do YouTube
│   └── utils.py       # Funções utilitárias
├── main.py            # Ponto de entrada do bot
├── requirements.txt   # Dependências do projeto
└── .env              # Variáveis de ambiente
```

## Funcionalidades

- Monitora canais do YouTube em tempo real
- Envia notificações com embed bonito no Discord
- Suporta múltiplos servidores
- Configuração personalizada por servidor
- Intervalo de verificação otimizado para gerenciamento de cota da API
- Envia notificações de vídeos e shorts antigos quando não há novos conteúdos
- Sistema inteligente de cache para evitar duplicação de notificações

## Requisitos

- Python 3.8+
- Discord.py
- Google API Python Client
- python-dotenv

## Instalação

1. Clone este repositório
2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente:
   - Crie um arquivo `.env` na raiz do projeto
   - Adicione seu token do Discord:
   ```
   DISCORD_TOKEN=seu_token_aqui
   ```
   - Adicione sua chave da API do YouTube:
   ```
   YOUTUBE_API_KEY=sua_chave_api_aqui
   ```

### Como obter a chave da API do YouTube

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto ou selecione um existente
3. Ative a YouTube Data API v3:
   - No menu lateral, vá em "APIs e Serviços" > "Biblioteca"
   - Pesquise por "YouTube Data API v3"
   - Clique em "Ativar"
4. Crie uma chave de API:
   - No menu lateral, vá em "APIs e Serviços" > "Credenciais"
   - Clique em "Criar Credenciais" > "Chave de API"
   - Copie a chave gerada e adicione ao arquivo `.env`

### Gerenciamento da Cota da API

A API do YouTube tem um limite diário de requisições. Para evitar exceder este limite:
- O intervalo padrão de verificação é de 4 horas (14400 segundos)
- Este intervalo pode ser ajustado, mas não recomendamos valores menores que 4 horas
- O bot utiliza um sistema de cache para minimizar o número de requisições
- Se você precisar de verificações mais frequentes, considere:
  - Solicitar um aumento de cota no Google Cloud Console
  - Utilizar múltiplas chaves de API
  - Aumentar o número de projetos no Google Cloud

## Configuração de Permissões

Antes de começar a usar o bot, é importante configurar corretamente as permissões no Discord. Siga estes passos:

1. **Adicione o bot ao servidor**:
   - Use o link de convite do bot que inclui as permissões necessárias
   - Ou adicione manualmente as seguintes permissões ao cargo do bot:
     - `Enviar Mensagens`
     - `Enviar Mensagens em Threads`
     - `Incorporar Links`
     - `Anexar Arquivos`
     - `Ler Mensagens`
     - `Ler o Histórico de Mensagens`
     - `Ver Canais`
     - `Usar Comandos de Aplicativo`

2. **Configure as permissões do canal**:
   - Antes de usar o comando `!start`, certifique-se de que o bot tem acesso ao canal onde você deseja receber as notificações
   - O bot deve ter permissão para:
     - Ver o canal
     - Enviar mensagens no canal
     - Incorporar links no canal

3. **Verifique a hierarquia de cargos**:
   - O cargo do bot deve estar acima do cargo dos usuários que irão configurá-lo
   - Isso garante que o bot possa gerenciar as configurações corretamente

4. **Importante**: Se você receber o erro "Missing Permissions", verifique se:
   - O bot foi adicionado ao canal de notificações
   - O bot tem todas as permissões necessárias no canal
   - O cargo do bot está na posição correta na hierarquia

## Uso

1. Execute o bot:
```bash
python main.py
```

2. No Discord, use o comando `!start` para iniciar a configuração do bot
3. Siga as instruções para configurar:
   - Canal de notificações
   - URL do canal do YouTube
   - Intervalo de verificação (recomendado: 14400 segundos = 4 horas)

### Comportamento das Notificações

O bot funciona da seguinte forma:
- Verifica novos vídeos e shorts no intervalo configurado (padrão: 4 horas)
- Se não encontrar novos conteúdos, busca vídeos e shorts antigos que ainda não foram notificados
- Mantém um registro de todos os vídeos já notificados para evitar duplicações
- Envia as notificações com informações detalhadas sobre o vídeo/short
- Gerencia automaticamente a cota da API para evitar erros de limite excedido

## Exemplo de Configuração

1. Digite `!start`
2. O bot pedirá para mencionar o canal de notificações:
   - Responda com: `#notificações`
3. O bot pedirá a URL do canal do YouTube:
   - Responda com: `https://www.youtube.com/@canal`
4. O bot pedirá o intervalo de verificação:
   - Responda com: `14400` (para verificar a cada 4 horas - recomendado)

O bot irá confirmar cada etapa e mostrar um resumo final da configuração quando concluído.

## Estrutura do Código

- `main.py`: Ponto de entrada do bot
- `src/bot.py`: Implementação principal do bot Discord
- `src/config.py`: Gerenciamento de configurações dos servidores
- `src/youtube.py`: Scraping de informações do YouTube
- `src/utils.py`: Funções utilitárias e helpers

## Suporte

Para suporte ou mais informações, visite [Prolldevs](https://developers.prollabe.com) 