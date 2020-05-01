import uuid

from flask import Flask, jsonify, request
from pydantic import ValidationError

from chain import BlockChain, TransactionData

# Generate a globally unique address for this node
node_identifier = str(uuid.uuid4()).replace('-', '')

# Instantiate a blockchain
blockchain = BlockChain()

app = Flask(__name__)


@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block
    last_proof = last_block.proof
    proof = blockchain.proof_of_work(last_proof)

    # Sender is "0" to signify that this node has mined a new coin
    blockchain.new_transaction(TransactionData(
        sender="0",
        recipient=node_identifier,
        amount=1,
    ))

    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        **block.dict(),
    }
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Validate required fields
    try:
        data = TransactionData(**values)
    except (TypeError, ValidationError):
        return "Missing values", 400

    index = blockchain.new_transaction(data)

    response = {'message': f"Transaction will be added to Block {index}"}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': [block.dict() for block in blockchain.chain],
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    try:
        nodes = values['nodes']
    except IndexError:
        return "Error: please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': "New nodes have been added",
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['Get'])
def consensus():
    if blockchain.resolve_conflicts():
        response = {
            'message': "Blockchain was replaced",
            'new_chain': [block.dict() for block in blockchain.chain],
        }
    else:
        response = {
            'message': "Blockchain is authoritative",
            'new_chain': [block.dict() for block in blockchain.chain],
        }
    return jsonify(response), 200


if __name__ == '__main__':
    print("URl paths:\n", app.url_map, '\n')
    app.run(host='0.0.0.0', port=5000)
