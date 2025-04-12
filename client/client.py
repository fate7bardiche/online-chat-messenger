import socket
import sys
import threading


# UDP
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
    server_port = 9002

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


# TCP
def tcp_flow():
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_address  = "0.0.0.0"
    server_port = 9001

    # サーバー側に揃える
    try:
        tcp_sock.connect((server_address, server_port))
    except socket.error as err:
        print(err)
        sys.exit(1)

    state = 0
    
    request = input_flow()
    tcp_sock.send(request)

    tcp_sock.settimeout(2)

    while True:
        res_header, res_body = parse_protocol(tcp_sock.recv(4096))
        room_name_length, operation, state, payload_length = parse_protocol_header(res_header)
        room_name, payload = parse_protocol_body(res_body, room_name_length, payload_length)
        if state == 1:
            print(f"ステータスコードは{payload}です。")
        if state == 2:
            print("トークンを受け取りました。")
            print(f"{room_name} チャットルームに参加しました。")
            break
    # tcp_sock.close()
    input_flow()


def input_flow():
    room_name = input("チャットルーム名を入力してください")
    user_name = input("ユーザー名を入力してください")
    operation = input("オペレーションの数字を入力してください。 作成→1, 参加→2")

    # tcp_sock.send(toriaezu.encode())
    # operation = 1
    state = 0
    header = create_tcp_header(len(room_name.encode()), int(operation), state, len(user_name.encode()))
    body = room_name.encode() + user_name.encode()
    return header + body

def parse_protocol(data: bytes):
    header = data[:32]
    body = data[32:]
    return header, body

def parse_protocol_header(header: bytes):
    room_name_length = int.from_bytes(header[:1], "big")
    operation = int.from_bytes(header[1:2], "big")
    state = int.from_bytes(header[2:3], "big")
    payload_length = int.from_bytes(header[3:33], "big")
    return room_name_length, operation, state, payload_length

def parse_protocol_body(body: bytes, room_name_length: int, payload_length: int):
    room_name = body[:room_name_length].decode()
    print(room_name)
    print(payload_length)
    operation_payload = body[room_name_length:].decode()
    print(operation_payload)
    return room_name, operation_payload

def create_tcp_header(room_name_length: int, opr: int, state_length: int, payload_length: int):
    return room_name_length.to_bytes(1, "big") + opr.to_bytes(1, "big") + state_length.to_bytes(1, "big") + payload_length.to_bytes(29, "big")

if __name__ == "__main__":
    # main()
    tcp_flow()
    print("finish!!!!")