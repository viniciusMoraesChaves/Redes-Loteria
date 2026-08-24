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

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    print("[CONFIGURACAO] :inicio <N>, :fim <N>, :qtd <N>")
    print("[APOSTAR] números separados por espaço.\n")

    tread1 = threading.Thread(target=send_data, args=(sock,), daemon=True)
    tread1.start()
    tread1.join()

    sock.close()

if __name__ == "__main__":
    main()