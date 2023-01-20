import logging
import os
import json
import boto3
import urllib3
from botocore.exceptions import ClientError


slack_url = os.environ['slack_url']
teams_url = os.environ['teams_url']
port = int(os.environ['port'])
blocked_port1 = int(os.environ['blocked_port1'])
blocked_port2 = int(os.environ['blocked_port2'])
# blocked_port3 = int(os.environ['blocked_port3'])
# blocked_port4 = int(os.environ['blocked_port4'])
# blocked_port5 = int(os.environ['blocked_port5'])
blocked_ports = [port,blocked_port1,blocked_port2]

def lambda_handler(event, context):
    print("##########3")
    print(event)
    # for i,j in event.items():
    #     a=j
    # for i,m in a.items():
    #         if 'configRuleName'==i:
    #             conf=m
    #             print(conf)
    #         if 'messageType'==i:
    #             mess=m
    #             print(mess)
    """Main Lambda hander - evaluates control and makes messaging decisions."""
    setup_logging()
    AccountId = boto3.client('sts').get_caller_identity().get('Account')
    region = event.get('region')
    #configRuleName = event.get['detail']
    print()
    result = remediate_sg(event,AccountId,region)
    if result:
        return 200

            

    
def remediate_sg(event, AccountId,region):
    print('Event is {}'.format(event))
    print('AccountId is {}'.format(AccountId))

    accounts = {
                    '602011150591' : 'opssbx',
                    '459602490943' : 'devsbx'

                }
    client = accounts[AccountId].split('-')[0]
    account_alias = accounts[AccountId]
    ec2 = boto3.client('ec2')
    try:
        SG = ec2.describe_security_groups(GroupIds=[event['detail']['requestParameters']['groupId']])
        print("@@@@@@@@@@@@@")
        print(SG)
        GroupId = SG.get('SecurityGroups', [{}])[0].get('GroupId', '')
        print("#################")
        print(GroupId)
        a = SG.get('SecurityGroups', [{}])[0].get('IpPermissions', '')
        print("%%%%%%%%%%%%%%%")
        print(a)
        log.info("Evaluating group " + GroupId)
        for Rule in SG.get('SecurityGroups', [{}])[0].get('IpPermissions', ''):
            print("++++++++++++++++++++++++")
            print(Rule) 
            if 'ToPort' in Rule:
                FromPort = int(Rule["FromPort"])
                ToPort = int(Rule["ToPort"])
                #cidr_ary = Rule.get('IpRanges',)[]
                CidrIp = Rule.get('IpRanges', [{}])
                con = False
                for everywhere in CidrIp:
                    print("***************")
                    print(everywhere.get("CidrIp", ''))
                    ac =everywhere.get("CidrIp", '')
                    if (str(ac) == "0.0.0.0/0"):
                        con = True
                # print(con)
                # print("^^^^^^^^^^^^^")
                # print(FromPort)
                # print(ToPort)
                # print(CidrIp)
                #print(cidr_ary)
                        print("00000000000000000000000000000000000")
                        if ((FromPort in blocked_ports) and (ToPort in blocked_ports) and (str(ac) == "0.0.0.0/0")):
                        #if ((FromPort in blocked_ports) and (ToPort in blocked_ports) and (str(CidrIp) == "0.0.0.0/0")):
                            print('World access to port 22 found for group ' + GroupId)
                            
                            print('Removing Rule for SSH 0.0.0.0/0 from group ' + GroupId)
                            log.info('World access to port 22 found for group ' + GroupId)
                            
                            log.info('Removing Rule for SSH 0.0.0.0/0 from group ' + GroupId)
                            res = [''.join(ele) for ele in CidrIp]
                            CidrIps = res
                            try:
                                response = ec2.revoke_security_group_ingress(
                                    GroupId=GroupId,
                                    CidrIp=ac,
                                    FromPort=FromPort,
                                    IpProtocol="tcp",
                                    ToPort=ToPort,
                                    DryRun=False
                                    )
                                log.info(response)
                                print("Executing the revoke step")
                                #message = "Remediation successful. Offending SG Rule revoked. Incident: Config-Critical-Port-Open-To-World. Account : " + account_alias + "\n" + '. SG ID : ' + str(GroupId) + '. Port : ' + str(ToPort)
                                message = "Remediation successful. Offending SG Rule revoked. \n" "Incident: Critical-Port-Open-To-World. \n" "Account : " + account_alias + "\n"+ "Region :" + region + "\n" +'SG ID : ' + str(GroupId) + "\n" + 'ToPort : ' + str(ToPort) + "\n" + 'FromPort : ' + str(FromPort)+ "\n"+'Cidr_Range :' + str(ac)
                                result1= post_to_slack(message,client)
                                print("!!!!!!!!!!!!!!!!!")
                                print(message)
                                log.info("#######################result1###################"+str(result1))
                                return True
                            except Exception as e:
                                print(e)
                                log.info("Error - failed to revoke rule")
                                return False
    except Exception as e:
        print(e)
        print("Failed to retrieve SG details.") 
        return False
        
    return False


def post_to_slack(message,client):
    webhook_url = slack_url
    log.info(str(webhook_url))
    teams_webhook_url = teams_url
    log.info(str(teams_webhook_url))
    slack_data = {'text': message}
    http = urllib3.PoolManager()
    headers={'Content-Type': 'application/json'}
    encoded_data = json.dumps(slack_data).encode('utf-8')
    response = http.request('POST',webhook_url,body=encoded_data,headers=headers)
    log.info('response is :'+str(response))
    response1 = http.request('POST',teams_webhook_url,body=encoded_data,headers=headers)
    log.info('response-1 is :'+str(response1))
    return True


def setup_logging():
    """
    Logging Function.
    Creates a global log object and sets its level.
    """
    global log
    log = logging.getLogger()
    log_levels = {'INFO': 20, 'WARNING': 30, 'ERROR': 40}

    if 'logging_level' in os.environ:
        log_level = os.environ['logging_level'].upper()
        if log_level in log_levels:
            log.setLevel(log_levels[log_level])
        else:
            log.setLevel(log_levels['ERROR'])
            log.error("The logging_level environment variable is not set to INFO, WARNING, or \
                    ERROR.  The log level is set to ERROR")
    else:
        log.setLevel(log_levels['ERROR'])
        log.warning('The logging_level environment variable is not set. The log level is set to \
                  ERROR')
        #log.info('Logging setup complete - set to log level ' + log_level)
