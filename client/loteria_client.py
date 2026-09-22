import socket, threading, os

HOST = '127.0.0.1'
PORT = 5000

# função referente a thread 1 que vai ler do teclado e enviar para o servidor
def send_data(sock):
    while True:
        try:
            message = input("Digite sua mensagem: ")

        except (EOFError, KeyboardInterrupt):
            print("\n[ENCERRANDO] Conexão encerrada pelo usuário.")
            sock.close()
            os._exit(0) 
        try:
            sock.sendall((message + '\n').encode())
            print(f"[ENVIADO] {message}")
        except OSError as e:
           print(f"\n[ERRO] Falha ao enviar dados: {e}")
           sock.close()
           os._exit(0)

# referente a Thread 2 que vai ler e imprimir na tela
def receive_data(sock):
    buffer = ""
    while True:
        try:
            data = sock.recv(1024)                    # limita a quantidade de bytes recebidos
            if not data:
                print("[DESCONECTADO DO SERVIDOR]")
                sock.close()
                # Encerra totalmente o processo se o servidor cair, não fica preso no input
                os._exit(0)

            buffer += data.decode(errors="ignore")      # adiciona os dados recebidos ao buffer
            while "\n" in buffer:                       # verifica se tem uma linha completa no buffer
                linha, buffer = buffer.split("\n", 1)
                if linha.strip():                       # remove espaços em branco
                    print(f"\n{linha}")
                    
                    # SE O SERVIDOR LOTOU, ENCERRA O CLIENTE AQUI MESMO!
                    if "lotado" in linha.lower():
                        sock.close()
                        os._exit(0)
                        
        except OSError:
            print("\n[DESCONECTADO] A conexão com o servidor foi perdida.")
            sock.close()
            #Encerra totalmente o processo em caso de erro na conexão
            os._exit(0)


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((HOST, PORT))
    except ConnectionRefusedError:
        print("[ERRO] Conexão recusada. O servidor está rodando?")
        sock.close()
        return
    except OSError as e:
        print(f"[ERRO] Falha ao conectar: {e}")
        sock.close()
        return

    print("[CONFIGURACAO] :inicio <N>, :fim <N>, :qtd <N>")
    print("[USO] :sair ; para encerrar a conexão.")
    print("[APOSTAR] números separados por espaço.\n")
    

    try:
        data = sock.recv(1024)
        if not data:
            print("[DESCONECTADO] Servidor fechou a conexão antes de responder.")
            sock.close()
            return
        msg1 = data.decode(errors="ignore")
    except OSError as e:
        print(f"[ERRO] Falha ao receber dados do servidor: {e}")
        sock.close()
        return

    print(msg1.strip())

    tread2 = threading.Thread(target=receive_data, args=(sock,), daemon=True)
    tread2.start()

    tread1 = threading.Thread(target=send_data, args=(sock,), daemon=True)
    tread1.start()
    tread1.join()

    sock.close()

if __name__ == "__main__":
    main()