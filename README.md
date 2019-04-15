<h1 align="center">
  <br>
        <a href="{project_link}">
                <img src="https://via.placeholder.com/150.png?text=LOGO" width="150" alt="zenroom-tp-python">
        </a>
  <br>
  zenroom-tp-python
  <br>
</h1>

| Zenroom Transaction Processor for Hyperledger Sawtooth |
:---:
| [![Dyne.org](https://img.shields.io/badge/%3C%2F%3E%20with%20%E2%9D%A4%20by-Dyne.org-blue.svg)](https://dyne.org) |


This repository integrates the [Zenroom VM](https://zenroom.dyne.org) to be used as a transaction processor in the [Sawtooth](https://sawtooth.hyperledger.org/) blockchain distributed by the Linux Foundation's [Hyperledger](https://www.hyperledger.org/) consortium.

To facilitate the creation of transaction families based on Zenroom and the [Zencode human-friendly language for smart-contracts](https://decodeproject.eu/blog/smart-contracts-english-speaker), this TP uses the [Sawtooth SDK](https://sawtooth.hyperledger.org/docs/core/releases/latest/sdks.html) in Python and the [zenroom-py](https://github.com/DECODEproject/zenroom-py) bindings.


<details>
 <summary><strong>:triangular_flag_on_post: Table of Contents</strong> (click to expand)</summary>

* [Docker](#whale-docker)
* [Configuration](#wrench-configuration)
* [Acknowledgements](#heart_eyes-acknowledgements)
* [Links](#globe_with_meridians-links)
* [Contributing](#busts_in_silhouette-contributing)
* [License](#briefcase-license)
</details>

***

## :play-button: Bash

We have included a bash script `xec.sh` which automates some common commands you might want to run.

### Pre-requisites (OSX)

```
brew install automake pkg-config libtool libffi gmp
python3 ./setup.py install
```

You will need an osx build of the zenroom-py module. Assuming you have checked out and built zenroom-py in the same top-levele dir as this repo...

```
. ./.sawtooth-tp.venv/bin/activate
pip uninstall zenroom
pip install ../zenroom-py/dist/zenroom-0.1.3.tar.gz 

```


To get started

```
./xec.sh install
```

This will create an alias so you only need to type `xec` from now on.

```bash
xec init
xec up
xec petition
```

This will initialise the docker compose file and build a local docker image for the zenroom transaction processor. It then brings up 
the set of services we need, which are:

| docker-compose service | Container name         | purpose |
| ---------------------- | ---------------------- | ------- |
| validator              | sawtooth-validator     | Main "node" of the blockchain which executes and validates transactions |
| zenroom-tp             | zenroom-tp             | The transaction processor that executes zencode
| rest-api               | rest-api               | Provides a http / json adaptor over the zeromq protocol to allow clients to talk to the validator from within and also from the host machine|
| shell                  | sawtooth-shell-default | Provides a container with various commands in it which allows you to connect to the rest api from within the docker network | 
| settings-tp            | settings-tp            | A standard transaction processor that allows settings to be configured in the blockchainsd

The key ones are the validator, the rest-api and the zenroom-tp.

The rest-api allows us too communicate with the validator inside the docker netowrk from our host.

The `xec petition` runs a python script called `scripts/execute_petition.py` which runs through all the steps needed to create and sign a petition.

It basically makes calls to the rest api, which can be found on `http:/localhost:8090/`



## :whale: Docker

```bash
docker-compose up --build
```

To run a transaction

```bash
docker exec -it zenroom-tp zenroom-tx
```

***
## :wrench: Configuration
dotenv used the only config is `ZTP_VALIDATOR_ENDPOINT`


***
## :heart_eyes: Acknowledgements

Copyright :copyright: 2019 by [Dyne.org](https://www.dyne.org) foundation, Amsterdam

Designed, written and maintained by Puria Nafisi Azizi.

<img src="https://zenroom.dyne.org/img/ec_logo.png" class="pic" alt="Project funded by the European Commission">

This project is receiving funding from the European Union’s Horizon 2020 research and innovation programme under grant agreement nr. 732546 (DECODE).


***
## :globe_with_meridians: Links

https://zenroom.dyne.org/

https://decodeproject.eu/

https://dyne.org/


***
## :busts_in_silhouette: Contributing

Please first take a look at the [Dyne.org - Contributor License Agreement](CONTRIBUTING.md) then

1.  :twisted_rightwards_arrows: [FORK IT](https://github.com/puria/README/fork)
2.  Create your feature branch `git checkout -b feature/branch`
3.  Commit your changes `git commit -am 'Add some fooBar'`
4.  Push to the branch `git push origin feature/branch`
5.  Create a new Pull Request
6.  :pray: Thank you


***
## :briefcase: License

    Zenroom TP Python
    Copyright (c) 2019 Dyne.org foundation, Amsterdam
    
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.
    
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.
    
    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
