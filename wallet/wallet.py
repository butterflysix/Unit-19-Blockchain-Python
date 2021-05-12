import subprocess
import json
import os
from constants import BTC, BTCTEST, ETH
from pprint import pprint
from bit import PrivateKeyTestnet
from bit.network import NetworkAPI
from web3 import Web3, middleware, Account
from web3.gas_strategies.time_based import medium_gas_price_strategy
from web3.middleware import geth_poa_middleware

# connect Web3
w3 = Web3(Web3.HTTPProvider(os.getenv('WEB3_PROVIDER', 'http://127.0.0.1:8545')))

# enable PoA
#web3.middleware_onion.inject(geth_poa_middleware, layer=0)
#w3.middleware_stack.inject(geth_poa_middleware, layer=0)

from web3.middleware import geth_poa_middleware
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
                             
# include mnemonic
mnemonic = os.getenv("MNEMONIC", "become shaft talk pave front auction employ share toe valve miracle rain")

def derive_wallets(coin=BTC, mnemonic=mnemonic, depth=3):
    command = f"php ./derive -g --mnemonic='{mnemonic}' --coin={coin} --numderive={depth} --cols=path,address,privkey,pubkey --format=json"
    p = subprocess.Popen(command,
        stdout=subprocess.PIPE,
        shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    return json.loads(output)

def priv_key_to_account(coin, priv_key):
    if coin == ETH:
        return Account.privateKeyToAccount(priv_key)
    if coin == BTCTEST:
        return PrivateKeyTestnet(priv_key)

def create_tx(coin, account, to, amount):
    if coin == ETH:
        value = w3.toWei(amount, "ether")
        gasEstimate = w3.eth.estimateGas({ "to": to, "from": account.address, "amount": value })
        return {
            "to": to,
            "from": account.address,
            "value": value,
            "gas": gasEstimate,
            "gasPrice": w3.eth.generateGasPrice(),
            "nonce": w3.eth.getTransactionCount(account.address),
            "chainId": w3.net.chainId
        }
    if coin == BTCTEST:
        return PrivateKeyTestnet.prepare_transaction(account.address, [(to, amount, BTC)])

def send_tx(coin, account, to, amount):
    if coin == ETH:
        raw_tx = create_tx(coin, account, to, amount)
        signed = account.signTransaction(raw_tx)
        return w3.eth.sendRawTransaction(signed.rawTransaction)
    if coin == BTCTEST:
        raw_tx = create_tx(coin, account, to, amount)
        signed = account.sign_transaction(raw_tx)
        return NetworkAPI.broadcast_tx_testnet(signed)

coins = {
    ETH: derive_wallets(coin=ETH),
    BTCTEST: derive_wallets(coin=BTCTEST),
}

pprint(coins)
