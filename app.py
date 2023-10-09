from flask import Flask, jsonify, request
from blockchain import Blockchain
from uuid import uuid4

# instantiate the node
app = Flask(__name__)

# instantiate the blockchain
network = Blockchain()

# generate a globally unique address for the node
node_id = str(uuid4()).replace('-', '.')

@app.route("/chain", methods=["GET"])
def get_chain():
    response = {
        "length": len(network.chain),
        "nodes": network.nodes,
        "chain": network.chain,
    }
    return jsonify(response), 200

@app.route('/mine', methods=['GET'])
def mine():
    last_block = network.last_block()
    nonce = network.proof_of_work()

    network.new_transaction(
        sender="0",
        recipient=node_id,
        amount=1
    )

    previous_hash = network.hash(last_block)
    block = network.new_block(nonce, previous_hash)

    response = {
        "message": "A new block has been mined.",
        "index": block["index"],
        "data": block["data"],
        "nonce": block["nonce"],
        "previous_hash": block["previous_hash"]
    }
    return jsonify(response), 200

@app.route("/new-transaction", methods=["POST"])
def new_transaction():
    values = request.get_json()
    required = ["sender", "recipient", "amount"]

    if not all(key in values for key in required):
        return "Missing values.", 400

    index = network.new_transaction(values["sender"], values["recipient"], values["amount"])

    response = {
        "message": f"This transaction will be added to the block {index}",
        "transactions": values,
        "block_hash": str(network.hash(network.last_block()))
    }
    return jsonify(response), 201

@app.route("/register-node", methods=["POST"])
def register_node():
    values = request.get_json()
    nodes = values.get("nodes")

    if nodes is None:
        return "[ERROR] supply a valid list of nodes", 400

    for node in nodes:
        network.register_node(node)

    response = {
        "response": "A list of new nodes have been added.",
        "total_nodes": len(network.nodes),
        "nodes": network.nodes
    }
    return jsonify(response), 201

@app.route("/consensus", methods=["GET"])
def consensus():
    replaced = network.aplly_consensus()

    if replaced is True:
        response = {
            "message": "This chain was replaced",
            "new_chain": network.chain
        }
    else:
        response = {
            "message": "This is chain is authoritative",
            "chain": network.chain
        }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
