import uuid as uuid_lib
import time

def get_uuid() -> str:
    generated = uuid_lib.UUID(int=int(time.time()*1000000))

    return str(generated)