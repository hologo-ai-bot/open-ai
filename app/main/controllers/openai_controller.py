from flask import Blueprint, jsonify, request, current_app
from main.services.openai_service import OpenAIService
from flask_socketio import SocketIO, emit, join_room, leave_room
from main.models.client import Client

openai_blueprint = Blueprint('convo', __name__)

openai_service = OpenAIService()

# const io = require("socket.io")(server, {
#   pingTimeout: 60000,
#   cors: {
#     origin: "http://localhost:5000",
#     // credentials: true,
#   },
# });

# io.on("connection", (socket) => {
#   console.log("Connected to socket.io");
#   socket.on("setup", (userData) => {
#     socket.join(userData._id);
#     socket.emit("connected");
#   });

# Dictionary to store sessions
user_sessions = {}

@openai_blueprint.route('/')
def index():
    return 'Open AI Controller Working'

# Initializes the SocketIO instance with the current Flask application and allows CORS access from any origin.
socketio = SocketIO(cors_allowed_origins='*')

def register_socketio_handlers(socketio):
    @socketio.on('connect', namespace='/convo')
    def handle_connect():
        emit('message', {'data': 'Connected to the bot'})

    @socketio.on('disconnect', namespace='/convo')
    def handle_disconnect():
        print('Client disconnected')

    @socketio.on('join', namespace='/convo')
    def handle_join(data):
        room = data['room']
        join_room(room)
        emit('message', {'data': f'Joined room: {room}'}, room=room)

    @socketio.on('leave', namespace='/convo')
    def handle_leave(data):
        room = data['room']
        leave_room(room)
        emit('message', {'data': f'Left room: {room}'}, room=room)

    @socketio.on('message', namespace='/convo')
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

# Initialize SocketIO
socketio.init_app(current_app)

# Register SocketIO handlers
register_socketio_handlers(socketio)


#   socket.on("join chat", (room) => {
#     socket.join(room);
#     console.log("User Joined Room: " + room);
#   });
#   socket.on("typing", (room) => socket.in(room).emit("typing"));
#   socket.on("stop typing", (room) => socket.in(room).emit("stop typing"));

#   socket.on("new message", (newMessageRecieved) => {
#     var chat = newMessageRecieved.chat;

#     if (!chat.users) return console.log("chat.users not defined");

#     chat.users.forEach((user) => {
#       if (user._id == newMessageRecieved.sender._id) return;

#       socket.in(user._id).emit("message recieved", newMessageRecieved);
#     });
#   });

#   socket.off("setup", () => {
#     console.log("USER DISCONNECTED");
#     socket.leave(userData._id);
#   });
# });


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
   



# import io from 'ocket.io-client';

# const socket = io('https://your-flask-app.com/convo', {
#   transports: ['websocket'],
#   query: {
#     EIO: '3',
#     transport: 'websocket',
#   },
# });

# socket.on('message', (data) => {
#   console.log(`Received message: ${data.data}`);
# });

# socket.on('response', (data) => {
#   console.log(`Received response: ${data}`);
# });

# socket.emit('join', { room: 'your_room_id' });

# socket.emit('message', { message: 'Hello..!' });
