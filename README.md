# portfolio-application-server

An demo application server that talks to Google Firestore written in python with Flask

## Setup

### Install dependencies

* Ensure a modern version of python is installed (3.x)
* ```pip install -r requirements.txt```

### Configure server

* ```cp config.yml.TEMPLATE config.yml```
* Edit config.yml as necessary

### Run server

#### Dev environment

* ```python3 server.py```
  
#### Production environment

* ```gunicorn start:app```

## Currently Known Bugs/WIP Features

### Known Bugs

* Logging currently not working with gunicorn production environment, only in the dev environment

### WIP Features

* SQL database support
