import sys
sys.path.append('..')
import socket
import threading
import os
import signal
from packages import config
from interface import tcp_encoder, tcp_decoder
import udp_encoder

token = ""
user_name = ""
chat_room_name = ""


# UDP関係
def udp_setup():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return sock

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
    # サーバーがクライアントのudpのaddressを知らないと、リレーできない
    # 一度保存しておけば、参加しただけでも他のユーザーのメッセージが自分宛にリレーされる
    first_join_request_message = f'{user_name} : {chat_room_name} に参加しました。'
    print(first_join_request_message)
    first_join_request_data = udp_encoder.create_udp_protocol(chat_room_name, token, first_join_request_message)
    sock.send(first_join_request_data)

    input_message_thread =  threading.Thread(target=input_message, args=(sock, ), daemon=True)
    receive_message_thread =  threading.Thread(target=receive_message, args=(sock, ), daemon=True)
    input_message_thread.start()
    receive_message_thread.start()
    input_message_thread.join()
    receive_message_thread.join()

def input_message(sock: socket.socket):
    while True:
        message = input(f'{user_name} > ')
        print("\033[2K\r", end="")

        request_message = f"{user_name} : {message}"
        request_data = udp_encoder.create_udp_protocol(chat_room_name, token, request_message)
        sock.send(request_data)
        socket.timeout(2)
        

def receive_message(sock: socket.socket):
    while True:
        # クライアントが受信するデータにはヘッダーは存在しない。
        # 送信時のデータのヘッダーが2バイトあり、その2を引いた4094をクライアントは受信する。
        response_data = sock.recv(4094)
        response_message = response_data.decode()

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



# TCP関係
def tcp_flow():
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        tcp_sock.connect((config.tcp_server_address, config.tcp_server_port))
    except socket.error as err:
        print(err)
        sys.exit(1)

    while True:
        global chat_room_name
        global user_name
        global token
    
        request = input_flow()
        tcp_sock.send(request)
        tcp_sock.settimeout(2)

        res_header, res_body = tcp_decoder.decode_tcp_protocol(tcp_sock.recv(4096))
        room_name_length, operation, state, payload_length = tcp_decoder.decode_tcp_protocol_header(res_header)
        chat_room_name, payload = tcp_decoder.decode_tcp_protocol_body(res_body, room_name_length)


        if not state == 1:
            print("stateが1ではありません。サーバーからのレスポンスに問題がありました。最初からやり直してください。")
            continue
        print(f"ステータスコードは{payload}です。")

        res_header, res_body = tcp_decoder.decode_tcp_protocol(tcp_sock.recv(4096))
        room_name_length, operation, state, payload_length = tcp_decoder.decode_tcp_protocol_header(res_header)
        chat_room_name, payload = tcp_decoder.decode_tcp_protocol_body(res_body, room_name_length)

        if not state == 2:
            print("stateが2ではありません。サーバーからのレスポンスに問題がありました。最初からやり直してください。")
            continue

        if config.error_flag_str in payload:
            error_message = payload.replace(config.error_flag_str, "")
            print(error_message)
            continue
        
        token = payload
        chat_room_name = chat_room_name
        print(f"{payload} トークンを受け取りました。")
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
        header = tcp_encoder.create_tcp_header(len(room_name.encode()), int(operation), state, len(user_name.encode()))
        body = room_name.encode() + user_name.encode()

        break
    return header + body


def on_finish(sock: socket.socket):
    request = udp_encoder.create_udp_protocol(chat_room_name, token,  config.exit_chat_room_flag_str)
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