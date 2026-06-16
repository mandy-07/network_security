import logging
import os
from datetime import datetime

# Create logs directory
LOG_DIR = "logs"
LOG_DIR_PATH = os.path.join(os.getcwd(), LOG_DIR)

os.makedirs(LOG_DIR_PATH, exist_ok=True)

# Create log file with timestamp
LOG_FILE = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
LOG_FILE_PATH = os.path.join(LOG_DIR_PATH, LOG_FILE)

# Configure logging
logging.basicConfig(
    filename=LOG_FILE_PATH,
    format="[%(asctime)s] %(name)s - %(levelname)s - %(message)s [Line:%(lineno)d]",
    level=logging.INFO,
)

# Logger object for entire project
logger = logging.getLogger("NetworkSecurity")