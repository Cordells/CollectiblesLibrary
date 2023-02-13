# Totalling Microservice

A microservice that provides the total value of each category of collectables and the total of the entire collection. 

## Table of Contents

- [Overview](#overview)
  - [Built With](#built-with)
- [Instructions](#instructions)
  - [Requesting Data](#requesting-data)
  - [Receiving Data](#receiving-data)
- [UML Sequence Diagram](#uml-sequence-diagram)
- [Contact](#contact)

## Overview

<!-- TODO: 

    - Provide general information about your project here.
    - What problem does it (intend to) solve?
    - What is the purpose of your project?
    - Why did you undertake it?
    - Add a screenshot of the live project
    - Link to demo
 -->
Expects request containing python dictionary of collectable items to server

Sends python dictionary containing:
 1) The total value of each category 
 2) The total value of entire collection

### Built With

<!-- TODO: List any MAJOR libraries/frameworks (e.g. React, Tailwind) with links to their homepages. -->
- [ZeroMQ](https://zeromq.org/)

## Instructions
 
### Requesting Data

To use this microservice, first install [ZeroMQ](https://zeromq.org/). 

#### Import libraries and connect to server:
```
import json
import zmq

context = zmq.Context()

# Socket to talk to server
print("Connecting to total microservice server…")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")
```

#### Make a request to the microsevice using a dictionary in the following format: 
``` 
collect_dict = 
    {'category': 
        {'name': 'category', 
        'image_loc': 'images/dvd.jpg', 
        'items': 
            {'item': 
                {'name': 'Matrix', 
                'description': 'Not today Mr.Anderson', 
                'value': 400, 
                'image_loc': 'images/default.png'
            }
        }
    }
```
e.g. using main_save.json:
```
with open('main_save.json', 'r') as infile:
    collect_dict = json.load(infile)
```
#### Make the request:
```
print(f"Sending request for total…")
socket.send_json(collect_dict)
```


### Receiving Data
#### Request reply:
```
cat_values = socket.recv_json()
print(f"Received total: {cat_values}")
```
#### Reply received in following dictionary format:
```
cat_values = 
    {
        'Category1': 32985,
        'Category2': 32985,
        'Total': 33041
    }
```

## UML Sequence Diagram

## Contact

<!-- TODO: Include icons and links to your RELEVANT, PROFESSIONAL 'DEV-ORIENTED' social media. -->
- Jessica Allman-LaPorte [LinkedIn](https://www.linkedin.com/in/jessa-l/) [GitHub](https://github.com/JessA-L)
