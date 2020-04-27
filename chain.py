"""
A blockchain is an immutable, sequential chain of records called Blocks.
They contain any data, but more importantly they are chained together using hashes.
If a hash is corrupted by an attacker than all subsequent blocks will have incorrect hashes.

To create/mine new Blocks, the Proof of Work algorithm must be solved. This algorithm discovers a number which
solves a problem; it must be difficult to solve but easy to verify computationally.
In this example, difficulty is related to the number of leading zeroes.

To ensure consensus, we make the rule that the longest valid chain is authoritative.
"""
import hashlib
import json
import time
from itertools import tee
from typing import List, Set
from urllib.parse import urlparse

import requests
from pydantic import BaseModel


class TransactionData(BaseModel):
    sender: str
    recipient: str
    amount: int


class Block(BaseModel):
    index: int
    timestamp: float
    data: List[TransactionData]
    proof: int
    previous_hash: str


def pairwise(iterable):
    """ s -> (s0,s1), (s1,s2), (s2, s3), ... """
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


class BlockChain:
    """ Responsible for managing the chain. """

    def __init__(self):
        self.nodes: Set[str] = set()  # "<ip>:<port>" of neighbouring nodes.
        self.chain: List[Block] = []
        self.current_transactions: List[TransactionData] = []

        # Create the genesis block
        self.new_block(proof=100, previous_hash='1')

    # Block Operations

    def new_block(self, proof: int, previous_hash: str = None) -> Block:
        """
        Create a new block in the blockchain
        :param proof: proof given by Proof of Work algorithm
        :param previous_hash: hash of previous block
        :return: new block
        """
        # Creates a new Block and adds it to the chain
        block = Block(
            index=len(self.chain) + 1,
            timestamp=time.time(),
            data=self.current_transactions,
            proof=proof,
            previous_hash=previous_hash or self.hash(self.chain[-1]),
        )
        self.current_transactions = []  # reset
        self.chain.append(block)
        return block

    def new_transaction(self, data: TransactionData) -> int:
        """
        Creates a new transaction to go into the next mined block
        :param data:
        :return: index of the Block that will hold this transaction
        """
        # Adds a new transaction to the list of transactions
        self.current_transactions.append(data)
        return self.last_block.index + 1

    @staticmethod
    def hash(block: Block) -> str:
        """ Creates a SHA-256 hash of a block """
        # Block data keys must be ordered to maintain a consistent hash
        block_string = json.dumps(block.dict(), sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self) -> Block:
        return self.chain[-1]

    # Proof of Work

    def proof_of_work(self, last_poof: int) -> int:
        """
        Proof of Work Algorithm:
        - Find a number p' such that hash(pp') contains leading 4 zeros, where p is the previous p'
        - p is the previous proof, p' is the new proof
        """
        proof = 0
        while self.is_validate_proof(last_poof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def is_validate_proof(last_proof: int, proof: int) -> bool:
        """ Returns True if hash(last_proof, proof) contains 4 leading zeros. """
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    # Node Registration

    def register_node(self, address: str):
        """
        Add new node to set of nodes
        :param address: e.g. 'http::/192.168.0.15:5000'
        :return: None
        """
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def is_valid_chain(self, chain: List[Block]) -> bool:
        """ Return True if given blockchain is valid """
        for prev_block, block in pairwise(chain):
            # Check hashes match between blocks
            if block.previous_hash != self.hash(prev_block):
                return False
            # Check that Proof of Work is correct between blocks
            if not self.is_validate_proof(prev_block.proof, block.proof):
                return False
        return True

    def resolve_conflicts(self) -> bool:
        """ Consensus algorithm which replaces current node with the longest valid chain in the network. """
        new_chain = None
        neighbours = self.nodes
        max_length = len(self.chain)

        # Collect & verify longer chains from neighbouring nodes
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = [Block(**block) for block in response.json()['chain']]

                # Store if chain is longer & valid
                if length > max_length and self.is_valid_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True
        return False
