def decode_tcp_protocol(data: bytes):
    header = data[:32]
    body = data[32:]
    return header, body

def decode_tcp_protocol_header(header: bytes):
    room_name_length = int.from_bytes(header[:1], "big")
    operation = int.from_bytes(header[1:2], "big")
    state = int.from_bytes(header[2:3], "big")
    payload_length = int.from_bytes(header[3:33], "big")
    return room_name_length, operation, state, payload_length

def decode_tcp_protocol_body(body: bytes, room_name_length: int):
    room_name = body[:room_name_length].decode()
    operation_payload = body[room_name_length:].decode()
    return room_name, operation_payload