import threading
import socket
import os
import sys

PORT = 8080
width = os.get_terminal_size().columns
pos = round(width/2)
usuarios = dict()
apelidos = list()
salas = {"sala_geral": [], "sala01": []}
ADMIN_SENHA = 'admin'

lista_comandos = b'\nComandos\n'\
				+ b'/criar Para criar uma sala\n'\
				+ b'/entrar Para entrar em uma sala\n' \
                + b'/listar Para listar as salas disponiveis\n' \
                + b'/deletar Para deletar uma sala\n'\
				+ b'/sair_sala Para sair da sala\n' \
				+ b'/sair Para encerrar a conexao com o servidor\n' \
                + b'/ajuda Para exibir a lista de comandos disponiveis\n' \
				+ b'\n'

def ajuda(cliente):
    cliente.sendall(lista_comandos)


def lista_salas(cliente):
    response = "Salas disponíveis: \n"
    for sala, clientes_sala in salas.items():
        response = "\n[+] Usuário na sala:\n"
        response += f"[+]{sala} : {len(clientes_sala)} Usuários\n"
    cliente.sendall(response.encode('utf-8'))


def entrar(cliente):
    cliente.sendall("\n[+] Salas disponíveis:\n".encode('utf-8'))
    for keys in salas:
        cliente.sendall(f"-> {keys}\n".encode('utf-8'))
    cliente.sendall("[+] Deseja entrar em qual sala: ".encode('utf-8'))
    nome_sala = cliente.recv(1024).decode('utf-8')
    nome_sala = nome_sala.replace("\n", "").replace("\r", "")
    try:
        sala_origem = procura_cliente_sala(cliente)
        salas[nome_sala].append(cliente)
        salas[sala_origem].remove(cliente)
        cliente.sendall(f"[!] Bem vindo a sala {nome_sala} [!]\n".encode('utf-8'))
    except:
        response = "[!] Essa sala não existe no servidor [!]\n"
        cliente.sendall(response.encode('utf-8'))


def sair_sala(cliente):
    try:
        cliente.sendall("[+] Tem certeza que deseja sair da sala? (sim/nao) ".encode('utf-8'))
        resposta = cliente.recv(1024).decode('utf-8')
        resposta = resposta.replace("\n", "").replace("\r", "")
        if resposta.lower() == 'sim':
            sala_origem = procura_cliente_sala(cliente)
            salas["sala_geral"].append(cliente)
            salas[sala_origem].remove(cliente)
            cliente.sendall(f"[+] Você saiu da sala {sala_origem} e está no Lobby!\n".encode('utf-8'))
        else:
            pass
    except:
        response = "[!] Erro ao sair da sala [!]\n"
        cliente.sendall(response.encode("utf-8"))

def criar_sala(cliente):
    sala_origem = procura_cliente_sala(cliente)
    cliente.sendall("[+] Entre com o nome da sala que deseja criar: ".encode('utf-8'))
    nome_sala = cliente.recv(1024).decode('utf-8')
    nome_sala = nome_sala.replace("\r", "").replace("\n", "")
    salas[nome_sala] = [cliente]
    salas[sala_origem].remove(cliente)
    entrar(cliente)
    print(f"[!] Sala {nome_sala} criada [!]\n")


def deleta_sala(cliente):
    try:
        cliente.sendall("[+] Entre com o nome da sala que deseja excluir: ".encode('utf-8'))
        nome_sala = cliente.recv(1024).decode('utf-8')
        nome_sala = nome_sala.replace("\r", "").replace("\n", "")
        clientes_sala = salas[nome_sala]
        salas["sala_geral"].append(clientes_sala)
        salas.pop(nome_sala)
        cliente.sendall(f"[!] Sala {nome_sala} deletada [!]\n".encode('utf-8'))
        print(f"[!] Sala {nome_sala} deletada [!]\n")
    except Exception as e:
        cliente.sendall(f"[!] Erro ao deletar a sala {nome_sala} [!]\n".encode('utf-8'))
        print(f"[!] Erro {e} ao deletar a sala {nome_sala} [!]\n")


def procura_cliente_sala(cliente):
    for sala, clientes_sala in salas.items():
        if cliente in clientes_sala:
            return sala

def procura_cliente_apelido(cliente):
    apelido_usuario = usuarios[cliente]['apelido']
    return apelido_usuario


def valida_senha(cliente, senha):
    if senha == usuarios[cliente]['password'] or senha == ADMIN_SENHA:
        return True
    else:
        return False



def sair_do_servidor(cliente):
    cliente.sendall("[+] Tem certeza que deseja sair do servidor? (sim/nao) ".encode('utf-8'))
    resposta = cliente.recv(1024).decode('utf-8')
    resposta = resposta.replace("\n", "").replace("\r", "")
    if resposta.lower() == 'sim':
        while True:
            cliente.sendall("[+] Digite sua senha: ".encode('utf-8'))
            senha = cliente.recv(1024).decode('utf-8')
            senha = senha.replace("\n", "").replace("\r", "")
            senha_checada = valida_senha(cliente, senha)
            if senha_checada == True:
                cliente.sendall(f"[!] Até logo... [!]\n".encode('utf-8'))
                apelido = procura_cliente_apelido(cliente)
                apelidos.remove(apelido)
                sala_origem = procura_cliente_sala(cliente)
                salas["sala_geral"].append(cliente)
                salas[sala_origem].remove(cliente)
                salas["sala_geral"].remove(cliente)
                del usuarios[cliente]
                cliente.shutdown(1)
                cliente.close()
                print(f"[!] O Usuário {apelido} escolheu sair do servidor [!]")
                break
            else:
                cliente.sendall("[!] Senha incorreta [!]\n".encode('utf-8'))
                continue
    else:
        cliente.sendall("[!] Otima escolha.... digite /help para exibir as opções [!]\n".encode('utf-8'))
        pass


