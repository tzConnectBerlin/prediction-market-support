import json
import summary

pm = summary.get_storage(summary.CONTRACT_ID)

balances = summary.get_ledger_balances(pm['tokens']['ledger'])

print(json.dumps(balances))
