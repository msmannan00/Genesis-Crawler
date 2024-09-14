import os

from dotenv import load_dotenv
load_dotenv()
S_SERVER = os.getenv('S_SERVER', 'http://localhost:8080')

class ELASTIC_CRUD_COMMANDS:
  S_INDEX = 7

class ELASTIC_REQUEST_COMMANDS:
  S_INDEX = 7

class ELASTIC_CONNECTIONS:
  S_DATABASE_IP = f"{S_SERVER}/crawl_index/"
