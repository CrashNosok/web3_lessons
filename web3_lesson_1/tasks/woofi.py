from web3 import Web3
from typing import Optional
import time

from client import Client
from data.config import WOOFI_ABI
from utils import read_json
from models import TokenAmount


class WooFi:
    eth_address = Web3.to_checksum_address('0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE')
    usdc_address = Web3.to_checksum_address('0xaf88d065e77c8cC2239327C5EDb3A432268e5831')

    router_abi = read_json(WOOFI_ABI)
    router_address = Web3.to_checksum_address('0x9aed3a8896a85fe9a8cac52c9b402d092b629a30')

    def __init__(self, client: Client):
        self.client = client

    def swap_eth_to_usdc(self, amount: TokenAmount, slippage: float = 1):
        contract = self.client.w3.eth.contract(
            abi=WooFi.router_abi,
            address=WooFi.router_address
        )

        eth_price = self.client.get_eth_price(token='ETH')
        min_to_amount = TokenAmount(
            amount=eth_price * float(amount.Ether) * (1 - slippage / 100),
            decimals=6
        )

        return self.client.send_transaction(
            to=WooFi.router_address,
            data=contract.encodeABI('swap',
                                    args=(
                                        WooFi.eth_address,
                                        WooFi.usdc_address,
                                        amount.Wei,
                                        min_to_amount.Wei,
                                        self.client.address,
                                        self.client.address,
                                    )),
            value=amount.Wei
        )

    def swap_usdc_to_eth(self, amount: Optional[TokenAmount] = None, slippage: float = 1):
        if not amount:
            amount = TokenAmount(
                amount=self.client.balance_of(contract_address=WooFi.usdc_address),
                decimals=6,
                wei=True
            )

        res = self.client.approve_interface(
            token_address=WooFi.usdc_address,
            spender=WooFi.router_address,
            amount=amount
        )
        if not res:
            return False
        time.sleep(5)

        contract = self.client.w3.eth.contract(
            abi=WooFi.router_abi,
            address=WooFi.router_address
        )

        eth_price = self.client.get_eth_price(token='ETH')
        min_to_amount = TokenAmount(
            amount=float(amount.Ether) / eth_price * (1 - slippage / 100),
        )

        return self.client.send_transaction(
            to=WooFi.router_address,
            data=contract.encodeABI('swap',
                                    args=(
                                        WooFi.usdc_address,
                                        WooFi.eth_address,
                                        amount.Wei,
                                        min_to_amount.Wei,
                                        self.client.address,
                                        self.client.address,
                                    ))
        )
