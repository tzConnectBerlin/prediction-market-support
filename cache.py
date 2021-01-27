
import summary

pm = summary.get_storage(summary.contract_id)

questions = summary.get_questions(pm['questions'])

ledger = summary.get_ledger(pm['tokens']['ledger'])

total_supply = summary.get_total_supply(pm['tokens']['token_total_supply'])

all_questions = []

for question_hash in questions.keys():
    question = questions[question_hash]
    uniswap_yes_balance = ledger.get(f"{summary.contract_id}.{question['tokens']['yes_token_id']}")
    uniswap_no_balance = ledger.get(f"{summary.contract_id}.{question['tokens']['no_token_id']}")
    if uniswap_no_balance is not None and uniswap_yes_balance is not None:
        yes = int(uniswap_yes_balance)
        no = int(uniswap_no_balance)
        question['price_yes'] = no / (yes + no )
    else:
        question['price_yes'] = None
    all_questions.append(question)

print(all_questions)
