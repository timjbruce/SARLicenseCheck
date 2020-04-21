import boto3
import json
import os

# import requests
sar = boto3.client('serverlessrepo')
sns = boto3.client('sns')

messagetype = os.getenv('messagetype','')
topicarn = os.getenv('topicarn','')
phone = os.getenv('phonenumber','')

def check_policy(appid):
    policyrule = ''
    policy = sar.get_application_policy(ApplicationId=appid) 
    if(not len(policy['Statements'])==0):
        for pol in policy['Statements']:
            if 'Deploy' in pol['Actions']:
                if '*' in pol.get('Principals','') and len(pol.get('PrincipalOrgIDs','')) == 0:
                    #shared with any account
                    policyrule = f'App {appid} shared with any account'
                    return False, policyrule
    license = sar.get_application(ApplicationId=appid)
    if (not license.get('SpdxLicenseId','') == '')  or (not license.get('LicenseUrl','') == ''):
        #has a license of some sort
        policyrule = f'App {appid} has a license of some sort'
        return False, policyrule
    return True, policyrule

def send_messages(outofpolicy):
    for app in outofpolicy:
        message = f'Application {app["appid"]} is out of compliance.  Reason {app["policy"]}'
        subject = 'SAR App out of compliance'
        if messagetype == 'sns':
            result = sns.publish(TopicArn=topicarn, Message=message, Subject=subject)
        else:
            result = sns.publish(PhoneNumber=phone, Message=message)

def lambda_handler(event, context):
    outofpolicy = []
    apps = sar.list_applications(MaxItems=10)
    if len(apps['Applications']) == 0:
        apps = None
    while not (apps == None):
        for app in apps['Applications']:
            appid = app.get('ApplicationId','')
            inpolicy, policyrule = check_policy(appid)
            if not inpolicy:
                item = {}
                item = {'appid':appid, 'policy':policyrule}
                outofpolicy.append(item)
        nextkey = apps.get('NextKey','')
        if not nextkey == '':
            apps.sar.list_applications(MaxItems=10, NextKey=nextkey)
        else:
            apps = None
    send_messages(outofpolicy)
    
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": {"appsoutofpolicy": len(outofpolicy)},
            # "location": ip.text.replace("\n", "")
        }),
    }
