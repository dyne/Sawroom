# Blockchain smart-contracts in human language

Sawroom integrates the [Zenroom VM](https://zenroom.org) to be used as a transaction processor in the [Sawtooth](https://sawtooth.hyperledger.org/) blockchain distributed by the Linux Foundation's [Hyperledger](https://www.hyperledger.org/) consortium.

The goal is facilitate the creation of transaction families based on Zenroom and the [Zencode human-friendly language for smart-contracts](https://decodeproject.eu/blog/smart-contracts-english-speaker), in particolar to bind the blockchain to the free online service [ApiRoom](https://apiroom.net) that makes it very easy to create an online API tied to any database and the Sawroom blockchain.

## Quick start

To try the Sawroom setup with a running Sawtooth is best to use Docker.

Our scripts will facilitate the use with some special options that
will setup a persistent storage on the disk of your host machine
inside the `/usr/lib/sawroom` directory. All data is saved there and
nowhere else!

To prepare the setup do:

```
sudo mkdir -p /var/lib/sawroom
sudo chown $(id -u):$(id -u) /var/lib/sawroom
```

Then pull the Sawroom docker image ready to run a testnet node

```
docker pull dyne/sawroom:testnet
```

Then create the new keys for this instance:

```
./run keys-create
```

One here should note down the output and communicate these keys to
enable the peering between nodes.

**Sawroom is running inside a Tor network and the nodes will find each
other automatically and tunneling through Tor**!

To fire up the node use the script `./run` without arguments.

To enter the running node open another terminal and use the script `./shell` inside sawroom.


That's all for now! more will follow...

## Acknowledgements

Sawroom is Copyright (C) 2019-2020 by [Dyne.org](https://www.dyne.org) foundation

Designed, written and maintained by Puria Nafisi Azizi and Denis Roio
    
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.
    
This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Affero General Public License for more details.
    
You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.

Sawtooth is Copyright (C) 2018 by Intel Corporation

Licensed under the Apache License, Version 2.0 (the "License"); you
may not use this file except in compliance with the License. You may
obtain a copy of the License at:
http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
implied.  See the License for the specific language governing
permissions and limitations under the License.
