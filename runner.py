from app.logg.logger import logger
from settings_for_start import socket, app


if __name__ == '__main__':
    logger.info('app-for-blogs success started')
    socket.run(app)
    logger.info('app-for-blogs stoped')

