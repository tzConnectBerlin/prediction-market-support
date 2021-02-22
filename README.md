# Scripts to support PM

## demo.py

Uses 4 accounts to exercise the PM.

Usage:

First download 4 files from [the faucet](https://faucet.tzalpha.net/) and rename them to `alice.json bob.json caleb.json donald.json`

then
```
python3 demo.py --activate-accounts=true
```
wait a while
```
python3 demo.py --reveal-accounts=true
```
Now you are good to go.

You can set your own questions, or use a randomly generated one. Randomly generated questions are of the form, what is the capital city of XXX? and are populated from the file `country-by-capital-city.json`.

Auction end time is now + 5 minutes. Market end time is now + 10 minutes.

There is a command line interface that use ./cli.py. The auction end time through the cli is + 30 min and the market end time us now + 60
