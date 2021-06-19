from app.logg.logger import logger
from settings_for_start import manager


if __name__ == '__main__':
    logger.info('app-for-blogs success started')
    manager.run()
    logger.info('app-for-blogs stoped')

