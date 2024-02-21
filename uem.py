# Init
import argparse
import pwd
import os 
import requests
import json
import base64
import re 
import dotenv
import time 

dotenv.load_dotenv()

parser = argparse.ArgumentParser()

mandatory = parser.add_argument_group('Mandatory Arguments')
optional = parser.add_argument_group('Optional Arguments')
toggle = parser.add_argument_group('Toggle Arguments')
schedule = parser.add_argument_group('Schedule Arguments')

# ================================================================================================================================================================ #
mandatory.add_argument(
    '-ws','--WorkspaceONEServer',
    required=True,
    help='Server URL for the Workspace ONE UEM API Server'
    )
mandatory.add_argument(
    '-wa','--WorkspaceONEAdmin',
    required=True,
    help='Client ID for OAuth Token'
)
mandatory.add_argument(
    '-wpw','--WorkspaceONEAdminPW',
    required=True,
    help='Client Secret for OAuth Token'
)
# ================================================================================================================================================================ #
optional.add_argument(
    '-GN','--OrganizationGroupName',
    required=False,
    help="""The display name of the Organization Group. You can find this at the top of the console, normally your company's name.
    Required to provide OrganizationGroupName or OrganizationGroupID."""
)
optional.add_argument(
    '-GID','--OrganizationGroupID',
    required=False,
    help="""The Group ID for your organization group. You can find this at the top of the console by hovering over the company name.
    Required to provide OrganizationGroupName or OrganizationGroupID."""
)
optional.add_argument(
    '-d','--ScriptsDirectory',
    required=False,
    help='The directory your script samples are located, default location is the current directory of this script.',
    default=os.getcwd()
)
optional.add_argument(
    '-sGID','--SmartGroupID',
    required=False,
    help=""" If provided, imported scripts will be assigned to this Smart Group. Exisiting assignments will be overwritten. 
    If wanting to assign, you are required to provide SmartGroupID or SmartGroupName. This option will prompt to select the correct Smart Group
    if multiple Smart Groups are found with a similar name."""
)
optional.add_argument(
    '-sGN','--SmartGroupName',
    required=False,
    help="""If provided, imported scripts will be assigned to this Smart Group. Exisiting assignments will be overwritten. 
    If wanting to assign, you are required to provide SmartGroupID or SmartGroupName. This option will prompt to select the correct Smart Group
    if multiple Smart Groups are found with a similar name."""
)
# ================================================================================================================================================================ #
toggle.add_argument(
    '-D','--DeleteScripts',
    required=False,
    action='store_false',
    help='If enabled, all scripts in your environment will be deleted. This action cannot be undone. Ensure you are targeting the correct Organization Group.'
)

toggle.add_argument(
    '-U','--UpdateScripts',
    required=False,
    action='store_false',
    help='If enabled, imported scripts will update matched scripts found in the Workspace ONE UEM Console.'
)

toggle.add_argument(
    '-E','--ExportScripts',
    required=False,
    action='store_false',
    help='If enabled, all scripts will be downloaded locally, this is a good option for backuping up scripts before making updates.'
)
toggle.add_argument(
    '-P','--Platform',
    required=False,
    action='store_false',
    help='Keep disabled to import all platforms. If enabled, determines what platform\'s scripts to import. Supported values are "Windows" or "macOS".'
)
# ================================================================================================================================================================ #

