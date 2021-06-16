from app.logg.logger import logger
from settings_for_start import app, socket


if __name__ == '__main__':
    logger.info('app-for-blogs success started')
    socket.run(app)
    logger.info('app-for-blogs stoped')

