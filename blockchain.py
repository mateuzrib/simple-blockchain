import hashlib
import datetime
import json
import requests
from typing import Any
from urllib.parse import urlparse

class Blockchain:

    def __init__(self) -> None:
        self.__chain: list[dict] = []
        self.__transactions: list[dict] = []
        self.__nodes: list[str] = []

        # creates the fist block of the chain: the genesis block
        self.new_block(nonce=0, previous_hash='0')

    @property
    def chain(self) -> list:
        return self.__chain

    @chain.setter
    def chain(self, new_value) -> None:
        self.__chain = new_value

    @property
    def transactions(self) -> list:
        return self.__transactions

    @transactions.setter
    def transactions(self, new_value) -> None:
        self.__transactions = new_value

    @property
    def nodes(self) -> list:
        return self.__nodes

    @nodes.setter
    def nodes(self, new_value) -> None:
        self.__nodes = new_value

    @staticmethod
    def calculate_hash(data: Any):
        hash = hashlib.sha256(str(data).encode()).hexdigest()
        return hash

    def new_block(self, nonce: int = None, previous_hash: str = None) -> dict:
        # creates a new block and adds it to the chain
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'data': self.transactions,
            'nonce': nonce,
            'previous_hash': previous_hash
        }

        self.chain.append(block)
        self.transactions = []
        return block

    def new_transaction(self, sender: str, recipient: str, amount: float) -> int:
        # adds a new transaction to the list of transactions
        transaction = {
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        }
        self.transactions.append(transaction)
        return self.last_block()['index'] + 1

    def proof_of_work(self) -> int:
        # simple proof of work algorithm
        nonce = 0
        last_block = self.last_block()

        while self.validate_proof(nonce, last_block) is False:
            nonce += 1
        return nonce

    def validate_proof(self, nonce: int, block: dict) -> bool:
        # valides the nonce calculated by the miner
        block['nonce'] = nonce
        hash = self.calculate_hash(block)

        if hash[:4] == '0000':
            return True
        return False

    def register_node(self, address: str) -> None:
        # adds a new node to the list of nodes
        parsed_url = urlparse(address).netloc
        if parsed_url not in self.nodes:
            self.nodes.append(parsed_url)

    def aplly_consensus(self) -> bool:
        # a simple consensus algorithm to resolve conflicts
        # by replacing short chains with the longest one in the network

        nodes = self.nodes
        new_chain = None

        max_length = len(self.chain)

        for node in nodes:
            response = requests.get(f'https://{node}/chain')
            if response.status_code == 200:
                length = response.json()['length']
                node_chain = response.json()['chain']

                if length > max_length and self.validate_chain(node_chain):
                    max_length = length
                    new_chain = node_chain

        if new_chain is not None:
            self.chain = new_chain
            return True
        return False

    def validate_chain(self, chain: list) -> bool:
        # determine if a given chain is valid
        previous_block = chain[0]
        index = 1

        while index < len(chain):
            block = chain[index]
            if block['previous_hash'] != self.calculate_hash(previous_block):
                return False

            if not self.validate_proof(block['nonce'], block):
                return False

            previous_block = block
            index += 1

        return True

    def hash(self, block: dict) -> str:
        # hashes a block
        block = json.dumps(block, sort_keys=True)
        return self.calculate_hash(block)

    def last_block(self) -> dict:
        # returns the last block added to the chain
        return self.chain[-1]

    def __str__(self):
        chain = json.dumps(self.chain, indent=3)
        return chain
