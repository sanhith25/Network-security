import logging
import os
from datetime import datetime

##  create unique log file with timestamp

LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"

##  define logs directory

logs_path = os.path.join(os.getcwd(), "logs",LOG_FILE)
os.makedirs(logs_path, exist_ok=True)

##  full log file path


LOG_FILE_PATH = os.path.join(logs_path, LOG_FILE)

## configure logging

logging.basicConfig(
    filename=LOG_FILE_PATH,
    format="[%(asctime)s] [%(name)s:%(lineno)d] - %(levelname)s - %(message)s",
    level=logging.INFO
)
