from tasks.woofi import WooFi
from models import TokenAmount

from client import Client
from data.config import private_key, arb_rpc


client = Client(private_key=private_key, rpc=arb_rpc)

woofi = WooFi(client=client)
# amount = TokenAmount(amount=0.5, decimals=6)
# tx = woofi.swap_eth_to_usdc(amount=amount)

tx = woofi.swap_usdc_to_eth()

res = woofi.client.verif_tx(tx_hash=tx)
print(res)
