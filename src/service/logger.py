import logging
import os

logname = str(os.path.realpath(__file__)).replace("logger.py", "logs.txt")

logging.basicConfig(filename=logname,
                    filemode='a',
                    format="%(asctime)s - %(levelname)-8s [%(filename)s:%(lineno)d in %(funcName)s()] %(message)s",
                    datefmt='%m-%d %H:%M:%S',
                    level=logging.INFO)

LOGGER = logging.getLogger(__name__)

logging.info('\n\n----------------------------------------------------------------NEW START----------------------------------------------------------------\n')
