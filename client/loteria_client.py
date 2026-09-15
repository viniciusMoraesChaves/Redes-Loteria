import socket
import threading

HOST = '127.0.0.1'
PORT = 5000

# função referente a thread 1 que vai ler do teclado e enviar para o servidor
def send_data(sock):
    while True:
        try:
            message = input("Digite sua mensagem: ")
        except EOFError:
            print("EOFError: Encerrando envio de dados.")
            break
        try:
            sock.sendall((message + '\n').encode())
            print(f"[ENVIADO] {message}")
        except OSError as e:
            print(f"Erro ao enviar dados: {e}")
            break

# referente a Thread 2 que vai ler e imprimir na tela
def receive_data(sock):
    buffer = ""
    while True:
        try:
            data = sock.recv(1024)                      # limita a quantidade de bytes recebidos
            if not data:
                print("[DESCONECTADO DO SERVIDOR]")
                break
            buffer += data.decode(errors="ignore")      # adiciona os dados recebidos ao buffer
            while "\n" in buffer:                       # verifica se tem uma linha completa no buffer
                linha, buffer = buffer.split("\n", 1)
                if linha.strip():                       # remove espaços em branco
                    print(f"\n{linha}")
        except OSError:
            break


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    print("[CONFIGURACAO] :inicio <N>, :fim <N>, :qtd <N>")
    print("[APOSTAR] números separados por espaço.\n")

    msg1 = sock.recv(1024).decode()
    print(msg1.strip())

    tread2 = threading.Thread(target=receive_data, args=(sock,), daemon=True)
    tread2.start()

    tread1 = threading.Thread(target=send_data, args=(sock,), daemon=True)
    tread1.start()
    tread1.join()

    sock.close()

if __name__ == "__main__":
    main()