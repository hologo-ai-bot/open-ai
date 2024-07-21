from mongoengine import Document, StringField, DateTimeField, ListField, EmbeddedDocument, EmbeddedDocumentField
import datetime
import uuid

class Message(EmbeddedDocument):
    content = StringField(required=True)
    timestamp = DateTimeField(default=datetime.datetime.utcnow)
    sender = StringField(required=True, choices=["user", "bot"])

    def to_json(self):
        return {
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "sender": self.sender
        }

class ChatHistory(Document):
    meta = {'collection': 'chatHistory'}  # Collection name in MongoDB
    
    session_id = StringField(required=True, unique=True, default=lambda: str(uuid.uuid4()))
    username = StringField(required=True, max_length=100)  # Increased max_length to accommodate date and time
    messages = ListField(EmbeddedDocumentField(Message))

    def __str__(self):
        return f"<ChatHistory {self.username}>"

    def add_message(self, content, sender):
        message = Message(content=content, sender=sender)
        self.messages.append(message)
        self.save()

    def to_json(self):
        return {
            "id": str(self.id),
            "session_id": self.session_id,
            "username": self.username,
            "messages": [message.to_json() for message in self.messages]
        }
