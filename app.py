from flask import Flask, jsonify, request, Response
import os
import datetime
import random
import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

app = Flask(__name__)

def question_gen(n):
    with open("questionbank.txt", 'r') as f:
        lines = f.readlines()

    if n > len(lines):
        return []

    randomnums = []
    for i in range(n):
        gen = random.randint(0, len(lines)-1)
        while lines[gen].rstrip("\n") in randomnums:
            gen = random.randint(0, len(lines)-1)
        randomnums.append(lines[gen].rstrip("\n"))
    return randomnums

def message_builder(message):
    result = ""
    for i in range(len(message)-1):
        result+=message[i]
        result+="\n"
    result+=message[-1]
    return result

@app.route('/')
def index():
    print("Recieved Request")
    return jsonify(test='success')

@app.route('/hello', methods=['POST', 'GET'])
def hello():
    print("/hello - SUCCESS!!!")
    today = datetime.date.today()
    date = today.strftime("%A, %B %-d, %Y")
    return jsonify(response_type="in_channel", text=f"*Open bot says hello...*\nToday is {date}! What a nice day.\nI am OpenBot! Use `/about` to learn more about me or `/help` to see my list commands.")

@app.route('/help', methods=['GET', 'POST'])
def help():
    message = [
        "Want help?",
        "There's no help!"
    ]
    return jsonify(response_type="in_channel", text=message_builder(message))

@app.route('/about')
def about():
    message = [
        "You just ran `/about`! btw my name is open bot goodbye"
    ]
    return jsonify(response_type="in_channel", text=message_builder(message))


@app.route('/daily', methods=['GET', 'POST'])
def daily():
    text = request.form.get('text', None)
    user = request.form.get('user_id', None)
    questions = question_gen(int(text))
    message = [
            f"Hello there <@{user}>, please answer the following questions:",
            questions[0]
    ]
    return jsonify(response_type="in_channel", text=message_builder(message))

@app.route('/answer', methods=['GET', 'POST'])
def answer():
    text = request.form.get('text', None)
    user = request.form.get('user_id', None)
    message = [
            f"*DEBUG:* <@{user}> response recieved, contents:", text, "Response Recieved, {n} questions remain. Next question:", "{question}"
            ]

#@app.route('/copycat', methods=['GET', 'POST'])
def copycat(fromchannel, user):
    client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
    logger = logging.getLogger(__name__)
    channel_name = "openbot-responses"
    conversation_id = None
    try:
        for result in client.conversations_list():
            if conversation_id is not None:
                break
            for channel in result["channels"]:
                if channel["name"] == channel_name:
                    conversation_id = channel["id"]
                    break


    except SlackApiError as e:
        print(f"Error: {e}")


    conv_history = []
    channel_id = fromchannel
    msg = ""
    try:
        result = client.conversations_history(channel=channel_id)

        conv_history = result["messages"]
        msg = conv_history[0]["text"]
        if conv_history[0]["user"] == 'U03KDLNH1RB':
            return 0
        logger.info("{} messages found in {}".format(len(conv_history), id))

    except SlackApiError as e:
        logger.error("Error creating conversation: {}".format(e))
    #print(msg)

    try:
        result = client.chat_postMessage(
            channel=conversation_id,
            text=message_builder([f"<@{user}> sent a message in <#{fromchannel}>!", "The message is below:", msg])
        )
        print(result)

    except SlackApiError as e:
        print(f"Error: {e}")

#    return jsonify()


@app.route('/event', methods=['GET', 'POST'])
def event():
    user = request.form.get("user")
    #channel = request.form.get("channel")
    copycat("C03L6AU206L", user)
    return 200

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080) 

