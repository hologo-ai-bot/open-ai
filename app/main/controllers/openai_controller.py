from flask import Blueprint, jsonify, request, current_app
from main.services.openai_service import OpenAIService
from main.models.client import Client

openai_blueprint = Blueprint('openai', __name__)

openai_service = OpenAIService()

# Dictionary to store sessions
user_sessions = {}

@openai_blueprint.route('/')
def index():
    return 'Open AI Controller Working'

def register_socketio_handlers(socketio):
    @socketio.on('connect')
    def handle_connect():
        emit('message', {'data': 'Connected to the bot'})

    @socketio.on('disconnect')
    def handle_disconnect():
        print('Client disconnected')

    @socketio.on('join')
    def handle_join(data):
        room = data['room']
        join_room(room)
        emit('message', {'data': f'Joined room: {room}'}, room=room)

    @socketio.on('leave')
    def handle_leave(data):
        room = data['room']
        leave_room(room)
        emit('message', {'data': f'Left room: {room}'}, room=room)

    @socketio.on('message')
    def handle_message(data):
        room = data.get('room')
        message = data.get('message')
        
        if message:
            openai_tkn = current_app.config['OPENAI_API_TOKEN']
            assistant_id = current_app.config['ASSISTANT_ID']
            
            response = openai_service.connectAi(openai_tkn, message, assistant_id)
            if response:
                emit('response', response, room=room)
            else:
                emit('response', {'error': 'No response from AI'}, room=room)
        else:
            emit('response', {'error': 'No message found'}, room=room)

@openai_blueprint.route('/convo', methods=['POST'])
def convo():
    if request.method == "POST":
        clientId = request.json.get('client_id')
        message = request.json.get('message')

        if not clientId or message is None:
         return jsonify({"error": "Invalid input data"}), 400

        client = Client.objects(id=clientId).first()

        if not client:
            return jsonify({"error": "Client not found"}), 404
        
        if  (len(message) >= client.tkns_remaining ) :
            return jsonify({"error": "Token limit exceeded"}), 402
        
        if message:
            openai_tkn = current_app.config['OPENAI_API_TOKEN']
            assistant_id = current_app.config['ASSISTANT_ID']
      
            response = openai_service.connectAi(openai_tkn, message, assistant_id)
            if response:
                tkns_used = response["request_tokens"] + response["reply_tokens"]
                print("total tkns used ",tkns_used)
                if client.tkns_remaining < tkns_used :
                    client.tkns_used += client.tkns_remaining
                    client.tkns_remaining = 0
                    client.save()
                    return jsonify({"error": "Token limit reached"}), 402
                else:
                    client.tkns_used += tkns_used
                    client.tkns_remaining -= tkns_used
                    client.save()
                    return jsonify(response), 200
            else:
                jsonify({"error": "Error fetching response"}), 500

        return "Invalid input data", 400

# @openai_blueprint.route('/tkns/check', methods=['GET'])
# def get_tkns():
   

