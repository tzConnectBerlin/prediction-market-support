#!/usr/bin/env python3

import configparser
import dateparser
from datetime import datetime
import ipfshttpclient
from pytezos import pytezos
import wolframalpha

config = configparser.ConfigParser()
config.read('woracle.ini')

pytezos.key = pytezos.Key.from_encoded_key(config['Tezos']['privkey'])

contract = pytezos.contract(config['Tezos']['contract'])

def answer(details):
    wolfram = wolframalpha.Client(config['Wolfram']['AppId'])
    ipfs = ipfshttpclient.connect(config['IPFS']['server'])
    question_details = ipfs.cat(details.query)
    res = wolfram.query(question_details.query)
    result = res['pod'][1]['subpod']['plaintext']
    if res.startswith(question_details.yes_answer):
        the_answer = True
    else:
        the_answer = False
    contract.

storage = contract.storage()

questions = storage.questions.keys()

for question in questions:
    details = storage['questions'][question]
    answer_at = dateparser.parse(details['answer_at'])
    if answer_at > datetime.now():
        answer(details)
