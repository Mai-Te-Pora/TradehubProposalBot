# TradehubProposalBot b0.670
# Copyright © 2021 Coco & Intsol for Switcheo / MaiTePora <3
# Licenced under GPL

# LIBRARYS
# ------------------------------------------------------------------------------
import urllib.request
import json
import time
    
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

# PARAMETERS
# ------------------------------------------------------------------------------
testing = True 
sleepTime = 300   #Time sleep (300 for 5 min)

# TEST MODE
# ------------------------------------------------------------------------------
if testing == True:
    sleepTime = 5
    proposalsStatus = "Passed"
    print ('Test mode')

# MAIN
# ------------------------------------------------------------------------------
print ('TradehubProposalBot b0.670')

while True :
    try:
        #Pause between checks
        time.sleep(sleepTime)   

        #Check for proposals
        with urllib.request.urlopen("https://tradescan.switcheo.org/gov/proposals") as url:
            info = json.loads(url.read().decode())

            #Check active proposal ID's
            activeProposals =[d for d in info["result"] if d['proposal_status'] == (proposalsStatus)]
            activeIdS = [] #Reset activeIdS
            for d in activeProposals:
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

            proposalsID = (activeIdS[0])       
           
            #Check if there is a new proposal
            proposals =[d for d in info["result"] if d['proposal_status'] == (proposalsStatus) if d['id'] == (proposalsID)]
            for d in proposals:
                proposalsID = (proposals[0]['id'])
                proposalsTitle = (proposals[0]['content']['value']['title'])

                print ("New proposal available -", proposalsID, "-", proposalsTitle, "- please give your vote on:", f"https://switcheo.org/governance/proposal/{proposalsID}")
                
                dataSave["announcedIdS"].append(proposalsID)
                dataSave["currentIdS"].append(proposalsID)

            #Check if a recent proposal has ended
            endProposal =[d for d in info["result"] if d['proposal_status'] == "Passed" or d['proposal_status'] == "Rejected" if d['id'] in dataSave["currentIdS"]]
            for d in endProposal:
                endProposalID = (endProposal[0]['id'])
                endProposalTitle = (endProposal[0]['content']['value']['title'])

                print ("Recent vote for proposal:", endProposalID, "-", endProposalTitle, "Here is the results =>", d['proposal_status'], f"https://switcheo.org/governance/proposal/{endProposalID}", "Thanks for your participation")
                
                dataSave["resultIdS"].append(d['id'])
                dataSave["currentIdS"].remove(d['id'])

            # Overwrite the saved data
            with open(JSON_FILE, 'w') as file:
                json.dump(dataSave, file)
               
    except:
        pass