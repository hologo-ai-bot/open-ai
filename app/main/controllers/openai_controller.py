from flask import Blueprint, jsonify, request
from main.services.openai_service import OpenAIService
from main.services.chat_service import ChatService
from flask_cors import cross_origin

openai_blueprint = Blueprint('openai', __name__)

openai_service = OpenAIService()
chat_service = ChatService()

@openai_blueprint.route('/')
def index():
    return 'Open AI Controller Working'

@openai_blueprint.route('/convo', methods=['POST'])
@cross_origin(origins='http://localhost:5173')
def convo():
    try:
        if request.method == "POST":
            clientID = request.json.get('clientID')
            message = request.json.get('message')
            sessionId = request.json.get("session_Id")

            if not sessionId or message is None:
                return jsonify({"error": "Invalid input data"}), 400
            if message:
                response = openai_service.connectAi(message, clientId=clientID)
                if response.get("error"):
                    return jsonify({"error": response["error"]}), 402       
                else:
                    res_message = response.get('message', '')
                    save_chat = chat_service.storeMessage(clientID=clientID, req_message=message, res_message=res_message, session_id=sessionId)
                    return jsonify(response), 200        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@openai_blueprint.route('/get_messages', methods=['GET'])
@cross_origin(origins='http://localhost:5173')
def get_messages():
    sessionId = request.args.get('session_id')
    
    if not sessionId:
        return jsonify({'error': 'Missing session_id'}), 400

    chat_history = chat_service.getMessage(session_id=sessionId)
    
    if not chat_history:
        return jsonify({'error': 'No chat history found'}), 404

    return jsonify({"messages" : chat_history.messages}), 200

@openai_blueprint.route('/new_chat', methods=['POST'])
@cross_origin(origins='http://localhost:5173')
def new_chat():
    username = request.json.get('username')
    
    if not username:
        return jsonify({'error': 'Missing username'}), 400

    chat_history = chat_service.createNewChat(username=username)
    print(chat_history)
    if not chat_history:
        return jsonify({'error': 'Unable to create new chat'}), 500

    return jsonify({'session_id': chat_history.session_id}), 200

@openai_blueprint.route('/list_chats', methods=['GET'])
@cross_origin(origins='http://localhost:5173')
def list_chats():
    username = request.args.get('username')
    
    if not username:
        return jsonify({'error': 'Missing username'}), 400

    chat_histories = chat_service.listChats(username=username)
    if not chat_histories:
        return jsonify({'error': 'No chat history found'}), 404

    return jsonify([chat.to_json() for chat in chat_histories]), 200
