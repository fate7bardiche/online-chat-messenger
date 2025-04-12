import socket
from datetime import datetime, timedelta
import time
import threading
import uuid
import time
from parser import parse_protocol, parse_protocol_header, parse_protocol_body

chat_room_list = {}
client_list = []

hoge = ["sdf", "sdf"]

# 各クライアントの最後のメッセージ送信時刻を追跡し、条件を満たせば削除する
def remove_client(client_list):
    while True:
        print(f"現在リレーシステムに存在しているclientは{len(client_list)}人")
        print(client_list)
        print("===========")
        now = datetime.now()
        for i in range(len(client_list) -1, -1, -1):
            diff = abs(now - client_list[i]["last_sent_at"])

            # 最後にメッセージを送ってから120秒以上経過しているクライアントをリレーシステムから削除
            expired_second = 120
            expired_at = timedelta(seconds=expired_second)
            if diff > expired_at:
                print("deleted client", client_list[i])
                client_list.pop(i)
 
        # リレーから削除するべきクライアントがいるかどうか、5秒ごとに確認する
        monitor_wait_second = 5
        time.sleep(monitor_wait_second)

def main_udp(client_list: list):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = '0.0.0.0'
    server_port = 9002

    sock.bind((server_address, server_port))

    thread = threading.Thread(target=remove_client, args=(client_list, ), daemon=True)
    thread.start()

    while True:
        data, address = sock.recvfrom(4096)

        # 受信したデータのaddressを持つaddressを持つclientがリレーシステムに存在するか確認
        # 存在するなら、最後のメッセージ送信時刻を更新する
        # 存在しないなら、リレーシステムにclientとして追加する
        result = next(((i, c) for i, c in enumerate(client_list) if c["address"] == address), None)
        if result == None:
            client_list.append({"address": address, "last_sent_at": datetime.now()})
        else:
            index, c = result
            client_list[index]["last_sent_at"] = datetime.now()

        user_name_len = int.from_bytes(data[:1], "big")
        user_name = data[:user_name_len + 1].decode()
        print("ユーザーネーム: ", user_name)
        print("メッセージ", data[user_name_len + 1:].decode())

        for client in client_list:
            client_addr = client["address"]
            if  client_addr[0] == address[0] and client_addr[1] == address[1]: continue
            print("send to", client_addr[1])
            sock.sendto(data, client_addr)







# TCP関係
def tcp_flow(connection: socket.socket, address: tuple[str, int]):
    while True:
        print("in while")

        try:
            data = connection.recv(4096)
        except socket.error as err:
            print(err)
            break

        header, body = parse_protocol(data)
        room_name_length, operation, state, payload_length = parse_protocol_header(header)
        room_name_bits = body[:room_name_length]
        room_name, payload = parse_protocol_body(body, room_name_length, payload_length)

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

        # break
    
    # connection.close()

def create_user(user_name: str, address: tuple[str, int], user_token: str):
    user = {
            "token": user_token,
            "user_name": user_name,
            "ip_address": address,
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
        # tcp_flow(tcp_sock, connection)

        tcp_thread = threading.Thread(target=tcp_flow, args=(connection, client_address), daemon=True)
        tcp_thread.start()
        # tcp_thread.join()
        




        

if __name__ == "__main__":
    
    # thread_remove_user = threading.Thread(target=remove_client, args=(client_list, ), daemon=True)
    # thread_tcp_flow = threading.Thread(target=tcp_flow, args=(), daemon=True)

    # thread_remove_user.start()
    # thread_tcp_flow.start()
    # tcp_flow()
    print("tcp finish")
    # main(client_list)
    tcp_main()