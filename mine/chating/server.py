import socket
import threading

PORT = 5050
HEADER = 64
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DIS = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

def hand(con, addr):
    print(f"[NEW CONNECTION] {addr} connected")
    connected = True
    while connected:
        msg_LEN = con.recv(HEADER).decode(FORMAT)
        if msg_LEN:
            msg_LEN = int(msg_LEN.strip())  # Fixed: properly parse header to int
            msg = con.recv(msg_LEN).decode(FORMAT)
            if msg == DIS:
                connected = False
            print(f"[{addr}, {msg}]")
            con.send("[Msg Received]".encode(FORMAT) )

    con.close()

def start():
    server.listen()
    print(f"[LISTENING] server is listening on {SERVER}]")
    while True:
        con, addr = server.accept()
        thread = threading.Thread(target=hand, args=(con, addr))
        thread.start()
        threading.active_count()  # Includes this thread now
        print(f"[Active] {threading.active_count() - 1}")

print("Server Starting")
start()
