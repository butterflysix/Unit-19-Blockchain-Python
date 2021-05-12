import subprocess
import json

## MacOs Users
# command = './hd-wallet-derive -g --mnemonic="INSERT HERE" --cols=path,address,privkey,pubkey --format=json'

## Windows Users
command = 'php hd-wallet-derive.php -g --mnemonic="suffer elephant glance leopard point device solar whip tip test banner inhale" --cols=path,address,privkey,pubkey'
# command = 'ls'

p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
(output, err) = p.communicate()
p_status = p.wait()

print(output, err)