from typing import Union
from decimal import Decimal
from dataclasses import dataclass

'''
Token:
    name
    address
    balance
'''

tokens_dict = {
    'ETH': {
        'address': '0x00000000000000000000000000000000000000',
        'balance': 1000000000000000000
    },
    'USDC': {
        'address': '0xIu67bubyTG23GBybuyb72672367826374gVHH76',
        'balance': 1000000
    }
}

'''
аннотоции типов
dicimals
try
'''


class TokenAmount:
    Wei: int
    Ether: Decimal
    decimals: int

    def __init__(self, amount: Union[int, float, str, Decimal], decimals: int = 18, wei: bool = False) -> None:
        if wei:
            self.Wei: int = amount
            self.Ether: Decimal = Decimal(str(amount)) / 10 ** decimals

        else:
            self.Wei: int = int(Decimal(str(amount)) * 10 ** decimals)
            self.Ether: Decimal = Decimal(str(amount))

        self.decimals = decimals

    def __str__(self):
        return f'{self.Ether}'


class Token:
    def __init__(self, name: str, address: str, balance: TokenAmount):
        self.name = name
        self.address = address
        self.balance = balance

    def __str__(self) -> str:
        return f'{self.name}: {self.balance}'


class Tokens:
    ETH = Token(
        name='ETH',
        address='0x00000000000000000000000000000000000000',
        balance=TokenAmount(amount=1)
    )
    USDC = Token(
        name='USDC',
        address='0xIu67bubyTG23GBybuyb72672367826374gVHH76',
        balance=TokenAmount(amount=1, decimals=6)
    )


@dataclass
class API:
    key: str
    url: str
    docs: str


class Person:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    def __add__(self, other):
        return Person(name=self.name, age=self.age + other.age)

    def __sub__(self, other):
        return Person(name=self.name, age=self.age - other.age)

    def __mul__(self, other):
        return Person(name=self.name, age=self.age * other.age)

    def __truediv__(self, other):
        return Person(name=self.name, age=self.age / other.age)

    def __eq__(self, other):
        return self.age == other.age

    def __ne__(self, other):
        return self.age != other.age

    def __str__(self):
        return f'{self.name} | {self.age}'


persor_a = Person(name='Bob', age=20)
persor_b = Person(name='Alice', age=21)

print(persor_a + persor_b)
print(persor_a - persor_b)
print(persor_a * persor_b)
print(persor_a / persor_b)
print(persor_a == persor_b)
print(persor_a != persor_b)

# print(persor_a > persor_b)
# print(persor_a < persor_b)
#
#











