def decode_udp_protocol(data: bytes):
    header = data[:2]
    body = data[2:]
    return header, body

def decode_udp_protocol_header(header: bytes):
    chat_room_name_length = int.from_bytes(header[:1], "big")
    token_length = int.from_bytes(header[1:2], "big")
    return chat_room_name_length, token_length

def decode_udp_protocol_body(body: bytes, chat_room_name_length: int, token_length: int):
    response_chat_room_name = body[:chat_room_name_length].decode()
    message_head_index = chat_room_name_length + token_length
    response_token = body[chat_room_name_length : message_head_index].decode()
    message = body[message_head_index:].decode()
    return response_chat_room_name, response_token, message