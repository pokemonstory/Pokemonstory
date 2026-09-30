import requests
import json
import sys

# --- Configuração ---
# ID do canal Pokémon da Pluto TV (Brasil)
CHANNEL_ID = '6838a98df9bd067a38d1b8f7' 

# Parâmetros para a API de boot da Pluto TV
# Estes valores foram atualizados para tentar contornar o erro 400
PLUTO_PARAMS = {
    'appName': 'web',
    'appVersion': '8.0.0',
    'deviceVersion': '122.0.0',
    'deviceModel': 'web',
    'deviceMake': 'chrome',
    'deviceType': 'web',
    'clientID': 'd3c4f6a3-3e2f-4a1a-9c1a-8a7b6c5d4e3f',
    'lang': 'pt-BR'
}

def get_jwt_token():
    """Obtém um novo token JWT da Pluto TV."""
    try:
        # AQUI ESTÁ A MUDANÇA: Adicionamos um cabeçalho (headers) para fingir ser um navegador
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get('https://boot.pluto.tv/v4/start', params=PLUTO_PARAMS, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get('sessionToken')
    except requests.exceptions.RequestException as e:
        print(f"Erro ao obter token: {e}", file=sys.stderr)
        return None

def generate_proxy_playlist(jwt_token):
    """Gera o arquivo M3U8 de proxy com o token embutido."""
    if not jwt_token:
        print("Token JWT inválido. Abortando.", file=sys.stderr)
        return

    # URL base do stream
    stream_base_url = f"https://service-stitcher.clusters.pluto.tv/v1/stitch/embed/hls/channel/{CHANNEL_ID}/master.m3u8"
    
    stream_params = {
        'deviceType': 'web',
        'deviceMake': 'chrome',
        'deviceModel': 'web',
        'deviceVersion': '122.0.0',
        'appName': 'web',
        'appVersion': '8.0.0',
        'jwt': jwt_token
    }

    final_url = f"{stream_base_url}?{'&'.join([f'{k}={v}' for k, v in stream_params.items()])}"

    with open('pluto-proxy.m3u8', 'w') as f:
        f.write("#EXTM3U\n")
        f.write("#EXT-X-STREAM-INF:BANDWIDTH=1000000,RESOLUTION=1280x720\n")
        f.write(final_url + "\n")

    print(f"Arquivo 'pluto-proxy.m3u8' gerado com sucesso!")

if __name__ == "__main__":
    print("Iniciando geração do proxy...")
    token = get_jwt_token()
    if token:
        generate_proxy_playlist(token)
    else:
        print("Falha ao obter o token. O proxy não foi atualizado.", file=sys.stderr)
        sys.exit(1)
