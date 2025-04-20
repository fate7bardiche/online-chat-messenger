import sys
sys.path.append('..')

import socket
import threading
import os
import signal
from packages import config
token = ""
user_name = ""
chat_room_name = ""



def udp_setup():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return sock

# UDP
def udp_flow(sock: socket.socket):

    print("token is ", token)
    print("user_name is ", user_name)
    print("chat_room_name is ", chat_room_name)

    try:
        sock.connect((config.udp_server_address, config.udp_server_port))
    except socket.error as err:
        print(err)
        sys.exit(1)

    # チャットルームに初回参加(作成し参加、　参加のいずれかを問わず)した際のメッセージ送信
    # 一度メッセージを送信することで、サーバー側にudp_のaddressが保存される
    first_join_request_message = f'{user_name} : {chat_room_name} に参加しました。'
    print(first_join_request_message)
    first_join_request_data = create_udp_protocol(first_join_request_message)
    sock.send(first_join_request_data)

    # sock.send(protocol_header(len(user_name)) + (user_name).encode())

    # stop_event = threading.Event()

    input_message_thread =  threading.Thread(target=input_message, args=(sock, ), daemon=True)
    receive_message_thread =  threading.Thread(target=receive_message, args=(sock, ), daemon=True)
    input_message_thread.start()
    receive_message_thread.start()
    input_message_thread.join()
    receive_message_thread.join()

    # joinしないパターンを試してみる

# def print_message(bytes_data: bytes):
#     user_name_len = int.from_bytes(bytes_data[:1], "big")
#     user_name = bytes_data[1:user_name_len + 1].decode()
#     message = bytes_data[user_name_len + 1:].decode()
#     print(f"{user_name}: {message}")

# def input_worker(result_queue: queue.Queue):
#     global now_input_message
#     print("in worker")
#     message = input(f'{user_name} > ')
#     print("before put")
#     result_queue.put(message)
#     print("after put")
#     now_input_message = False
#     return message

def input_message(sock: socket.socket):
    while True:
        message = input(f'{user_name} > ')
        print("after input thread start")
    
        # message = result_q.get()
        print("\033[1A\033[2K", end="")
        request_message = f"{user_name} : {message}"

        request_data = create_udp_protocol(request_message)

        sock.send(request_data)
        
        socket.timeout(2)
        
        # print("インプットのループ確認")
        

def receive_message(sock: socket.socket):
    global flow_state
    
    while True:
        # クライアントが受信するデータにはヘッダーは存在しない。
        # 送信時のデータのヘッダーが2バイトで、その2を引いた4094をクライアントは受信する。
        response_data = sock.recv(4094)

        response_message = response_data.decode()

        # header, body = decode_udp_protocol(response_data)
        # chat_room_name_length, token_length = decode_udp_protocol_header(header)

        if(config.exit_chat_room_flag_str in response_message):
            exit_message = response_message.replace(config.exit_chat_room_flag_str, "")
            print("\033[2K\r", end="")
            print(exit_message)

            sock.close()
            # 本当は入力受付と、受信受付それぞれのスレッドを終わらせて、TCPのフローに戻したい。
            os.kill(os.getpid(), signal.SIGKILL)

            break
        else:
            print("\033[2K\r", end="")
            print(response_message)
        # print_message(response_message)

def create_udp_protocol(message: str):
    chat_room_name_bits = chat_room_name.encode()
    token_bits = token.encode()
    header = create_udp_header(len(chat_room_name_bits), len(token_bits))
    body = chat_room_name_bits + token_bits + message.encode()
    return header + body

def create_udp_header(room_name_length: int, token_length: int):
    return room_name_length.to_bytes(1, "big") + token_length.to_bytes(1, "big")

# def decode_udp_protocol(data: bytes):
#     header = data[:2]
#     body = data[2:]
#     return header, body

