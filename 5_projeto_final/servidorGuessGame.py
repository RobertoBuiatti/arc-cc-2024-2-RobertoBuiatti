import socket
import threading
import random

HOST = "127.0.0.1"
PORT = 1060
MAX_BYTES = 65535

jogadores = []  # Lista de jogadores conectados (nome e socket)
pontuacoes = {}  # Pontuações dos jogadores
dificuldade = None
num_jogadores = 0
lock = threading.Lock()  # Lock para evitar condições de corrida

def recvall(sock):
    """Recebe uma mensagem do cliente."""
    try:
        data = sock.recv(MAX_BYTES)
        if not data:
            raise EOFError("Conexão fechada pelo cliente.")
        return data
    except Exception as e:
        print(f"Erro ao receber dados: {e}")
        return None

def cliente(conn, client_address):
    """Gerencia a conexão de cada cliente."""
    global dificuldade

    try:
        # Recebe o nome do jogador
        player_name = conn.recv(MAX_BYTES).decode("utf-8").strip()
        if not player_name:
            print(
                f"Jogador não enviou um nome. Encerrando conexão com {client_address}."
            )
            conn.close()
            return

        # Adiciona o jogador à lista com lock
        with lock:
            jogadores.append((player_name, conn))
            pontuacoes[player_name] = 50

        print(f"Jogador conectado: {player_name} ({client_address})")
        broadcast(f"Jogadores na sala: {len(jogadores)}/{num_jogadores}\n")

        # Aguarda que todos os jogadores estejam conectados
        while True:
            with lock:
                if len(jogadores) == num_jogadores:
                    break
            conn.sendall("Aguardando outros jogadores...\n".encode("utf-8"))
            threading.Event().wait(200)

        # Escolha da dificuldade (apenas pelo primeiro jogador)
        if dificuldade is None:
            p1_name, p1_conn = jogadores[0]
            for jogador, socket in jogadores:
                if jogador == p1_name:
                    socket.sendall(
                        "Sala completa! Escolha a dificuldade do jogo:\n[1] - Fácil\n[2] - Médio\n[3] - Difícil\n".encode(
                            "utf-8"
                        )
                    )
                else:
                    socket.sendall(
                        f"Sala completa! O jogador {p1_name} está escolhendo a dificuldade.\n".encode(
                            "utf-8"
                        )
                    )

            while True:
                try:
                    data = p1_conn.recv(MAX_BYTES).decode("utf-8").strip()
                    if data in ["1", "2", "3"]:
                        with lock:
                            dificuldade = int(data)
                        dificuldades = {1: "Fácil", 2: "Médio", 3: "Difícil"}
                        print(f"Dificuldade escolhida: {dificuldades[dificuldade]}")
                        broadcast(
                            f"A dificuldade escolhida foi: {dificuldades[dificuldade]}. O jogo vai começar agora!\n"
                        )
                        game()
                        return
                    else:
                        p1_conn.sendall(
                            "Entrada inválida! Escolha entre [1], [2], ou [3].\n".encode(
                                "utf-8"
                            )
                        )
                except Exception as e:
                    print(f"Erro ao processar escolha de dificuldade: {e}")
                    p1_conn.sendall(
                        "Erro ao escolher dificuldade. Tente novamente.\n".encode(
                            "utf-8"
                        )
                    )

    except Exception as e:
        print(f"Erro ao processar mensagens do cliente {client_address}: {e}")
    finally:
        with lock:
            # Remove o jogador da lista ao desconectar
            jogadores[:] = [(name, sock) for name, sock in jogadores if sock != conn]
        conn.close()

def broadcast(message):
    """Envia uma mensagem para todos os jogadores."""
    with lock:
        for _, client_socket in jogadores:
            try:
                client_socket.sendall(message.encode("utf-8"))
            except Exception as e:
                print(f"Erro ao enviar mensagem para um cliente: {e}")

def game():
    """Inicia o jogo de adivinhação."""
    numero_secreto = random.randint(1, 50)
    tentativas_totais = {1: 30, 2: 20, 3: 10}[dificuldade]
    tentativas_restantes = {player_name: tentativas_totais for player_name, _ in jogadores}
    print(f"Número secreto gerado: {numero_secreto}")

    while any(tentativas > 0 for tentativas in tentativas_restantes.values()):
        for player_name, client_socket in jogadores:
            if tentativas_restantes[player_name] > 0:
                try:
                    client_socket.sendall(
                        f"{player_name}, digite um número (1 a 50). Você tem {tentativas_restantes[player_name]} tentativas restantes: ".encode("utf-8")
                    )
                    guess = int(client_socket.recv(MAX_BYTES).decode("utf-8").strip())
                    print(f"{player_name} tentou: {guess}")

                    tentativas_restantes[player_name] -= 1
                    pontuacoes[player_name] -= 1

                    if guess == numero_secreto:
                        broadcast(
                            f"{player_name} acertou o número secreto! Fim do jogo.\n"
                        )
                        pontuacoes[player_name] += 100  # Bônus por acertar
                        score()
                        final()
                        return
                    elif guess < numero_secreto:
                        client_socket.sendall("O número secreto é maior!\n".encode("utf-8"))
                    else:
                        client_socket.sendall("O número secreto é menor!\n".encode("utf-8"))

                except ValueError:
                    client_socket.sendall(
                        "Entrada inválida. Digite um número entre 1 e 50.\n".encode("utf-8")
                    )
                except Exception as e:
                    print(f"Erro ao receber tentativa de {player_name}: {e}")

    broadcast("Fim do jogo! Ninguém acertou o número secreto.\n")
    score()
    final()

def score():
    """Envia e exibe as pontuações finais."""
    scores_message = "\nPontuação final:\n"
    with lock:
        for player_name, score in pontuacoes.items():
            scores_message += f"{player_name}: {score} pontos\n"
    broadcast(scores_message)
    print(scores_message)

def final():
    """Encerra o jogo e as conexões."""
    broadcast("FIM_DO_JOGO")
    with lock:
        for _, client_socket in jogadores:
            try:
                client_socket.close()
            except Exception as e:
                print(f"Erro ao fechar conexão com cliente: {e}")

def main():
    """Função principal do servidor."""
    global num_jogadores

    try:
        num_jogadores = int(input("Digite o número de jogadores (mínimo 3): "))
        if num_jogadores < 3:
            print("O número mínimo de jogadores é 3. Encerrando.")
            return
    except ValueError:
        print("Entrada inválida. Encerrando.")
        return

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(num_jogadores)
    print(f"Servidor rodando em {HOST}:{PORT}, aguardando {num_jogadores} jogadores...")

    try:
        while len(jogadores) < num_jogadores:
            conn, client_address = server_socket.accept()
            print(f"Conexão aceita de {client_address}")
            threading.Thread(target=cliente, args=(conn, client_address)).start()
    except Exception as e:
        print(f"Erro no servidor: {e}")
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()
