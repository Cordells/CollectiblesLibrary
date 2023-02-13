# Example call to tally microservice
# Connects REQ socket to tcp://localhost:5555
# Sends request containing python dictionary of collectable items to server, 
#   expects python dictionary containing: 
#     1) the total value of each category and 
#     2) the total value of entire collection

import json
import zmq

context = zmq.Context()

# Socket to talk to server
print("Connecting to tally microservice server…")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

with open('main_save.json', 'r') as infile:
    collect_dict = json.load(infile)

# Make a request containing a python dictionary
print(f"Sending request for tally…")
socket.send_json(collect_dict)

# Get the reply as a python dictionary
cat_values = socket.recv_json()
print(f"Received tally: {cat_values}")
