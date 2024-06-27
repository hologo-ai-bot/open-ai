import requests
import time
import tiktoken
from flask import current_app
from main.models.client import Client
from threading import Thread, Lock
from queue import Queue

class OpenAIService:

    def __init__(self):
        self.locks = {}
        self.queues = {}

    def get_lock(self, clientId):
        # print("get_lock")
        if clientId not in self.locks:
            self.locks[clientId] = Lock()
        return self.locks[clientId]

    def get_queue(self, clientId):
        # print("get_queue")
        if clientId not in self.queues:
            self.queues[clientId] = Queue()
        return self.queues[clientId]

    def worker(self, app, clientId):
        # print("worker")
        with app.app_context():
            queue = self.get_queue(clientId)
            while True:
                task = queue.get()
                if task is None:
                    break
                task()
                queue.task_done()

    def start_worker(self, app, clientId):
        # print("start_worker")
        thread = Thread(target=self.worker, args=(app, clientId))
        thread.daemon = True
        thread.start()

    def updateTokenUsage(self, clientId, tkns_used):
        # print("updateTokenUsage")
        with self.get_lock(clientId):
            client = Client.objects.get(id=clientId)
            client.tkns_used += tkns_used
            client.tkns_remaining -= tkns_used
            client.save()

    def createThread(self, apiToken):
        # print("createThread")
        url = 'https://api.openai.com/v1/threads'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {apiToken}',
            'OpenAI-Beta': 'assistants=v2'
        }

        response = requests.post(url, headers=headers)
        return response.json()['id']

    def sendMessageThread(self, apiToken, threadID, message, clientId):
        # print("sendMessageThread")
        url = f'https://api.openai.com/v1/threads/{threadID}/messages'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {apiToken}',
            'OpenAI-Beta': 'assistants=v2'
        }

        data = {
            "role": "user",
            "content": message
        }

        num_tokens = self.getTokenCount([data])
        self.updateTokenUsage(clientId, num_tokens)

        response = requests.post(url, headers=headers, json=data)
        return response.json(), num_tokens

    def runThread(self, apiToken, threadID, assistant_ID):
        # print("runThread")
        url = f'https://api.openai.com/v1/threads/{threadID}/runs'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {apiToken}',
            'OpenAI-Beta': 'assistants=v2'
        }

        data = {"assistant_id": assistant_ID}

        response = requests.post(url, headers=headers, json=data)
        return response.json()['id']

    def checkRunStatus(self, apiToken, threadID, runID):
        # print("checkRunStatus")
        url = f'https://api.openai.com/v1/threads/{threadID}/runs/{runID}'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {apiToken}',
            'OpenAI-Beta': 'assistants=v2'
        }
        response = requests.get(url, headers=headers)
        return response.json()['status']

    def retrieveMessage(self, apiToken, threadID, clientId):
        # print("retrieveMessage")
        url = f'https://api.openai.com/v1/threads/{threadID}/messages'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {apiToken}',
            'OpenAI-Beta': 'assistants=v2'
        }
        response = requests.get(url, headers=headers)
        reply_data = response.json()['data'][0]['content'][0]['text']['value']
        reply_tokens = self.getTokenCount([{"role": "assistant", "content": reply_data}])
        self.updateTokenUsage(clientId, reply_tokens)
        return reply_data, reply_tokens

    def process_request(self, apiToken, assistant_ID, message, clientId):
        try:
            # print("process_request")
            threadID = self.createThread(apiToken)
            if threadID:
                _, request_tokens = self.sendMessageThread(apiToken, threadID, message, clientId)
                runID = self.runThread(apiToken, threadID, assistant_ID)
                if runID:
                    status = ''
                    while status != "completed":
                        print(f"Current status: {status}. Checking again in 5 seconds...")
                        time.sleep(5)
                        status = self.checkRunStatus(apiToken, threadID, runID)
                    if status == "completed":
                        final_message, reply_tokens = self.retrieveMessage(apiToken, threadID, clientId)
                        return {
                            "message": final_message,
                            "request_tokens": request_tokens,
                            "reply_tokens": reply_tokens,
                            "total_deducted": reply_tokens + request_tokens
                        }
        except Exception as e:
            return {"error": str(e)}

    def connectAi(self, message, clientId):
        try:
            # print("connectAi")
            print("req received : ", clientId, " - ", message)
            remaining_tkns = self.checkRemainingTokens(clientId)
            msg_tkn = self.getTokenCount([{"role": "user", "content": message}])

            if (msg_tkn * 2 >= remaining_tkns) or (remaining_tkns < 1000):
                return {"error": "Remaining tokens are too low. Please recharge to get replies"}

            if remaining_tkns <= 0:
                return {"error": "Token limit reached"}

            result = self.process_request(
                current_app.config['OPENAI_API_TOKEN'],
                current_app.config['ASSISTANT_ID'],
                message,
                clientId
            )
            return result

        except Client.DoesNotExist:
            return {"error": "Unauthorized access"}

    def checkRemainingTokens(self, clientId):
        return Client.objects.get(id=clientId).tkns_remaining

    def getTokenCount(self, messages):
        """Returns the number of tokens used by a list of messages."""
        try:
            model = current_app.config['OPENAI_MODEL']
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        if model == "gpt-3.5-turbo-0125":  # note: future models may deviate from this
            num_tokens = 0
            for message in messages:
                num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
                for key, value in message.items():
                    num_tokens += len(encoding.encode(value))
                    if key == "name":  # if there's a name, the role is omitted
                        num_tokens += -1  # role is always required and always 1 token
            num_tokens += 2  # every reply is primed with <im_start>
            return num_tokens
        else:
            raise NotImplementedError(f"""getTokenCount() is not presently implemented for model {model}.""")
