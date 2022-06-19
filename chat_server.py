from datetime import datetime
import threading
import socket
import os
import sys
import hashlib

PORT = 8080
width = os.get_terminal_size().columns
pos = round(width/2)
usuarios = dict()
apelidos = list()
salas = {"sala_geral": [], "sala01": []}
ADMIN_HASHED_PASSWD = hashlib.sha256('adminpassword'.encode('utf-8')).hexdigest()

lista_comandos = b'\nComandos\n'\
				+ b'/criar Para criar uma sala\n'\
				+ b'/entrar Para entrar em uma sala\n' \
                + b'/listar Para listar as salas disponiveis\n' \
                + b'/LISTUSERS Para listar os usuarios conectados\n' \
                + b'/LISTBANNED Para listar os usuarios banidos\n' \
                + b'/deletar Para deletar uma sala\n'\
                + b'/TIME Para mostrar o horario atual\n' \
                + b'/BAN  Para banir um usuario\n' \
                + b'/UNBAN Para desbanir um usuario do servidor\n' \
				+ b'/LEAVE Para sair da sala\n' \
				+ b'/sair Para encerrar a conexao com o servidor\n' \
				+ b'/KICK Para kickar um usuario da sala\n' \
                + b'/HELP Para exibir a lista de comandos disponiveis\n' \
				+ b'\n'

def ajuda(cliente):
    cliente.sendall(lista_comandos)


def lista_salas(cliente):
    response = "Salas disponíveis: \n"
    for sala, clientes_sala in salas.items():
        response = "\n[+] Usuário na sala:\n"
        response += f"[+]{sala} : {len(clientes_sala)} Usuários\n"
    cliente.sendall(response.encode('utf-8'))

"""
def list_users(cliente):
    if len(apelidos) != 0 :
        response = "\n[+] Usuários Conectados:\n"
        for apelido in apelidos:
            response += f"[+] {apelido} "
            response += "\n"
        client.sendall(response.encode('utf-8'))
    else:
        response = "[!] Não existem usuários conectados[!]\n"
        client.sendall(response.encode("utf-8"))
"""

"""
def list_banned_users(cliente):
    with open('bans.txt', 'r') as f:
        data = f.readlines()
        f.close()
        banned_users = [line.strip("\n") for line in data]
        if len(banned_users) == 0:
            response = "[!] Não existem usuários Banidos [!]\n"
            cliente.sendall(response.encode("utf-8"))
        else:
            banned_user_list = "\n[+] Lista de usuarios Banidos [+]\n"
            for users in banned_users:
                banned_user_list += f"[+] {users}"
                banned_user_list += "\n"
            cliente.sendall(banned_user_list.encode('utf-8'))  
"""

def entrar(cliente):
    cliente.sendall("\n[+] Salas disponíveis:\n".encode('utf-8'))
    for keys in salas:
        cliente.sendall(f"-> {keys}\n".encode('utf-8'))
    cliente.sendall("[+] Deseja entrar em qual sala: ".encode('utf-8'))
    nome_sala = cliente.recv(1024).decode('utf-8')
    nome_sala = nome_sala.replace("\n", "").replace("\r", "")
    try:
        sala_origem = find_client_room(cliente)
        salas[nome_sala].append(cliente)
        salas[sala_origem].remove(cliente)
        cliente.sendall(f"[!] Bem vindo a sala {nome_sala} [!]\n".encode('utf-8'))
    except:
        response = "[!] Essa sala não existe no servidor [!]\n"
        cliente.sendall(response.encode('utf-8'))


def sair(cliente):
    try:
        cliente.sendall("[+] Tem certeza que deseja sair da sala? (sim/nao) ".encode('utf-8'))
        resposta = cliente.recv(1024).decode('utf-8')
        resposta = resposta.replace("\n", "").replace("\r", "")
        if resposta.lower() == 'sim':
            sala_origem = find_client_room(cliente)
            salas["sala_geral"].append(cliente)
            salas[sala_origem].remove(cliente)
            cliente.sendall(f"[+] Você saiu da sala {sala_origem} e está no Lobby!\n".encode('utf-8'))
        else:
            pass
    except:
        response = "[!] Erro ao sair da sala [!]\n"
        cliente.sendall(response.encode("utf-8"))

def criar_sala(cliente):
    sala_origem = find_client_room(cliente)
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


def find_client_room(cliente):
    for sala, clientes_sala in salas.items():
        if cliente in clientes_sala:
            return sala

