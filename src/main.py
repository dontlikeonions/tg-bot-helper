from telegram.ext import CommandHandler, MessageHandler, ChatMemberHandler, Application, filters

import asyncio

from service.bot_info import TOKEN
from handlers import commands, messages
from data import data



def main():
    app = Application.builder().token(TOKEN).build()

    handlers = [
        ChatMemberHandler(commands.greet_chat_members, ChatMemberHandler.CHAT_MEMBER),
        
        # private commands
        CommandHandler("release", commands.send_release_info),
        CommandHandler("get_logs", commands.get_logs),

        # puclic commands
        CommandHandler("start", commands.start),
        CommandHandler("help", commands.help),
        CommandHandler("vote", commands.vote),
        CommandHandler("stop_vote", commands.stop_vote),

        MessageHandler(filters.TEXT, messages.text_handler),
        MessageHandler(filters.ATTACHMENT, messages.attachment_handler),
    ]

    app.add_handlers(handlers)
    data.deserialize()
    app.run_polling()



if __name__=='__main__':
    main()
