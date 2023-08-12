import asyncio
from loguru import logger
from web3 import Web3

from sdk.data.models import Networks
from sdk.client import Client

from private_data import proxy


async def check_empty_wallets(index: int):
    client = Client(network=Networks.Ethereum, proxy=proxy[index], check_proxy=True)
    balance = await client.wallet.balance()
    logger.success(f'balance: {balance} - address: {client.account.address}')


async def main():
    tasks = []
    while True:
        for i in range(1):
            tasks.append(asyncio.create_task(check_empty_wallets(i)))
        await asyncio.gather(*tasks)

    '''
    token_address = Web3.to_checksum_address('0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8')

    tasks = []
    for private_key in [private_key1, private_key2, private_key3]:
        client = Client(private_key=private_key, network=Networks.Arbitrum)
        tasks.append(asyncio.create_task(client.wallet.balance(token_address=token_address)))

    await asyncio.gather(*tasks)
    await asyncio.wait([*tasks])

    for task in tasks:
        print(task.result())
    '''
    '''
    asyncio.gather() принимает список асинхронных задач (coroutines) в качестве аргументов и запускает их одновременно.
    Она возвращает список результатов, соответствующих выполненным задачам в том же порядке, в котором задачи были переданы в функцию.
    Если во время выполнения задачи возникает исключение, asyncio.gather() прекращает выполнение остальных задач и сразу же выбрасывает исключение.

    asyncio.wait() принимает список асинхронных задач (coroutines) в качестве аргументов и запускает их одновременно.
    Она возвращает кортеж из двух множеств: множество выполненных задач и множество невыполненных задач.
    Если во время выполнения задачи возникает исключение, asyncio.wait() продолжает выполнение остальных задач и не выбрасывает исключение.
    '''


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())