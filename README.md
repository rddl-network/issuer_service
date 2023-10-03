# issuer_service

A CLI tool to issue machine NFTs on liquid

# Installation

Install the the requirements by executing the following 
```
git clone https://github.com/rddl-network/issuer_service.git
cd issuer_service
poetry install
```


# Configuration

issue2liquid expects the following variables to be set:
```
RPC_PORT=
RPC_USER=
RPC_PASSWORD=
WALLET_NAME=
ISSUANCE_DOMAIN=assets.rddl.io #(default)
```
These can be set within the ```.env``` file (an example env.example file is given) or as environment variables.

# Execution 
There are two ways to execute the script from within the project folder

1. by entering the envionment and executing the script thereafter
```
poetry shell
python issuer_service/issue2liquid.py <name> <ext. liquid pub key>
```
2. or by using poetry to execute the script directly
```
poetry run python issuer_service/issue2liquid.py <name> <ext. liquid pub key >
```

