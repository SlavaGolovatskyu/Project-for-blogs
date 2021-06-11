import logging


file_log = logging.FileHandler('app/logg/app.log', encoding='utf-8')
console_out = logging.StreamHandler()


logging.basicConfig(level='INFO',
                    handlers=(file_log, console_out),
                    format='[%(asctime)s] [%(levelname)s] => %(message)s', 
                    datefmt='%d-%m-%Y %H:%M:%S'
                    )

logger = logging.getLogger('app_for_blogs')
logger.setLevel(20)