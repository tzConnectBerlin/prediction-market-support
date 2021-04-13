import zmq
import json
from pytezos import pytezos

from src.utils import print_error, submit_transaction

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

count = 0
operations_in_queue = []
transactions_in_validation = []


# format of data received:-
# type of operation
# quantity
# address concerned

STABLECOIN_ADDRESS = "KT18gWJQE7XwjCQi4VDgocZvMn8jpc45etiT"

admin_account_client = pytezos.using(
    key="edsk3QoqBuvdamxouPhin7swCvkQNgq4jP5KZPbwWNnwdZpSpJiEbq",
    shell="http://localhost:20000"
).contract(STABLECOIN_ADDRESS)

print(admin_account_client)

operations_type = {
    "burn": admin_account_client.burn,
    "mint": admin_account_client.mint
}


def check_valid_operation(operation):
    assert operation.id in operations_type
    assert operation.amount > 0
    return


def manage_transactions():
    # receive the list of transactions and send them to the queue
    # format
    # bulk them
    # inject them
    # return an error if it's not working
    return


def read_operation(operation):
    op_content = operation["content"]
    op_type = operation["id"]
    transaction = operations_type[op_type](op_content)
    return transaction.as_transaction()


def inject_operations(operations):
    transaction_list = []
    for operation in operations:
        transaction_list.append(read_operation(operation))
    bulk_operations = admin_account_client.bulk(*transaction_list)
    submit_transaction(bulk_operations, error_func=print_error)


while True:
    message = socket.recv()
    # Log transaction reception
    print(f"Received request: {message}")
    operation = json.loads(str(message))
    if check_valid_operation(operation):
        operations_in_queue.append(operation)
        count += 1
    # parse message
    if count >= 50:
        operations_in_validation = operations_in_queue.copy()
        operations_in_queue = []
        inject_operations(operations_in_validation)
        count = 0


