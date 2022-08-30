import time
import sys
import logging
from datetime import datetime
import os

import json

from piawg import piawg

class PiaWGDaemon:
    def __init__(self):


        self.req_key = {
            "USERNAME" : str,
            "PASSWORD" : str,
            "UPDATE_INTERVAL" : int,
            "REGION" : str
        }

        self.config = {}

        logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')
        for key in self.req_key:
                current_param = os.environ.get(key)

                if current_param is None:
                    error_msg = "{} key was not found in enviorment".format(key)

                    logging.error(error_msg)
                    raise KeyError("Required Key {} Was not found in json")

                if not isinstance(current_param, self.req_key[key]):
                    found_type = type(current_param)
                    try:
                        current_param = self.req_key[key](current_param)
                    except:
                        error_msg = "{} key was of wrong type. Found : {} Expected: {} ".format(
                            key,
                            found_type,
                            self.req_key[key]
                        )

                        logging.error(error_msg)
                        raise KeyError(error_msg)


                self.config[key] = current_param

        pia = piawg()

        if self.config["REGION"] not in pia.server_list.keys():
            error_msg = "{} Region is not a valid one ".format(
                self.config["REGION"]
            )

            logging.error(error_msg)
            raise KeyError(error_msg)


        '''
        with open(CONFIG_FILE, "r") as f:
            self.config = json.load(f)
            for key in self.req_key:
                if key not in self.config:
                    error_msg = "{} key was not found in json".format(key)
                    logging.error(error_msg)
                    raise KeyError("Required Key {} Was not found in json")

                if not isinstance(self.config[key], self.req_key[key]):
                    error_msg = "{} key was of wrong type. Found : {} Expected: {} ".format(
                        key,
                        type(self.config[key]),
                        self.req_key[key]
                    )

                    logging.error(error_msg)
                    raise KeyError(error_msg)

                pia = piawg()

                if self.config["region"] not in pia.server_list.keys():
                    error_msg = "{} Region is not a valid one ".format(
                        self.config["region"]
                    )

                    logging.error(error_msg)
                    raise KeyError(error_msg)
        '''

        self.timout_period = 5


    def event_loop(self):
        last_update = 0
        try:
            while True:
                print("files", os.listdir("."))
                if time.monotonic() - last_update >= self.config["UPDATE_INTERVAL"]:
                    logging.info("Updating Token")

                    pia = piawg()
                    pia.generate_keys()
                    pia.set_region(self.config["REGION"])

                    if pia.get_token(self.config["USERNAME"], self.config["PASSWORD"]):
                        successful_login = True
                        logging.info("Login Succesful")
                    else:
                        logging.error("Error Logging In")
                        successful_login = False

                    last_update = time.monotonic()

                    if not successful_login:
                        continue

                    status, response = pia.addkey()

                    if status:
                        logging.info("Added key to server!")
                    else:
                        logging.error("Error adding key to server")
                        logging.error(response)
                        continue

                    self.write_file(pia)

                else:
                    time.sleep(self.timout_period)

        except KeyboardInterrupt:
            logging.info("Event Loop Interrupted, exiting")
            exit()


    def write_file(self, pia):
        logging.info("Writing Config")
        timestamp = int(datetime.now().timestamp())
        with open("/app/wg0.conf", 'w+') as file:
            file.write('[Interface]\n')
            file.write('Address = {}\n'.format(pia.connection['peer_ip']))
            file.write('PrivateKey = {}\n'.format(pia.privatekey))
            file.write('DNS = {},{}\n\n'.format(pia.connection['dns_servers'][0], pia.connection['dns_servers'][1]))
            file.write('[Peer]\n')
            file.write('PublicKey = {}\n'.format(pia.connection['server_key']))
            file.write('Endpoint = {}:1337\n'.format(pia.connection['server_ip']))
            file.write('AllowedIPs = 0.0.0.0/0\n')
            file.write('PersistentKeepalive = 25\n')

if __name__ == "__main__":
    PiaWGDaemon().event_loop()
