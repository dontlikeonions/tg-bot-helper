from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from random import choice
from pathlib import Path

from service.logger import LOGGER
from service.bot_info import BOT_OWNER_ID

from responses import *
import release_notes 
import states
from handlers import shared
from data import mgmt, data



LOGS_PATH = Path(__file__).parents[1] / "service/logs.txt"

COMMANDS_INFO = {
    '/start': '/start ~ Запуск бота',
    '/help': '/help или /help </имя_команды> ~ Выдает справку о командах',
    '/vote': '/vote <варианты> ~ Запускает голосование с указанными вариантами',
    '/stop_vote': '/stop_vote ~ Останавливает запущенное голосование',
}



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:    
    if data.is_new_chat(update.effective_chat.id) == True:
        mgmt.add_chat(update.effective_chat.id)
        
    await update.effective_chat.send_message(START_MSG)



async def help(update: Update, context: ContextTypes.DEFAULT_TYPE, command_name: str = None) -> None:
    msg = "Эта команда используется так:\n\n"
    instruction = ""

    if len(context.args) != 0:
        command_name = context.args[0]

    if not command_name:
        msg = "Вот, что я умею:\n\n"
        for command in COMMANDS_INFO.items():
            instruction += command[1].replace(' ~ ', '\n') + "\n\n"
    
    for command in COMMANDS_INFO.items():
        if command_name == command[0]:
            instruction = command[1].replace(' ~ ', '\n') + "\n\n"
            break

    if len(instruction) == 0:
        await update.effective_chat.send_message("Имя команды указано непрвильно")
        LOGGER.info(f"Could not find the command '{command_name}'")
        return
    
    await update.effective_chat.send_message(msg + instruction)
    


async def vote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args = context.args
    chat_id = update.effective_chat.id

    if len(args) < 1:
        await update.effective_chat.send_message("Необходимо минимум два варианта выбора")
        return
    
    msg_id = (await update.effective_chat.send_message("Голосование началось!")).id
    state, chat = data.get_vote_state(chat_id)

    if len(chat) == 0:
        LOGGER.info(f"Cant find chat for changing vote state, chat_id='{chat_id}'")
    elif state == True:
        await context.bot.editMessageText(
            "Предыдущее голосование остановлено.\nВведите команду еще раз, чтобы запустить новое", 
            update.effective_chat.id, 
            msg_id
        )
        mgmt.disable_voting(chat)
    else:
        mgmt.enable_voting(chat, msg_id, args)
        await shared.send_vote_result(update, context)    




async def stop_vote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    state, chat = data.get_vote_state(chat_id)
    if state == False:
        await update.effective_chat.send_message("Нет запущенного голосования")
    else:
        mgmt.disable_voting(chat)
        await update.effective_chat.send_message("Голосование остановлено")




async def greet_chat_members(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = mgmt.extract_status_change(update.chat_member)
    if result is None:
        return

    was_member, is_member = result

    cause_mention = update.chat_member.from_user.mention_html()
    member = update.chat_member.new_chat_member.user
    member_mention = member.mention_html()


    if not was_member and is_member:
        response = choice(GREETINGS).format(member_mention, cause_mention)
        mgmt.add_user(update.effective_chat.id, member)

    elif was_member and not is_member:
        response = choice(GOODBYES).format(cause_mention, member_mention)
        mgmt.delete_user(update.effective_chat.id, member)


    await update.effective_chat.send_message(
        response,
        parse_mode=ParseMode.HTML,
    )



async def send_release_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_message.from_user.id == BOT_OWNER_ID:
        if states.IS_RELEASENOTES_SENDED == False:
            for id in data.get_chats():
                await context.bot.send_message(chat_id=id, text=release_notes.NOTES)
                
            states.IS_RELEASENOTES_SENDED = True



async def get_logs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_message.from_user.id == BOT_OWNER_ID:
        with open(LOGS_PATH, 'r') as file:
            await update.effective_chat.send_document(file)
            LOGGER.info(f"Logs sent to chat_id='{update.effective_chat.id}'")