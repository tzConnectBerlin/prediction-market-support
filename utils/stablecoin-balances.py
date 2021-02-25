import json
import summary

pm = summary.get_storage(summary.CONTRACT_ID)

sc = summary.get_storage(pm['stablecoin'])

balances = summary.get_stablecoin_ledger(sc['ledger'])

print(json.dumps(balances))
