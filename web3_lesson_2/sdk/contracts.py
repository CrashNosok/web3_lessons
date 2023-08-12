from eth_typing import ChecksumAddress
from web3.contract import AsyncContract

from sdk.data.models import DefaultABIs


class Contracts:
    def __init__(self, client) -> None:
        self.client = client

    async def default_token(self, contract_address: ChecksumAddress) -> AsyncContract:
        return self.client.w3.eth.contract(address=contract_address, abi=DefaultABIs.Token)
