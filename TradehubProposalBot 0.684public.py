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
sleepTime = 300   #Time sleep (300 for 5 min)
telegram_bot_token = '10987485:AAF8RrWYxQH6vzwyN3dmSflGT57_8'
telegram_bot_chatID = '-43098739'
    
# CONSTANTS
# ------------------------------------------------------------------------------
JSON_FILE = 'proposalpassed.json'

proposalsStatus = "VotingPeriod"

activeIdS = []
currentIdS = []
announcedIdS = []
resultIdS = []

dataSave = {}
dataSave["announcedIdS"] = announcedIdS
dataSave["resultIdS"] = resultIdS
dataSave["currentIdS"] = currentIdS

# FUNCTIONS
# ------------------------------------------------------------------------------
def telegram_bot_sendtext(bot_message):
    
    bot_token = telegram_bot_token
    bot_chatID = telegram_bot_chatID
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message

    response = requests.get(send_text)

    return response.json()

# TEST MODE
# ------------------------------------------------------------------------------
if testing == True:
    sleepTime = 5
    proposalStatus = "Passed"
    print ('Test mode')

# MAIN
# ------------------------------------------------------------------------------
print ('TradehubProposalBot b0.684')

while True :
    try:
        #Pause between checks
        time.sleep(sleepTime)   

        #Check for proposal
        with urllib.request.urlopen("https://tradescan.switcheo.org/gov/proposals") as url:
            info = json.loads(url.read().decode())

            #Check active proposal ID's
            activeProposal =[d for d in info["result"] if d['proposal_status'] == (proposalStatus)]
            activeIdS = [] #Reset activeIdS
            for d in activeProposal:
                activeIdS.append(d['id'])

            # Try to load any existing saved data
            try:
                with open(JSON_FILE, 'r') as file:
                    dataSave = json.load(file)
                    if testing == True:
                        print ("Data loaded", dataSave)
            except:
                    print ("No data loaded")
            pass

            # Actualize data
            for elem in dataSave["announcedIdS"]:
                activeIdS.remove(elem)

            proposalIdS = (activeIdS[0])       
           
            #Check if there is a new proposal
            proposal =[d for d in info["result"] if d['proposal_status'] == (proposalStatus) if d['id'] == (proposalIdS)]
            for d in proposal:
                proposalIdS = (proposal[0]['id'])
                proposalTitle = (proposal[0]['content']['value']['title'])

                proposalText = f"New proposal available - {proposalIdS} - {proposalTitle} - please give your vote on: https://switcheo.org/governance/proposal/{proposalIdS}"
                test = telegram_bot_sendtext(proposalText)
                print (test)

                dataSave["announcedIdS"].append(proposalIdS)
                dataSave["currentIdS"].append(proposalIdS)

            #Check if a recent proposal has ended
            endProposal =[d for d in info["result"] if d['proposal_status'] == "Passed" or d['proposal_status'] == "Rejected" if d['id'] in dataSave["currentIdS"]]
            for d in endProposal:
                endProposalID = (endProposal[0]['id'])
                endProposalTitle = (endProposal[0]['content']['value']['title'])
                
                proposalText = f"Recent vote for proposal - {endProposalID} - {endProposalTitle} - Here is the results => https://switcheo.org/governance/proposal/{endProposalID} - {d['proposal_status']} <- Thanks for your participation"
                test = telegram_bot_sendtext(proposalText)
                print (test)

                dataSave["resultIdS"].append(d['id'])
                dataSave["currentIdS"].remove(d['id'])

            # Overwrite the saved data
            with open(JSON_FILE, 'w') as file:
                json.dump(dataSave, file)
               
    except:
        pass