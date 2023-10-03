from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from decouple import config
import hashlib
import json
import six
import sys


RPC_PORT: int = config("RPC_PORT", default=18884, cast=int)
RPC_USER: str = config("RPC_USER", default="")
RPC_PASSWORD: str = config("RPC_PASSWORD", default="")
WALLET_NAME: str = config("WALLET_NAME", default="")
ISSUANCE_DOMAIN: str = config("ISSUANCE_DOMAIN", default="assets.rddl.io")



def issue_machine_nft(argv):
    NAME = str(argv[1])
    MACHINE_ADDR = str(argv[2])
    ASSET_AMOUNT = 1
    TOKEN_AMOUNT = 0
    PRECISION = 0
    VERSION = 0

    FEERATE = 0.00001000

    try:
        rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:%s/wallet/%s"%(RPC_USER, RPC_PASSWORD, RPC_PORT, WALLET_NAME))
        NEWADDR = rpc_connection.getnewaddress("", "legacy")
        VALIDATEADDR = rpc_connection.getaddressinfo(NEWADDR)
        PUBKEY = VALIDATEADDR["pubkey"]
        ASSET_ADDR = NEWADDR
        NEWADDR = rpc_connection.getnewaddress("WRAPPEDtoken", "legacy")
        TOKEN_ADDR = NEWADDR

    except JSONRPCException as json_exception:
        print("A JSON RPX exception occured: " + str(json_exception))
    except Exception as general_exception:
        print("An exception occured: " + str(general_exception))

    '''print(VALIDATEADDR)
    print(PUBKEY)
    print(ASSET_ADDR)
    print(TOKEN_ADDR)'''



    CONTRACT = f"{{\"entity\":{{\"domain\":\"{ISSUANCE_DOMAIN}\"}}, \"machine_addr\":\"{MACHINE_ADDR}\", \"name\":\"{NAME}\", \"precision\":{PRECISION}, \"version\":{VERSION}}}"
    # print(CONTRACT)

    CONTRACT_SORTED=json.dumps(json.loads(CONTRACT), sort_keys=True, separators=(",",":"))
    CONTRACT_HASH=hashlib.sha256(six.ensure_binary(CONTRACT_SORTED)).hexdigest()
    # print(CONTRACT_HASH)

    CONTRACT_HASH_REV="".join(reversed([CONTRACT_HASH[i:i+2] for i in range(0, len(CONTRACT_HASH), 2)]))
    # print(CONTRACT_HASH_REV)


    RAWTX = rpc_connection.createrawtransaction([], [{"data":"00"}])
    # print(RAWTX)


    FRT = rpc_connection.fundrawtransaction(RAWTX, {"feeRate":FEERATE})
    # print(FRT)

    HEXFRT = FRT["hex"]
    # print(HEXFRT)

    RIA = rpc_connection.rawissueasset(HEXFRT, [{"asset_amount":ASSET_AMOUNT,
                                            "asset_address":ASSET_ADDR,
                                            "token_amount":TOKEN_AMOUNT,
                                            "token_address":TOKEN_ADDR,
                                            "blind":False,
                                            "contract_hash":CONTRACT_HASH_REV,}])
    # print(RIA)

    HEXRIA = RIA[0]["hex"]
    ASSET = RIA[0]["asset"]
    ENTROPY = RIA[0]["entropy"]
    TOKEN = RIA[0]["token"]

    BRT = rpc_connection.blindrawtransaction(HEXRIA, True, [], False)
    SRT = rpc_connection.signrawtransactionwithwallet(BRT)
    HEXSRT = SRT["hex"]

    ##  TEST = rpc_connection.testmempoolaccept(['"' + HEXSRT + '"'])
    TEST = rpc_connection.testmempoolaccept([HEXSRT])
    ALLOWED = TEST[0]["allowed"]
    # print(ALLOWED)

    ISSUETX = rpc_connection.sendrawtransaction(HEXSRT)

    #print("\n\n")
    #print(F"ASSET_ID: {ASSET}")
    #print(F"CONTRACT: {CONTRACT}")

    return (F"{ASSET}\n{CONTRACT}\n")
    # return(ASSET)

def show(argv):
    n1 = str(argv[1])
    n2 = str(argv[2])

    return ( [n1, n2])


if __name__ == '__main__':
    print ( issue_machine_nft(sys.argv))


"""

ddf8c4c47b19b4cc99f421d4ac826a41a3f8de153f78ae43a6bd1e26df0d6f94

'/home/nestor/elements-elements-0.21.0.2/bin/elements-qt' -datadir='/home/nestor/elements-elements-0.21.0.2/Liquid/liquid_network_1' >/dev/null 2>&1

python3.10 '/home/nestor/libwally-core/src/test/live_issue2liquid_testnet.py' 'Transport Token' 'L-TRNS' 'lab.r3c.network' 21000000 1 0

python3.10 '/home/nestor/libwally-core/src/test/live_issue2liquid_testnet.py' 'Transport Token' 'L-TRNS' 'lab.r3c.network' 0.00000001 0.00000001 8

https://blockstream.info/testnet/

"""
