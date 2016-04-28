from web3 import Web3, IPCProvider
import atexit

#def exit_handler():
#    closeAllChannels()

#atexit.register(exit_handler)

web3 = Web3(IPCProvider(testnet=True))
web3.config.defaultAccount = "0x3b63b366a72e5742B2aaa13a5e86725ED06a68f3"

contract_address = "0x115782Da52Db7569891B6f9Dab5b062b10cc7288"

abi = """[ { "constant": true, "inputs": [ { "name": "channel", "type": "uint256" }, { "name": "value", "type": "uint256" } ], "name": "getHash", "outputs": [ { "name": "", "type": "bytes32", "value": "0xa331b2c89b871c6e936922b6b1189e48afa5a3c56b2db98b07c5cdc494fd57af", "displayName": "" } ], "type": "function" }, { "constant": false, "inputs": [ { "name": "channel", "type": "uint256" } ], "name": "reclaim", "outputs": [], "type": "function" }, { "constant": true, "inputs": [ { "name": "channel", "type": "uint256" }, { "name": "value", "type": "uint256" }, { "name": "v", "type": "uint8" }, { "name": "r", "type": "bytes32" }, { "name": "s", "type": "bytes32" } ], "name": "verify", "outputs": [ { "name": "", "type": "bool", "value": false, "displayName": "" } ], "type": "function" }, { "constant": false, "inputs": [ { "name": "channel", "type": "uint256" } ], "name": "deposit", "outputs": [], "type": "function" }, { "constant": true, "inputs": [ { "name": "channel", "type": "uint256" } ], "name": "isValidChannel", "outputs": [ { "name": "", "type": "bool", "value": true, "displayName": "" } ], "type": "function" }, { "constant": false, "inputs": [ { "name": "receiver", "type": "address" }, { "name": "expiry", "type": "uint256" } ], "name": "createChannel", "outputs": [], "type": "function" }, { "constant": true, "inputs": [ { "name": "", "type": "uint256" } ], "name": "channels", "outputs": [ { "name": "sender", "type": "address", "value": "0x3b63b366a72e5742b2aaa13a5e86725ed06a68f3", "displayName": "sender" }, { "name": "receiver", "type": "address", "value": "0x3b63b366a72e5742b2aaa13a5e86725ed06a68f3", "displayName": "receiver" }, { "name": "value", "type": "uint256", "value": "8000000000000000", "displayName": "value" }, { "name": "expiry", "type": "uint256", "value": "31000000000000000000", "displayName": "expiry" }, { "name": "valid", "type": "bool", "value": true, "displayName": "valid" } ], "type": "function" }, { "constant": false, "inputs": [ { "name": "channel", "type": "uint256" }, { "name": "value", "type": "uint256" }, { "name": "v", "type": "uint8" }, { "name": "r", "type": "bytes32" }, { "name": "s", "type": "bytes32" } ], "name": "claim", "outputs": [], "type": "function" }, { "anonymous": false, "inputs": [ { "indexed": true, "name": "sender", "type": "address" }, { "indexed": true, "name": "receiver", "type": "address" }, { "indexed": false, "name": "channel", "type": "uint256" } ], "name": "NewChannel", "type": "event" }, { "anonymous": false, "inputs": [ { "indexed": true, "name": "sender", "type": "address" }, { "indexed": true, "name": "receiver", "type": "address" }, { "indexed": false, "name": "channel", "type": "uint256" } ], "name": "Deposit", "type": "event" }, { "anonymous": false, "inputs": [ { "indexed": true, "name": "who", "type": "address" }, { "indexed": true, "name": "channel", "type": "uint256" } ], "name": "Claim", "type": "event" }, { "anonymous": false, "inputs": [ { "indexed": true, "name": "channel", "type": "bytes32" } ], "name": "Reclaim", "type": "event" } ]"""

contract = web3.eth.contract(abi).at(contract_address)
channelid = 0
channel = contract.channels(channelid)
value = 1
signature = web3.eth.sign(channel[0], contract.getHash(channelid, value))
signature = signature[2:]

res = {
    "r" : "0x" + signature[:64],
    "s" : "0x" + signature[64:128],
    "v" : web3.toHex(web3.toDecimal(signature[128:130]) + 27)
}

result = {
    "channel": channelid,
    "value": value,
    "signature": res
}

import json
# res should be amended with payment channel info (just opened/updated/reclaim etc. and channel id, value)
header = web3.fromUtf8(json.dumps(result))[2:]
print(header)
header = web3.toUtf8(header)
result = json.loads(header)
print(json.dumps(result, sort_keys=True, indent=4, separators=(',', ': ')))

v = contract.verify(channelid, value, res["v"], res["r"], res["s"])
print(v)