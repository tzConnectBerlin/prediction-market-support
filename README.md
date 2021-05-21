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
# `main`

High level options

**Usage**:

```console
$ main [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `-w, --with-account TEXT`
* `--ignore-account TEXT`
* `-e, --endpoint TEXT`
* `-c, --contract TEXT`
* `--admin-key TEXT`
* `--config-file TEXT`: [default: cli.ini]
* `-f, --force`
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `approve-market`: Approve a quantity of stablecoin to be use by...
* `ask-question`: Create a question in IPFS question: string...
* `bid-auction`: Bid on an auction market_id: the contract to...
* `burn`: Burn a quantity stablecoin for account
* `claim-winnings`: Claim winnings for user
* `clear-market`: Clear the auction market_id: the id of the...
* `close-market`: Close the market market_id: the id of the...
* `display-tokens`
* `enter-market`: Enter the market
* `exit-market`: Exit the market
* `fund-stablecoin`: Fund all accounts with a random quantity of...
* `get-market-liquidity`
* `get-market-metadata`
* `list-accounts`: List all of the accounts
* `manage-accounts`: Management of accounts in the user folder
* `mint`: Mint a quantity of stablecoin for user
* `random-bids`: Launch random bid on a auction for all of the...
* `stablecoin-balance`: Get balance for user
* `swap-liquidity`: Update the liquidity for the market
* `swap-tokens`: Swap one outcome token through the liquidity...
* `transfer-stablecoin`: Transfer a certain amount of coins toward an...
* `withdraw-auction`: Withdraw the auction market_id: the id of the...

## `main approve-market`

Approve a quantity of stablecoin to be use by the market

**Usage**:

```console
$ main approve-market [OPTIONS] USER AMOUNT
```

**Arguments**:

* `USER`: [required]
* `AMOUNT`: [required]

**Options**:

* `--help`: Show this message and exit.

## `main ask-question`

Create a question in IPFS

question: string representing the answer asked
answer: string representing the possible answer
user: string representing the questions owner
quantity: integer representing the quantity of stable coin generated
rate: rate

**Usage**:

```console
$ main ask-question [OPTIONS] QUESTION ANSWER USER [QUANTITY] [RATE] [AUCTION_END_DATE]
```

**Arguments**:

* `QUESTION`: [required]
* `ANSWER`: [required]
* `USER`: [required]
* `[QUANTITY]`: [default: 5000000000]
* `[RATE]`: [default: 4571870618034696826]
* `[AUCTION_END_DATE]`: [default: 1]

**Options**:

* `--help`: Show this message and exit.

## `main bid-auction`

Bid on an auction

market_id: the contract to use
user: string representing the user who is bidding
quantity: quantity of stable coins bid during the auction
rate: What is rate?

**Usage**:

```console
$ main bid-auction [OPTIONS] MARKET_ID USER [QUANTITY] [RATE]
```

**Arguments**:

* `MARKET_ID`: [required]
* `USER`: [required]
* `[QUANTITY]`: [default: 500000000]
* `[RATE]`: [default: 12759921066255100347]

**Options**:

* `--help`: Show this message and exit.

## `main burn`

Burn a quantity stablecoin for account

**Usage**:

```console
$ main burn [OPTIONS] MARKET_ID USER AMOUNT
```

**Arguments**:

* `MARKET_ID`: [required]
* `USER`: [required]
* `AMOUNT`: [required]

**Options**:

* `--help`: Show this message and exit.

## `main claim-winnings`

Claim winnings for user

**Usage**:

```console
$ main claim-winnings [OPTIONS] MARKET_ID USER
```

**Arguments**:

* `MARKET_ID`: [required]
* `USER`: [required]

**Options**:

* `--help`: Show this message and exit.

## `main clear-market`

Clear the auction

market_id: the id of the question

**Usage**:

```console
$ main clear-market [OPTIONS] MARKET_ID USER
```

**Arguments**:

* `MARKET_ID`: [required]
* `USER`: [required]

**Options**:

* `--help`: Show this message and exit.

## `main close-market`

Close the market

market_id: the id of the concerned market
token_type: type of the token
user: owner of the market

**Usage**:

```console
$ main close-market [OPTIONS] MARKET_ID USER [TOKEN_TYPE]
```

**Arguments**:

* `MARKET_ID`: [required]
* `USER`: [required]
* `[TOKEN_TYPE]`: [default: True]

**Options**:

* `--help`: Show this message and exit.

## `main display-tokens`

**Usage**:

```console
$ main display-tokens [OPTIONS] MARKET_ID USER
```

**Arguments**:

* `MARKET_ID`: [required]
* `USER`: [required]

**Options**:

* `--help`: Show this message and exit.

## `main enter-market`

Enter the market

**Usage**:

```console
$ main enter-market [OPTIONS] MARKET_ID USER AMOUNT
```

**Arguments**:

* `MARKET_ID`: [required]
* `USER`: [required]
* `AMOUNT`: [required]

**Options**:

* `--help`: Show this message and exit.

## `main exit-market`

Exit the market

**Usage**:

```console
$ main exit-market [OPTIONS] MARKET_ID USER AMOUNT
```

**Arguments**:

* `MARKET_ID`: [required]
* `USER`: [required]
* `AMOUNT`: [required]

**Options**:

* `--help`: Show this message and exit.

## `main fund-stablecoin`

Fund all accounts with a random quantity of tezos

value: the amont of tezos funded

**Usage**:

```console
$ main fund-stablecoin [OPTIONS] [VALUE]
```

**Arguments**:

* `[VALUE]`: [default: 100000000000]

**Options**:

* `--help`: Show this message and exit.

## `main get-market-liquidity`

**Usage**:

```console
$ main get-market-liquidity [OPTIONS] MARKET_ID USER
```

**Arguments**:

* `MARKET_ID`: [required]
* `USER`: [required]

**Options**:

* `--help`: Show this message and exit.

## `main get-market-metadata`

**Usage**:

```console
$ main get-market-metadata [OPTIONS] MARKET_ID
```

**Arguments**:

* `MARKET_ID`: [required]

**Options**:

* `--help`: Show this message and exit.

## `main list-accounts`

List all of the accounts

**Usage**:

```console
$ main list-accounts [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `main manage-accounts`

Management of accounts in the user folder

**Usage**:

```console
$ main manage-accounts [OPTIONS]
```

**Options**:

* `-a, --activate`: [default: False]
* `-r, --reveal`: [default: False]
* `-i, --import`: [default: False]
* `--help`: Show this message and exit.

## `main mint`

Mint a quantity of stablecoin for user

**Usage**:

```console
$ main mint [OPTIONS] MARKET_ID USER AMOUNT
```

**Arguments**:

* `MARKET_ID`: [required]
* `USER`: [required]
* `AMOUNT`: [required]

**Options**:

* `--help`: Show this message and exit.

## `main random-bids`

Launch random bid on a auction for all of the chosen users folder

market_id: Contract on which the bid are made

**Usage**:

```console
$ main random-bids [OPTIONS] MARKET_ID [QUANTITY]
```

**Arguments**:

* `MARKET_ID`: [required]
* `[QUANTITY]`: [default: 500000000]

**Options**:

* `--rate INTEGER`: [default: -1]
* `--help`: Show this message and exit.

## `main stablecoin-balance`

Get balance for user

**Usage**:

```console
$ main stablecoin-balance [OPTIONS] USER
```

**Arguments**:

* `USER`: [required]

**Options**:

* `--help`: Show this message and exit.

## `main swap-liquidity`

Update the liquidity for the market

**Usage**:

```console
$ main swap-liquidity [OPTIONS] MARKET_ID USER DIRECTION AMOUNT
```

**Arguments**:

* `MARKET_ID`: [required]
* `USER`: [required]
* `DIRECTION`: [required]
* `AMOUNT`: [required]

**Options**:

* `--help`: Show this message and exit.

## `main swap-tokens`

Swap one outcome token through the liquidity pool for its opposing pair
as a fixed input swap operation

**Usage**:

```console
$ main swap-tokens [OPTIONS] MARKET_ID USER TOKEN_TO_SELL AMOUNT
```

**Arguments**:

* `MARKET_ID`: [required]
* `USER`: [required]
* `TOKEN_TO_SELL`: [required]
* `AMOUNT`: [required]

**Options**:

* `--help`: Show this message and exit.

## `main transfer-stablecoin`

Transfer a certain amount of coins toward an user address

dest: user address that will receive the funds

**Usage**:

```console
$ main transfer-stablecoin [OPTIONS] SRC DEST [VALUE]
```

**Arguments**:

* `SRC`: [required]
* `DEST`: [required]
* `[VALUE]`: [default: 100000000000]

**Options**:

* `--help`: Show this message and exit.

## `main withdraw-auction`

Withdraw the auction

market_id: the id of the question

**Usage**:

```console
$ main withdraw-auction [OPTIONS] MARKET_ID USER
```

**Arguments**:

* `MARKET_ID`: [required]
* `USER`: [required]

**Options**:

* `--help`: Show this message and exit.

