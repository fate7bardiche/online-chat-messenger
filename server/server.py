import socket
from datetime import datetime, timedelta
import time
import threading

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

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = '0.0.0.0'
    server_port = 9001

    sock.bind((server_address, server_port))

    client_list = []

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

if __name__ == "__main__":
    main()