schedule.add_argument(
    '-Tt','--TriggerType',
    choices=['SCHEDULE', 'EVENT', 'SCHEDULE_AND_EVENT'],
    required=False, 
    help="Required when using 'SmartGroupID' or 'SmartGroupName' parameters. Specify the trigger type: 'SCHEDULE', 'EVENT', or 'SCHEDULE_AND_EVENT'"
)
schedule.add_argument(
    '-S','--SCHEDULE', 
    choices=['FOUR_HOURS', 'SIX_HOURS', 'EIGHT_HOURS', 'TWELVE_HOURS', 'TWENTY_FOUR_HOURS'],
    required=False, 
    help="Required when using 'SCHEDULE' or 'SCHEDULE_AND_EVENT' as TriggerType. Provide the schedule interval."
)
schedule.add_argument(
    '-Li','--LOGIN',
    required=False,
    action='store_true', 
    help="Optional: Specify to use the 'LOGIN' event as a trigger. Required when 'EVENT' or 'SCHEDULE_AND_EVENT' is chosen as TriggerType."
)
schedule.add_argument(
    '-Lo','--LOGOUT',
    required=False,
    action='store_true', 
    help="Optional: Specify to use the 'LOGOUT' event as a trigger. Required when 'EVENT' or 'SCHEDULE_AND_EVENT' is chosen as TriggerType."
)
schedule.add_argument(
    '-Su','--STARTUP',
    required=False,
    action='store_true', 
    help="Optional: Specify to use the 'STARTUP' event as a trigger. Required when 'EVENT' or 'SCHEDULE_AND_EVENT' is chosen as TriggerType."
)
schedule.add_argument(
    '-R','--RUN_IMMEDIATELY', 
    required=False,
    action='store_true', 
    help="Optional: Specify to use the 'RUN_IMMEDIATELY' event as a trigger. Required when 'EVENT' or 'SCHEDULE_AND_EVENT' is chosen as TriggerType."
)
schedule.add_argument(
    '-Nc','--NETWORK_CHANGE', 
    required=False,
    action='store_true', 
    help="Optional: Specify to use the 'NETWORK_CHANGE' event as a trigger. Required when 'EVENT' or 'SCHEDULE_AND_EVENT' is chosen as TriggerType."
)
# ================================================================================================================================================================ #

args = parser.parse_args()


def SaveToken(TOKEN,TIMESTAMP):
     with open('.env','w') as f:
        f.seek(0)
        f.write(f"TOKEN={TOKEN}\n")
        f.write(f"TIMESTAMP={TIMESTAMP}\n")
        f.truncate()


def IsTokenExpired():
    TOKEN_TS = int(os.getenv('TIMESTAMP'))
    CURRENT_TS = int(time.time())
    if CURRENT_TS - TOKEN_TS > 3600: 
        return True
    else:
        return False 

# Global Vars

URL = args.WorkspaceONEServer + "/API"

AUTH_URL = 'https://apac.uemauth.vmwservices.com/connect/token'

cred = {
    'grant_type': 'client_credentials',
    'client_id':args.WorkspaceONEAdmin,
    'client_secret':args.WorkspaceONEAdminPW
}

# HANDLE TOKEN 
TOKEN = os.getenv('TOKEN')
if TOKEN:
    if IsTokenExpired():
        TOKEN = requests.post(AUTH_URL,cred)
        TOKEN = json.loads(TOKEN.text)['access_token']
        TIMESTAMP = int(time.time())
        SaveToken(TOKEN,TIMESTAMP)  
    else:
        pass 
else:
    TOKEN = requests.post(AUTH_URL,cred)
    TOKEN = json.loads(TOKEN.text)['access_token']
    TIMESTAMP = int(time.time())
    SaveToken(TOKEN,TIMESTAMP)

# Construct REST HEADER
header = {
"Authorization" : f"Bearer {TOKEN}",
"Accept"		: "application/json",
"Content-Type"  : "application/json"
}

headerv2 = {
"Authorization"  : f"Bearer {TOKEN}",
"Accept"		 : "application/json;version=2",
"Content-Type"   : "application/json"
}


