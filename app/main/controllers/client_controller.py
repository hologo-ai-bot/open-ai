from flask import Blueprint, jsonify,  request
from main.models.client import Client

client_blueprint = Blueprint('token', __name__)

@client_blueprint.route('/')
def index():
    return 'Token Controller Working'

@client_blueprint.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    first_name = data.get('fname')
    last_name = data.get('lname')
    tkns_remaining = data.get('tokens')

    if not username or not email or not password or not first_name or not last_name :
        return jsonify({"error": "Invalid data provided"}), 400

    client= Client(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        tkns_remaining=tkns_remaining
    )

    try:
        client.save()
        return jsonify("Success ",client.to_json()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@client_blueprint.route('/<username>', methods=['GET'])
def get_user(username):
    client= Client.objects(username=username).first()
    if client:
        return jsonify(client.to_json()), 200
    else:
        return jsonify({"error": "User not found"}), 404

@client_blueprint.route('/token/<username>', methods=['GET'])
def get_token(username):
    client = Client.objects(username=username).first()
    if client:
        response = f"Allocated tokens: {client.tkns_remaining + client.tkns_used}",f"Remaining tokens: {client.tkns_remaining}", f"tokens used: {client.tkns_used}"
        return jsonify(response), 200
    else:
        return jsonify({"error": "User not found"}), 404

@client_blueprint.route('/token/update', methods=['PUT'])
def update_token():
    data = request.json
    username = data.get('username')
    add_tkn = data.get('add_tkn')

    if not username or add_tkn is None :
        return jsonify({"error": "Invalid input data"}), 400

    client = Client.objects(username=username).first()
    if client:
        #client.update(set__remaining_tkns=(client.remaining_tkns + add_tkn))
        client.update(inc__tkns_remaining=add_tkn)
        return jsonify({"success": "Token update success"}), 200
    else:
        return jsonify({"error": "User not found"}), 404

@client_blueprint.route('/delete', methods=['Delete'])
def delete_client():
    data = request.json
    clientId = data.get('clientId')

    if clientId is None:
        return jsonify({"error": "Invalid input data"}), 400

    client = Client.objects(id=clientId).first()
    if client:
        client.delete()
        return jsonify({"success": "client deletion success"}), 200
    else:
        return jsonify({"error": "Client not found"}), 404

