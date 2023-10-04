from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from decouple import config
import hashlib
import json
import six
import sys


RPC_PORT: int = config("RPC_PORT", default=18884, cast=int)
RPC_USER: str = config("RPC_USER", default="")
RPC_HOST: str = config("RPC_HOST", default="localhost")
RPC_PROTOCOL: str = config("RPC_PROTOCOL", default="http")
RPC_PASSWORD: str = config("RPC_PASSWORD", default="")
WALLET_NAME: str = config("WALLET_NAME", default="")
ISSUANCE_DOMAIN: str = config("ISSUANCE_DOMAIN", default="assets.rddl.io")



def issue_machine_nft(argv):
    NAME = str(argv[1])
    MACHINE_ADDR = str(argv[2])
    ASSET_AMOUNT = 0.00000001
    TOKEN_AMOUNT = 1
    PRECISION = 0
    VERSION = 0

    FEERATE = 0.00001000

    try:
        rpc_connection = AuthServiceProxy("%s://%s:%s@%s:%s/wallet/%s"%(RPC_PROTOCOL, RPC_USER, RPC_PASSWORD, RPC_HOST, RPC_PORT, WALLET_NAME))
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
    #print(RAWTX)


    FRT = rpc_connection.fundrawtransaction(RAWTX, {"feeRate":FEERATE})
    #FRT = rpc_connection.fundrawtransaction(RAWTX)
    #print(FRT)

    HEXFRT = FRT["hex"]
    #print(HEXFRT)
    #RIA = rpc_connection.rawissueasset(HEXFRT, [{"asset_amount":ASSET_AMOUNT,
    RIA = rpc_connection.rawissueasset(HEXFRT, [{"asset_amount":ASSET_AMOUNT, "asset_address":ASSET_ADDR, "token_amount":TOKEN_AMOUNT, "token_address":TOKEN_ADDR, "blind":False, "contract_hash":CONTRACT_HASH_REV,}])
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

    return (F"{ASSET}\n{CONTRACT}")
    # return(ASSET)

def show(argv):
    n1 = str(argv[1])
    n2 = str(argv[2])

    return ( [n1, n2])


if __name__ == '__main__':
    print ( issue_machine_nft(sys.argv))