def GetOrganizationIDbyName(_OrganizationGroupName):
    print("Getting Organization ID from Group Name")
    endpointURL = URL + "/system/groups/search?name=" + args.OrganizationGroupName
    response = requests.get(endpointURL, headers=headerv2)
    webReturn = response.json()
    # Extract the specific fields from the JSON response
    print(webReturn)
    OGSearchOGs = webReturn.get('OrganizationGroups')
    OGSearchTotal = webReturn.get('TotalResults')
    
    if OGSearchTotal == 0:
        print(f"Group Name: {_OrganizationGroupName} not found")
    elif OGSearchTotal == 1:
        Choice = 0 
    elif OGSearchTotal > 1: 
        ValidChoices = list(range(len(OGSearchOGs)))
        ValidChoices.append('Q')
        print("Multiple OGs found. Please select an OG from the list: ")
        Choice = ''
        
        while Choice != '':
            i = 0
            for OG in OGSearchOGs:
                print('{0}:{1}   {2}   {3}'.format(i,OG['Name'],OG['GroupID'],OG['Country']) )
                i += 1
            Choice = input('Type the number that corresponds to the OG you want, or Press "Q" to quit')

            if Choice in ValidChoices:
                if Choice == 'Q':
                    print('Exiting Script')
                    exit
                else: 
                    Choice = Choice 
            else:
                print(f'{Choice} is NOT a valid selection.')
                print('Please try again ...')
                Choice = ''
        getOG = OGSearchOGs[Choice]
        global OrganizationGroupName 
        global WorkspaceONEOgId 
        global WorkspaceONEGroupUUID 
        OrganizationGroupName = getOG['Name']
        WorkspaceONEOgId = getOG['Id']
        WorkspaceONEGroupUUID = getOG['Uuid']
        print(f"Organization ID for {OrganizationGroupName} = {WorkspaceONEOgId} with UUID = {WorkspaceONEGroupUUID}")


def GetOrganizationIDbyID(OrganizationGroupID):
    print("Getting Organization ID from Group ID")
    endpointURL = URL + "/system/groups/" + OrganizationGroupID
    response = requests.get(endpointURL,headers=header)
    # print(response.text)
    webReturn = response.json()
    # print(webReturn)
    global WorkspaceONEOgId 
    WorkspaceONEOgId = str(webReturn['Id']['Value'])
    if WorkspaceONEOgId == OrganizationGroupID :
        global OrganizationGroupName 
        global WorkspaceONEGroupUUID 
        OrganizationGroupName = webReturn['Name']
        WorkspaceONEGroupUUID = webReturn['Uuid']
    else:
        print(f"Group ID: {OrganizationGroupID} not found")

def GetSmartGroupUUIDbyID(SGID):
    print("Getting Group UUID from group name")
    endpointURL = URL + "/mdm/smartgroups/" + SGID
    response = requests.get(endpointURL,headers=header)
    webReturn = response.json()
    print(webReturn)
    global SmartGroupID 
    SmartGroupID = webReturn.get('SmartGroupID')
    if SmartGroupID == SGID:
        global SmartGroupUUID 
        global SmartGroupName 
        SmartGroupUUID = webReturn.get('SmartGroupUuid')
        SmartGroupName = webReturn.get('Name')
    else:
        print(f"Smart Group ID {SGID} not found")

def GetSmartGroupUUIDbyName(SGName,WorkspaceONEOgId):
    endpointURL = URL + f"/mdm/smartgroups/search?name={SGName}&managedbyorganizationgroupid={WorkspaceONEOgId}"
    response = requests.get(endpointURL,headers=header)
    # print(response.text)
    webReturn = response.json()
    # print(webReturn)
    SGSearch = webReturn.get('SmartGroups')
    SGSearchTotal = webReturn.get('Total')
    
    if SGSearchTotal == 0:
        print(f"Smart Group Name: {SGName} not found. Please check your assignment group name and try again.")
    elif SGSearchTotal == 1:
        Choice = 0
    elif SGSearchTotal > 1:
        ValidChoices = list(range(len(SGSearch)))
        ValidChoices.append('Q')
        print("Multiple Smart Groups found. Please select an SG from the list: ")
        Choice = ''
        while Choice != '':
            i = 0
            for SG in SGSearch:
                print("{0}: {1}   {2}   {3}".format(i,SG['Name'],SG['SmartGroupId'],SG['ManagedByOrganizationGroupName']))
                i += 1
            Choice = input('Type the number that corresponds to the SG you want, or Press "Q" to quit')
            if Choice in ValidChoices:
                if Choice == 'Q':
                    print('Exiting Script')
                    exit
                else: 
                    Choice = Choice 
            else:
                print(f'{Choice} is NOT a valid selection.')
                print('Please try again ...')
                Choice = ''
        getSG = SGSearch[Choice]
        SmartGroupUUID = getSG.get('SmartGroupUuid')
        return SmartGroupUUID

