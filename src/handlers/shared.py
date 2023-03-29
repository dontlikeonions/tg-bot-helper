from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from data import data

emoji_nums = {
    '1': '1️⃣',
    '2': '2️⃣',
    '3': '3️⃣',
    '4': '4️⃣',
    '5': '5️⃣',
    '6': '6️⃣',
    '7': '7️⃣',
    '8': '8️⃣',
    '9': '9️⃣',
}


async def send_vote_result(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    chat = data.get_chat(chat_id)
    vote_choices = chat.get('vote_choices')
    votes = chat.get('votes')

    msg = "Голосование началось!\n\n"
    for num, choice in enumerate(vote_choices):
        msg += emoji_nums.get(str(num + 1)) + "  " + choice + "  ➡️  " + str(votes[num]) + "\n"

    vote_msg_id = chat.get('vote_msg_id')
    await context.bot.editMessageText("*" + msg + "*", chat_id, vote_msg_id, parse_mode=ParseMode.MARKDOWN)
