# Title: Tally Microservice
# Author: Jessica Allman-LaPorte
# GitHub: JessA-L
# Date: 2/13/2023
# Description:
#   Expects request containing python dictionary of collectable items to server
#   Sends python dictionary containing:
#     1) the total value of each category and 
#     2)   the total value of entire collection

import zmq

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

while True:
    # Wait for next request from client
    collect_dict = socket.recv_json()
    print(f"Received request for tally...")

    # Tally total value of each category
    cat_values = {}
    total_value = 0
    for category in collect_dict.values():
        cat_values[category["name"]] = 0
        for item in category["items"].values():
            cat_values[category["name"]] += item["value"]
            total_value += item["value"]

    # Add total value of all categories
    cat_values["Total"] = total_value


    # Send reply back to client
    socket.send_json(cat_values)
    print(f"sending {cat_values}...")
