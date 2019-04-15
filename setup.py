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
import setuptools

setuptools.setup(
    name="zenroom-tp",
    version="0.0.1",
    author="Puria Nafisi Azizi",
    author_email="puria@dyne.org",
    description="Zenroom Transaction Processor for Hyperledger Sawtooth",
    long_description_content_type="text/markdown",
    url="https://github.com/DECODEproject/zenroom-py",
    packages=setuptools.find_packages(),
    entry_points={
        "console_scripts": [
            "zenroom-tp-python = tp.main:main",
            "zenroom-tx = tp.client.main:main",
        ]
    },
    setup_requires=["pytest-runner"],
    tests_require=[],
    install_requires=[
        "zenroom==0.2.5",
        "pre-commit==1.14.4",
        "cbor==1.0.0",
        "colorlog",
        "sawtooth-sdk",
        "sawtooth-signing",
        "environs==4.1.0",
    ],
    python_requires=">=3.5",
    project_urls={
        "Zenroom": "https://zenroom.dyne.org",
        "DECODE": "https://decodeproject.eu",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Intended Audience :: Developers",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Security",
    ],
)
