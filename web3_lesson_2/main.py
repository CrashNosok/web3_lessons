from web3.middleware import geth_poa_middleware

from client import Client
from data.config import private_key
from models import Arbitrum, Avalanche, Optimism, Polygon
from tasks.woofi import WooFi
from models import TokenAmount


client = Client(private_key=private_key, network=Avalanche)
client.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

block = client.w3.eth.get_block('latest')
# print(client.w3.eth.max_priority_fee)

# woofi = WooFi(client=client)
# amount = TokenAmount(amount=0.001)
# tx = woofi.swap_eth_to_usdc(amount=amount)
# res = woofi.client.verif_tx(tx_hash=tx)
# print(res)

res = Client.get_max_priority_fee_per_gas(w3=client.w3, block=block)
print(res)
