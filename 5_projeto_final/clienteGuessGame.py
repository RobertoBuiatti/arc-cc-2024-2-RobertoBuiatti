import socket

HOST = "127.0.0.1"
PORT = 1060
MAX_BYTES = 65535


def recvall(sock, length):
    data = b""
    while len(data) < length:
        more = sock.recv(length - len(data))
        if not more:
            raise EOFError(
                "was expecting %d bytes but only received"
                " %d bytes before the socket closed" % (length, len(data))
            )
        data += more
    return data


def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((HOST, PORT))

        player_name = input("Digite seu nome jogador: ").strip()
        client_socket.sendall(player_name.encode("utf-8"))

        while True:
            try:
                message = recvall(client_socket, MAX_BYTES).decode("utf-8")
                if message == "FIM_DO_JOGO":
                    print("ACABOUUU. Obrigado por jogar!")
                    break
                print(message)

                if (
                    "digite um número" in message.lower()
                    or "escolha a dificuldade" in message.lower()
                ):
                    user_input = input()
                    client_socket.sendall(user_input.encode("utf-8"))

            except EOFError:
                print("Conexão fechada pelo servidor.")
                break
            except Exception as e:
                print(f"Erro ao receber mensagem: {e}")
                break

    finally:
        client_socket.close()


if __name__ == "__main__":
    main()
