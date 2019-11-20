##############################################################################
#
#    Petition TP, Transaction processor for Decode Petition over sawtooth
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
from sawtooth_sdk.processor.log import (
    log_configuration,
    init_console_logging,
    create_console_handler,
)

from tp.processor.handler import PetitionTransactionHandler

env = Env()
env.read_env()


def main():
    try:
        url = env("SAWTOOTH_VALIDATOR_ENDPOINT", "tcp://validator:4004")
        processor = TransactionProcessor(url=url)
        log_configuration(log_dir=get_log_dir(), name="petition_tp")
        create_console_handler(5)
        init_console_logging(5)
        handler = PetitionTransactionHandler()  # url=rest_api)
        processor.add_handler(handler)
        processor.start()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print("Error: {}".format(e), file=sys.stderr)
    finally:
        if processor is not None:
            processor.stop()
