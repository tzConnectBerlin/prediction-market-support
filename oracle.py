#!/usr/bin/env python3

import configparser
import ipfshttpclient
from pytezos import pytezos
import wolframalpha

config = configparser.ConfigParser()
config.read('woracle.ini')

wolfram = wolframalpha.Client(config['Wolfram']['AppId'])

ipfs = ipfshttpclient.connect(config['IPFS']['server'])
ipfs.cat('QmWkFfFjDUiJkQ8kBz45ACr2SQ9iPFUENLz6PTx92Ykq36')
