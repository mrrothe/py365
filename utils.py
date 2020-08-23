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
        url = "https://login.microsoftonline.com/rothe.uk/oauth2/v2.0/token"
        payload = f"client_id={config.clientid}&scope=https%3A//graph.microsoft.com/.default%0A&client_secret={config.secret}&grant_type=client_credentials"
        response = requests.post(url, headers={"Content-Type": "application/x-www-form-urlencoded"}, data=payload,).json()
        authExpiry = datetime.datetime.now() + datetime.timedelta(seconds=int(response["expires_in"]))
        authToken = response["access_token"]
    return authToken


def getFolderName(userID, folderID):
    token = getAuth()
    url = f"https://graph.microsoft.com/beta/users/{userID}/mailFolders/{folderID}"
    response = requests.get(url, headers={"Authorization": "Bearer " + token}).json()
    return response["displayName"]

