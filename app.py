from flask import Flask, jsonify, request, Response, render_template, redirect, flash
import os
import datetime
import random
import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import csv

def question_gen(n):
    with open("questionbank.txt", 'r') as f:
        lines = f.readlines()

    if n > len(lines):
        return "No more questions"
    else:
        return lines

def message_builder(message):
    result = ""
    for i in range(len(message)-1):
        result+=message[i]
        result+="\n"
    result+=message[-1]
    return result

error=None
app = Flask(__name__)
app.config['SECRET_KEY'] = "1bfd4baac57db7282f9a941d02511082524cbdf29bb74d60"

def copycat(fromchannel, user):
    client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
    logger = logging.getLogger(__name__)
    channel_name = "openbot-responses"
    conversation_id = client.conversations_open(users=user)['channel']['id']

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
    if msg == "daily" and fromchannel == 'C03L6AU206L':
        try:
            result = client.chat_postMessage(channel=fromchannel,text=message_builder([f"User <@{user}> started a report here in <#{fromchannel}>", f"{question_gen(1)[0]}"]))
        except SlackApiError as e:
            print(f"Error: {e}")
    elif msg.startswith("report"):
        param = msg[7:].split()
        try:
            int(param[-1])
        except:
            param.append('10')
        detail = False
        if param[0] == "summary":
            result = client.chat_postMessage(channel=fromchannel,text="👀")
        elif param[0] == "?" or param[0] == "help":
            result = client.chat_postMessage(channel=fromchannel,text=message_builder([
                "*report help:*",
                "*syntax:* `report [detail] @person1 [@person2 ... @personN] days`",
                    "*all arguments in [] are OPTIONAL*",
                    "detail: add the word 'detail' before all other arguments for extra detail in the report (OPTIONAL)",
                    "@personN: mention people you would like included in the report",
                    "days: the number of days of history you would like a report of"
                ]))
        else:
            if param[0] == "detail":
                detail=True
                del param[0]
            if param[0] == "all":
               print("coming soon feature") 
            elif len(param) == 2:
                print(param[0][2:13])
                userinfo = []
                with open('users.csv', 'r') as f:
                        reader = csv.reader(f)
                        for row in reader:
                            if param[0][2:13] == row[5]:
                                userinfo = row
                                break
                print(userinfo)
                counter = 0
                reports = []
                dates = []
                with open('responses.csv', 'r') as f:
                        reader = csv.reader(f)
                        for row in reader:
                            print(row)
                            if row[0] == userinfo[5] and datetime.datetime.strptime(row[3], '%Y,%m,%d,%H,%M,%S') >= datetime.datetime.now() - datetime.timedelta(days=int(param[-1])):
                                reports.append(f"{datetime.datetime.strptime(row[3], '%Y,%m,%d,%H,%M,%S').strftime('%m/%d/%Y')} Status: `{row[2]}`")
                                if not datetime.datetime.strptime(row[3], '%Y,%m,%d,%H,%M,%S').strftime('%m,%d,%Y') in dates:
                                    counter+=1
                                    dates.append(datetime.datetime.strptime(row[3], '%Y,%m,%d,%H,%M,%S').strftime('%m,%d,%Y'))

                try:
                    if detail:
                        result = client.chat_postMessage(
                            channel=fromchannel,text=message_builder([f"*Report for* <@{userinfo[5]}>*:*", f"*Engagement in the last {param[-1]} days:*", f"{counter}/{param[-1]}        {counter/int(param[-1])*100}%"]
                                + reports))
                    else:
                       result = client.chat_postMessage(
                            channel=fromchannel,text=message_builder([f"*Report for* <@{userinfo[5]}>*:*", f"*Engagement in the last {param[-1]} days:*", f"{counter}/{param[-1]}        {counter/int(param[-1])*100}%"]
                                ))
                except SlackApiError as e:
                    print(f"Error: {e}")
            else:
                userinfos = []
                reports = []
                counters = []
                for i in range(len(param)-1):
                    print(param)
                    print(param[i][2:13])
                    userinfo = []
                    with open('users.csv', 'r') as f:
                            f.seek(0)
                            reader = csv.reader(f)
                            for row in reader:
                                print(row)
                                if param[i][2:13] == row[5]:
                                    userinfo = row
                                    break
                    print(userinfo)
                    counter = 0
                    dates = []
                    with open('responses.csv', 'r') as f:
                            f.seek(0)
                            reader = csv.reader(f)
                            for row in reader:
                                print(row)
                                if row[0] == userinfo[5] and datetime.datetime.strptime(row[3], '%Y,%m,%d,%H,%M,%S') >= datetime.datetime.now() - datetime.timedelta(days=int(param[-1])):
                                    reports.append(f"<@{userinfo[5]}> {datetime.datetime.strptime(row[3], '%Y,%m,%d,%H,%M,%S').strftime('%m/%d/%Y')} Status: `{row[2]}`")
                                    if not datetime.datetime.strptime(row[3], '%Y,%m,%d,%H,%M,%S').strftime('%m,%d,%Y') in dates:
                                        counter+=1
                                        dates.append(datetime.datetime.strptime(row[3], '%Y,%m,%d,%H,%M,%S').strftime('%m,%d,%Y'))
                    userinfos.append(userinfo)
                    counters.append(counter)
                thepeople = ""
                for i in range(len(param)-2):
                    thepeople+=param[i]+", "
                thepeople+="and "+param[len(param)-2]
                leaderboard = []
                for i in range(len(param)-1):
                    temp = ""
                    temp+=param[i]+":   "
                    temp+=str(counters[i])
                    leaderboard.append(temp)
                leaderboard.sort(key=lambda x: x.split(": ")[0], reverse=False)
                try:
                    if not detail:
                        result = client.chat_postMessage(
                            channel=fromchannel,text=message_builder([f"*Report for *{thepeople}*:*", f"*Average engagement for these {len(param)-1} people in the last {param[-1]} days:*", f"{sum(counters)/(len(param)-1)}/{float(param[-1])}        {(sum(counters)/(len(param)-1))/int(param[-1])*100}%", "*Leaderboard:*"] + leaderboard))
                    else:
                        result = client.chat_postMessage(
                            channel=fromchannel,text=message_builder([f"*Report for *{thepeople}*:*", f"*Average engagement for these {len(param)-1} people in the last {param[-1]} days:*", f"{sum(counters)/(len(param)-1)}/{float(param[-1])}        {(sum(counters)/(len(param)-1))/int(param[-1])*100}%", "*Leaderboard:*"] + leaderboard + reports))

                except SlackApiError as e:
                    print(f"Error: {e}")

    elif fromchannel == 'C03L6AU206L':
        lastquestion = ""
        # lastnum = 0
        for i in range(len(conv_history)):
            if conv_history[i]["user"] == 'U03KDLNH1RB':
                lastquestion = conv_history[i]["text"].split("\n")[1]
                # lastnum = conv_history[i]["text"].split("\n")[1][1]
                break
        row = [f'{user}', f'{lastquestion}', f'{msg}', f'{datetime.datetime.now().strftime("%Y,%m,%d,%H,%M,%S")}']
        with open('responses.csv', 'a') as f:
            writer = csv.writer(f)

            writer.writerow(row)

        try:
            result = client.chat_postMessage(channel=fromchannel,text=message_builder([f"Thank you for submitting a response, <@{user}>! It has been copied over to <#{conversation_id}>.", f"Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"]))
        except SlackApiError as e:
            print(f"Error: {e}")
        
        try:
            result = client.chat_postMessage(channel=conversation_id,text=message_builder([f"User <@{user}>'s status:", f"`{msg}`"]))
        except SlackApiError as e:
            print(f"Error: {e}")


#    return jsonify()


@app.route('/event', methods=['GET', 'POST'])
def event():
    #print("uh")
    event = request.get_json()["event"]
    user = event["user"]
    channel = event["channel"]
    print(event)
    copycat(channel, user)
    return ""

if __name__ == "__main__":
    from waitress import serve
    print("Server Started!")
    serve(app, host="0.0.0.0", port=8080) 

