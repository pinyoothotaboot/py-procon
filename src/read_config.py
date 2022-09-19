from distutils.command.config import config
import sys
import configparser
from os.path import exists
from log import Logger

log = Logger('CONFIG').get_logger()

def initial_config(path = "./config.ini"):
    try:
        if not exists(path):
            log.error("Not found file : {}".format(path))
            sys.exit(0)

        config = configparser.ConfigParser()
        datas = config.read(path)

        if not datas:
            log.error("Not found datas!.")
            return {
                "host" : "127.0.0.1",
                "port" : 3456,
                "buff_size" : 2048,
                "connection" : 256,
                "handle_accept_sleep" : 0.2,
                "handle_receive_sleep" : 0.1,
                "handle_callback" : 2,
                "handle_broadcast" : 2
            }

        return {
            "host" : config['config']['host'],
            "port" : int(config['config']['port']),
            "buff_size" : int(config['config']['buff_size']),
            "connection" : int(config['config']['connection']),
            "handle_accept_sleep" : float(config['config']['handle_accept_sleep']),
            "handle_receive_sleep" : float(config['config']['handle_receive_sleep']),
            "handle_callback" : float(config['config']['handle_callback']),
            "handle_broadcast" : float(config['config']['handle_broadcast'])
        }
        
    except Exception as ex:
        log.error("Error : {}".format(ex))
        sys.exit(0)

if __name__=="__main__":
    try:
        configs = initial_config()
        print("CONFIG",configs)
    except KeyboardInterrupt:
        log.info("Exit program..")
        sys.exit()