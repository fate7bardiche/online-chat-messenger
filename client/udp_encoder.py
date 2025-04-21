def create_udp_protocol(chat_room_name: str, token: str,message: str):
    chat_room_name_bits = chat_room_name.encode()
    token_bits = token.encode()
    header = create_udp_header(len(chat_room_name_bits), len(token_bits))
    body = chat_room_name_bits + token_bits + message.encode()
    return header + body

def create_udp_header(room_name_length: int, token_length: int):
    return room_name_length.to_bytes(1, "big") + token_length.to_bytes(1, "big")

