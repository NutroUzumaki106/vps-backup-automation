from utils import DBBackup, FileBackup
from utils import configure_logger
from dotenv import load_dotenv
from datetime import datetime
from time import sleep
import schedule
import os

load_dotenv()

BASE_PATH = os.path.dirname(os.path.abspath(__file__).replace(os.path.sep, "/"))

logger = configure_logger()
logger.info("Logger Ready!")


def start_backup():
    logger.info("Starting backup!")
    db_backup = DBBackup(BASE_PATH)
    db_backup.start_backup()
    file_backup = FileBackup(BASE_PATH)
    file_backup.start_backup()


schedule.every().day.at(os.getenv("BACKUP_TIME")).do(start_backup)

# this condition is for when pods restart or the server is restarted
if (
    datetime.now().time()
    >= datetime.strptime(os.getenv("BACKUP_TIME"), "%H:%M").time()
):
    logger.info("Initial Run")
    start_backup()

while True:
    schedule.run_pending()
    sleep(1)
