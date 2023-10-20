import logging
import telebot
from telebot import types
import requests

TOKEN = "6178884849:AAE8ThOk3m2cjRiTztt1heXm-BIBZkeagw0"
CHAT_ID = 1774165209

logging.basicConfig(level=logging.INFO)

bot = telebot.TeleBot(TOKEN)


def send_request_to_django(endpoint, data):
    url = f"http://127.0.0.1:8000/api/orders/{endpoint}/"

    with requests.Session() as session:
        session.headers.update({"Authorization": f"Bot {TOKEN}"})
        response = session.post(url, json=data)
        return response


def send_order_notification(order):
    message = f"New order created:\nID: {order.id}\nItem: {order.item}\nUser: {order.item.owner}\nCreated at: {order.created_at}\nStatus: {order.step}"

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    accept_button = types.InlineKeyboardButton(
        text="Accept", callback_data=f"accept_{order.id}"
    )
    decline_button = types.InlineKeyboardButton(
        text="Decline", callback_data=f"decline_{order.id}"
    )
    keyboard.add(accept_button, decline_button)

    bot.send_message(
        CHAT_ID, message, reply_markup=keyboard, parse_mode="HTML"
    )


@bot.callback_query_handler(
    func=lambda c: c.data.startswith("accept_") or c.data.startswith("decline_")
)
def process_order_response(call):
    order_id = call.data.split("_")[1]
    response = call.data.split("_")[0]

    if response == "accept":
        new_text = call.message.text + "\nAccepted by: " + call.from_user.first_name
    else:
        new_text = call.message.text + "\nDeclined by: " + call.from_user.first_name

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=new_text)
    bot.answer_callback_query(call.id, text="Your response has been sent.", show_alert=False)

    response = send_request_to_django(response, {"id": order_id})
    data = response.json()
    if response.status_code != 200:
        return bot.send_message(CHAT_ID, f"Что-то пошло не так. Ошибка:\n\n{data['error']}")

    return bot.send_message(CHAT_ID, f"Успешно!")


def main():
    bot.send_message(CHAT_ID, "Бот запущен")
    bot.polling(none_stop=True)


if __name__ == "__main__":
    main()
