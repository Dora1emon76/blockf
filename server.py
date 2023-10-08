import asyncio
import requests
from flask import Flask, request
import pyrogram
import threading
import re
import subprocess
import atexit
import os

# List of patterns to match
patterns = ['#','#Ad', '#branԁDiscount', '#paidAD', '#paidad', '#AD', '#Paidad', '#PaidAD', 'bots.business/ads', '#PaidAd','#PromotіonInғ1uencer','#sales','#influеncermarketіпg','#placementAd', 'sponsored','#AdvertisementMarketing']

# Combine the patterns into a single regex pattern
pattern = '|'.join(re.escape(p) for p in patterns)

app = Flask(__name__)

# Function to send the post request in a separate thread
def send_post_request(bot_token, data):
    try:
        requests.post("https://api.bots.business/tg_webhooks/" + bot_token, json=data)
    except Exception as e:
        print(e)

# Start serveo and create a tunnel

def start_serveo():
    try:
        serveo_process = subprocess.Popen(['ssh', '-R', '80:localhost:88', 'serveo.net'], stdout=subprocess.PIPE)
        atexit.register(lambda: serveo_process.terminate())
        
        # Read both stdout and stderr to capture any potential error messages
        serveo_url = serveo_process.stdout.readline().decode().strip()
        serveo_error = serveo_process.stderr.read().decode().strip()
        
        if serveo_url:
            os.environ["SERVEO_URL"] = serveo_url
            print(f'serveo URL: {os.environ["SERVEO_URL"]}')
        else:
            print(f"Serveo error: {serveo_error}")

    except Exception as e:
        print(f"Error starting serveo: {e}")

# serveo initialization
serveo_thread = threading.Thread(target=start_serveo)
serveo_thread.start()




@app.route("/set")
def set_webhook():
    bot_token = request.args.get("token")
    # Use serveo public URL as the webhook URL
    serveo_url = os.environ.get("SERVEO_URL", "https://localhost:88")
    requests.get(f"https://api.telegram.org/bot{bot_token}/setWebhook?url={serveo_url}/tg_webhook?token={bot_token}")
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

if __name__ == '__main__':
    serveo_url = os.environ.get("SERVEO_URL", "https://localhost:88")
    app.run(host='localhost', port=88)
