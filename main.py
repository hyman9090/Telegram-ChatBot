# Reference: https://pixnashpython.pixnet.net/blog/post/32391757-%E3%80%90telegram-api%E3%80%91python

from dotenv import load_dotenv
import os
from datetime import datetime

# 匯入相關套件
from telegram.ext import Updater  # 更新者
from telegram.ext import CommandHandler, CallbackQueryHandler  # 註冊處理 一般用 回答用
from telegram.ext import MessageHandler, Filters  # Filters過濾訊息
from telegram import InlineKeyboardMarkup, InlineKeyboardButton  # 互動式按鈕

from utils import convert_timestamp, second2HHMMSS

from llm import LLM


def main():
    load_dotenv("token")

    # 設定 token
    token = os.getenv("token")

    # set up a LLM model
    llm = LLM("Lai Hoi Man description.pdf")

    # 初始化bot
    updater = Updater(token=token, use_context=False)

    # 設定一個dispatcher(調度器)
    dispatcher = updater.dispatcher

    # 定義收到訊息後的動作(新增handler)
    def start(bot, update):
        # print('json file update : ' ,update)
        # print("json file bot : ', bot)
        chat_id = update.message.chat_id
        first_name = update.message.chat.first_name
        last_name = update.message.chat.last_name
        username = update.message.chat.username
        hyman_tg_id = os.getenv("hyman9090_tg_id")

        text = f"""Hello {username}, nice to meet up here. \nI am a bot to answer questions about Hyman. \nFeel free to me any questions. 😉"""

        bot.sendMessage(chat_id, text)

        # Let the user to choose who he/she wants to talk to
        update.message.reply_text(
            "Chat with me or you can choose to chat with Hyman directly",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Chat with bot",
                            callback_data="Thank you for choosing me. Let's keep our conversation here!",
                        ),
                        InlineKeyboardButton(
                            "Chat with Hyman directly",
                            url=f"https://t.me/{hyman_tg_id}",
                        ),
                    ]
                ]
            ),
        )

    def answer_user(bot, update):
        yours = update.callback_query.data  # 一樣從update中抽取資料
        update.callback_query.edit_message_text(text=yours)
        update._effective_message.reply_text(
            "What's your question? You can ask in any language. \nBut please do not send message other than text."
        )

    def notification_to_hyman(bot, update):
        pass

    def echo_non_text(bot, update):  # 其他訊息
        update.message.reply_text(text="Please don't send any non-text messages to me.")

    def echo_text(bot, update):

        hyman_tg_chat_id = os.getenv("chat_id")

        time_fmt = "%d %B %Y %H:%M:%S"

        sender_info = update._effective_message.from_user
        sender_id = sender_info["id"]
        sender_username = sender_info["username"]
        sender_is_bot = sender_info["is_bot"]
        sender_msg = update._effective_message.text
        sender_datetime = convert_timestamp(update._effective_message.date).strftime(
            time_fmt
        )

        bot_answer = llm.ask_llm(sender_msg)
        bot_answer = update.message.reply_text(text=bot_answer)

        bot_answer_datetime = convert_timestamp(bot_answer["date"]).strftime(time_fmt)

        timeSpan = second2HHMMSS(
            datetime.strptime(bot_answer_datetime, time_fmt)
            - datetime.strptime(sender_datetime, time_fmt)
        )

        response_metadata = f"""This person has sent you a message.
        
{"Message Time:":<23}{sender_datetime:<30}
{"User_ID:":<31}{sender_id:<30}
{"Username:":<27}@{sender_username:<30}
{"Is_Bot:":<33}{sender_is_bot:<30}
{"Message:":<29}{sender_msg:<30}

{"Bot's reply Time:":<26}{bot_answer_datetime:<30}
{"Bot's reply:":<31}{bot_answer.text:<30}

{"Time Span:":<28}{timeSpan:<30}"""

        bot.sendMessage(hyman_tg_chat_id, response_metadata)

    # 把handler加入dispatcher()
    start_command = CommandHandler("start", start)
    answer_start_command = CallbackQueryHandler(answer_user)
    noti_hyman = CallbackQueryHandler(notification_to_hyman)
    text_msg_reply = MessageHandler(Filters.text, echo_text)
    non_text_msg_reply = MessageHandler(~Filters.text, echo_non_text)

    updater.dispatcher.add_handler(start_command)
    updater.dispatcher.add_handler(answer_start_command)  # 回答問題
    updater.dispatcher.add_handler(noti_hyman)
    updater.dispatcher.add_handler(text_msg_reply)  # Filters如果是文字就呼叫start
    updater.dispatcher.add_handler(non_text_msg_reply)

    # 開始運作bot
    updater.start_polling()

    # 待命 若要停止按Ctrl-C 就好
    updater.idle()

    # 離開
    # updater.stop()


if __name__ == "__main__":
    main()