def find_nickname_client(cliente):
    apelido_usuario = usuarios[cliente]['apelido']
    return apelido_usuario


def find_client_nickname(apelidos):
    for con, usuario in usuarios.items():
        for keys in usuario.items():
            if apelidos in keys:
                usuario_cliente = con
    return usuario_cliente


def check_password(cliente, senha):
    senha.encode('utf-8')
    hashed_passwd = hashlib.sha256(senha.encode('utf-8')).hexdigest()
    if hashed_passwd == usuarios[cliente]['password'] or hashed_passwd == ADMIN_HASHED_PASSWD:
        return True
    else:
        return False

"""
def ban_user(client):
    while True:
        client.sendall("[+] Digite a senha de ADMIN: ".encode('utf-8'))
        psswd = client.recv(1024).decode('utf-8')
        psswd = psswd.replace("\n", "").replace("\r", "")
        checked_psswd = check_password(client, psswd)
        if checked_psswd == True:
            client.sendall("[+] Digite o nome do usuário que será banido: ".encode('utf-8'))
            user = client.recv(1024).decode('utf-8')
            user = user.replace("\n", "").replace("\r", "")
            with open('bans.txt', 'a') as f:
                f.write(f'{user}\n')
                f.close()
            client.sendall((Fore.RED + f'[!] O usuário {user} foi banido do chat [!]\n' + Style.RESET_ALL).encode('utf-8'))
            print(Fore.RED + f'[!] O usuário {user} foi banido do chat [!]\n' + Style.RESET_ALL)
            break
        else:
            client.sendall((Fore.RED + "[!] Senha incorreta [!]\n" + Style.RESET_ALL).encode('utf-8'))
            continue

def unban_user(client):
    while True:
        client.sendall("[+] Digite a senha de ADMIN: ".encode('utf-8'))
        psswd = client.recv(1024).decode('utf-8')
        psswd = psswd.replace("\n", "").replace("\r", "")
        checked_psswd = check_password(client, psswd)
        if checked_psswd == True:
            client.sendall("[+] Digite o nome do usuário que será desbanido: ".encode('utf-8'))
            user = client.recv(1024).decode('utf-8')
            user = user.replace("\n", "").replace("\r", "")
            with open("bans.txt", "r+") as f:
                data = f.readlines()
                f.truncate(0)
                f.close()
                wr_name = False
                with open("bans.txt", "w") as f:
                    for line in data :
                        if line == user+"\n":
                            wr_name = True
                            try:
                                data.remove(line)
                                for names in data:
                                    f.write(names)
                                f.close()
                            except Exception as e:
                                client.sendall((Fore.RED + f"[!] Erro ao gravar no arquivo [!]\n" + Style.RESET_ALL).encode('utf-8'))
                                print(Fore.RED + (f"[!] Erro {e} ao gravar no arquivo [!]\n") + Style.RESET_ALL)
                    if wr_name == False :
                        client.sendall((Fore.GREEN + f"[!] Usuário {user} não está na lista de banimento [!]\n" + Style.RESET_ALL).encode('utf-8'))
                        break
                client.sendall((Fore.GREEN + f"[!] Usuário {user} foi desbanido do chat [!]\n" + Style.RESET_ALL).encode('utf-8'))
                print(Fore.GREEN + (f"[!] O Usuário {user} foi Desbanido do servidor [!]\n") + Style.RESET_ALL)
                break
        else:
            client.sendall((Fore.RED + "[!] Senha incorreta [!]\n" + Style.RESET_ALL).encode('utf-8'))
            continue



def kick_user(client):
    while True:
        client.sendall("[+] Digite a senha de ADMIN: ".encode('utf-8'))
        psswd = client.recv(1024).decode('utf-8')
        psswd = psswd.replace("\n", "").replace("\r", "")
        checked_psswd = check_password(client, psswd)
        if checked_psswd == True:
            client.sendall("[+] Digite o nick do usuario que sera kickado:".encode('utf-8'))
            kick_user = client.recv(2046).decode('utf-8')
            kick_user = kick_user.replace("\n", "").replace("\r", "")
            user_con = find_client_nickname(kick_user)
            origin_room = find_client_room(user_con)
            rooms["Lobby"].append(user_con)
            rooms[origin_room].remove(user_con)
            client.sendall((Fore.RED + f"[!] Usuário {kick_user} foi Kickado da sala {origin_room} [!]\n" + Style.RESET_ALL).encode('utf-8'))
            user_con.sendall((Fore.RED + f"[!] Você foi Kickado da sala {origin_room} [!]\n"+ Style.RESET_ALL).encode('utf-8'))
            print(Fore.RED + (f"[!] O Usuário {kick_user} foi kickado da sala {origin_room} [!]\n") + Style.RESET_ALL)
            break
        else:
            client.sendall((Fore.RED + "[!] Senha incorreta [!]\n" + Style.RESET_ALL).encode('utf-8'))
            continue

def time(client):
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    client.sendall((Fore.BLUE + "[!] Always on time... [!]\n" + Style.RESET_ALL).encode('utf-8'))
    client.sendall(f"[+] Horario atual: {current_time}\n".encode('utf-8'))
"""

