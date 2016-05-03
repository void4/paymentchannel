from web3 import Web3, IPCProvider, RPCProvider
import requests
import base64
import time
import json
import six

from store import PersistentStore

from urllib.parse import urlparse

pstore = PersistentStore()

web3 = Web3(RPCProvider())
web3.config.defaultAccount = "0x3b63b366a72e5742B2aaa13a5e86725ED06a68f3"

contract_address = "0x1EEcb87dE18ac28c1824d9274f2cEBC5442F8c57"

abi = """[ { "constant": true, "inputs": [ { "name": "channel", "type": "uint256" }, { "name": "value", "type": "uint256" } ], "name": "getHash", "outputs": [ { "name": "", "type": "bytes32", "value": "0x1c44b375153723d5b41d6a7350691ea6f95b8a08e93f90b8c6d1f3ee6552bbba", "displayName": "" } ], "type": "function" }, { "constant": false, "inputs": [ { "name": "channel", "type": "uint256" } ], "name": "reclaim", "outputs": [], "type": "function" }, { "constant": true, "inputs": [ { "name": "channel", "type": "uint256" }, { "name": "value", "type": "uint256" }, { "name": "v", "type": "uint8" }, { "name": "r", "type": "bytes32" }, { "name": "s", "type": "bytes32" } ], "name": "verify", "outputs": [ { "name": "", "type": "bool", "value": false, "displayName": "" } ], "type": "function" }, { "constant": true, "inputs": [], "name": "channelCount", "outputs": [ { "name": "", "type": "uint256", "value": "0", "displayName": "" } ], "type": "function" }, { "constant": false, "inputs": [ { "name": "channel", "type": "uint256" } ], "name": "deposit", "outputs": [], "type": "function" }, { "constant": true, "inputs": [ { "name": "channel", "type": "uint256" } ], "name": "isValidChannel", "outputs": [ { "name": "", "type": "bool", "value": false, "displayName": "" } ], "type": "function" }, { "constant": false, "inputs": [ { "name": "receiver", "type": "address" }, { "name": "expiry", "type": "uint256" } ], "name": "createChannel", "outputs": [ { "name": "channel", "type": "uint256" } ], "type": "function" }, { "constant": true, "inputs": [ { "name": "", "type": "uint256" } ], "name": "channels", "outputs": [ { "name": "sender", "type": "address", "value": "0x", "displayName": "sender" }, { "name": "receiver", "type": "address", "value": "0x", "displayName": "receiver" }, { "name": "value", "type": "uint256", "value": "0", "displayName": "value" }, { "name": "expiry", "type": "uint256", "value": "0", "displayName": "expiry" }, { "name": "valid", "type": "bool", "value": false, "displayName": "valid" } ], "type": "function" }, { "constant": false, "inputs": [ { "name": "channel", "type": "uint256" }, { "name": "value", "type": "uint256" }, { "name": "v", "type": "uint8" }, { "name": "r", "type": "bytes32" }, { "name": "s", "type": "bytes32" } ], "name": "claim", "outputs": [], "type": "function" }, { "anonymous": false, "inputs": [ { "indexed": true, "name": "sender", "type": "address" }, { "indexed": true, "name": "receiver", "type": "address" }, { "indexed": false, "name": "channel", "type": "uint256" } ], "name": "NewChannel", "type": "event" }, { "anonymous": false, "inputs": [ { "indexed": true, "name": "sender", "type": "address" }, { "indexed": true, "name": "receiver", "type": "address" }, { "indexed": false, "name": "channel", "type": "uint256" } ], "name": "Deposit", "type": "event" }, { "anonymous": false, "inputs": [ { "indexed": true, "name": "who", "type": "address" }, { "indexed": true, "name": "channel", "type": "uint256" } ], "name": "Claim", "type": "event" }, { "anonymous": false, "inputs": [ { "indexed": true, "name": "channel", "type": "bytes32" } ], "name": "Reclaim", "type": "event" } ]"""

contract = web3.eth.contract(abi).at(contract_address)

doccache = {}
cachetime = 10#seconds
def getEndpoint(method, path):
    parsed_uri = urlparse(path)
    domain = "{uri.scheme}://{uri.netloc}/".format(uri=parsed_uri)

    if domain in doccache and time.time()-doccache[domain]["time"] < cachetime:
        documentation = doccache[domain]["documentation"]
    else:
        documentation = json.loads(requests.get(domain).text)["documentation"]
        doccache[domain] = {"time": time.time(), "documentation": documentation}

    handler = documentation["handlers"][parsed_uri.path][method]
    if "requires" in handler:
        for requirement in handler["requires"]:
            print(requirement)
            if requirement.startswith("pay://"):
                parsedpay = urlparse(requirement)
                return parsedpay.netloc, int(parsedpay.path[1:])

def sign(account, value, channelvalue=1000):

    # EVM channel
    channel = None

    # Local channel signatures
    channelsig = None
    channelid = None

    # Search for existing channels to account
    for pchannel in pstore.load():
        channel = contract.channels(pchannel)
        if channel[1] == account:
            channelsig = pstore.get(pchannel)
            channelid = pchannel
            break

    # No channel found, create a new one
    if channelsig is None:
        expiry = 100000000000000000000000000
        start = contract.channelCount()
        txid = contract.createChannel(account, expiry, gas=200000, value=channelvalue)
        print("{0}\nCreating new channel...".format(txid))
        while True:
            try:
                receipt = web3.eth.getTransactionReceipt(txid)
                break
            except KeyError:
                time.sleep(1)

        end = contract.channelCount()
        channelid = None
        for i in range(start, end):
            if contract.channels(i)[1] == account.lower():
                channel = contract.channels(i)
                channelid = i
                break

        if channelid is None:
            raise KeyError("Channel creation failed")

        channelsig = {"channel": channelid, "value": 0}
        print(channel)
        print("Channel created.")

    # Sign (last signed value + increment)
    value += channelsig["value"]

    signature = web3.eth.sign(channel[0], contract.getHash(channelid, value))
    signature = signature[2:]

    # include signed receiver to prevent necessary node communication at provider?
    result = {
        "channel": channelid,
        "value": value,
        "signature": {
            "r" : "0x" + signature[:64],
            "s" : "0x" + signature[64:128],
            "v" : web3.toHex(web3.toDecimal(signature[128:130]) + 27)
        }
    }

    pstore.set(channelid, result)

    header = json.dumps(result)

    #header = web3.fromUtf8(header)[2:]

    if six.PY3:
        header = header.encode("utf8")
    header = base64.b64encode(header)

    return header

for i in range(5):
    print(i)
    path = "http://localhost:8000/pay"
    endpoint = getEndpoint("GET", path)
    if endpoint:
        headers = {"X-Signature": sign(*endpoint)}
    else:
        headers = {}
    r = requests.get(path, headers=headers)
    print(r)
    print(r.text)
