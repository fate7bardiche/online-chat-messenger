def parse_udp_protocol(data: bytes):
    header = data[:2]
    body = data[2:]
    return header, body

def parse_udp_protocol_header(header: bytes):
    chat_room_name_length = int.from_bytes(header[:1], "big")
    print("chat_room_name_length is ", chat_room_name_length)
    token_length = int.from_bytes(header[1:2], "big")
    print("token_length is ", token_length)
    return chat_room_name_length, token_length


# トークンのparseうまくいっていない。
# 一部メッセージの方にも漏れてしまっている。

def parse_udp_protocol_body(body: bytes, chat_room_name_length: int, token_length: int):
    response_chat_room_name = body[:chat_room_name_length].decode()
    print(response_chat_room_name)
    message_head_index = chat_room_name_length + token_length
    response_token = body[chat_room_name_length : message_head_index].decode()
    print(response_token)
    message = body[message_head_index:].decode()
    print(message)
    return response_chat_room_name, response_token, message