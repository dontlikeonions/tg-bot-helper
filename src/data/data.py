import sys
import json
from json import JSONDecodeError
from typing import Tuple

from service.logger import LOGGER


sys.path.append("..")
DATA_PATH = r'src/data/data.json'
ENCODING = 'utf8'
DATA = []



def serialize(path: str = DATA_PATH, encd: str = ENCODING) -> None:
    try:
        file = open(path, "w", encoding=encd)
        json.dump(DATA, file, indent=4, ensure_ascii=False)
        file.close()
    except:
        LOGGER.exception("failsed to serialize data")


def deserialize(path: str = DATA_PATH, encd: str = ENCODING) -> None:
    global DATA
    try:
        file = open(path, 'r+', encoding=encd)
        DATA = json.load(file)
        file.close()
    except JSONDecodeError:
        LOGGER.exception("unable to access the data")




def is_new_chat(chat_id: int) -> bool:
    for ent in DATA:
        if ent.get('id') == chat_id:
            return False
    
    return True


def get_chats() -> list:
    chats = []
    for chat in DATA:
        chats.append(chat.get('id'))

    return chats


def get_chat(chat_id: int) -> dict:
    for chat in DATA:
        if chat.get('id') == chat_id:
            return chat
        
    return {}




def get_user(chat_id: int, user_id: int) -> dict:
    chat = get_chat(chat_id)
    for user in chat.get('users'):
        if user.get('id') == user_id:
            return user
    
    LOGGER.critical(f"could not found the user in chat, chat_id='{chat_id}', user_id={user_id}")
    return {}
        