import socket

# Definindo o endereço e a porta do servidor
SERVER_HOST = '127.0.0.1'  # Endereço local (localhost)
SERVER_PORT = 12345        # Porta do servidor

def start_client():
    # Criando o socket UDP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Receber a string do usuário
    user_input = input("Digite a mensagem para enviar ao servidor: ")
    
    # Enviar a mensagem para o servidor
    client_socket.sendto(user_input.encode(), (SERVER_HOST, SERVER_PORT))
    
    # Aguardar a resposta do servidor
    modified_message, server_address = client_socket.recvfrom(1024)
    
    # Exibir a resposta recebida
    print(f"Mensagem recebida do servidor: {modified_message.decode()}")
    
    # Fechar o socket do cliente
    client_socket.close()

if __name__ == "__main__":
    start_client()
