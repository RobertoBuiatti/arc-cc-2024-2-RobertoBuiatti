import socket
import threading
import random

HOST = '127.0.0.1'
PORT = 1060
MAX_BYTES = 65535
jogadores = []
dificuldade = None
pontuacoes = {}

def cliente(client_socket, client_address, player_name):
    global dificuldade

    # Adiciona o jogador à lista de jogadores e inicia com 50 pontos
    jogadores.append((player_name, client_socket))
    pontuacoes[player_name] = 50
    print(f"Jogador conectado: {player_name} ({client_address})")
    broadcast(f"Jogadores na sala: {len(jogadores)}/3\n")

    if len(jogadores) < 3:
        client_socket.sendall("Aguarde os outros jogadores.\n".encode('utf-8'))
        return

    if len(jogadores) == 3 and dificuldade is None:
        p1_name, p1_socket = jogadores[0]
        for jogador, socket in jogadores:
            if jogador == p1_name:
                socket.sendall("Sala completa! Escolha a dificuldade do jogo:\n[1] - Fácil\n[2] - Médio\n[3] - Difícil\n".encode('utf-8'))
            else:
                socket.sendall(f"Sala completa! O jogador {p1_name} está escolhendo a dificuldade.\n".encode('utf-8'))

        # Recebe a dificuldade de P1
        data = p1_socket.recv(MAX_BYTES).decode('utf-8').strip()
        if data in ["1", "2", "3"]:
            dificuldade = int(data)
            dificuldades = {1: "Fácil", 2: "Médio", 3: "Difícil"}
            print(f"Dificuldade escolhida por {p1_name}: {dificuldades[dificuldade]}")
            broadcast(f"A dificuldade escolhida foi: {dificuldades[dificuldade]}. O jogo vai começar agora!\n")
            game()
        else:
            p1_socket.sendall("Entrada inválida! Escolha entre [1], [2], ou [3].".encode('utf-8'))

def broadcast(message):
    for _, client_socket in jogadores:
        client_socket.sendall(message.encode('utf-8'))

def game():
    global dificuldade

    numero_secreto = random.randint(1, 200)
    tentativas_restantes = {1: 30, 2: 20, 3: 10}[dificuldade]
    print("Número secreto gerado pelo servidor.")

    for rodada in range(tentativas_restantes):
        for player_name, client_socket in jogadores:
            try:
                client_socket.sendall(f"\n{player_name}, digite um número (1 a 200): ".encode('utf-8'))
                guess = int(client_socket.recv(MAX_BYTES).decode('utf-8').strip())
                print(f"{player_name} digitou: {guess}")

                if guess == numero_secreto:
                    broadcast(f"\n{player_name} acertou o número secreto na rodada {rodada + 1}! Fim do jogo.")
                    pontuacoes[player_name] += 100 # Bônus por acertar
                    score()
                    final()
                    return
                elif guess < numero_secreto:
                    client_socket.sendall("O número secreto é maior!\n".encode('utf-8'))
                else:
                    client_socket.sendall("O número secreto é menor!\n".encode('utf-8'))

                # Atualiza a pontuação com base na diferença
                pontuacoes[player_name] -= abs(numero_secreto - guess)

            except ValueError:
                client_socket.sendall("Entrada inválida. Digite um número entre 1 e 100.\n".encode('utf-8'))

    broadcast("Fim do jogo! Ninguém acertou o número secreto.")
    score()
    final()

def score():
    scores_message = "\n*********************************\nPontuação final:\n"
    for player_name, score in pontuacoes.items():
        scores_message += f"{player_name}: {score} pontos\n"
    scores_message += "*********************************\n"
    broadcast(scores_message)
    print(scores_message)

def final():
    broadcast("FIM_DO_JOGO")
    for _, client_socket in jogadores:
        client_socket.close()

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(3)
    print(f"Servidor rodando {HOST} na porta {PORT}...")

    while len(jogadores) < 3:
        client_socket, client_address = server_socket.accept()
        player_name = client_socket.recv(MAX_BYTES).decode('utf-8').strip()
        thread = threading.Thread(target=cliente, args=(client_socket, client_address, player_name))
        thread.start()

if __name__ == "__main__":
    main()