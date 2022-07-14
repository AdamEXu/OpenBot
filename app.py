from flask import Flask, jsonify, request, Response, render_template, redirect, flash
import datetime
import logging
import random
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import csv

def message_builder(message):
    result = ""
    for i in range(len(message)-1):
        result+=message[i]
        result+="\n"
    result+=message[-1]
    return result

app = Flask(__name__)

configs = []

def eventfunc(fromchannel, user):
    print(config)
    client = WebClient(token=config[6])
    logger = logging.getLogger(__name__)

    if user == config[1]:
        return
    conv_history = []
    channel_id = fromchannel
    msg = ""
    try:
        result = client.conversations_history(channel=channel_id)
        conv_history = result["messages"]
        msg = conv_history[0]["text"]
        logger.info("{} messages found in {}".format(len(conv_history), id))

    except SlackApiError as e:
        logger.error("Error creating conversation: {}".format(e))
    if msg.startswith(config[2]):
        param = msg[7:].split()
        try:
            int(param[-1])
        except:
            param.append(config[3])
        detail = False
        if param[0] == "?" or param[0] == "help":
            result = client.chat_postMessage(channel=fromchannel,text="report [detail] @user [num_of_days]\n[] is optional\n*Example:*\n`report @user 10`\n`report summary @user 10`\n`report detail @user 5`")
        else:
            if param[0] == "detail":
                detail=True
                del param[0]
            if param[0] == "all":
                userinfos = []
                reports = []
                counters = []
                with open(f'{config[4]}.csv', 'r') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        if row[0] != "UserID":
                            userinfos.append(row)
                for i in range(len(userinfos)):
                    dates = []
                    userinfo = userinfos[i]
                    print(userinfo)
                    counter = 0
                    with open(f'{config[5]}.csv', 'r') as f:
                        reader = csv.reader(f)
                        for row in reader:
                            if row[0] == 'UserID':
                                continue
                            elif row[0] == userinfo[5]:
                                print(row)
                                if datetime.datetime.strptime(row[3], '%Y,%m,%d,%H,%M,%S') >= datetime.datetime.now() - datetime.timedelta(days=int(param[-1])-1):
                                    reports.append(f"<@{userinfo[5]}> {datetime.datetime.strptime(row[3], '%Y,%m,%d,%H,%M,%S').strftime('%m/%d/%Y')} Status: `{row[2]}`")
                                    if not datetime.datetime.strptime(row[3], '%Y,%m,%d,%H,%M,%S').strftime('%m,%d,%Y') in dates:
                                        counter+=1
                                        dates.append(datetime.datetime.strptime(row[3], '%Y,%m,%d,%H,%M,%S').strftime('%m,%d,%Y'))
                    counters.append(counter)
                thepeople = ""
                for i in range(len(userinfos)-1):
                    thepeople+=f"<@{userinfos[i][5]}>, "
                thepeople+=f"and <@{userinfos[-1][5]}>"
                leaderboard = []
                for i in range(len(userinfos)):
                    temp = ""
                    temp+=f"<@{userinfos[i][5]}>: "
                    temp+=str(counters[i])
                    leaderboard.append(temp)
                leaderboard.sort(key=lambda x: x.split(": ")[1], reverse=True)
                try:
                    if not detail:
                        result = client.chat_postMessage(
                            channel=fromchannel,text=message_builder([f"*Report for *{thepeople}*:*", f"*Average engagement for these {len(userinfos)} people in the last {param[-1]} days:*", f"{round(sum(counters)/len(userinfos), 2)}/{float(param[-1])}        {round((sum(counters)/(len(userinfos)))/int(param[-1])*100, 2)}%", "*Leaderboard:*"] + leaderboard))
                    else:
                        print(reports, "\n\n\n\n\n\n")
                        result = client.chat_postMessage(
                            channel=fromchannel,text=message_builder([f"*Report for *{thepeople}*:*", f"*Average engagement for these {len(userinfos)} people in the last {param[-1]} days:*", f"{round(sum(counters)/len(userinfos), 2)}/{float(param[-1])}        {round((sum(counters)/(len(userinfos)))/int(param[-1])*100, 2)}%", "*Leaderboard:*"] + leaderboard + reports))

                except SlackApiError as e:
                    print(f"Error: {e}")
            elif len(param) == 2:
                print(param[0][2:].rstrip(">"))
                userinfo = []
                with open(f'{config[4]}.csv', 'r') as f:
                        reader = csv.reader(f)
                        for row in reader:
                            print(row)
                            if param[0][2:].rstrip(">") == row[5]:
                                userinfo = row
                                break
                print(userinfo)
                counter = 0
                reports = []
                dates = []
                with open(f'{config[5]}.csv', 'r') as f:
                        reader = csv.reader(f)
                        for row in reader:
                            print(row)
                            print(userinfo)
                            if row[0] != 'UserID':
                                if row[0] == userinfo[5] and datetime.datetime.strptime(row[3], '%Y,%m,%d,%H,%M,%S') >= datetime.datetime.now() - datetime.timedelta(days=int(param[-1])-1):
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
                       result = client.chat_postMessage(channel=fromchannel,text=message_builder([f"*Report for* <@{userinfo[5]}>*:*", f"*Engagement in the last {param[-1]} days:*", f"{counter}/{param[-1]}        {counter/int(param[-1])*100}%"]))
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
                    with open(f'{config[4]}.csv', 'r') as f:
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
                    with open(f'{config[5]}.csv', 'r') as f:
                            f.seek(0)
                            reader = csv.reader(f)
                            for row in reader:
                                print(row)
                                if row[0] == userinfo[5] and datetime.datetime.strptime(row[3], '%Y,%m,%d,%H,%M,%S') >= datetime.datetime.now() - datetime.timedelta(days=int(param[-1])-1):
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

    elif msg.startswith("migrate"):
        param = msg[7:].split()
        print(param)
        userids = client.conversations_members(channel=param[0])
        with open('num.txt', 'w') as f:
            f.write("1")
        f = open(f'{config[4]}.csv', 'w')
        f.close()
        for i in range(len(userids["members"])):
            userid = userids["members"][i]
            if userid == config[1]:
                continue
            print(userid)
            userinfo = client.users_info(user=userid)["user"]
            print(userinfo)
            with open('num.txt', 'r') as f:
                num = int(f.readline())
            with open('num.txt', 'w') as f:
                f.write(str(num+1))
            row = [f'{num}', f'{userinfo["real_name"].split()[0]}', f'{userinfo["real_name"].split()[-1]}', f'TEMP@TEMP.TEMP', f'{userinfo["team_id"]}', f'{userid}']
            with open(f'{config[4]}.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow(row)
        f = open(f'{config[5]}.csv', 'w')
        f.close()
        messages = client.conversations_history(channel=config[0])
        for i in range(len(messages["messages"])):
            message = messages["messages"][i]
            print(message)
            try:
                if message["user"] == config[1]:
                    continue
                if message["type"] == "message":
                    with open(f'{config[5]}.csv', 'a') as f:
                        writer = csv.writer(f)
                        writer.writerow([f'{message["user"]}', "Status", f'{message["text"]}', datetime.datetime.fromtimestamp(int(float(message["ts"]))).strftime('%Y,%m,%d,%H,%M,%S')])
            except:
                continue
        try:
            result = client.chat_postMessage(
                channel=fromchannel,text=message_builder([f"Successfully migrated {len(userids['members'])} users and {''} statuses over to your brand new shiny OpenBot system!", f"Try out a command like `report <@{userids['members'][random.randint(0,len(userids['members']))]}> {random.randint(5, 10)}`!", f"Or alternatively you can use `report help` to see the syntax of the command for yourself!"])
            )
        except SlackApiError as e:
            print(f"Error: {e}")

    elif fromchannel == config[0]:
        row = [f'{user}', f'Status', f'{msg}', f'{datetime.datetime.now().strftime("%Y,%m,%d,%H,%M,%S")}']
        with open(f'{config[5]}.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow(row)
        # try:
        #     result = client.chat_postMessage(channel=fromchannel,text=message_builder([f"Daily status accepted from <@{user}>!", f"Timestamp: `{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`"]))
        # except SlackApiError as e:
        #     print(f"Error: {e}")

@app.route('/event', methods=['GET', 'POST'])
def event():
    if request.method == 'POST':
        print("hello")
        event = request.get_json()["event"]
        user = event["user"]
        channel = event["channel"]
        eventfunc(channel, user)
        # print(request.get_json())
        # return request.get_json()["challenge"]
        return ""
    elif request.method == 'GET':
        return render_template('index.html')

if __name__ == "__main__":
    from waitress import serve
    with open('config.txt', 'r') as f:
        config = f.readlines()
    for i in range(len(config)):
        config[i] = config[i].split('::')[1].rstrip()
    print("Server Started!")
    serve(app, host="0.0.0.0", port=8080) 