def apelido_unico(apelido, cliente):
    while apelido in apelidos:
        cliente.sendall("[+] Este Nickname já está em uso...\n".encode('utf-8'))
        cliente.sendall("[+] Nickname: ".encode('utf-8'))
        received = cliente.recv(1024).decode('utf-8')
        apelido = received.replace("\n", "").replace("\r", "")
    return apelido

COMANDOS = [
    {
        "action": "/listar",
        "function": lista_salas,
    },
    {
        "action": "/ajuda",
        "function": ajuda,
    },
    {
        "action": "/entrar",
        "function": entrar,
    },
    {
        "action": "/sair_sala",
        "function": sair_sala,
    },
    {
        "action": "/criar",
        "function": criar_sala,
    },
    {
        "action": "/deletar",
        "function": deleta_sala,
    },
    
    {
        "action": "/sair",
        "function": sair_do_servidor,
    },
]


def valida_comando(msg, cliente):
    auxiliar = 0
    if msg.startswith("/") == True:
        comando = str(msg).lower()
        for cmd in COMANDOS:
            if comando == cmd["action"]:
                cmd["function"](cliente)
                return True
            elif auxiliar == len(COMANDOS) and comando != cmd["action"]:
                cliente.sendall(("[!] Comando inválido [!]\n").encode('utf-8'))
                return False
            else:
                pass
            auxiliar+=1
        return False
    else:
        return False

def main():
    try:
        server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print("[+] Socket criado com sucesso!! [+]")
    except socket.error as err:
        print("[+] Erro ao criar o socket... [+]",err)
        sys.exit()
    try:
        server.bind(("127.0.0.1",PORT))
        print(f"[+] Servidor atrelado a porta {PORT} [+] ")
    except:
        print("[!] Erro ao atrelar o servidor a porta... [!]")
        server.close()
        sys.exit()

    server.listen(100)
    print("[+] Servidor aguardando novas conexões... [+]\n")
    print("[+] A senha de administrador é: adminpassword")

    while True:
        cliente, addr = server.accept()
        print(f"[+] Conexão realizada com o endereço {addr} [+]\n")
        cliente.sendall("[+] Nickname: ".encode('utf-8'))
        apelido = cliente.recv(1024).decode('utf-8')
        apelido = apelido.replace("\n", "").replace("\r", "")
        apelido = apelido_unico(apelido, cliente)
        
        
        cliente.sendall("[+] Nome Completo: ".encode('utf-8'))
        full_name = cliente.recv(1024).decode('utf-8')
        full_name = full_name.replace("\n", "").replace("\r", "")

        cliente.sendall("[+] Senha: ".encode('utf-8'))
        senha = cliente.recv(1024).decode('utf-8')
        senha = senha.replace("\n", "").replace("\r", "")
        

        apelidos.append(apelido)
        salas["sala_geral"].append(cliente)
        usuario = {} 
        usuario["apelido"] = apelido
        usuario["con"] = cliente
        usuario["full_name"] = full_name
        usuario["password"] = senha
        usuarios[cliente] = usuario
        ajuda(cliente)
        print(f"[+] Usuário {full_name} com o Nickname {apelido} conectado ao servidor [!]\n")
        
        thread = threading.Thread(target=valida_msg, args=[cliente])
        thread.start()


def valida_msg(cliente):
    while True:
        try:
            msg = cliente.recv(2048).decode('utf-8')
            msg = msg.replace("\n", "").replace("\r", "")
            try:
                has_command = valida_comando(str(msg), cliente)
                if has_command == False:
                    broadcast(msg, cliente)
            except:
                deleta_cliente(cliente)
                break
        except UnicodeDecodeError:
            cliente.sendall(f"[!] Até logo... [!]\n".encode('utf-8'))
            apelido = procura_cliente_apelido(cliente)
            apelidos.remove(apelido)
            deleta_cliente(cliente)
            del usuarios[cliente]
            cliente.shutdown(1)
            cliente.close()
            print(f"[!] Usuário {apelido} foi Desconectado por CTRL + C [!]\n")
            break
        except BaseException as e:
            pass

def broadcast(msg, cliente):
    user = procura_cliente_apelido(cliente)
    msg_true = ("@"+str(user) + msg.rjust(pos) + '\n\r')
    for clientes_sala in salas.values():
        if cliente in clientes_sala:
            for cliente_item in clientes_sala:
                if cliente_item != cliente:
                    try:
                        cliente_item.send((msg_true + '>').encode('utf-8'))
                    except:
                        print(f"[!] Erro ao realizar o Broadcast da mensagem [!]\n")
                        deleta_cliente(cliente_item)
            break

def deleta_cliente(cliente):
    for clientes_sala in salas.values():
        if cliente in clientes_sala:
            clientes_sala.remove(cliente)
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"[!] Servidor Encerrado [!]")
        print(f"[!] Até logo... [!]")
        sys.exit()