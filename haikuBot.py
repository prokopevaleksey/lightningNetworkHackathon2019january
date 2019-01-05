import requests
import json
import numpy as np

import logging
import telegram
from telegram.error import NetworkError, Unauthorized
from time import sleep

apikey = "supply your open node api key here"
token = "supply your telegram token here"

def generateCharge(amount,currency="USD"):
    r = requests.post(url = "https://dev-api.opennode.co/v1/charges",
                  headers = {
                        'Content-Type': 'application/json',
                        'Authorization': apikey
                            },
                  data = json.dumps({
                        "amount": amount,
                        "currency": currency,
                        "callback_url": "https://site.com/?handler=opennode",
                        "success_url": "https://site.com/order/abc123"
                            })
                 )
    return r.json()

def paidCharges():
    r = requests.get(url = 'https://dev-api.opennode.co/v1/charges', 
                    headers={
                  'Content-Type': 'application/json',
                  'Authorization': apikey
                        }
                   )
    return r.json()

def chargeInfo(idx):
    r = requests.get(url = 'https://dev-api.opennode.co/v1/charge/'+idx, 
                   headers={
                          'Content-Type': 'application/json',
                          'Authorization': apikey
                        })
    return r.json()

def take_order():
    start = time()

    haiku = haikuGenerator()

    server_cost = time()-start

    commition = 0.1

    total_cost = server_cost+commition

    print('your invoice is',"%0.2f" % total_cost)

    charge = generateCharge(total_cost)

    print('lightning Request:',charge['data']['lightning_invoice']['payreq'])

    idx = charge['data']['id']
    
    return haiku,total_cost,charge['data']['lightning_invoice']['payreq'],idx

update_id = None

orders = {}

def main():
    global update_id
    bot = telegram.Bot(token)

    try:
        update_id = bot.get_updates()[0].update_id
    except IndexError:
        update_id = None

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    while True:
        try:
            haikuBot(bot)
        except NetworkError:
            sleep(1)
        except Unauthorized:
            update_id += 1

def haikuBot(bot):
    global update_id
    # Request updates after the last update_id
    for update in bot.get_updates(offset=update_id, timeout=100):
        update_id = update.update_id + 1

        if update.message:  # your bot can receive updates without messages
            # Reply to the message
            if update.message.text == "gimme a haiku":
                haiku,total_cost,payreq,idx = take_order()
                orders[idx] = haiku
                update.message.reply_text("it will cost you "+str(total_cost))
                update.message.reply_text("you can pay it followinf this link: https://dev-checkout.opennode.co/"+idx)
                update.message.reply_text('send this number to get your haiku after you pay:')
                update.message.reply_text(idx)
                print('secret haiku is\n',haiku)
                
                
            elif update.message.text in orders.keys():
                haiku = orders[update.message.text]
                
                info = chargeInfo(update.message.text)
                    
                if info['data']['status'] == 'paid':
                    update.message.reply_text('here we go:\n'+haiku)
                else:
                    update.message.reply_text("you didn't pay!")
            else:
                update.message.reply_text("say gimme a haiku")

def haikuGenerator():
    wordList1 = ["Enchanting", "Amazing", "Colourful", "Delightful", "Delicate"]
    wordList2 = ["visions", "distance", "conscience", "process", "chaos"]
    wordList3 = ["superstitious", "contrasting", "graceful", "inviting", "contradicting", "overwhelming"]
    wordList4 = ["true", "dark", "cold", "warm", "great"]
    wordList5 = ["scenery","season", "colours","lights","Spring","Winter","Summer","Autumn"]
    wordList6 = ["undeniable", "beautiful", "irreplaceable", "unbelievable", "irrevocable"]
    wordList7 = ["inspiration", "imagination", "wisdom", "thoughts"]
    wordIndex1=np.random.randint(0, len(wordList1)-1)
    wordIndex2=np.random.randint(0, len(wordList2)-1)
    wordIndex3=np.random.randint(0, len(wordList3)-1)
    wordIndex4=np.random.randint(0, len(wordList4)-1)
    wordIndex5=np.random.randint(0, len(wordList5)-1)
    wordIndex6=np.random.randint(0, len(wordList6)-1)
    wordIndex7=np.random.randint(0, len(wordList7)-1)

    haiku = wordList1[wordIndex1] + " " + wordList2[wordIndex2] + ",\n" 
    haiku = haiku + wordList3[wordIndex3] + " " + wordList4[wordIndex4] + " " + wordList5[wordIndex5]  + ",\n"
    haiku = haiku + wordList6[wordIndex6] + " " + wordList7[wordIndex7] + "."

    return haiku

if __name__ == '__main__':
    main()