from web3 import Web3
from typing import Optional
import requests
from web3.middleware import geth_poa_middleware

from models import DefaultABIs, TokenAmount
from utils import read_json
from models import Network

from data.config import TOKEN_ABI


class Client:
    # default_abi = DefaultABIs.Token
    default_abi = read_json(TOKEN_ABI)

    def __init__(
            self,
            private_key: str,
            network: Network
    ):
        self.private_key = private_key
        self.network = network
        self.w3 = Web3(Web3.HTTPProvider(endpoint_uri=self.network.rpc))
        self.address = Web3.to_checksum_address(self.w3.eth.account.from_key(private_key=private_key).address)

    def get_decimals(self, contract_address: str) -> int:
        return int(self.w3.eth.contract(
            address=Web3.to_checksum_address(contract_address),
            abi=Client.default_abi
        ).functions.decimals().call())

    def balance_of(self, contract_address: str, address: Optional[str] = None) -> TokenAmount:
        if not address:
            address = self.address
        contract = self.w3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=Client.default_abi)
        return TokenAmount(
            amount=contract.functions.balanceOf(address).call(),
            decimals=self.get_decimals(contract_address=contract_address),
            wei=True
        )

    def get_allowance(self, token_address: str, spender: str) -> TokenAmount:
        contract = self.w3.eth.contract(address=Web3.to_checksum_address(token_address), abi=Client.default_abi)
        return TokenAmount(
            amount=contract.functions.allowance(self.address, spender).call(),
            decimals=self.get_decimals(contract_address=token_address),
            wei=True
        )

    def check_balance_interface(self, token_address, min_value) -> bool:
        print(f'{self.address} | balanceOf | check balance of {token_address}')
        balance = self.balance_of(contract_address=token_address)
        decimal = self.get_decimals(contract_address=token_address)
        if balance < min_value * 10 ** decimal:
            print(f'{self.address} | balanceOf | not enough {token_address}')
            return False
        return True

    @staticmethod
    def get_max_priority_fee_per_gas(w3: Web3, block: dict) -> int:
        block_number = block['number']
        latest_block_transaction_count = w3.eth.get_block_transaction_count(block_number)
        max_priority_fee_per_gas_lst = []
        for i in range(latest_block_transaction_count):
            try:
                transaction = w3.eth.get_transaction_by_block(block_number, i)
                if 'maxPriorityFeePerGas' in transaction:
                    max_priority_fee_per_gas_lst.append(transaction['maxPriorityFeePerGas'])
            except Exception:
                continue

        if not max_priority_fee_per_gas_lst:
            max_priority_fee_per_gas = w3.eth.max_priority_fee
        else:
            max_priority_fee_per_gas_lst.sort()
            max_priority_fee_per_gas = max_priority_fee_per_gas_lst[len(max_priority_fee_per_gas_lst) // 2]
        return max_priority_fee_per_gas

    def send_transaction(
            self,
            to,
            data=None,
            from_=None,
            increase_gas=1.,
            value=None,
            max_priority_fee_per_gas: Optional[int] = None,
            max_fee_per_gas: Optional[int] = None
    ):
        if not from_:
            from_ = self.address

        tx_params = {
            'chainId': self.w3.eth.chain_id,
            'nonce': self.w3.eth.get_transaction_count(self.address),
            'from': Web3.to_checksum_address(from_),
            'to': Web3.to_checksum_address(to),
        }
        if data:
            tx_params['data'] = data

        if self.network.eip1559_tx:
            w3 = Web3(provider=Web3.HTTPProvider(endpoint_uri=self.network.rpc))
            w3.middleware_onion.inject(geth_poa_middleware, layer=0)

            last_block = w3.eth.get_block('latest')
            if not max_priority_fee_per_gas:
                # max_priority_fee_per_gas = self.w3.eth.max_priority_fee
                max_priority_fee_per_gas = Client.get_max_priority_fee_per_gas(w3=w3, block=last_block)
            if not max_fee_per_gas:
                # base_fee = int(last_block['baseFeePerGas'] * 1.125)
                base_fee = int(last_block['baseFeePerGas'] * increase_gas)
                max_fee_per_gas = base_fee + max_priority_fee_per_gas
            tx_params['maxPriorityFeePerGas'] = max_priority_fee_per_gas
            tx_params['maxFeePerGas'] = max_fee_per_gas

        else:
            tx_params['gasPrice'] = self.w3.eth.gas_price

        if value:
            tx_params['value'] = value

        try:
            tx_params['gas'] = int(self.w3.eth.estimate_gas(tx_params) * increase_gas)
        except Exception as err:
            print(f'{self.address} | Transaction failed | {err}')
            return None

        sign = self.w3.eth.account.sign_transaction(tx_params, self.private_key)
        return self.w3.eth.send_raw_transaction(sign.rawTransaction)

    def verif_tx(self, tx_hash) -> bool:
        try:
            data = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=200)
            if 'status' in data and data['status'] == 1:
                print(f'{self.address} | transaction was successful: {tx_hash.hex()}')
                return True
            else:
                print(f'{self.address} | transaction failed {data["transactionHash"].hex()}')
                return False
        except Exception as err:
            print(f'{self.address} | unexpected error in <verif_tx> function: {err}')
            return False

    def approve(self, token_address, spender, amount: Optional[TokenAmount] = None):
        contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(token_address),
            abi=Client.default_abi
        )
        return self.send_transaction(
            to=token_address,
            data=contract.encodeABI('approve',
                                    args=(
                                        spender,
                                        amount.Wei
                                    ))
        )

    def approve_interface(self, token_address: str, spender: str, amount: Optional[TokenAmount] = None) -> bool:
        print(f'{self.address} | approve | start approve {token_address} for spender {spender}')
        decimals = self.get_decimals(contract_address=token_address)
        balance = self.balance_of(contract_address=token_address)

        if balance.Wei <= 0:
            print(f'{self.address} | approve | zero balance')
            return False

        if not amount or amount.Wei > balance.Wei:
            amount = balance

        approved = self.get_allowance(token_address=token_address, spender=spender)
        if amount.Wei <= approved.Wei:
            print(f'{self.address} | approve | already approved')
            return True

        tx_hash = self.approve(token_address=token_address, spender=spender, amount=amount)
        if not self.verif_tx(tx_hash=tx_hash):
            print(f'{self.address} | approve | {token_address} for spender {spender}')
            return False
        return True

    def get_eth_price(self, token='ETH'):
        token = token.upper()
        print(f'{self.address} | getting {token} price')
        response = requests.get(f'https://api.binance.com/api/v3/depth?limit=1&symbol={token}USDT')
        if response.status_code != 200:
            print(f'code: {response.status_code} | json: {response.json()}')
            return None
        result_dict = response.json()
        if 'asks' not in result_dict:
            print(f'code: {response.status} | json: {response.json()}')
            return None
        return float(result_dict['asks'][0][0])
