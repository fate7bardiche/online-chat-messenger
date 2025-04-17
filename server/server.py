import socket
from datetime import datetime, timedelta
import time
import threading
import uuid
import time
from tcp_decoder import decode_tcp_protocol, decode_tcp_protocol_header, decode_tcp_protocol_body
from udp_decoder import decode_udp_protocol, decode_udp_protocol_header, decode_udp_protocol_body

chat_room_list = {}
# client_list = []

# 各クライアントの最後のメッセージ送信時刻を追跡し、条件を満たせば削除する
def remove_client(sock: socket.socket):
    while True:
        # print(f"現在リレーシステムに存在しているclientは{len(client_list)}人")
        # print(client_list)
        print("======================")
        now = datetime.now()

        chat_room_name_list = chat_room_list.keys()
        print(chat_room_list)
        for chat_room_name in chat_room_name_list:
            chat_room_users = chat_room_list[chat_room_name]["users"]
            # user_token_list = 
            for user_token in list(chat_room_users.keys()):
                user = chat_room_users[user_token]
                diff = abs(now - user["last_accessed_at"])

                # 最後にメッセージを送ってから120秒以上経過しているクライアントをリレーシステムから削除
                expired_second = 16
                expired_at = timedelta(seconds=expired_second)
                if diff > expired_at:
                    
                    print("--- deleted client: ", chat_room_name, user)
                    chat_room_users.pop(user_token)
                    delete_message = "exit: 最後に投稿してから一定時間が経過したので、チャットから自動的に退出しました。"
                    sock.sendto(delete_message.encode(), user["udp_ip_address"])
 
        # リレーから削除するべきクライアントがいるかどうか、5秒ごとに確認する
        monitor_wait_second = 5
        time.sleep(monitor_wait_second)



# UDP関係
def udp_main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = '0.0.0.0'
    server_port = 9002

    sock.bind((server_address, server_port))

    thread = threading.Thread(target=remove_client, args=(sock, ), daemon=True)
    thread.start()

    while True:
        data, address = sock.recvfrom(4096)

        header, body = decode_udp_protocol(data)
        chat_room_name_length, token_length = decode_udp_protocol_header(header)
        response_chat_room_name, response_token, response_message = decode_udp_protocol_body(body, chat_room_name_length, token_length)

        chat_room: dict = chat_room_list[response_chat_room_name]

        print(chat_room)
        
        
        # todo: chat_roomがundefineの場合は、該当する名前のチャットルームがないことを表す。
        # チャットルームが存在しません系のメッセージをsendしておく。
        if chat_room == None:
            print("chat_room is undefined")
            continue
       
        chat_room_users = chat_room["users"]
        user: dict = chat_room_users[response_token]
        if user == None:
            print("user is undefined")
            continue

        user["last_accessed_at"] = datetime.now()
        if(user["udp_ip_address"] == None):
            user["udp_ip_address"] = address
        
        user_name = user["user_name"]
        print("ユーザーネーム: ", user_name)
        print("メッセージ", response_message)

        users_tokens = chat_room_users.keys()
        print(chat_room_users)
        for user_token in users_tokens:
            destination_user = chat_room_users[user_token]
            destination_addr = destination_user["udp_ip_address"]
            # 今回メッセージを送ったuser以外にメッセージを送信する
            if  destination_addr[0] == address[0] and destination_addr[1] == address[1]: continue
            print("send to", destination_user)
            sock.sendto(response_message.encode(), destination_addr)





# TCP関係
def tcp_flow(connection: socket.socket, address: tuple[str, int]):
    while True:
        print("in while")

        try:
            data = connection.recv(4096)
        except socket.error as err:
            print(err)
            break

        header, body = decode_tcp_protocol(data)
        room_name_length, operation, state, payload_length = decode_tcp_protocol_header(header)
        room_name_bits = body[:room_name_length]
        room_name, payload = decode_tcp_protocol_body(body, room_name_length)

        print(room_name_length)
        print(operation)
        print(state)
        print(payload_length)
        print(room_name)
        print(payload)

        state += 1
        status_code = "200"
        status_code_bits = status_code.encode()
        state_1_header = create_tcp_header(room_name_length, operation, state, len(status_code_bits))
        state_1_response = state_1_header + room_name_bits + status_code_bits
        connection.send(state_1_response)

        time.sleep(0.5)

        # ChatRoomの作成
        if operation == 1:
            state += 1
            host_user_token_uuid = uuid.uuid4()
            host_user_token = str(host_user_token_uuid)

            # crate chat room
            host_user = create_user(payload, address, host_user_token)
            chat_room = {
                "host_token": host_user_token,
                "name": room_name,
                "users": {host_user_token:  host_user}
            }
            chat_room_list.setdefault(room_name, chat_room)

            host_user_token_bits = host_user_token.encode()
            state_2_header = create_tcp_header(room_name_length, operation, state, len(host_user_token_bits))
            state_2_response = state_2_header + room_name_bits + host_user_token_bits
            connection.send(state_2_response)
            print(f"{room_name} チャットルームを作成しました。")

        # ChatRoomに参加
        elif operation == 2:
            state += 1

            user_token_uuid = uuid.uuid4()
            user_token = str(user_token_uuid)
            user =  host_user = create_user(payload, address, user_token)

            chat_room = chat_room_list[room_name]
            # todo: チャットルームがないなら、エラーをレスポンスとして返す処理を書く
            chat_room["users"][user_token] = user

            user_token_bits = user_token.encode()
            state_2_header = create_tcp_header(room_name_length, operation, state, len(user_token_bits))
            state_2_response = state_2_header + room_name_bits + user_token_bits
            connection.send(state_2_response)
            print(f"{room_name} チャットルームに参加しました。")
        else:
            print("operationが不正です。")

        break

def create_user(user_name: str, address: tuple[str, int], user_token: str):
    user = {
            "token": user_token,
            "user_name": user_name,
            "tcp_ip_address": address,
            "udp_ip_address": None,
            "last_accessed_at": datetime.now()
        }
    return user


def create_tcp_header(room_name_length: int, opr: int, state_length: int, payload_length: int):
    return room_name_length.to_bytes(1, "big") + opr.to_bytes(1, "big") + state_length.to_bytes(1, "big") + payload_length.to_bytes(29, "big")

def tcp_main():
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_address = '0.0.0.0'
    server_port = 9001
    tcp_sock.bind((server_address, server_port))
    tcp_sock.listen(5)

    while True:
        print("before acept")
        try:
            connection, client_address = tcp_sock.accept()
        except socket.error as err:
            print("err block")
            print(err)
            break
    
        print("after acept")
        print(client_address)

        tcp_thread = threading.Thread(target=tcp_flow, args=(connection, client_address), daemon=True)
        tcp_thread.start()
        






if __name__ == "__main__":
    
    # thread_remove_user = threading.Thread(target=remove_client, args=(client_list, ), daemon=True)
    # thread_tcp_flow = threading.Thread(target=tcp_flow, args=(), daemon=True)

    # thread_remove_user.start()
    # thread_tcp_flow.start()
    # tcp_flow()
    thread_udp_flow = threading.Thread(target=udp_main, args=(), daemon=True)
    thread_udp_flow.start()
    tcp_main()