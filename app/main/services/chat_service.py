import re
from flask import jsonify
from main.models.chat_history import ChatHistory
from bson import ObjectId
import datetime


class ChatService:
    def storeMessage(self, session_id, req_message, res_message,clientID):
        try:
            chat_history = ChatHistory.objects(session_id=session_id).first()
        
            if not chat_history:
                return jsonify({'error': 'Chat session not found'}), 404
            
            # Add both user and bot messages to the ChatHistory document
            chat_history.add_message(req_message, "user")
            chat_history.add_message(res_message, "bot")
            
            # Save the updated ChatHistory document
            chat_history.save()
            
            return chat_history
        except Exception:
            return None

    def createNewChat(self, username):
        try:
            # Append the current date and time to the username
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            formatted_username = f"{username}_{timestamp}"
            
            chat_history = ChatHistory(username=formatted_username)
            chat_history.save()
            return chat_history
        except Exception as e:
            print(f"Error creating new chat: {e}")
            return None
    
    def getMessage(self, session_id):
        try:
            chat_history = ChatHistory.objects(session_id=session_id).first()
            if not chat_history:
                return jsonify({'error': 'No chat history found'}), 404

            return chat_history
        except Exception:
            return None

    def listChats(self, username):
        try:
            regex = re.compile(f'^{username}_.*')
            chat_histories = ChatHistory.objects(username=regex).all()
            # chat_histories = ChatHistory.objects(username=username).all()
            if not chat_histories:
                return jsonify({'error': 'No chat history found'}), 404
            
            return chat_histories
        except Exception:
            return None
