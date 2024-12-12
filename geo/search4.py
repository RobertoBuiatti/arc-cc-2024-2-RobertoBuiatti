import socket
import ssl
from urllib.parse import quote_plus
import json

request_text = """\
GET /search?q={}&format=json HTTP/1.1\r\n\
Host: nominatim.openstreetmap.org\r\n\
User-Agent: Search4.py\r\n\
Connection: close\r\n\
\r\n\
"""

def geocode(address):
    try:
        # Criar o socket não criptografado
        unencrypted_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        unencrypted_sock.connect(('nominatim.openstreetmap.org', 443))
        
        # Criar um contexto SSL
        context = ssl.create_default_context()
        sock = context.wrap_socket(unencrypted_sock, server_hostname='nominatim.openstreetmap.org')
        
        # Codificar o endereço e formatar a requisição
        request = request_text.format(quote_plus(address))
        sock.sendall(request.encode('ascii'))
        
        # Receber a resposta
        raw_reply = b''
        while True:
            more = sock.recv(4096)
            if not more:
                break
            raw_reply += more
        
        # Decodificar a resposta em formato UTF-8
        response = raw_reply.decode('utf-8')
        
        # Fechar o socket após o uso
        sock.close()

        # Imprimir a resposta bruta
        print("Resposta bruta:")
        print(response)
        
        # Tentar analisar a resposta JSON
        try:
            reply = json.loads(response)
            if reply:
                latitude = reply[0]['lat']
                longitude = reply[0]['lon']
                print(f"Latitude: {latitude}, Longitude: {longitude}")
            else:
                print("Endereço não encontrado.")
        except json.JSONDecodeError:
            print("Erro ao processar a resposta JSON.")
    except socket.error as e:
        print(f"Erro de rede: {e}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
        

if __name__ == '__main__':
    geocode('Belarmino Vilela Junqueira, Ituiutaba, MG')
