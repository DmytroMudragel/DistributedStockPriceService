 
from rpyc import connect
from time import sleep

if __name__ == "__main__":
    sleep(10)
    server_ip = "server"
    server_port = 4242

    for i in range(1, 4):
        conn = connect(server_ip + str(i), int(server_port) + i - 1)
        try:
            conn.root.stop_server()
        except EOFError:
            pass
