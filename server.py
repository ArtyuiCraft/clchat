import socket
import threading
from configparser import ConfigParser
import os
from datetime import datetime
from time import strftime, gmtime

os.system('cls' if os.name == 'nt' else 'clear')

HEADER = 2048
FORMAT = 'utf-8'
DISCONNECT = "_!499!_"
STOP = "!_410_!"

#open server.ini file
config = ConfigParser()
if os.path.isfile("server.ini"):
    config.read('server.ini')
    #get values from server.ini
    PORT = config.get('network','port')
    SERVER = config.get('network','ip')
    NAME = config.get('server','name')
    ADDR = (SERVER, int(PORT))
else:
    #if server.ini does not exist create
    while True:
        print("first setup")
        PORT = input("PORT: ")
        NAME = input("server name: ")
        SERVER = socket.gethostbyname(socket.gethostname())
        ADDR = (SERVER, int(PORT))
        os.system('cls' if os.name == 'nt' else 'clear')
        print("are these options correct?")
        print("port: "+PORT)
        print("name: "+NAME)
        if input("y/n: ").lower() == "y":
            os.system('cls' if os.name == 'nt' else 'clear')
            break

    #save to file
    conf = f'''[network]
port = {PORT}
ip = {SERVER}

[server]
name = {NAME}'''
    open('server.ini','w').write(conf)

print(f"({strftime('%d %b %Y %H:%M', gmtime())})[server] initialized with values:")
print("name:"+NAME)
print("IP:"+SERVER)
print("Port:"+PORT)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print(ADDR)
server.bind(ADDR)

clients = [] 

print(f"({strftime('%d %b %Y %H:%M', gmtime())})[server] initialized with values:")
print("name:"+NAME)
print("IP:"+SERVER)
print("Port:"+PORT)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

clients = [] 

def handle_client(conn, addr):
    print(f"({strftime('%d %b %Y %H:%M', gmtime())})[NEW CONNECTION] {addr} connected")
    send_to_all(f"({strftime('%d %b %Y %H:%M', gmtime())})[{addr}] connected")
    clients.append(conn)
    print("clients: ", clients)
    conn.recv(2048)
    CLIENTNAME = conn.recv(2048).decode(FORMAT)
    while True:
        try:
            msg_length = conn.recv(HEADER).decode(FORMAT)
            if msg_length:
                msg_length = int(msg_length)
                msg = conn.recv(msg_length).decode(FORMAT)
                if msg == DISCONNECT:
                    print(f"({strftime('%d %b %Y %H:%M', gmtime())})[{CLIENTNAME}] disconnected")
                    clients.remove(conn)
                    send_to_all(f"({strftime('%d %b %Y %H:%M', gmtime())})[{CLIENTNAME}] disconnected")
                    break
                if msg == STOP:
                    print("Server shutting down...")
                    server.close()
                    exit()
                print(f"({strftime('%d %b %Y %H:%M', gmtime())})[{CLIENTNAME}] {msg}")
                # Broadcast the message to all clients, including the sender
                send_to_all(f"({strftime('%d %b %Y %H:%M', gmtime())})[{CLIENTNAME}] {msg}")
        except ConnectionResetError:
            print(f"({strftime('%d %b %Y %H:%M', gmtime())})[{CLIENTNAME}] disconnected abruptly")
            clients.remove(conn)
            send_to_all(f"({strftime('%d %b %Y %H:%M', gmtime())})[{CLIENTNAME}] disconnected abruptly")
            break
    conn.close()

def send_to_all(msg):
    msg = msg.encode(FORMAT)
    msg_length = len(msg)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    for client in clients:
        client.send(send_length)
        client.send(msg)

def start():
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Set socket option
    server.listen()
    try:
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            print(f"({strftime('%d %b %Y %H:%M', gmtime())})[ACTIVE CONNECTIONS] {threading.active_count()}")
            thread.start()
    except KeyboardInterrupt:
        print("Server shutting down...")
        server.close()
        exit()

print(f"({strftime('%d %b %Y %H:%M', gmtime())})[server] is starting")
start()
