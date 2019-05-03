from pathlib import Path

from scripts.config.config import BaseConfig

config = BaseConfig()
log = config.logger
CONTRACTS_DIR = Path(config.get("contracts_path"))


def get_contract(name):
    # if python 2.7...
    # path = config.get("contracts_path")
    # filename = path + "/" + name
    # f = open(filename, 'r')
    # return f.read()
    #else if python 3...
    return CONTRACTS_DIR.joinpath(name).read_text().encode()


