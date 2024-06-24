from main.models.client import Client

class ClientService:
    def clientRegister(self, username, email, password, first_name, last_name, tkns_remaining):
        client= Client(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        tkns_remaining=tkns_remaining
        )
        client.save()
        return client
    
    def returnClient(self, username):
        client = Client.objects.get(username=username)
        return client

    def returnTokenInfo(self, username):
        client = Client.objects.get(username=username)
        return f"Allocated tokens: {client.tkns_remaining + client.tkns_used}",f"Remaining tokens: {client.tkns_remaining}", f"tokens used: {client.tkns_used}"

    def updateClientToken(self, username, addition):
        client = Client.objects.get(username=username)
        # client.update(inc__tkns_remaining=add_tkn)
        client.tkns_remaining += addition
        client.save()
        return True
    
    def deleteClient(self, clientId):
        client = Client.objects.get(id=clientId)
        client.delete()
        return True