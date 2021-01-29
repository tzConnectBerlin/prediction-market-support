#!/usr/bin/env python3

import configparser
import dateparser
from datetime import datetime
import ipfshttpclient
import json
import pytezos
import pytz
import wolframalpha

config = configparser.ConfigParser()
config.read('oracle.ini')

pytezos.key = pytezos.Key.from_encoded_key(config['Tezos']['privkey'])
print(config['Tezos']['privkey'])
contract = pytezos.pytezos.contract(config['Tezos']['contract'])

def answer(details):
    wolfram = wolframalpha.Client(config['Wolfram']['AppId'])
    ipfs = ipfshttpclient.connect(config['IPFS']['server'])
    question_details = ipfs.get_json(details['question_id'])
    res = wolfram.query(question_details.query)
    result = res['pod'][1]['subpod']['plaintext']
    if res.startswith(question_details.yes_answer):
        the_answer = True
    else:
        the_answer = False
#    contract.answer(ipfs, the_answer).inject()

storage = contract.storage()

questions = storage['questions'].keys()

for question in questions:
    print(question)
    details = storage['questions'][question]
    print(details)
    answer_at = dateparser.parse(details['answer_at'])
    # if answer_at > pytz.UTC.localize(datetime.now()):
    answer(details)
    # else:
    #print("Not time yet")
