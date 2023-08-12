from typing import Optional
import requests
import random

from fake_useragent import UserAgent
from web3 import Web3
from web3.eth import AsyncEth
from eth_account.signers.local import LocalAccount

from sdk.exceptions import InvalidProxy
from sdk.wallet import Wallet
from sdk.contracts import Contracts
from sdk.data.models import Networks, Network


class Client:
    network: Network
    account: Optional[LocalAccount]
    w3: Web3

    def __init__(self, private_key: Optional[str] = None, network: Network = Networks.Goerli,
                 proxy: Optional[str] = None, check_proxy: bool = True) -> None:
        self.network = network
        self.headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json',
            'user-agent': UserAgent().chrome
        }
        self.proxy = proxy
        if self.proxy:
            try:
                if 'http' not in self.proxy:
                    self.proxy = f'http://{self.proxy}'

                if check_proxy:
                    your_ip = requests.get(
                        'https://icanhazip.com', proxies={'http': self.proxy, 'https': self.proxy}, timeout=10
                    ).text.rstrip()
                    if your_ip not in proxy:
                        raise InvalidProxy(f"Proxy doesn't work! Your IP is {your_ip}.")

            except InvalidProxy:
                pass

            except Exception as err:
                raise InvalidProxy(str(err))

        self.w3 = Web3(
            provider=Web3.AsyncHTTPProvider(
                endpoint_uri=self.network.rpc,
                request_kwargs={'proxy': self.proxy, 'headers': self.headers}
            ),
            modules={'eth': (AsyncEth,)},
            middlewares=[]
        )

        if private_key:
            self.account = self.w3.eth.account.from_key(private_key=private_key)
        elif private_key is None:
            self.account = self.w3.eth.account.create(extra_entropy=str(random.randint(1, 999_999_999)))
        else:
            self.account = None

        self.wallet = Wallet(self)
        self.contracts = Contracts(self)
