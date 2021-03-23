import json
import summary

pm = summary.get_storage(summary.CONTRACT_ID)

sc = summary.get_storage(pm['stablecoin'])

questions = summary.get_questions(pm['questions'])

ledger = summary.get_ledger(pm['tokens']['ledger'])

total_supply = summary.get_total_supply(pm['tokens']['token_total_supply'])

all_questions = {}

for question_hash in questions.keys():
    question = questions[question_hash]
    uniswap_yes_balance = ledger.get(f"{summary.CONTRACT_ID}.{question['tokens']['yes_token_id']}") or 1
    uniswap_no_balance = ledger.get(f"{summary.CONTRACT_ID}.{question['tokens']['no_token_id']}") or 1

    if uniswap_no_balance is not None and uniswap_yes_balance is not None:
        yes = int(uniswap_yes_balance)
        no = int(uniswap_no_balance)
        question['price_yes'] = no / (yes + no )
    else:
        question['price_yes'] = None
    all_questions.update({question_hash: question})


print(json.dumps(all_questions))
