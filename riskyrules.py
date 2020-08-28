import requests
import utils
import re
from jinja2 import Template


class riskFactor:
    def __init__(self, ruleElement, subType, risk, value=None, regex=None):
        self.ruleElement = ruleElement
        self.subType = subType
        self.risk = risk
        self.value = value
        self.regex = regex

    def calculateRisk(self, rule, user):
        if self.ruleElement == "condition" and "condition" in rule:
            for condition, conditionValue in rule["conditions"].items():
                if self.subType == condition and self.value is None and self.regex is None:  # if rule doesn't specify a value/regex
                    return self.risk
                elif self.subType == condition and self.value == conditionValue:  # If rule specifies a fixed string
                    return self.risk
                elif self.subType == condition and self.regex and bool(re.search(self.regex, "".join(conditionValue), re.IGNORECASE)):  # If rule specifies a regex
                    return self.risk
                else:
                    return 0
        elif self.ruleElement == "action":
            for action, actionValue in rule["actions"].items():
                if action == "moveToFolder":  # Rules contain folderID rather than folder name so we need to look it up
                    actionValue = utils.getFolderName(user, actionValue)
                if isinstance(actionValue, list):
                    if isinstance(actionValue[0], dict):
                        actionValue = actionValue[0]["emailAddress"]["address"]
                if self.subType == action and self.value is None and self.regex is None:  # if rule doesn't specify a value/regex
                    return self.risk
                elif self.subType == action and self.value == "".join(actionValue):  # If rule specifies a fixed string
                    return self.risk
                elif self.subType == action and self.regex and bool(re.search(self.regex, "".join(actionValue), re.IGNORECASE)):  # If rule specifies a regex
                    return self.risk
                else:
                    return 0
        else:
            return 0

    def __getitem__(self, item):  # allows a['text'] syntax
        return getattr(self, item)


riskFactors = []
riskFactors.append(riskFactor(ruleElement="condition", subType="subjectContains", risk=5))
riskFactors.append(riskFactor(ruleElement="condition", subType="bodyContains", risk=15))
riskFactors.append(riskFactor(ruleElement="condition", subType="subjectContains", regex="(financ|bank|swift|transaction)", risk=50))
riskFactors.append(riskFactor(ruleElement="condition", subType="subjectContains", regex="(hack|breach|compromise|phishing)", risk=50))

riskFactors.append(riskFactor(ruleElement="action", subType="moveToFolder", risk=2))
riskFactors.append(riskFactor(ruleElement="action", subType="moveToFolder", value="RSS Feeds", risk=70))
riskFactors.append(riskFactor(ruleElement="action", subType="moveToFolder", regex="(deleted|junk|spam)", risk=40))

riskFactors.append(riskFactor(ruleElement="action", subType="forwardTo", risk=25))
riskFactors.append(riskFactor(ruleElement="action", subType="redirectTo", risk=35))
riskFactors.append(riskFactor(ruleElement="action", subType="forwardAsAttachmentTo", risk=35))
riskFactors.append(riskFactor(ruleElement="action", subType="forwardTo", regex="g(oogle)?mail.com", risk=25))


def getRules(userid):
    token = utils.getAuth()
    url = f"https://graph.microsoft.com/beta/users/{userid}/mailFolders/inbox/messagerules"
    response = requests.get(url, headers={"Authorization": "Bearer " + token}).json()
    try:
        return response["value"]
    except KeyError: # Account has no rules
        return {}


def getAllRules():
    output = []
    for user in utils.getUsers():
        if user["assignedLicenses"]:
            for rule in getRules(user["userPrincipalName"]):
                if "conditions" in rule or "actions" in rule:  # Rules without a condition list are client-only and there's nothing to examine
                    output.append(getRuleRisk(rule, user["userPrincipalName"]))
    return output


def ruleSummarize(rule, user):
    r = utils.rulePrinter(rule, user)
    return r.outputObj()


def getRuleRisk(rule, user):
    risk = 0
    for factor in riskFactors:
        risk += factor.calculateRisk(rule, user)
    if not "conditions" in rule:  # Rule that matches every message
        risk += 60
    ruleOutput = {"username": user, "rulename": rule["displayName"], "rulesummary": ruleSummarize(rule, user), "risk": risk}
    return ruleOutput


def renderRules():
    rulesTemplate = Template(open("rules.html").read())
    rulesdata = getAllRules()
    rulesHTML = rulesTemplate.render(rulesdata=rulesdata)
    with open("report.html", "w") as f:
        f.write(rulesHTML)


renderRules()

