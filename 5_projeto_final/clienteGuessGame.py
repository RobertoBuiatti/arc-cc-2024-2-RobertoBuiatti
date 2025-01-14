import socket

HOST = '127.0.0.1'
PORT = 1060
MAX_BYTES = 65535

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    player_name = input("Digite seu nome jogador: ").strip()
    client_socket.sendall(player_name.encode('utf-8'))

    while True:
        try:
            message = client_socket.recv(MAX_BYTES).decode('utf-8')
            if message == "FIM_DO_JOGO":
                print("ACABOUUU. Obrigado por jogar!")
                break
            print(message)

            if "digite um número" in message.lower() or "escolha a dificuldade" in message.lower():
                user_input = input()
                client_socket.sendall(user_input.encode('utf-8'))

        except KeyboardInterrupt:
            print("Saindo do jogo...")
            client_socket.close()
            break

    client_socket.close()

if __name__ == "__main__":
    main()