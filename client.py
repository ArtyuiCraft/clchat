import curses
import socket
import threading
import requests
from configparser import ConfigParser
import time

config = ConfigParser()

HEADER = 2048
FORMAT = 'utf-8'
DISCONNECT = "_!499!_"
STOP = "_!410!_"
NAME = input("name? ")

GITSERVER = input("server? ")
GITSERVER = "https://raw.githubusercontent.com/" + GITSERVER + "/main/server.ini"
SETTINGS = requests.get(GITSERVER)
config.read_string(SETTINGS.text)

PORT = config.get('network','port')
SERVER = config.get('network','ip')
ADDR = (SERVER, int(PORT))
print(ADDR)
print(f"joining {config.get('server','name')}...")
time.sleep(1)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)


# Function to receive messages from the server
def receive_messages(stdscr, client):
    while True:
        msg_length = client.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = client.recv(msg_length).decode(FORMAT)
            add_message(stdscr,msg)

# Function to add a message to the window
def add_message(stdscr, message):
    max_y, max_x = stdscr.getmaxyx()
    if len(message) > max_x - 3:
        message = message[:max_x - 6] + "..."
    messages.append(message)
    if len(messages) > max_y - 3:
        messages.pop(0)
    redraw(stdscr)

# Function to redraw the window
def redraw(stdscr):
    stdscr.clear()
    max_y, max_x = stdscr.getmaxyx()
    for i, message in enumerate(messages):
        stdscr.addstr(max_y - 3 - len(messages) + i, 0, message)
    stdscr.addstr(max_y - 1, 0, "input> " + input_buffer)
    stdscr.refresh()

# Function to send messages to the server
def send(client, msg):
    if msg == ":q":
        send(client,DISCONNECT)
        exit()
    #elif msg == ":stop":
    #    send(client,STOP)
    #    send(client,DISCONNECT)
    #    exit()
    msg = msg.encode(FORMAT)
    msg_length = len(msg)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(msg)

# Main function
def main(stdscr):
    global input_buffer
    input_buffer = ""
    stdscr.clear()
    curses.echo()
    while True:
        stdscr.clear()
        redraw(stdscr)
        c = stdscr.getch()
        if c == ord('\n'):
            send(client, input_buffer)
            input_buffer = ""
        elif c == curses.KEY_BACKSPACE or c == 127:
            input_buffer = input_buffer[:-1]
        else:
            input_buffer += chr(c)

# Initialize ncurses
stdscr = curses.initscr()
curses.cbreak()
curses.noecho()
stdscr.keypad(True)

# Start receiving messages from the server in a separate thread
messages = []
receive_thread = threading.Thread(target=receive_messages, args=(stdscr, client))
receive_thread.start()

send(client,NAME)

# Start the main loop
try:
    main(stdscr)
finally:
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()
