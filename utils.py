import requests
import datetime
import requests_cache
import config

requests_cache.install_cache(backend="memory")

authExpiry = datetime.datetime.now()
authToken = ""


def getUsers():
    token = getAuth()
    url = "https://graph.microsoft.com/beta/users/"
    response = requests.get(url, headers={"Authorization": "Bearer " + token}).json()
    return response["value"]


def getAuth():
    global authExpiry, authToken
    expDelta = authExpiry - datetime.datetime.now()
    if expDelta.total_seconds() < 0:  # token expired or not yet generated
        url = f"https://login.microsoftonline.com/{config.domain}/oauth2/v2.0/token"
        payload = f"client_id={config.clientid}&scope=https%3A//graph.microsoft.com/.default%0A&client_secret={config.secret}&grant_type=client_credentials"
        response = requests.post(url, headers={"Content-Type": "application/x-www-form-urlencoded"}, data=payload,).json()
        authExpiry = datetime.datetime.now() + datetime.timedelta(seconds=int(response["expires_in"]))
        authToken = response["access_token"]
    return authToken


def getFolderName(userID, folderID):
    token = getAuth()
    url = f"https://graph.microsoft.com/beta/users/{userID}/mailFolders/{folderID}"
    try:
        response = requests.get(url, headers={"Authorization": "Bearer " + token}).json()["displayName"]
    except KeyError:
        response = "Folder does not exist"
    return response

class rulePrinter:
    def __init__(self,rule,user):
        self.rule=rule
        self.user=user
        self.output=""
    
    def outputObj(self):
        self.formatObj(self.rule)
        return self.output

    def formatObj(self,obj):
        if isinstance(obj, str):
            if len(obj)==120: # Assume folder ID
                self.output += getFolderName(self.user, obj) + "\n"
            else:
                self.output += obj  + "\n"
        if isinstance(obj, bool) or isinstance(obj, int):
            self.output += str(obj)  + "\n"
        if isinstance(obj, dict):
            for k, v in obj.items():
                self.output += k + " : "
                self.formatObj(v)
        if isinstance(obj, list):
            for i in obj:
                self.formatObj(i)
