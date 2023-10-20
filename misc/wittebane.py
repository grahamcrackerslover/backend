import logging
import telebot
from telebot import types

from orders.models import Orders, update_queue

logging.basicConfig(level=logging.INFO)

TOKEN = "6009492790:AAHNCcwm21Dlb9IUJihW8Zjj7z7he-egD9s"
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
servers = {
    "6": "America",
    "7": "Europe",
    "8": "Asia",
    "9": "TW, HK, MO",
}

PH_CHAT_ID = 5821731502
BUG_CHAT_ID = 5821731502
@bot.message_handler(commands=["id"])
def get_chat_id(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, f"Chat ID: {chat_id}")


def send_order(order):
    try:
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        accept_button = types.InlineKeyboardButton(
            text="Accept", callback_data=f"accept_{order.id}"
        )
        keyboard.add(accept_button)

        message = (
            f"<b>Order #{order.id}</b>\n------------\nItem: {order.item.real_name or order.item.name}\nUID: {order.genshin_uid}"
            f"\nServer: {servers.get(str(order.genshin_uid)[0], 'Unknown, please contact Kleewish immediately')}"
        )
        bot.send_message(PH_CHAT_ID, message, reply_markup=keyboard)
    except Exception as e:
        logging.error(f"Failed to send order #{order.id}. Please contact Kleewish immediately")



@bot.callback_query_handler(func=lambda call: call.data.startswith("accept_"))
def on_accept_button_click(call):
    order_id = call.data.split("_")[1]
    user_full_name = call.from_user.full_name
    old_message_text = call.message.html_text
    new_message_text = old_message_text + f"\nAccepted by {user_full_name}"

    new_keyboard = types.InlineKeyboardMarkup(row_width=1)
    finish_button = types.InlineKeyboardButton(
        text="Finish", callback_data=f"finish_{order_id}"
    )
    new_keyboard.add(finish_button)

    order = Orders.objects.get(id=order_id)
    order.step = "withdrawing"
    order.save()

    bot.edit_message_text(
        new_message_text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=new_keyboard,
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("finish_"))
def on_finish_button_click(call):
    order_id = call.data.split("_")[1]
    user_full_name = call.from_user.full_name
    accepted_by_text = f"Accepted by {user_full_name}"

    if accepted_by_text not in call.message.text:
        bot.answer_callback_query(
            call.id, "Only the person who accepted the order can finish it.", show_alert=True
        )
        return

    new_message_text = call.message.html_text.replace(
        accepted_by_text, f"Finished by {user_full_name}"
    )

    new_keyboard = None

    order = Orders.objects.get(id=order_id)
    order.step = "withdrawn"
    order.is_in_queue = False
    order.save()

    update_queue()

    bot.edit_message_text(
        new_message_text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=new_keyboard,
    )


def on_startup():
    bot.send_message(BUG_CHAT_ID, "Бот по обработке ордеров запущен")


def on_shutdown():
    bot.send_message(BUG_CHAT_ID, "Бот по обработке ордеров выключен")


if __name__ == "__main__":
    on_startup()
    bot.polling()
    on_shutdown()
