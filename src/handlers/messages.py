from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from random import choice
from datetime import datetime
import re

from service.logger import LOGGER

from data import mgmt, data
from responses import TRIGGER_WORDS, TRIGGER_REPLIES
import handlers.shared as shared



async def add_user_if_new(update: Update) -> bool:
    if mgmt.add_user(update.effective_chat.id, update.effective_message.from_user) == False:
        await update.effective_chat.send_message("Пожалуйста, напишите команду /start")
        return False
    
    return True


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await add_user_if_new(update) == False:
        return
    
    text = update.effective_message.text
    vote_state, chat = data.get_vote_state(update.effective_chat.id)

    if vote_state == True:
        await vote_handling(update, context, text, chat)

    await check_trigger(update, text)



async def attachment_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await add_user_if_new(update) == False:
        return
    
    await check_trigger(update, update.effective_message.caption)



async def vote_handling(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, chat: dict) -> None:
    try:
        num = int(text)
    except ValueError:
        return 
    
    if not 0 < num < len(chat.get('votes')):
        await update._effective_message.reply_text("Такой позиции в голосовании нет")
        return
    
    user_id = update.effective_user.id
    if mgmt.set_vote(chat, user_id, num) == True:
        await shared.send_vote_result(update, context)
    else:
        await update.effective_message.reply_text("Вы уже проголосовали")
        return 
        




async def check_trigger(update: Update, text: str) -> None:
    if text == None:
        return
    
    txt_len = len(text)
    if not 1 < txt_len < 100:
        return

    with open('words.txt', 'a', encoding='utf-8') as file:
        file.write(text + '\n')

    words = re.sub(r'[^\w\s]', '', text.lower()).split(' ')
    wpairs = set(make_words_pairs(words))

    for triggers in TRIGGER_WORDS.items():
        trigger_set = set(triggers[1])
        
        if wpairs.isdisjoint(trigger_set) == False or \
            set(words).isdisjoint(trigger_set) == False:
            
            reply = get_reply_for_trigger(triggers[0])
            await reply_for_trigger(reply, update)
            return
           

def make_words_pairs(words: list) -> list:
    words_pairs = []
    w_pair = words[0]

    for word in words:
        w_pair += " " + word
        words_pairs.append(w_pair)
        w_pair = word

    if len(words) == 1:
        words_pairs.append(w_pair)

    return words_pairs


async def reply_for_trigger(reply : str, update: Update) -> None:
    mention = update.message.from_user.mention_html()

    await update.effective_chat.send_message(
        reply.format(mention),
        parse_mode=ParseMode.HTML
    )
    

def get_reply_for_trigger(trigger_type : str) -> str:
    replies = TRIGGER_REPLIES.get(trigger_type)
    if not replies:
        LOGGER.info(f"Сould not find a '{trigger_type}' type of trigger")

    msg = ""
    current_hour = datetime.now().hour

    if isinstance(replies, dict):
        if 0 <= current_hour <= 5:
            msg = choice(replies.get('night'))
        elif 6 <= current_hour <= 11:
            msg = choice(replies.get('morning'))
        elif 12 <= current_hour <= 19:
            msg = choice(replies.get('afternoon'))
        elif 20 <= current_hour <= 24:
            msg = choice(replies.get('evening'))
        else:
            msg = choice(replies.get('night'))
    else:
        msg = choice(replies)

    return msg
