# TradehubProposalBot b0.684
# Copyright © 2021 Coco & Intsol for Switcheo / MaiTePora <3
# Licenced under GPL

# This version supports the updatedCarbon API endpoints and JSON

# LIBRARYS
# ------------------------------------------------------------------------------
import urllib.request
import json
import time
import requests
import traceback

# https://github.com/cosmos/cosmos-sdk/blob/v0.44.4/x/gov/types/gov.pb.go#L98
# Proposal voting stages
# ref: https://github.com/cosmos/cosmos-sdk/blob/v0.44.4/x/gov/types/gov.pb.go#L98
ProposalStatusName = {
    0: "Unspecified",
    1: "Deposit",
    2: "Voting",
    3: "Passed",
    4: "Rejected",
    5: "Failed",
}

# PARAMETERS
# ------------------------------------------------------------------------------
TESTING = False
proposalAPI = "https://api.carbon.network/gov/proposals"
voteURL     = "https://scan.carbon.network/governance/proposal/"

# CONSTANTS
# ------------------------------------------------------------------------------
JSON_FILE = 'proposalpassed.json'

activeIDs = []
announcedIDs = []
resultIDs = []

dataSave = {}
dataSave["announcedIDs"] = announcedIDs
dataSave["resultIDs"] = resultIDs

# TEST MODE
# ------------------------------------------------------------------------------
if TESTING:
    testing = True
    sleepTime = 5  # Time sleep (300 for 5 min)
    telegramBotToken = '<BOT_TOKEN>'
    telegramBotChatIDs = ['<CHAT-ID>']

    discordWebHooks = [
        'https://discord.com/api/webhooks/<channel-webhook>',
    ]
else:
    testing = False
    sleepTime = 300  # Time sleep (300 for 5 min)
    telegramBotToken = '<BOT_TOKEN>'
    telegramBotChatIDs = ['<CHAT-ID>',]

    discordWebHooks = [
        'https://discord.com/api/webhooks/<channel-webhook>',
    ]


# FUNCTIONS
# ------------------------------------------------------------------------------
def telegramBotSendtext(botMessage):
    botToken = telegramBotToken
    for botChatID in telegramBotChatIDs:
        sendText = f'https://api.telegram.org/bot{botToken}/sendMessage?chat_id={botChatID}&parse_mode=Markdown&text={botMessage}'
        response = requests.get(sendText)

    return response.json()


def discordSendText(message):
    data = {"content": message}

    for hook in discordWebHooks:
        try:
            response = requests.post(hook, json=data)
        except:
            print('Error posting to discord')


# MAIN
# ------------------------------------------------------------------------------
print('TradehubProposalBot b0.685')

while True:
    try:

        # Check for proposals
        with urllib.request.urlopen(proposalAPI) as url:
            proposals = json.loads(url.read().decode())

            # Check active proposal ID's
            allProposals = proposals["result"]

            # Try to load any existing saved data
            try:
                with open(JSON_FILE, 'r') as file:
                    dataSave = json.load(file)
                    if TESTING == True:
                        print("Data loaded", dataSave)
            except:
                print("No data loaded")
            pass

            # Check if there are any new proposals
            newProposals = [d for d in allProposals if d['status'] == 2 if d['id'] not in dataSave['announcedIDs'] ]

            for d in newProposals:
                proposalId = (d['id'])
                proposalTitle = (d['content']['value']['title'])

                proposalText = f"**Proposal {proposalId} available for voting** \n{proposalTitle} - please vote [here]({voteURL}{proposalId})"

                resp = telegramBotSendtext(proposalText)
                print(resp)

                discordSendText(proposalText)

                dataSave["announcedIDs"].append(proposalId)

            # Check if a recent proposal has ended
            endProposals = [d for d in allProposals if d['status'] in [3,4] if d['id'] not in dataSave['resultIDs'] ]

            print(endProposals)

            for d in endProposals:
                endProposalId = (d['id'])
                endProposalTitle = (d['content']['value']['title'])

                proposalText = f"**Vote for proposal {endProposalId} has ended** - {endProposalTitle}\nThe results are [here]({voteURL}{endProposalId})\nThe Proposal: **{ProposalStatusName[d['status']]}**\nThanks for your participation"
                resp = telegramBotSendtext(proposalText)
                print(resp)

                discordSendText(proposalText)

                dataSave["resultIDs"].append(d['id'])

            # Overwrite the saved data
            with open(JSON_FILE, 'w') as file:
                json.dump(dataSave, file)

    except Exception as exc:
        print(traceback.format_exc())
        print(exc)

    finally:
        # Pause between checks
        time.sleep(sleepTime)