def CheckConsoleVersion():
    endpointURL = URL + "/system/info"
    respnose = requests.get(endpointURL,headers=header)
    webReturn = respnose.json()
    ProductVersion = webReturn.get('ProductVersion')
    Version = int(re.sub('[\.]','',ProductVersion))
    
    if Version >= 20100:
        print(f"Console version : {Version}")
        return None 
    else:
        print(f"Your Console Version is {ProductVersion} scripts only works on Console Version 2010 or above.")
        Response = input("Would you like to continue anyways? Only continue if you are sure you are running 2010+ ( y / n )").lower()
        if Response == 'y':
            print("Yes, Continuing Anyways")
            return None 
        elif Response == 'n':
            print("Existing Script")
            exit 
        else:
            print("Existing Script")
            exit 

def GetScript():
    print("Getting List of Script in the Console")
    endpointURL = URL + "/mdm/groups/" + WorkspaceONEGroupUUID + "/scripts?page=1000"
    response = requests.get(endpointURL,headers=headerv2)
    Scripts = response.json()
    if Scripts:
        print(f"{Scripts.get('RecordCount')} scripts found in console.")
    else:
        print("No scripts found in console.")
    return Scripts

def SetScript(Description,Context,ScriptName,Timeout,Script,Script_Type,OS,Architecture,Variables):
    endpointURL = URL + "/mdm/groups/" + WorkspaceONEGroupUUID + "/scripts"
    if Variables:
        KeyValuePair = Variables.split(';')
        VariableBody = []

        for i in KeyValuePair:
            Key = i.split(',')[0]
            Value = i.split(',')[1]
            VariableBody.append({'name': Key,'value':Value})
    
    if not Architecture:
        Architecture = "UNKNOWN"
    body = {
        'name'                  : ScriptName,
        'description'           : Description,
        'platform'              : OS, 
        'script_type'           : Script_Type,
        'platform_architecture' : Architecture,
        'execution_context'     : Context,
        'script_data'           : Script,
        'timeout'               : Timeout,
        'script_variables'      : VariableBody,
        'allowed_in_catalog'    : False
    }
    
    webReturn = requests.post(endpointURL,headers=header,json=body)
    Status = webReturn
    return Status 

def UpdateScript(Description,Context,ScriptName,Timeout,Script,Script_Type,OS,Architecture,Variables,ScriptUUID):
    endpointURL = URL + "/mdm/scripts/" + ScriptUUID
    
    if Variables:
        KeyValuePair = Variables.split(';')
        VariableBody = []

        for i in KeyValuePair:
            Key = i.split(',')[0]
            Value = i.split(',')[1]
            VariableBody.append({'name': Key,'value':Value})
    if not Architecture:
        Architecture = "UNKNOWN"
    body = {
        'name'                  : ScriptName,
        'description'           : Description,
        'platform'              : OS, 
        'script_type'           : Script_Type,
        'platform_architecture' : Architecture,
        'execution_context'     : Context,
        'script_data'           : Script,
        'timeout'               : Timeout,
        'script_variables'      : VariableBody,
        'allowed_in_catalog'    : False
    }
    webReturn = requests.post(endpointURL,headers=header,json=body)
    Status = webReturn
    return Status 
