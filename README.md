# Scripts to support PM


## Installation
```
poetry install
```

Usage:
```
poetry shell
./cli.py
```
How to use:

First set up your own environement using the cli.ini file
```
  [IPFS]
  server=/ip4/49.12.41.161/tcp/5001
  
  [Tezos]
  node=tezos.newby.org
  port=8732
  endpoint=http://localhost:20000
  pm_contract=KT1MLoV9BMpWAPYZNm9NDJ18Vch3HLjXdFT6
  stablecoin=KT1VKHPi2rWsRGPpZ6WpNxrKGtGA1LRcgFAp
  contract_path=/home/killua/prediction-market-contracts-lazy/container/main.mligo  .m4
  stablecoin_path=/home/killua/Projects/tezos/prediction-market-contracts/src/cont  racts/third-party/FA12Permissive.ligo
  owner=tz1VSUr8wwNhLAzempoch5d6hLRiTh8Cjcjb
_ privkey=edsk3QoqBuvdamxouPhin7swCvkQNgq4jP5KZPbwWNnwdZpSpJiEbq

```

It uses accounts imported in your tezos client
Basic use is:
```
./cli.py [flags ][command] [user using the command] [command options]
```

./cli.py gives you a partial documentation on how to use the tool  [IPFS]
