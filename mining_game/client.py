import socket
import pygame
from os import system, mkdir
from os.path import exists
from platform import platform
from random import random
from json import dump, dumps, loads
from threading import Thread

OS = platform()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

window = None

account_data = {
    "username": f"User_{int(random()*(10**17))}",
    "pos": [300, 300],
    "vel": [0, 0],
    "moving": False,
    "jump": False
}

class Server_setings:
    block_id_offset = 64
    
pygame.init()
pygame.font.init()

class Events:
    class mouse:
        c = False,
        h = False,
        b = 0,
        p = (0, 0)
    class keyboard:
        c = False,
        h = False,
        k = pygame.key.get_pressed()
        
def generate_map(layers):
    map = []
    
    for layer in range(layers):
        print(f"Creating layer {layer}/{layers}")
        map.append([chr(1+Server_setings.block_id_offset) for _ in range(16)])
    
    m = ""
    
    for c in map:
        for b in c:
            m += b
        m += "-"
        
    return m
        
def server_init():
    if not exists("server"):
        mkdir("server")
    with open("server/map", "w") as f:
        f.write(generate_map(32))
        print("Made server map file")
        
class Connection:
    ci = 0
    def __init__(self, c, i):
        self.s = c[0]
        self.a = c[1]
        self.i = i
        self.au = False
        self.ig = False
        self.d = None
    def recv(self):
        global players
        
        try:
            return loads(self.s.recv(1024).decode())
        except:
            players[self.i] = {"username": None}
            self.s.close()
            return False
    def send(self, d):
        self.s.send(dumps(d).encode())
        
players = []
map = []
decoded_map = []
scroll = 0


def decode_map():
    global decoded_map
    
    decoded_map = []
    
    b = 0
    c = 0
    
    while True:
        if b > (len(map)/16)-1 and c > (len(map[len(map)-1]))-1:
            break
        match map[c]:
            case "A":
                i = pygame.transform.scale(pygame.image.load("blocks/stone.png"), (50, 500))
                id = "stone"
                p = False
            case "-":
                b += 1
                c = 0
                p = True
                id = "newline"
                i = pygame.transform.scale(pygame.image.load("blocks/air.png"), (50, 50))
            case _:
                i = pygame.transform.scale(pygame.image.load("blocks/air.png"), (50, 50))
                p = True
                id = "air"
                    
        decoded_map.append({"pos": (c*50, b*50), "img": i, "p": p, "id": id})
        c += 1
            
def handle_connection(s, id):
    global players
    
    print(f"[Server] [HC] Client with ID {id} joined your game.")
    while True:
        d = s.recv()
        if not d:
            break
        if not s.au and d['t'] == "auth":
            players[id] = d['d']
            s.au = True
            print(f"[Server] [HC] {d['d']['username']} joined.")
            s.send({"t": "map", "d": map})
        if s.au and d['t'] == "loop":
            players[id] = d['d']
            s.send({"t": "loop", "d": {"map": map, "players": players}})
                    
    Connection.ci -= 1
    
    print(f"[Server] [HC] Client {id} left your game")
        
def listen_connections():
    while True:
        thread_hc = Thread(target=handle_connection, args=(Connection(sock.accept(), Connection.ci), Connection.ci))
        thread_hc.daemon = True
        thread_hc.start()
        Connection.ci += 1
        
def start_server():
    print("[Server] [Startup] Starting thread LC...")
    thread_lc = Thread(target=listen_connections)
    thread_lc.daemon = True
    thread_lc.start()
    print("[Server] [Startup] Started thread LC.")
    while True:
        command = input("").lower()
        if command == "stop":
            break
        
connected = False
    
def send(s, d):
    if connected:
        s.send(dumps(d).encode())
    else:
        return False
def recv(s):
    if connected:
        return loads(s.recv(1024).decode())
    else:
        return False

def connect(s):
    global map
    print("[Client] sending authorization stuff")
    send(s, {"t": "auth", "d": account_data})
    print("[Client] Downloading map...")
    map = recv(s)
    print("[Client] Downloaded map.")
    
max_speed, speed_decrease, speed_increase = 10, 1.2, 0.7
fall = True
ml, mr, cmr, cml = False, False, True, True
    
