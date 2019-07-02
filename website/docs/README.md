# Blockchain smart-contracts in human language

Zentooth integrates the [Zenroom VM](https://zenroom.dyne.org) to be used as a transaction processor in the [Sawtooth](https://sawtooth.hyperledger.org/) blockchain distributed by the Linux Foundation's [Hyperledger](https://www.hyperledger.org/) consortium.

To facilitate the creation of transaction families based on Zenroom and the [Zencode human-friendly language for smart-contracts](https://decodeproject.eu/blog/smart-contracts-english-speaker), the Zentooth TP uses the [Sawtooth SDK](https://sawtooth.hyperledger.org/docs/core/releases/latest/sdks.html) in Python and the [zenroom-py](https://github.com/DECODEproject/zenroom-py) bindings.

## Quick start

To try the Zentooth setup with a running Sawtooth is best to use the docker-compose inside docker-dyne-software repository:

```
git clone https://github.com/dyne/docker-dyne-software
cd zentooth
docker-compose up --build
```

Once all daemons are running, to run a transaction see:

```bash
docker exec -it zenroom-tp zenroom-tx --help
```

This will show you all the commands available from the zenroom-tx cli interface, which takes a Zencode script from stdin and sends its results into a transaction.

### keygen

To send a transaction first generate a keypair using the `keygen` command
```
docker exec -it zenroom-tp zenroom-tx keygen FILENAME
```

### transaction

```bash
docker exec -it zenroom-tp zenroom-tx transaction --help
```


## Configuration

The only environmental configuration accepted is is `ZTP_VALIDATOR_ENDPOINT`.


## Acknowledgements

Copyright (C) 2019 by [Dyne.org](https://www.dyne.org) foundation, Amsterdam

Designed, written and maintained by Puria Nafisi Azizi.

Documentation contributed by Denis Roio.

## License

    Zentooth is Copyright (c) 2019 by the Dyne.org foundation
    
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
