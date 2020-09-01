import utils
import requests
import json
import re
from jinja2 import Template

class riskFactor:
    def __init__(self, appProperty, risk, value=None, regex=None):
        self.appProperty = appProperty
        self.risk = risk
        self.value = value
        self.regex = regex

    def calculateRisk(self, app):
        risk=0
        print("Calculating")
        for appProperty, appValue in app.items():
            if self.appProperty == appProperty and self.value is None and self.regex is None:  # if rule doesn't specify a value/regex
                risk+=self.risk
            elif self.appProperty == appProperty and isinstance(appValue,str):
                if self.value == appValue:  # If rule specifies a fixed string
                    risk+= self.risk
            elif self.appProperty == appProperty and isinstance(appValue,list) and isinstance(self.value,str):
                if self.value in appValue:  # If rule specifies a fixed string
                    risk+= self.risk
            elif self.appProperty == appProperty and isinstance(appValue,list) and isinstance(self.value,list):
                    if set(appValue).intersection(self.value):
                        risk+= len(set(appValue).intersection(self.value))*self.risk
            elif self.appProperty == appProperty and self.regex and bool(re.search(self.regex, "".join(appValue), re.IGNORECASE)):  # If rule specifies a regex
                risk+= self.risk
        return risk

class Apps:
    def __init__(self):
        self.appData=[]
        self.appOut=[]

    def getAllApps(self):
        token = utils.getAuth()
        url = f"https://graph.microsoft.com/v1.0/oauth2PermissionGrants"
        response = requests.get(url, headers={"Authorization": "Bearer " + token}).json()    
        self.appData=response['value']
        self.enrich()
        return self.appOut

    def enrich(self):
        for app in self.appData:
            appDetails={}
            appDetails['ids']={}
            appDetails['ids']['principalId']=app['principalId']
            appDetails['ids']['grantId']=app['id']
            appDetails['ids']['clientId']=app['clientId']
            appDetails['ids']['resourceId']=app['resourceId']

            if app['principalId']: # If app is user consented get user's name
                appDetails['principalName']=utils.getObjName(app['principalId'])['displayName']
            else:
                app['principalName']="Admin Consented App"

            appDetails['resourceName']=utils.getObjName(app['resourceId'])['appDisplayName']
            appDetails['clientName']=utils.getObjName(app['clientId'])['appDisplayName']

            appDetails['resourceURLs']=utils.getObjName(app['resourceId'])['replyUrls']
            appDetails['clientURLs']=utils.getObjName(app['clientId'])['replyUrls']
            appDetails['scope']=app['scope'].strip().split(" ")
            appDetails['risk']=self.getRisk(appDetails)
            self.appOut.append(appDetails)

    def getRisk(self,app):
        risk=0
        for factor in riskFactors:
            print("Getting Risk")
            risk += factor.calculateRisk(app)
        return risk

def renderApps():
    appsTemplate = Template(open("apps.html").read())
    appsdata = apps.getAllApps()
    appsHTML = appsTemplate.render(appdata=appsdata)
    with open("apps-report.html", "w") as f:
        f.write(appsHTML)

riskFactors = []
riskFactors.append(riskFactor(appProperty="scope", value=["Mail.ReadWrite","MailboxSettings.Read"], risk=20))
riskFactors.append(riskFactor(appProperty="clientName", regex="0365", risk=50))



apps=Apps()
renderApps()