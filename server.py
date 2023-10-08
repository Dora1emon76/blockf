import asyncio
import requests
from flask import Flask, request
import pyrogram
import threading
import re
import ssl
# List of patterns to match
patterns = ['#Ad', '#branԁDiscount', '#paidAD', '#paidad', '#AD', '#Paidad', '#PaidAD', 'bots.business/ads', '#PaidAd','#PromotіonInғ1uencer','#sales','#influеncermarketіпg','#placementAd', 'sponsored','#AdvertisementMarketing']

# Combine the patterns into a single regex pattern
pattern = '|'.join(re.escape(p) for p in patterns)

app = Flask(__name__)

# Function to send the post request in a separate thread
def send_post_request(bot_token, data):
    try:
        requests.post("https://api.bots.business/tg_webhooks/" + bot_token, json=data)
    except Exception as e:
        print(e)

@app.route("/set")
def set_webhook():
    bot_token = request.args.get("token")
    requests.get("https://api.telegram.org/bot" + bot_token + "/setWebhook?url=https://62.72.24.208:88/tg_webhook?token=" + bot_token)
    return "SUCCESS!"

@app.route("/")
def hello():
    return "Hello, World!"

@app.route("/tg_webhook", methods=["GET", "POST"])
def handle_webhook():
    try:
        data = request.get_json()
        print(data)
        bot_token = request.args.get("token")

        # Start a separate thread to send the post request
        post_thread = threading.Thread(target=send_post_request, args=(bot_token, data))
        post_thread.start()

        async def run_and_idle(bot):
            async with bot:
                current_msg_id = data['message']['message_id']
                chat_id = data['message']['chat']['id']
                for i in range(1, 10):
                    message = await bot.get_messages(chat_id, current_msg_id+i)

                    # Check if the message text matches any pattern using regex
                    if re.search(pattern, message.text):
                        await message.delete()
                        print(f'Message with id {current_msg_id+i} deleted successfully')

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        bot = pyrogram.Client(name="my_client" + bot_token, bot_token=bot_token, api_id=27327983, api_hash="6055fdf20578072d6bd4db34953496e2")
        loop.run_until_complete(run_and_idle(bot))
        return "got it", 200
    except Exception as e:
        print(e)
        return "Hi", 200
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain('server.crt', 'server.key')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=88, ssl_context=ssl_context)
