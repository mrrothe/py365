# Py365
A collection of scripts for finding threats in Office365

## Risky Rules
A tool for finding risky or suspicious inbox rules - more detail in [this post](https://blog.rothe.uk/risky-rules-in-office365/)

### Prerequisities
This tool requires Reqeusts, Requests-cache and Jinja2 - these can be installed with ```pip install -r requirements.txt ```
It requires an administrative access to AzureAD & Office365 environment to set up but no specific account is required for its continued use.
You will need to create a new application registration in the AzureAD portal and grant it the following permissions at the application level and grant admin consent for them:
+ Microsoft Graph
    + Mail.ReadBasic.All
    + MailboxSettings.Read
    + User.Read.All

![AzureAD App](https://blog.rothe.uk/content/images/2020/08/2020-08-23-10_52_34-py365-_-API-permissions---Microsoft-Azure-and-13-more-pages---Home---Microsoft--.png)

Next, generate a secret and make a record of the secret string as well as the app/client ID.
You will then need to make a copy of config.example.py and update it with your own domain, app id and secret

### Usage
Just run riskyrules.py - no arguments are required and once the script has finished the report will be saved as report.html in the current directory