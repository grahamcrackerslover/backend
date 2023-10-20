import logging

import requests

TELEGRAM_BOT_TOKEN = "6091067433:AAGbyH08gkuq6Y9pjURJ34SgS5GNJ_m2kGc"
VK_COMMUNITY_ACCESS_TOKEN = "vk1.a.3rVJsG9AsoA0gSl8mFVrz7uMXPH80VWieCvC7O9LmeHQ8mSh7MvmiVTcj8QRLVvrdANP-dTavD5aBVcEB4GHJpJxoHR_EdE2aHuZ370Is8NRx8FlonlcZeSSDwPBXGp7NPArOZUGY2DuwwxnTEE8vjh2cdGBP2yZyZ8Jb6McFRmBimmZOWdXRbVbWUxvwolK4ntFv2OaNqdPAJXFVSfmmw"
CHAT_ID = 0
CHANNEL_ID = -1001932365694
COMMUNITY_ID = 219974975
VK_API_VERSION = "5.131"

logging.basicConfig(level=logging.INFO)

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/"


def check_telegram_user_subscription(user_id):
    def api_request(method, data=None):
        url = TELEGRAM_API_URL + method
        try:
            response = requests.post(url, json=data).json()
            if response["ok"]:
                return response["result"]
            else:
                logging.error("Error {}: {}".format(response["error_code"], response["description"]))
                return None
        except Exception as e:
            logging.error(e)
            return None

    print("running check tg subs")
    try:
        member = api_request("getChatMember", {"chat_id": CHANNEL_ID, "user_id": user_id})
        if member:
            return member["status"] in ("creator", "administrator", "member")
    except Exception as e:
        logging.error(e)

    return None


def check_vk_user_subscription(user_id):
    payload = {
        "access_token": VK_COMMUNITY_ACCESS_TOKEN,
        "group_id": COMMUNITY_ID,
        "v": VK_API_VERSION,
    }

    req = requests.get(f"https://api.vk.com/method/groups.getMember", params=payload)
    data = req.json()

    users = data["response"]["items"]
    return user_id in users


def check_user_wallpost(user_id, access_token, desired_text):
    payload = {"access_token": access_token, "owner_id": user_id, "v": VK_API_VERSION}

    response = requests.get("https://api.vk.com/method/wall.get", params=payload)
    data = response.json()
    wall_posts = data["response"]["items"]

    return any([desired_text == post["text"] for post in wall_posts])
