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


async def main_msg_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:   
    if mgmt.add_user(update.effective_chat.id, update.effective_message.from_user) == False:
        await update.effective_chat.send_message("Пожалуйста, напишите команду /start, чтобы я мог нормально работать")
    
    if data.get_chat(update.effective_chat.id).get('vote_state') == True:
        await vote_handling(update, context)
        return

    await check_trigger(update, context)




async def vote_handling(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.effective_message.text
    if len(text) != 1:
        return
    
    num = int(update.effective_message.text)
    res = mgmt.set_vote(update.effective_chat.id, update.effective_message.from_user.id, num)
    if res == True:
        await shared.send_vote_result(update, context, )
    else:
        await update.effective_chat.send_message("Вы уже проголосовали")




async def check_trigger(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.effective_message.text
    text_length = len(text)

    if text == None or text_length > 100 or text_length == 0:
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
        LOGGER.info(f"TRIGGER_REPLIES : could not find command of type \"{trigger_type}\"")

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
