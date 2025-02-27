import logging
logger = logging.getLogger()
logHandler = logging.StreamHandler()# пишем в консоль
logger.addHandler(logHandler)
logger.setLevel("INFO")
