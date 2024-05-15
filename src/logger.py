import logging
import time
import os

'''
Logger setup module for the tool
If not --stdout provided, logs will be written to a file in logs directory
Otherwise, logs will be written to stdout
'''


def setup_logger(to_stdout=False, debug=False):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    epoch_time = int(time.time())
    log_dir = os.getenv('LOG_DIR', '../logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    handler = logging.StreamHandler() if to_stdout else logging.FileHandler(
        f'{log_dir}/gh_data_extraction_{epoch_time}.log')
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)
    return logger
