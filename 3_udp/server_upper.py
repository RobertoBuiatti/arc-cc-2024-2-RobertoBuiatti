import socket

# Definindo o endereço e a porta do servidor
SERVER_HOST = '127.0.0.1'  # Endereço local (localhost)
SERVER_PORT = 12345        # Porta do servidor

def start_server():
    # Criando o socket UDP (SOCK_DGRAM)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Associando o socket ao endereço e porta
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    
    print(f"Servidor UDP iniciado em {SERVER_HOST}:{SERVER_PORT}")
    
    while True:
        # Receber a mensagem do cliente
        message, client_address = server_socket.recvfrom(1024)  # Buffer de 1024 bytes
        
        print(f"Recebido de {client_address}: {message.decode()}")
        
        # Converter a mensagem para maiúsculas
        upper_message = message.decode().upper()
        
        # Enviar a resposta ao cliente
        server_socket.sendto(upper_message.encode(), client_address)
        print(f"Enviado para {client_address}: {upper_message}")

if __name__ == "__main__":
    start_server()
