from ctypes import addressof
import json
from web3 import Web3

project_id = "<ID>"
web3 = Web3(Web3.HTTPProvider("https://ropsten.infura.io/v3/" + project_id))

abi = json.loads('[{"inputs": [{"internalType": "string","name": "_password","type": "string"}],"stateMutability": "nonpayable","type": "constructor"},{"inputs": [{"internalType": "string","name": "_password","type": "string"}],"name": "isPassword","outputs": [{"internalType": "bool","name": "","type": "bool"}],"stateMutability": "view","type": "function"},{"inputs": [],"name": "password","outputs": [{"internalType": "string","name": "","type": "string"}],"stateMutability": "view","type": "function"}]')
contract = web3.eth.contract(address="0xB65E30DeD2cD7d5C4758082BACE737976F8b214B", abi=abi)
key = contract.functions.password().call()
print(key)

# M0N_M07_D3_P4553_357_7r0P_53CUr153_6r4C3_4_14_810CKCH41N