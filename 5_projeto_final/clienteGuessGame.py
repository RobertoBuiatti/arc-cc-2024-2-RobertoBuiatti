import socket

HOST = "127.0.0.1"
PORT = 1060
MAX_BYTES = 65535


def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((HOST, PORT))

        # Enviar o nome do jogador
        player_name = input("Digite seu nome jogador: ").strip()
        if not player_name:
            print("Nome do jogador não pode estar vazio.")
            return
        client_socket.sendall(player_name.encode("utf-8"))

        while True:
            try:
                # Receber mensagem do servidor
                message = client_socket.recv(MAX_BYTES).decode("utf-8")
                if not message:
                    print("Conexão encerrada pelo servidor.")
                    break
                if message == "FIM_DO_JOGO":
                    print("Jogo encerrado. Obrigado por jogar!")
                    break
                print(message)

                # Interagir com o servidor
                if (
                    "digite um número" in message.lower()
                    or "escolha a dificuldade" in message.lower()
                ):
                    user_input = input("Sua resposta: ").strip()
                    client_socket.sendall(user_input.encode("utf-8"))

            except Exception as e:
                print(f"Erro na comunicação com o servidor: {e}")
                break

    finally:
        try:
            client_socket.close()
        except Exception as e:
            print(f"Erro ao fechar a conexão: {e}")


if __name__ == "__main__":
    main()
