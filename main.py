import asyncio
import requests
from flask import Flask, request
import pyrogram
import threading
import re
from pyngrok import ngrok  # Install pyngrok using pip install pyngrok

# List of patterns to match

# Combine the patterns into a single regex patter

app = Flask(__name__)

# Function to send the post request in a separate thread
def send_post_request(bot_token, data):
    try:
        requests.post("https://api.bots.business/tg_webhooks/" + bot_token, json=data)
    except Exception as e:
        print(e)

# Start ngrok and create a tunnel
#public_url = ngrok.connect(port=5000)

#print(" * ngrok tunnel \"{}\" -> \"http://127.0.0.1:{}/\"".format(public_url, 5000))

#def get_ngrok_url():
   # return public_url

@app.route("/set")
def set_webhook():
    bot_token = request.args.get("token")
    # Use ngrok public URL as the webhook URL
   # ngrok_url = get_ngrok_url()
    requests.get(f"https://api.telegram.org/bot{bot_token}/setWebhook?url=https://bbadblock.vercel.app/tg_webhook?token={bot_token}")
    return "SUCCESS!"

@app.route("/")
def hello():
    return "Hello, World!"

@app.route("/tg_webhook", methods=["GET", "POST"])
def handle_webhook():
    try:
        data = request.get_json()
        bot_token = request.args.get("token")
        bot_id = bot_token.split(":")[0]
        patterns = [request.args.get("keyword")]
        pattern = '|'.join(re.escape(p) for p in patterns)

        # Start a separate thread to send the post request
        post_thread = threading.Thread(target=send_post_request, args=(bot_token, data))
        post_thread.start()

        async def run_and_idle(bot):
            async with bot:
                current_msg_id = data['message']['message_id']
                chat_id = data['message']['chat']['id']
                for i in range(1, 6):
                    message = await bot.get_messages(chat_id, current_msg_id + i)
                    print(f"msg: {message}")
                    # Check if the message text matches any pattern
                    if message.from_user.id == bot_id and not re.search(pattern, message.text):
                        await message.delete()
                    await asyncio.sleep(0.5) 
                        #print(f'Message with id {current_msg_id + i} deleted successfully')

        # Define the loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # bot = pyrogram.Client(name="mylient" + bot_token, bot_token=bot_token, api_id=28905453, api_hash="21073abfe2bf0652881caf8ec8f104e4")
        bot = pyrogram.Client(
            name=":memory:" + bot_token,
            bot_token=bot_token,
            api_id=28905453,
            api_hash="21073abfe2bf0652881caf8ec8f104e4",
            in_memory=True,
        )
        loop.run_until_complete(run_and_idle(bot))
        return "got it", 200
    except Exception as e:
        print(f"error: {e}")
        return "Hi", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=3000 )
