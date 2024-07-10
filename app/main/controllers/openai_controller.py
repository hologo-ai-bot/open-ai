from flask import Blueprint, jsonify, request, current_app
from main.services.openai_service import OpenAIService
from flask_socketio import SocketIO, emit, join_room, leave_room

openai_blueprint = Blueprint('openai', __name__)

openai_service = OpenAIService()

# # Dictionary to store sessions
# user_sessions = {}

@openai_blueprint.route('/')
def index():
    return 'Open AI Controller Working'


#web socket implementation
def register_socketio_handlers(socketio):
    @socketio.on('connect')
    def handle_connect():
        print('new client connection established')
        emit('message', {'data': 'Connected to the bot'})

    @socketio.on('disconnect')
    def handle_disconnect():
        print('Client disconnected')

    @socketio.on('message')
    def handle_message(data):
        print('msg received ', data)
        message = (data.get('message'))
        # print(message)
        clientId = data.get('client_id')

        try:
            if not clientId or message is None:
                emit('response', "Something went wrong")
            if message and clientId:
                response = openai_service.connectAi( message, clientId)
                if response.get("error"):
                    emit('response', response['error'])
                else:
                    print('response', response)
                    emit('response', response['message'])
        except Exception as e:
            emit('response', str(e))     

@openai_blueprint.route('/convo', methods=['POST'])
def convo():
   
    try:
        if request.method == "POST":
            clientId = request.json.get('client_id')
            message = request.json.get('message')

            if not clientId or message is None:
                return jsonify({"error": "Invalid input data"}), 400
            if message and clientId:
                response = openai_service.connectAi(message, clientId)
                if response.get("error"):
                    return jsonify({"error": response["error"]}), 402       
                else:
                    # print("response :", response)
                    return jsonify(response), 200        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
    
    

   

