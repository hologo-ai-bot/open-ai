from flask import Blueprint, jsonify, request, current_app
from main.services.openai_service import OpenAIService
from flask_socketio import SocketIO, emit, join_room, leave_room

openai_blueprint = Blueprint('openai', __name__)

openai_service = OpenAIService()

# Dictionary to store sessions
user_sessions = {}

@openai_blueprint.route('/')
def index():
    return 'Open AI Controller Working'

#web socket implementation
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
    try:
        if request.method == "POST":
            clientId = request.json.get('client_id')
            message = request.json.get('message')

            if not clientId or message is None:
                return jsonify({"error": "Invalid input data"}), 400
            if message:
                response = openai_service.connectAi(message, clientId)
                if response.get("error"):
                    return jsonify({"error": response["error"]}), 402       
                else:
                    # print("response :", response)
                    return jsonify(response), 200        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    

   

