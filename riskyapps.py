import utils
import requests

def getAllApps():
    token = utils.getAuth()

    url = f"https://graph.microsoft.com/v1.0/oauth2PermissionGrants"
    response = requests.get(url, headers={"Authorization": "Bearer " + token}).json()
    for app in response['value']:
        print(app)
    output=None    
    return output


getAllApps()