# def decode_udp_protocol_header(header: bytes):
#     chat_room_name_length = int.from_bytes(header[:1], "big")
#     token_length = int.from_bytes(header[1:], "big")
#     return chat_room_name_length, token_length

# def decode_udp_protocol_body(body: bytes, chat_room_name_length: int, token_length: int):
#     response_chat_room_name = body[:chat_room_name_length].decode()
#     response_token = body[chat_room_name_length:token_length].decode()
#     message = body[token_length:].decode()
#     return response_chat_room_name, response_token, message











# TCP
def tcp_flow():
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # サーバー側に揃える
    try:
        tcp_sock.connect((config.tcp_server_address, config.tcp_server_port))
    except socket.error as err:
        print(err)
        sys.exit(1)



    while True:
        global chat_room_name
        global user_name

        state = 0
    
        request = input_flow()
        tcp_sock.send(request)

        tcp_sock.settimeout(2)

        res_header, res_body = decode_protocol(tcp_sock.recv(4096))
        room_name_length, operation, state, payload_length = decode_protocol_header(res_header)
        chat_room_name, payload = decode_protocol_body(res_body, room_name_length, payload_length)


        print(f"ステータスコードは{payload}です。")

        res_header, res_body = decode_protocol(tcp_sock.recv(4096))
        room_name_length, operation, state, payload_length = decode_protocol_header(res_header)
        chat_room_name, payload = decode_protocol_body(res_body, room_name_length, payload_length)

        if config.error_flag_str in payload:
            print(payload.replace(config.error_flag_str, ""))
            continue

        print(f"{payload} トークンを受け取りました。")
        global token
        token = payload
        chat_room_name = chat_room_name
        print(f"{chat_room_name} チャットルームに参加しました。")
        break
    tcp_sock.close()


def input_flow():
    global user_name

    while True:

        room_name = input("チャットルーム名を入力してください > ")
        user_name = input("ユーザー名を入力してください > ")
        operation = input("オペレーションの数字を入力してください。 作成: 1, 参加: 2  > ")
        if not operation in ["1", "2"]:
            print("オペレーションは選択肢の中から選んでください。")
            continue

        state = 0
        header = create_tcp_header(len(room_name.encode()), int(operation), state, len(user_name.encode()))
        body = room_name.encode() + user_name.encode()

        break
    return header + body

def decode_protocol(data: bytes):
    header = data[:32]
    body = data[32:]
    return header, body

def decode_protocol_header(header: bytes):
    room_name_length = int.from_bytes(header[:1], "big")
    operation = int.from_bytes(header[1:2], "big")
    state = int.from_bytes(header[2:3], "big")
    payload_length = int.from_bytes(header[3:33], "big")
    return room_name_length, operation, state, payload_length

def decode_protocol_body(body: bytes, room_name_length: int, payload_length: int):
    room_name = body[:room_name_length].decode()
    print(room_name)
    print(payload_length)
    operation_payload = body[room_name_length:].decode()
    print(operation_payload)
    return room_name, operation_payload

def create_tcp_header(room_name_length: int, opr: int, state_length: int, payload_length: int):
    return room_name_length.to_bytes(1, "big") + opr.to_bytes(1, "big") + state_length.to_bytes(1, "big") + payload_length.to_bytes(29, "big")

def on_finish(sock: socket.socket):
    request = create_udp_protocol(config.exit_chat_room_flag_str)
    sock.send(request)
    print("チャットルームから退出しました")


def finish_handler(udp_sock: socket.socket):
    on_finish(udp_sock)
    sys.exit()

def main():
    tcp_flow()

    udp_sock = udp_setup()
    signal.signal(signal.SIGTERM, lambda a, b: finish_handler(udp_sock))
    signal.signal(signal.SIGINT, lambda a, b: finish_handler(udp_sock))
    udp_flow(udp_sock)


    
if __name__ == "__main__":
    main()

    # TCPかUDP、どちらのフローを表示するのかに、stateでSwitch的に切り替えるパターン