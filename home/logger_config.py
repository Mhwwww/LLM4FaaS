import logging

# Define the logging configuration
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(filename)s - %(funcName)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('llm4faas')
logger.setLevel(logging.WARNING)  # Set the logger level to WARNING

# NOTSET=0
# DEBUG=10
# INFO=20
# WARN=30
# ERROR=40
# CRITICAL=50
