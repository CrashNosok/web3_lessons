import asyncio
import random
import time

from loguru import logger


async def foo(param):
    await asyncio.sleep(random.randint(1, 3))
    logger.success(f'start foo with param {param}')
    await asyncio.sleep(random.randint(1, 3))
    logger.success(f'end foo with param {param}')


async def foo2(param):
    await asyncio.sleep(random.randint(1, 3))
    logger.success(f'start foo2 with param {param}')
    await asyncio.sleep(random.randint(1, 3))
    logger.success(f'end foo2 with param {param}')
    return f'param: {param}; res: {random.randint(1, 10)}'


async def main():
    t1 = time.time()
    await asyncio.wait([
        asyncio.create_task(foo(1)),
        asyncio.create_task(foo(2)),
        asyncio.create_task(foo(3)),
    ])
    t2 = time.time()
    logger.success(t2 - t1)


async def main2():
    t1 = time.time()
    await asyncio.gather(
        asyncio.create_task(foo(1)),
        asyncio.create_task(foo(2)),
        asyncio.create_task(foo(3)),
    )
    t2 = time.time()
    logger.success(t2 - t1)

    '''
    asyncio.gather() принимает список асинхронных задач (coroutines) в качестве аргументов и запускает их одновременно.
    Она возвращает список результатов, соответствующих выполненным задачам в том же порядке, в котором задачи были переданы в функцию.
    Если во время выполнения задачи возникает исключение, asyncio.gather() прекращает выполнение остальных задач и сразу же выбрасывает исключение.

    asyncio.wait() принимает список асинхронных задач (coroutines) в качестве аргументов и запускает их одновременно.
    Она возвращает кортеж из двух множеств: множество выполненных задач и множество невыполненных задач.
    Если во время выполнения задачи возникает исключение, asyncio.wait() продолжает выполнение остальных задач и не выбрасывает исключение.
    '''


async def main3():
    t1 = time.time()
    tasks = []
    for i in range(1, 6):
        tasks.append(asyncio.create_task(foo2(i)))
    await asyncio.gather(*tasks)
    t2 = time.time()
    logger.success(t2 - t1)

    for task in tasks:
        logger.success(task.result())


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main3())




















