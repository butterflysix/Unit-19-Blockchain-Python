# Multi-Blockchain Wallet in Python

## HD Wallets is a universal crypto wallet that supports BIP32, BIP39, BIP44 and other non standard derivation paths for the most popular wallets.

#### Dependencies List:
- Clone the [`hd-wallet-derive`](https://github.com/dan-da/hd-wallet-derive) tool.

- [`bit`](https://ofek.github.io/bit/) Python Bitcoin library.

- [`web3.py`](https://github.com/ethereum/web3.py) Python Ethereum library.

### Derive the wallet keys

- The function,`derive_wallets`will:
    - Use the subprocess library to create a shell command that calls the `./derive` script from Python.
       - The following flags must be passed into the shell command as variables:
          - Mnemonic (`--mnemonic`) must be set from an environment variable, or default to a test mnemonic
          - Coin (`--coin`)
          - Numderive (`--numderive`) to set number of child keys generated
          - Format (`--format=json`) to parse the output into a JSON object using `json.loads(output)`
    - Use the `subprocess` library to create a shell command that calls the `./derive` script from Python.
    - Create a dictionary object called `coins` that uses the `derive_wallets` function to derive `ETH` and `BTCTEST` wallets.
- Now you should be able to select child accounts and also private keys by accessing items in the `coins` dictionary: `coins[COINTYPE][INDEX]['privkey']`
  ```
  def derive_wallets(coin=BTC, mnemonic=mnemonic, depth=3):
    command = f"php ./derive -g --mnemonic='{mnemonic}' --coin={coin} --numderive={depth} --cols=path,address,privkey,pubkey --format=json"
    p = subprocess.Popen(command,
        stdout=subprocess.PIPE,
        shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    return json.loads(output)
  ```

### Linking the transaction signing libraries

 - Use `bit` and `web3.py` to leverage the keys stored in the `coins` object by creating three more functions:

      - `priv_key_to_account`:
  
          - This function will convert the `privkey` string in a child key to an account object that `bit` or `web3.py` can use to transact.
          - This function needs the following parameters:

            - `coin` -- the coin type (defined in `constants.py`).
            - `priv_key` -- the `privkey` string will be passed through here.

               - Check the coin type, then return one of the following functions based on the library:

      - For `ETH`, return `Account.privateKeyToAccount(priv_key)`
          - This function returns an account object from the private key string. 
      - For `BTCTEST`, return `PrivateKeyTestnet(priv_key)`
          - This is a function from the `bit` library that converts the private key string into a WIF (Wallet Import Format) object.
            ```
            def priv_key_to_account(coin, priv_key):
            if coin == ETH:
                return Account.privateKeyToAccount(priv_key)
            if coin == BTCTEST:
                return PrivateKeyTestnet(priv_key)
            ```

    - `create_tx`: 
      - This function will create the raw, unsigned transaction that contains all metadata needed to transact.
      - This function needs the following parameters:

        - `coin` -- the coin type (defined in `constants.py`).
        - `account` -- the account object from `priv_key_to_account`.
        - `to` -- the recipient address.
        - `amount` -- the amount of the coin to send.
        - Check the coin type, then return one of the following functions based on the library:

          - For `ETH`, return an object containing `to`, `from`, `value`, `gas`, `gasPrice`, `nonce`, and `chainID`.
            Make sure to calculate all of these values properly using `web3.py`!
          - For `BTCTEST`, return `PrivateKeyTestnet.prepare_transaction(account.address, [(to, amount, BTC)])`
            ```
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
            ```

    - `send_tx`:
       - This function will call `create_tx`, sign the transaction, then send it to the designated network.
       - This function needs the following parameters:

         - `coin` -- the coin type (defined in `constants.py`).
         - `account` -- the account object from `priv_key_to_account`.
         - `to` -- the recipient address.
         - `amount` -- the amount of the coin to send.
            ```
            def send_tx(coin, account, to, amount):
                if coin == ETH:
                    raw_tx = create_tx(coin, account, to, amount)
                    signed = account.signTransaction(raw_tx)
                    return w3.eth.sendRawTransaction(signed.rawTransaction)
                if coin == BTCTEST:
                    raw_tx = create_tx(coin, account, to, amount)
                    signed = account.sign_transaction(raw_tx)
                    return NetworkAPI.broadcast_tx_testnet(signed)
            ```

  - Check the coin, then create a `raw_tx` object by calling `create_tx`. Then, sign the `raw_tx` using `bit` or `web3.py` 

  - Once you've signed the transaction, send it to the designated blockchain network.

    - For `ETH`, return `w3.eth.sendRawTransaction(signed.rawTransaction)`
    - For `BTCTEST`, return `NetworkAPI.broadcast_tx_testnet(signed)`
      ```
      coins = {
          ETH: derive_wallets(coin=ETH),
          BTCTEST: derive_wallets(coin=BTCTEST),
      }
      ```

### Sending transactions

#### Fund wallets using testnet faucets.
  - Open up a new terminal window inside of `wallet`.
  - Run the command `python` to open the Python shell. 
  - Within the Python shell, run the command `from wallet import *`. This will allow you to access the functions in `wallet.py` interactively.
  - You'll need to set the account with  `priv_key_to_account` and use `send_tx` to send transactions.

  - **Bitcoin Testnet transaction**

    - Fund a `BTCTEST` address using [this testnet faucet](https://testnet-faucet.mempool.co/).

    - Use a [block explorer](https://tbtc.bitaps.com/) to watch transactions on the address.

    - Send a transaction to another testnet address (either your own, or the faucet's).
    
      ![bitcoin_testnet](https://github.com/butterflysix/Unit-19-Blockchain-Python/blob/main/images/bitcoin_testnet.png)
                
  - **Local PoA Ethereum transaction**

    - Add one of the `ETH` addresses to the pre-allocated accounts in your `networkname.json`.

    - Delete the `geth` folder in each node, then re-initialize using `geth --datadir nodeX init networkname.json`.
      This will create a new chain, and will pre-fund the new account.

    - [Add the following middleware](https://web3py.readthedocs.io/en/stable/middleware.html#geth-style-proof-of-authority)
      to `web3.py` to support the PoA algorithm:

      ```
      from web3.middleware import geth_poa_middleware

      w3.middleware_onion.inject(geth_poa_middleware, layer=0)
      ```

    - Due to a bug in `web3.py`, you will need to send a transaction or two with MyCrypto first, since the
      `w3.eth.generateGasPrice()` function does not work with an empty chain. You can use one of the `ETH` address `privkey`,
      or one of the `node` keystore files.
