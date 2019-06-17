##############################################################################
#
#    Zenroom TP, Transaction processor for zenroom over sawtooth
#    Copyright (c) 2019-TODAY Dyne.org <http://dyne.org>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import sys

from environs import Env
from sawtooth_sdk.processor.config import get_log_dir
from sawtooth_sdk.processor.core import TransactionProcessor
from sawtooth_sdk.processor.log import log_configuration, init_console_logging

from tp.processor.handler import ZenroomTransactionHandler

env = Env()
env.read_env()


def main():
    try:
        url = env("ZTP_VALIDATOR_ENDPOINT", "tcp://validator:4004")
        rest_api = env("ZTP_REST_ENDPOINT", "http://rest-api:8090")
        processor = TransactionProcessor(url=url)
        log_dir = get_log_dir()
        # use the transaction processor zmq identity for filename
        log_configuration(
            log_dir=log_dir, name="zenroom-" + str(processor.zmq_id)[2:-1]
        )

        init_console_logging()
        handler = ZenroomTransactionHandler(url=rest_api)
        processor.add_handler(handler)
        processor.start()

    except KeyboardInterrupt:
        pass
    except Exception as e:
        print("Error: {}".format(e), file=sys.stderr)
    finally:
        if processor is not None:
            processor.stop()
