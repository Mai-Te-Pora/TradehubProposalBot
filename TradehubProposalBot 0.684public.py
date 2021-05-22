# TradehubProposalBot b0.684
# Copyright © 2021 Coco & Intsol for Switcheo / MaiTePora <3
# Licenced under GPL

# LIBRARYS
# ------------------------------------------------------------------------------
import urllib.request
import json
import time
import requests

# PARAMETERS
# ------------------------------------------------------------------------------
testing = True
sleepTime = 300  # Time sleep (300 for 5 min)
telegramBotToken = '<BOT_TOKEN>'
telegramBotChatIDs = ['<CHAT-ID>']

discordWebHooks = [
    'https://discord.com/api/webhooks/<channel-webhook>',
    ]

# CONSTANTS
# ------------------------------------------------------------------------------
JSON_FILE = 'proposalpassed.json'

proposalStatus = "VotingPeriod"

activeIDs = []
currentIDs = []
announcedIDs = []
resultIDs = []

dataSave = {}
dataSave["announcedIDs"] = announcedIDs
dataSave["resultIDs"] = resultIDs
dataSave["currentIDs"] = currentIDs


# FUNCTIONS
# ------------------------------------------------------------------------------
def telegramBotSendtext(botMessage):
    botToken = telegramBotToken
    for botChatID in telegramBotChatIDs:
        sendText = 'https://api.telegram.org/bot' + botToken + '/sendMessage?chat_id=' + botChatID + '&parse_mode=Markdown&text=' + botMessage
        response = requests.get(sendText)

    return response.json()


def discordSendText(message):

    data = {"content": message}

    for hook in discordWebHooks:
        try:
            response = requests.post(hook, json=data)
        except:
            print('Error posting to discord')


# TEST MODE
# ------------------------------------------------------------------------------
if testing:
    sleepTime = 5
    proposalStatus = "Passed"
    print('Test mode')

# MAIN
# ------------------------------------------------------------------------------
print('TradehubProposalBot b0.684')

while True:
    try:
        # Pause between checks
        time.sleep(sleepTime)

        # Check for proposals
        with urllib.request.urlopen("https://tradescan.switcheo.org/gov/proposals") as url:
            proposals = json.loads(url.read().decode())

            # Check active proposal ID's
            activeProposals = [d for d in proposals["result"] if d['proposal_status'] == (proposalStatus)]
            activeIDs = []  # Reset activeIDs
            for d in activeProposals:
                activeIDs.append(d['id'])

            # Try to load any existing saved data
            try:
                with open(JSON_FILE, 'r') as file:
                    dataSave = json.load(file)
                    if testing == True:
                        print("Data loaded", dataSave)
            except:
                print("No data loaded")
            pass

            # Remove the already announced proposals
            for elem in dataSave["announcedIDs"]:
                activeIDs.remove(elem)

            # get the earliest proposal
            proposalsID = (activeIDs[0])

            # Check if there are any new proposals
            newProposals = [d for d in proposals["result"] if d['proposal_status'] == (proposalStatus) if
                            d['id'] == (proposalsID)]
            for d in newProposals:
                proposalId = (d['id'])
                proposalTitle = (d['content']['value']['title'])

                proposalText = f"New proposal available - {proposalId} - {proposalTitle} - please vote [here](https://switcheo.org/governance/proposal/{proposalId})"
                resp = telegramBotSendtext(proposalText)
                print(resp)

                discordSendText(proposalText)

                dataSave["announcedIDs"].append(proposalId)
                dataSave["currentIDs"].append(proposalId)

            # Check if a recent proposal has ended
            endProposal = [d for d in proposals["result"] if
                           d['proposal_status'] == "Passed" or d['proposal_status'] == "Rejected" if
                           d['id'] in dataSave["currentIDs"]]

            for d in endProposal:
                endProposalId = (endProposal[0]['id'])
                endProposalTitle = (endProposal[0]['content']['value']['title'])

                proposalText = f"Recent vote for proposal - {endProposalId} - {endProposalTitle} has ended.\n\nThe results are [here](https://switcheo.org/governance/proposal/{endProposalId})\n\n The Proposal: {d['proposal_status']}\n\n Thanks for your participation"
                resp = telegramBotSendtext(proposalText)
                print(resp)

                discordSendText(proposalText)

                dataSave["resultIDs"].append(d['id'])
                dataSave["currentIDs"].remove(d['id'])

            # Overwrite the saved data
            with open(JSON_FILE, 'w') as file:
                json.dump(dataSave, file)

    except:
        pass