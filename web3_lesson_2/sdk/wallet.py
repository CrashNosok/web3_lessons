from typing import Optional, Union

from eth_typing import ChecksumAddress
from sdk.data.models import Wei, TokenAmount

from web3 import Web3


class Wallet:
    def __init__(self, client) -> None:
        self.client = client

    async def balance(self, token_address: Optional[str] = None,
                      address: Optional[ChecksumAddress] = None) -> Union[Wei, TokenAmount]:
        if not address:
            address = self.client.account.address

        address = Web3.to_checksum_address(address)
        if not token_address:
            return Wei(await self.client.w3.eth.get_balance(account=address))

        token_address = Web3.to_checksum_address(token_address)
        contract = await self.client.contracts.default_token(contract_address=token_address)
        return TokenAmount(
            amount=await contract.functions.balanceOf(address).call(),
            decimals=await contract.functions.decimals().call(),
            wei=True
        )

    async def nonce(self, address: Optional[ChecksumAddress] = None) -> int:
        if not address:
            address = self.client.account.address
        return await self.client.w3.eth.get_transaction_count(address)
