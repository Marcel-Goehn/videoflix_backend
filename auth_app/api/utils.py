import base64


# Encodes the id
def encode_id(id):
    string_id = str(id)
    string_id_bytes = string_id.encode("ascii")

    base64_bytes = base64.b64encode(string_id_bytes)
    base64_string = base64_bytes.decode("ascii")
    return base64_string


# Decodes the id
def decode_id(id):
    base64_string = str(id)
    base64_bytes = base64_string.encode("ascii")

    id_string_bytes = base64.b64decode(base64_bytes)
    id_string = id_string_bytes.decode("ascii")
    id_int = int(id_string)
    return id_int