def update_player():    
    global fall, ml, mr, cmr, cml
    account_data['moving'] = False
        
    
    if Events.keyboard.k[pygame.K_UP]:
        if not account_data['jump'] and fall:
            account_data['jump'] = True
            account_data["vel"][1] = 15
            
    if Events.keyboard.k[pygame.K_LEFT]:
        account_data['vel'][0] -= speed_increase
        account_data['moving'] = True
        ml = True
            
    if Events.keyboard.k[pygame.K_RIGHT] and cmr:
        account_data['vel'][0] += speed_increase
        account_data['moving'] = True
        mr = True
            
    if not account_data['moving']:
        if account_data['vel'][0] > 0:
            account_data['vel'][0] -= 1
        if account_data['vel'][0] < 0:
            account_data['vel'][0] += 1
            
        if 1 > abs(account_data['vel'][0]) > 0:
            account_data['vel'][0] = 0
    
    if not account_data['jump']:
        if account_data['pos'][1] < window.get_height()-32:
            account_data['jump'] = True
            
    if account_data['pos'][1] > window.get_height()-32:
        account_data['pos'][1] = window.get_height()-32
        account_data['vel'][1] = 0
    
    if account_data['jump']:
        if account_data['pos'][1] >= window.get_height()-32:
            account_data['jump'] = False
        account_data['vel'][1] -= 1
        
    if account_data['vel'][0] > max_speed:
        account_data['vel'][0] = max_speed
    elif account_data['vel'][0] < -max_speed:
        account_data['vel'][0] = -max_speed
        
    if account_data['pos'][0] > window.get_width()-40:
        account_data['pos'][0] = window.get_width()-40
    elif account_data['pos'][0] < 8:
        account_data['pos'][0] = 8
        
    for b in decoded_map:
        if not b['p']:
            if b['pos'][0] + 50 > account_data['pos'][0] > b['pos'][0] - 25 and account_data['pos'][1] < (b['pos'][1]+(window.get_height()-50))-(scroll*50) < account_data['pos'][1] + 50:
                if account_data['vel'][1] < 0:
                    account_data['pos'][1] = (b['pos'][1]+(window.get_height()-50))-(scroll*50)
                    account_data['vel'][1] = 0
                    print(f"'{map}'\n\n")
        
    account_data['pos'][1] -= account_data['vel'][1]
    account_data['pos'][0] += account_data['vel'][0]
    
def draw():
    window.fill("white")
    
    update_player()
    
    window.blit(pygame.font.SysFont('Arial', 20).render(account_data['username'], False, (0, 0, 0)), (account_data['pos'][0], account_data['pos'][1]-20))
    pygame.draw.rect(window, "blue", (account_data['pos'][0], account_data['pos'][1], 32, 32))
            
    for p in players:
        if not p['username'] in [None, account_data['username']]:
            window.blit(pygame.font.SysFont('Arial', 20).render(p['username'], False, (0, 0, 0)), (p['pos'][0], p['pos'][1]-20))
            pygame.draw.rect(window, "red", (p['pos'][0], p['pos'][1], 32, 32))
            
    for b in decoded_map:
        window.blit(b['img'], (b['pos'][0], (b['pos'][1]+(window.get_height()-50))-(scroll*50)))

def start_GUI():
    global window
    
    window = pygame.display.set_mode((800, 600))
    run = True
    clock = pygame.time.Clock()
    while run:        
        Events.keyboard.c = False
        Events.keyboard.k = pygame.key.get_pressed()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEMOTION:
                Events.mouse.p = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONDOWN:
                Events.mouse.c = True
                Events.mouse.h = True
                Events.mouse.b = pygame.mouse.get_pressed()
            if event.type == pygame.MOUSEBUTTONUP:
                Events.mouse.h = False
            if event.type == pygame.KEYDOWN:
                Events.keyboard.c = True
                Events.keyboard.h = True
            if event.type == pygame.KEYUP:
                Events.keyboard.h = False
        
        clock.tick(60)
        draw()
        pygame.display.update()
    pygame.quit()
    
def handle_conn(s):
    global players
    global map
    
    print("[Client] Starting connection loop...")
    send(s, {"t": "loop", "d": account_data})
    while True:
        d = recv(s)
        if not d:
            break
        players = d['d']['players']
        map = d['d']['map']
        decode_map()
        send(s, {"t": "loop", "d": account_data})
    
def join_server(s):
    print("[Client] joining server...")
    connect(s)
    thread_hc = Thread(target=handle_conn, args=(s,))
    thread_hc.daemon = True
    thread_hc.start()
    start_GUI()
    
def main():
    global map
    global players
    global connected
    global sock
    
    print("Welcome to mining game!\n")
    
    while True:
        command = input("> ")
        match command.lower():
            case "create_server":
                server_init()
            case "start_server":
                mx = int(input("max connections: "))
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                players = [{"username": None} for _ in range(mx)]
                ip = "127.0.0.1"
                port = "25565"
                
                sock.bind((ip, int(port)))
                sock.listen(mx)
                
                print(f"Starting a server on IP {ip}:{port}")
                
                with open("server/map", "r") as f:
                    map = f.read()
                    
                start_server()
                sock.close()
                
                print("[Server] Closed.")
            case "join_server":
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                ip = "127.0.0.1"
                port = "25565"
                
                sock.connect((ip, int(port)))
                connected = True
                
                pygame.init()
                pygame.font.init()
                
                join_server(sock)
                connected = False
                
                sock.close()
                print("[Client] You left the game.")
            case "set_user":
                account_data[input("Change: ")] = input("To: ")
            case "view_account_data":
                print(account_data)
            case "exit":
                break
            case _:
                print("Command not found")
                    
main()