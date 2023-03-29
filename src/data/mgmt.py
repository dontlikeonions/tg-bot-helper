from telegram import User, ChatMember, ChatMemberUpdated
from typing import Optional, Tuple

from data import templates
from service.logger import LOGGER

from data import data



def add_chat(chat_id: int) -> None:
    dict = {
        'id': chat_id,
        'users': [],
    }
    dict.update(templates.chat)
    data.DATA.append(dict)
    data.serialize()
    LOGGER.info(f"added new chat, chat_id='{chat_id}'")
  

def add_user(chat_id: int, user: User) -> None:
    chat = data.get_chat(chat_id)

    if len(chat) == 0:
        LOGGER.info(f"could not find chat, chat_id='{chat_id}'")
        return
    
    users = chat.get('users')
    for ent in users:
        if user.id == ent.get('id'):
            return

    user_dict = user.to_dict()
    user_dict.update(templates.user)
    users.append(user_dict)
    chat.update({'users': users})
    data.serialize()

    LOGGER.info(f"added new user, chat_id='{chat_id}', user_id='{user.id}'")



def delete_user(chat_id: int, user_id: int) -> None:
    chat = data.get_chat(chat_id)
    users = chat.get('users')

    for user in users:
        if user.get('id') == user_id:
            users.remove(user)
            chat.update({'users': users})
            LOGGER.info(f"deleted user, chat_id='{chat_id}', user_id='{user_id}'")
            return

    LOGGER.info(f"could not find user, chat_id='{chat_id}', user_id='{user_id}'")



def extract_status_change(chat_member_update: ChatMemberUpdated) -> Optional[Tuple[bool, bool]]:
    status_change = chat_member_update.difference().get("status")
    old_is_member, new_is_member = chat_member_update.difference().get("is_member", (None, None))

    if status_change is None:
        return None

    old_status, new_status = status_change
    was_member = old_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (old_status == ChatMember.RESTRICTED and old_is_member is True)

    is_member = new_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (new_status == ChatMember.RESTRICTED and new_is_member is True)

    return was_member, is_member




def change_vote_state(chat_id: int, vote_msg_id: int = None, vote_choices: list = []) -> bool:
    chat = data.get_chat(chat_id)
    if len(chat) == 0:
        LOGGER.info(f"could not find chat, chat_id='{chat_id}'")
        return False  
            
    new_state = not chat.get('vote_state')
    votes = []

    if new_state == True:        
        votes = [0] * len(vote_choices)
    else:
        for user in chat.get('users'):
            user.update({'is_voted': False})
                
    chat.update({'vote_state': new_state})
    chat.update({'vote_msg_id': vote_msg_id})
    chat.update({'votes': votes})
    chat.update({'vote_choices': vote_choices})
    data.serialize()

    return True



def set_vote(chat_id: int, user_id: int, vote_num: int) -> bool:
    chat = data.get_chat(chat_id)
    if len(chat) == 0:
        LOGGER.info(f"could not find chat, chat_id='{chat_id}'")
        return False  
    
    for user in chat.get('users'):
        if user.get('id') == user_id and user.get('is_voted') == False:
            user.update({'is_voted': True})
            votes = chat.get('votes')
            votes[vote_num - 1] += 1
            chat.update({'votes': votes})
            data.serialize()
            return True
        
    return False
