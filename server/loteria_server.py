import socket
import threading

HOST = '0.0.0.0'
PORT = 5000

#essa função precisa interpretar a linha recebida do cliente
def think(line, state, lock)

#essa função aqui precisa gerar um número aleatório pro sorteio e enviar o resultado
def random_number(conn, state, lock):

#essa função precisa receber a conexão e o endereço do cliente
def handle_client(conn, addr):


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f'[LISTENING] Servidor rodando em [{HOST}:{PORT}]')

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()


if __name__ == '__main__':  
    main()