def sair_do_servidor(cliente):
    cliente.sendall("[+] Tem certeza que deseja sair do servidor? (sim/nao) ".encode('utf-8'))
    resposta = cliente.recv(1024).decode('utf-8')
    resposta = resposta.replace("\n", "").replace("\r", "")
    if resposta.lower() == 'sim':
        while True:
            cliente.sendall("[+] Digite sua senha: ".encode('utf-8'))
            senha = cliente.recv(1024).decode('utf-8')
            senha = senha.replace("\n", "").replace("\r", "")
            senha_checada = check_password(cliente, senha)
            if senha_checada == True:
                cliente.sendall(f"[!] Até logo... [!]\n".encode('utf-8'))
                apelido = find_nickname_client(cliente)
                apelidos.remove(apelido)
                sala_origem = find_client_room(cliente)
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


def unique_nickname(apelido, cliente):
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
        "action": "/help",
        "function": help,
    },
    {
        "action": "/entrar",
        "function": entrar,
    },
    {
        "action": "/sair",
        "function": sair,
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


def is_valid_command(msg, cliente):
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
        apelido = unique_nickname(apelido, cliente)
        
        
        cliente.sendall("[+] Nome Completo: ".encode('utf-8'))
        full_name = cliente.recv(1024).decode('utf-8')
        full_name = full_name.replace("\n", "").replace("\r", "")

        cliente.sendall("[+] Senha: ".encode('utf-8'))
        passwd = cliente.recv(1024).decode('utf-8')
        passwd = passwd.replace("\n", "").replace("\r", "")
        hash_passwd  = hashlib.sha256(passwd.encode('utf-8')).hexdigest()   

        with open('bans.txt', 'r') as f:
            bans = f.readlines()

        if apelido+"\n" in bans:
            cliente.send('[!] Você foi banido do servidor [!]\n'.encode('utf-8'))
            cliente.close()
            print(f"[!] O Usuário {apelido} foi Banido e tentou se conectar [!]\n")
        else:
            apelidos.append(apelido)
            salas["sala_geral"].append(cliente)
            usuario = {} 
            usuario["apelido"] = apelido
            usuario["con"] = cliente
            usuario["full_name"] = full_name
            usuario["password"] = hash_passwd
            usuarios[cliente] = usuario
            help(cliente)
            print(f"[+] Usuário {full_name} com o Nickname {apelido} conectado ao servidor [!]\n")
        
        thread = threading.Thread(target=messages_treatment, args=[cliente])
        thread.start()


def messages_treatment(cliente):
    while True:
        try:
            msg = cliente.recv(2048).decode('utf-8')
            msg = msg.replace("\n", "").replace("\r", "")
            try:
                has_command = is_valid_command(str(msg), cliente)
                if has_command == False:
                    broadcast(msg, cliente)
            except:
                delete_client(cliente)
                break
        except UnicodeDecodeError:
            cliente.sendall(f"[!] Até logo... [!]\n".encode('utf-8'))
            apelido = find_nickname_client(cliente)
            apelidos.remove(apelido)
            delete_client(cliente)
            del usuarios[cliente]
            cliente.shutdown(1)
            cliente.close()
            print(f"[!] Usuário {apelido} foi Desconectado por CTRL + C [!]\n")
            break
        except BaseException as e:
            pass

def broadcast(msg, cliente):
    user = find_nickname_client(cliente)
    msg_true = ("@"+str(user) + msg.rjust(pos) + '\n\r')
    for clientes_sala in salas.values():
        if cliente in clientes_sala:
            for cliente_item in clientes_sala:
                if cliente_item != cliente:
                    try:
                        cliente_item.send((msg_true + '>').encode('utf-8'))
                    except:
                        print(f"[!] Erro ao realizar o Broadcast da mensagem [!]\n")
                        delete_client(cliente_item)
            break

def delete_client(cliente):
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