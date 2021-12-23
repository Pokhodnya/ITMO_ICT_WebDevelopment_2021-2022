import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((socket.gethostname(), 8888))
s.listen(1)

while True:
    try:
        client_socket, addr = s.accept()
        print(f"Connection to {addr} done!")
        data = list(client_socket.recv(2048).decode('utf-8').split(' '))
        a, h = int(data[0]), int(data[1])
        p_sqr = a * h
        p_sqr = str(p_sqr)
        client_socket.send(bytes("Площадь параллелограмма равна " + p_sqr, "utf-8"))
    except KeyboardInterrupt:
        s.close()
        break 