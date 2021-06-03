import zmq
import json

context = zmq.Context()
socket = context.socket(zmq.Req)
socket.connect("tcp://localhost:5555")


#def convert_transaction():
    # convert the transaction
#    return

"""
Format transaction:
type
address
amount
"""

def send_transaction(operation):
    # logging the hash sent
    print(f"Sending request to {hash}")
    socket.send(operation)
    message = socket.recv()
    if message is "failed":
        raise Exception("fail")
    print(f"transaction was successfully sent")