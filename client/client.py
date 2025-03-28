import socket
import sys
import threading

def protocol_header(username_length):
    return int.to_bytes(username_length, 1, "big")

def print_message(bytes_data: bytes):
    user_name_len = int.from_bytes(bytes_data[:1], "big")
    user_name = bytes_data[1:user_name_len + 1].decode()
    message = bytes_data[user_name_len + 1:].decode()
    print(f"{user_name}: {message}")

def input_message(sock: socket, user_name: str):
    while True:
        message = input(f'{user_name} : > ')
        print("\033[1A\033[2K", end="")
        print(f"{user_name} : {message}")

        sock.send(protocol_header(len(user_name)) + (user_name + message).encode())
        
        socket.timeout(2)

def receive_message(sock: socket):
    while True:
        response_data = sock.recv(4096)
        print("\033[2K\r", end="")
        print_message(response_data)


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server_address  = "0.0.0.0"
    server_port = 9001

    try:
        sock.connect((server_address, server_port))
    except socket.error as err:
        print(err)
        sys.exit(1)

    print("接続しました。")

    user_name = input('ユーザーネームを入力してください。')

    print(f"{user_name}がチャットに参加しました。")

    sock.send(protocol_header(len(user_name)) + (user_name).encode())

    input_message_thread =  threading.Thread(target=input_message, args=(sock, user_name, ), daemon=True)
    receive_message_thread =  threading.Thread(target=receive_message, args=(sock, ), daemon=True)
    input_message_thread.start()
    receive_message_thread.start()
    input_message_thread.join()
    receive_message_thread.join()

if __name__ == "__main__":
    main()