from ast import Try
import socket, threading, random, datetime, time, sys, os, argparse
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helpers import RED, GREEN, YELLOW, RESET

HOST = '0.0.0.0'
PORT = 5000

clientes_lock = threading.Lock()
clientes_conectados = 0
MAX_CLIENTES = 5

# entende o comando digitado pelo usuário
def think(line, state, lock):
    line = line.strip()
    if not line:
        return
 
    if line.startswith(":"):
        parts = line[1:].split()
        if len(parts) == 2:
            cmd, value = parts[0].lower(), parts[1]
            try:
                value = int(value)
            except ValueError:
                return
            with lock:
                if cmd == "inicio":
                    state["inicio"] = value
                elif cmd == "fim":
                    state["fim"] = value
                elif cmd == "qtd":
                    state["qtd"] = value
    else:
        try:
            nums = [int(x) for x in line.split()]
            if nums:
                with lock:
                    state["apostas"].append(nums)
        except ValueError:
            pass  # linha inválida, ignora

def thread_recebe_comandos(conn, state, lock):
    buffer = ""
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break
            buffer += data.decode(errors="ignore")
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                think(line, state, lock)
        except OSError:
            break
 
    with lock:
        state["ativo"] = False
 

#essa função aqui gera um número aleatório pro sorteio e enviar o resultado
def thread_numeros(conn, state, lock):
    while True:
        # espera 1 minuto, mas checando a cada segundo se a conexão ainda está ativa
        # se o cliente cair no meio da espera, a thread não fica presa 60s à toa
        for _ in range(60):
            time.sleep(1)
            with lock:
                if not state["ativo"]:
                    return

        # pega a config e as apostas acumuladas, e já zera a lista pra próxima rodada
        with lock:
            inicio = state["inicio"]
            fim = state["fim"]
            qtd = state["qtd"]
            apostas = state["apostas"][:]
            state["apostas"] = []

        # formatação dos números sorteados
        correctNumbers = random.sample(range(inicio, fim + 1), qtd)
        sorteados_str = "[" + "|".join(str(n) for n in correctNumbers) + "]"

        try:
            conn.sendall(f'{GREEN}[SORTEIO]{RESET}: {sorteados_str}\n'.encode())

            # aqui é feita a verificação de acertos do usuário
            for aposta in apostas:
                acertos = [n for n in aposta if n in correctNumbers]
                acertos_str = "[" + "|".join(str(n) for n in acertos) + "]"
                aposta_str = "[" + "|".join(str(n) for n in aposta) + "]"
                conn.sendall(f'{YELLOW}[SUA APOSTA]{RESET} : {aposta_str} -> Acertos: {acertos_str}\n'.encode())
        except OSError:
            return  


#essa função precisa receber a conexão e o endereço do cliente
def handle_client(conn, addr):
    global clientes_conectados

    with clientes_lock:
        if clientes_conectados >= MAX_CLIENTES:
            try:
                conn.sendall(f"{RED}SERVIDOR LOTADO! {RESET}Tente novamente mais tarde.\n".encode())
            except OSError:
                pass
            conn.close()
            print(f"{RED}[RECUSADO]{RESET} {addr} - limite atingido.")
            return
        clientes_conectados += 1

    print(f"{GREEN}[NOVA CONEXAO]{RESET} {addr} conectado.")
    try:
    horario = datetime.datetime.now().strftime("%H:%M:%S")
    conn.sendall(f"{horario}: CONECTADO!!\n".encode())
 
    # "Memória compartilhada" entre a thread 1 e a thread 2 desta conexão
    estado = {
        "inicio": 0,
        "fim": 100,
        "qtd": 5,
        "apostas": [],
        "ativo": True,
    }
    lock = threading.Lock()
 
    t1 = threading.Thread(target=thread_recebe_comandos, args=(conn, estado, lock))
    t2 = threading.Thread(target=thread_numeros, args=(conn, estado, lock))
 
    t1.start()
    t2.start()
 
    t1.join()
    t2.join()

    conn.close()
    finally:
    with clientes_lock:
        clientes_conectados -= 1

    
    print(f"{RED}[DESCONECTADO]{RESET} {addr}({clientes_conectados}/{MAX_CLIENTES})")


def main():
    if len(sys.argv) != 2: #verifica se o usuário passou o limite de clientes como argumento
        print(f"{RED}[ERRO]{RESET} Uso correto: python loteria_server.py <limite_de_clientes>")
        sys.exit(1)
    try:
        limite_clientes = int(sys.argv[1]) 
        if limite_clientes <= 0: #verifica se o limite de clientes é maior que zero
            print(f"{RED}[ERRO]{RESET} O limite deve ser um número maior que zero.")
            sys.exit(1)
    except ValueError: #verifica se o limite de clientes é um número inteiro
        print(f"{RED}[ERRO]{RESET} O limite de clientes deve ser um número inteiro.")
        sys.exit(1)

    print(f"{GREEN}[INFO]{RESET} Servidor configurado para limite de {limite_clientes} clientes.") 
    global MAX_CLIENTES
    parser = argparse.ArgumentParser()
    parser.add_argument('--max-clientes', type=int, default=5)
    args = parser.parse_args()
    MAX_CLIENTES = limite_clientes


    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f'{GREEN}[LISTENING]{RESET} Servidor rodando em [{HOST}:{PORT}] com limite de {limite_maximo} clientes')

    while True:
        conn, addr = server.accept()
        
        # O lock protege a checagem e o incremento do contador de vagas
        with lock_vagas:
            if clientes_ativos >= limite_maximo:
                print(f"{YELLOW}[RECUSADO]{RESET} Conexão de {addr} recusada (Servidor lotado).")
                conn.sendall(b"Servidor lotado. Tente novamente mais tarde.\n")
                conn.close()
                continue # Pula para a próxima conexão sem iniciar thread
            else:
                clientes_ativos += 1
                print(f"[DEBUG] Vaga ocupada. Clientes ativos: {clientes_ativos}/{limite_maximo}")
                
        # Cria e inicia a thread apenas se passou da checagem e tem vaga
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

if __name__ == '__main__':
    main()

