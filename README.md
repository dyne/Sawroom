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
## :whale: Docker

```bash
docker-compose up --build
```

To run a transaction

```bash
docker exec -it zenroom-tp zenroom-tx --help
```

shows you all the commands available of the little zenroom-tx cli interface

#### keygen
```bash
docker exec -it zenroom-tp zenroom-tx keygen FILENAME
```

#### transaction
```bash
docker exec -it zenroom-tp zenroom-tx transaction --help
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
