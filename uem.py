# Init
import argparse
import pwd
import os 
import requests
import json
import base64
import re
import time
from rich import print
import ssl
import sys
import dotenv
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
    default=f"{os.getcwd()}/scripts/"
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

optional.add_argument(
    "-suuid","--ScriptUUID",
    required=False,
    help="ScriptUUID to delete"
)
# ================================================================================================================================================================ #
toggle.add_argument(
    '-D','--DeleteScripts',
    required=False,
    action='store_true',
    default=False,
    help='If enabled, all scripts in your environment will be deleted. This action cannot be undone. Ensure you are targeting the correct Organization Group.'
)

toggle.add_argument(
    '-U','--UpdateScripts',
    required=False,
    action='store_true',
    default=False,
    help='If enabled, imported scripts will update matched scripts found in the Workspace ONE UEM Console.'
)

toggle.add_argument(
    '-E','--ExportScripts',
    required=False,
    action='store_true',
    default=False,
    help='If enabled, all scripts will be downloaded locally, this is a good option for backuping up scripts before making updates.'
)
toggle.add_argument(
    '-P','--Platform',
    required=False,
    action='store_true',
    default=False,
    help='Keep disabled to import all platforms. If enabled, determines what platform\'s scripts to import. Supported values are "Windows" or "macOS".'
)

toggle.add_argument(
    '-ds','--DeleteAScript',
    required=False,
    action='store_true',
    default=False,
    help='Delete single script. Require script UUID'
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
    # print(webReturn)
    global SmartGroupID 
    SmartGroupID = str(webReturn.get('SmartGroupID'))
    if SmartGroupID == SGID:
        global SmartGroupUUID 
        global SmartGroupName 
        SmartGroupUUID = webReturn.get('SmartGroupUuid')
        SmartGroupName = webReturn.get('Name')
        return SmartGroupUUID
    else:
        print(f"Smart Group ID {SGID} not found")
        return False

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

def GetScripts():
    print("Getting List of Script in the Console")
    endpointURL = URL + "/mdm/groups/" + WorkspaceONEGroupUUID + "/scripts"
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
    print(webReturn.text)
    Status = webReturn
    return Status 

def UpdateScripts(Description,Context,ScriptName,Timeout,Script,Script_Type,OS,Architecture,Variables,ScriptUUID):
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
    webReturn = requests.put(endpointURL,headers=header,json=body)
    return webReturn 


# Updates Exisiting Scripts in the Workspace ONE UEM Console
# def Update_Scripts(description, context, script_name, timeout, script, script_type, os, architecture=None, variables=None, script_uuid=None):
#     endpointURL = URL + "/mdm/scripts/" + script_uuid
#     if variables:
#         variable_string = ";".join([f"{key},{value}" for key, value in variables.items()])
#         KeyValuePair = variable_string.split(';')
#         VaribleBody = []
#         for i in KeyValuePair:
#             key = i.split(',')[0]
#             value = i.split(',')[1]
#             VaribleBody.append({"Key": key, "Value": value})
#     if not architecture:
#         architecture = "UNKNOWN"

#     body = {
#         "name": script_name,
#         "description": description,
#         "platform": os,
#         "script_type": script_type,
#         "platform_architecture": architecture,
#         "execution_context": context,
#         "script_data": script,
#         "timeout": timeout,
#         "script_variables": VaribleBody,
#         "allowed_in_catalog": False
#     }
#     json_data = json.dumps(body, indent=4)
#     #This not sure
#     headers = {'Content-Type': 'application/json'}
#     webReturn = requests.put(endpointURL, headers=headers, data=json_data)
#     status = webReturn.status_code
#     return status



# Returns list of SG assignments to a Sensor
def GetScriptAssignments(ScriptUUID):
    endpointURL = URL + "/mdm/scripts/" + ScriptUUID + "/assignments"
    #headers = {'Content-Type': 'application/json'}
    webReturn = requests.get(endpointURL, headers=headerv2)
    assignments = webReturn.json()["SearchResults"][0]["assigned_smart_groups"]
    return assignments

# Assigns Scripts
# Not like origin powershell code
def AssignScript(script_uuid, smart_group_name, smart_group_uuid,TriggerSchedule = None):
    endpointURL = URL + "/mdm/scripts/" + script_uuid + "/updateassignments"
    EventBody = []
    if not args.TriggerType:
        args.TriggerType = "SCHEDULE"
        if not TriggerSchedule:
            TriggerSchedule = "FOUR_HOURS"
    elif args.TriggerType == "SCHEDULE":
        if not TriggerSchedule:
            TriggerSchedule = "FOUR_HOURS"
    elif args.TriggerType == "EVENT":
        if args.LOGIN:
            EventBody.append("LOGIN")
        if args.LOGOUT:
            EventBody.append("LOGOUT")
        if args.STARTUP:
            EventBody.append("STARTUP")
        if args.RUN_IMMEDIATELY:
            EventBody.append("RUN_IMMEDIATELY")
        if args.NETWORK_CHANGE:
            EventBody.append("NETWORK_CHANGE")
    elif args.TriggerType == "SCHEDULE_AND_EVENT":
        if TriggerSchedule:
            TriggerSchedule = "FOUR_HOURS"
        if args.LOGIN:
            EventBody.append("LOGIN")
        if args.LOGOUT:
            EventBody.append("LOGOUT")
        if args.STARTUP:
            EventBody.append("STARTUP")
        if args.RUN_IMMEDIATELY:
            EventBody.append("RUN_IMMEDIATELY")
        if args.NETWORK_CHANGE:
            EventBody.append("NETWORK_CHANGE")
    smart_group_body = [{
        'smart_group_uuid': smart_group_uuid,
        'smart_group_name': smart_group_name
    }]
    assignment_body = [{
        'assignement_uuid': "00000000-0000-0000-0000-000000000000",
        'name' : smart_group_name,
        'priority' : 1,
        'deployment_mode' : "AUTO",
        'show_in_catalog' : False,
        'memberships' : smart_group_body,
        'script_deployment' : {
            'trigger_type' : args.TriggerType,
            'trigger_events' : EventBody,
            'trigger_schedule' : TriggerSchedule 
        }
    }]
    body = {
        "assignments": assignment_body
    }
    json_data = json.dumps(body, indent=2)
    webReturn = requests.post(endpointURL, headers=header, data=json_data)
    return webReturn

# Parse Local PowerShell Files
def GetLocalScripts():
    print("Parsing Local Files for Scripts")
    script_directory = f"{os.getcwd()}/scripts"
    ExcludedTemplates = 'import_script_sample|template*'
    Scripts =  [
        f for f in os.listdir(script_directory)
        if os.path.isfile(os.path.join(script_directory, f))
        and not re.match(ExcludedTemplates, f)
    ]
    print(f"Found {len(Scripts)} Script Samples")
    return Scripts
    
# scripts = GetLocalScripts()
# for script in scripts:
#     print(script)  # Process each script as needed

#Check for Duplicates
def CheckDuplicatesScript(script_name, current_scripts):
    global CurrentScriptUUID
    duplicate = False
    num = len(current_scripts) -1
    while num >=0:
        if current_scripts[num]['name'] == script_name:
            duplicate = True
            CurrentScriptUUID = current_scripts[num]['script_uuid']
            break
        num -= 1
    return duplicate

#Delete A Script
def DeleteAScript(script_uuid):
    ExistingScripts = GetScripts()
    if ExistingScripts:
        num = ExistingScripts['RecordCount'] - 1
        Curren_Scripts = ExistingScripts['SearchResults']
        while num >= 0:
            console_script_uuid = Curren_Scripts[num]['script_uuid']
            script_name = Curren_Scripts[num]['name']
            if script_uuid == console_script_uuid:
                print(f"Deleting Script {script_name}")
                endpointURL = URL + "/mdm/groups/" + WorkspaceONEGroupUUID + "/scripts/bulkdelete"
                json_data = json.dumps([script_uuid])
                webReturn = requests.post(endpointURL, headers=header, data=json_data)
                return webReturn 
#Delete All Scripts
def DeleteScript():
    ExistingScripts = GetScripts()
    if ExistingScripts:
        num = ExistingScripts['RecordCount'] - 1
        Curren_Scripts = ExistingScripts['SearchResults']
        while num >= 0:
            script_uuid = Curren_Scripts[num]['script_uuid']
            script_name = Curren_Scripts[num]['Name']
            if script_uuid:
                print(f"Deleting Script {script_name}")
                endpointURL = URL + "/mdm/groups/" + args.WorspaceONEGroupUUID + "/scripts/bulkdelete"
                json_data = json.dumps([script_uuid])
                web_return = requests.post(endpointURL, headers=header, data=json_data)
                status = web_return.json()
            num -= 1
#Gets Script's Details (Script Data)
def GetScript(script_uuid):
    endpointURL = URL + "/mdm/scripts/" + script_uuid
    web_return = requests.get(endpointURL, headers=header)
    script_data = web_return.json()
    return script_data

#Downloads Scripts from Console Locally
def ExportScript(path):
    console_scripts = GetScripts()
    num = console_scripts['RecordCount'] - 1
    console_scripts = console_scripts['SearchResults']
    while num >= 0:
        script_uuid = console_scripts[num]['script_uuid']
        script = GetScript(script_uuid)
        script_body = script['script_data']
        script_type = script['script_type']
        script_name = script['name']
        print(f"Exporting {script['name']}")
        if script_body:
            script_data_decoded = base64.b64decode(script_body).decode('utf-8')
            file_extension = {
                'POWERSHELL': '.ps1',
                '2' : '.py',
                '4' : '.zsh',
                '3' : '.sh'
            }.get(script_type, '.txt')
            file_path = os.path.join(download_path, f"{script_name}{file_extension}")
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(script_data_decoded)
        num -= 1

def GetScriptUUIDbyName(ScriptName,ScriptList):
    for Script in ScriptList:
        if Script['name'] == ScriptName:
            return Script['script_uuid']

#Usage
def Usage(script_name):
    print("[*]*****************************************************************")
    print("        [$script_name] Header Missing ")
    print("[*]*****************************************************************")
    print("\nPlease ensure that the $script_name script includes the required header so that it can be imported correctly.\n")
    print("Note: The \"Variables:\" metadata is optional for all platforms. Please do not include if not relevant.\n")

    print("\nExample Windows Script Header")
    print("# Description: Description\n")
    print("# Execution Context: System | User\n")
    print("# Execution Architecture: EITHER64OR32BIT | ONLY_32BIT | ONLY_64BIT | LEGACY\n")
    print("# Timeout: ## greater than 0\n")
    print("# Variables: KEY,VALUE; KEY,VALUE\n")
    print("<YOUR POWERSHELL COMMANDS>\n")

    print("\nExample macOS/Linux Script Header")
    print("<YOUR SCRIPT COMMANDS>\n")
    print("# Description: Description\n")
    print("# Execution Context: System | User\n")
    print("# Execution Architecture: UNKNOWN\n")
    print("# Timeout: ## greater than 0\n")
    print("# Variables: KEY,VALUE; KEY,VALUE\n")
    print("Note: The \"Execution Architecture: UNKNOWN\" metadata is mandatory for macOS/Linux platforms.\n")

    input("Press any key to continue...")



# Print messages
print(f"*****************************************************************")
print("                Starting up the Import Process")
print(f"*****************************************************************")

# Get ogID and UUID from Organizational Group Name
if args.OrganizationGroupName:
    GetOrganizationIDbyName(args.OrganizationGroupName)
elif args.OrganizationGroupID:
    GetOrganizationIDbyID(args.OrganizationGroupID)
else:
    print("Please provide a value for OrganizationGroupName or OrganizationGroupID", file=sys.stderr)
    sys.exit(1)  # Exit with an error code 

#Checking for Supported Console Version
CheckConsoleVersion()
print(args)
# Downloads Scripts Locally if using the -ExportScript parameter
if args.ExportScripts:
    download_path = input("Input path to download Script samples. Press enter to use the current directory: ")
    if not download_path:
        download_path = "./"
    ExportScript(download_path)
    print("*****************************************************************")
    print("Scripts have been downloaded to", download_path)  
    print("*****************************************************************")
    sys.exit()

# If DeleteScripts switch is called, then deletes all Script samples
if args.DeleteScripts:
    DeleteScript()
    sys.exit()

#Clear Variables
# Clear variables, if they exist, avoiding potential errors
PSScripts = []
NumScripts = None

#Pull in Script Samples
PSScripts = GetLocalScripts()
NumScripts = len(PSScripts) - 1
new_scripts = []

#Get List of existing Scripts
ExistingScripts = GetScripts()
if ExistingScripts:
    Num = ExistingScripts['RecordCount'] - 1
    CurrentScripts = ExistingScripts['SearchResults']

while NumScripts >=0:
    Script = PSScripts[NumScripts]
    ScriptName = Script.split('.')[0]
    print(f"Working on {ScriptName}")
    #Get the actual content
    with open(f"{args.ScriptsDirectory}/{Script}", 'r') as file:
        content = file.read()
    usageflag = False
    d = re.findall(r"# Description :?(.*)",content)[0]
    if d:
        Description = d.strip()
    else:
        usageflag = True
    
    c = re.findall(r"# Execution Context :?(.*)",content)[0]
    if c:
        Context = c.strip()
    else:
        usageflag = True

    a = re.findall(r"# Execution Architecture :?(.*)",content)[0]
    if a:
        Architecture = a.strip()
    else:
        usageflag = True

    t = re.findall(r"# Timeout :?(.*)",content)[0]
    if t:
        Timeout = t.strip()
    else:
        usageflag = True
    
    v = re.findall(r"# Variables :?(.*)",content)[0]
    if v:
        Variables = v.strip()
    if usageflag:
        Usage(ScriptName)
        NumScripts -= 1
        continue

    #Encode Script
    with open(f"{args.ScriptsDirectory}/{Script}", 'r', encoding='utf-8') as file:
        Data = file.read()
        Bytes = Data.encode('utf-8')
        Script = base64.b64encode(Bytes).decode('utf-8')
    if ScriptName.endswith(".ps1"):
        Script_Type = "POWERSHELL"
        os_type = "WIN_RT"
        ScriptName = ScriptName.replace(".ps1", "").replace(" ", "_")
    elif ScriptName.endswith(".py"):
        Script_Type = "PYTHON"
        os_type = "APPLE_OSX"
        ScriptName = ScriptName.replace(".py", "").replace(" ", "_")
    elif ScriptName.endswith(".zsh"):
        Script_Type = "ZSH"
        os_type = "APPLE_OSX"
        ScriptName = ScriptName.replace(".zsh", "").replace(" ", "_")
    elif ScriptName.endswith(".sh"):
        ShaBang = content.splitlines()[0].lower()
        if "/bash" in ShaBang:
            Script_Type = "BASH"
        elif "/zsh" in ShaBang:
            Script_Type = "ZSH"
        else:
            Script_Type = "BASH"
        os_type = "APPLE_OSX"
        ScriptName = ScriptName.replace(".sh", "").replace(" ", "_")
    else:
        ShaBang = content.lower()
        if "/bash" in ShaBang:
            Script_Type = "BASH"
        elif "/zsh" in ShaBang:
            Script_Type = "ZSH"
        elif "/python" in ShaBang:
            Script_Type = "PYTHON"
        else:
            Script_Type = "BASH"
        os_type = "APPLE_OSX"
        ScriptName = ScriptName.replace(" ", "_")

    # Check if Script Already Exists
    if CheckDuplicatesScript(ScriptName,CurrentScripts):
        # If script already exists & UpdateSensor parameter is provided, then update into the console
        ScripttobeAssigned = False
        if args.UpdateScripts:
            # Check if Script Already Exists
            print(f"{ScriptName} already exists in this tenant. Updating the Script in the Console")
            if not args.Platform or (args.Platform == 'Windows' and os_type == 'WIN_RT') or (args.Platform == 'macOS' and os_type == 'APPLE_OSX'):
                ScriptUUID = GetScriptUUIDbyName(ScriptName,CurrentScripts)
                UpdateStatus = UpdateScripts(Description, Context, ScriptName, Timeout, Script, Script_Type, os_type, Architecture, Variables, ScriptUUID)
                if UpdateStatus.status_code == 204:
                    print(f"Updated {ScriptName}")
                else:
                    print(f"Failed to update {ScriptName}")
                # Add this script to an array to be used to assign to Smart Group
                new_scripts.append(ScriptName.replace(" ", "_"))
            else:
                print(f"{ScriptName} isn't for {args.Platform}. Skipping!")
        else:
            print("Script is a duplicate and UpdateScript option is not set. Do Nothing.")
    else:
        # Import new Scripts
        if not args.Platform or (args.Platform == 'Windows' and os_type == 'WIN_RT') or (args.Platform == 'macOS' and os_type == 'APPLE_OSX'):
            SetScript(Description, Context, ScriptName, Timeout, Script, Script_Type, os_type, Architecture, Variables)
            # Add this script to an array to be used to assign to Smart Group
            new_scripts.append(ScriptName.replace(" ", "_"))
        else:
            print(f"{ScriptName} isn't for {args.Platform}. Skipping!")

    NumScripts -= 1

#Assgign Scripts to Smart Group if option is set
# Get Smart Group ID and UUID
if args.SmartGroupID !=0 or args.SmartGroupName:
    if args.SmartGroupID:
        SmartGroupUUID = GetSmartGroupUUIDbyID(args.SmartGroupID)
        if SmartGroupUUID:
            print(f"Assigning Scripts to Smart Group {SmartGroupName}")
        else:
            pass
    elif args.SmartGroupName:
        SmartGroupUUID = GetSmartGroupUUIDbyName(args.SmartGroupName, WorkspaceONEOgId)
        if SmartGroupUUID:
            print(f"Assigning Scripts to Smart Group {args.SmartGroupName}")
        else:
            pass
    else:
        print("Please check your values for SmartGroupID or SmartGroupName")
        exit()
    
    if SmartGroupUUID:
        # Get List of Scripts from the Console as ScriptUUID not provided when creating a Script
        Scripts = GetScripts()
        Num = Scripts['RecordCount']
        Scripts = Scripts['SearchResults']

        for Num in range (Num - 1, -1, -1):
             # iterate through Console scripts and get the name
            ConsoleScript = Scripts[Num]['name'].replace(" ", "_")

            newscript = next((script for script in new_scripts if script == ConsoleScript), None)
            if newscript:
                # Check if assigned
                CurrentScriptsAssignmentCount = Scripts[Num]['assignment_count']
                ScriptUUID = Scripts[Num]['script_uuid']
                
                if CurrentScriptsAssignmentCount > 0:
                    # Check existing assignment
                    ScriptAssignments = GetScriptAssignments(ScriptUUID)
                    for assignment in ScriptAssignments:
                        if assignment['smart_group_uuid'] == SmartGroupUUID:
                            ScripttobeAssigned = False
                            print(f"Sensor already assigned to SG: {SmartGroupName}")
                        else:
                            ScripttobeAssigned = True

                    if ScripttobeAssigned:
                        AssignStatus = AssignScript(ScriptUUID, SmartGroupName, SmartGroupUUID, args.TriggerType)
                        if AssignStatus.status_code == 204:
                            print(f"Assigned Script: {Scripts[Num]['name']} to SG: {SmartGroupName}")
                        else:
                            print(f"Failed to assign script {Scripts[Num]['name']} to SG: {SmartGroupName}")
                else:
                    AssignStatus = AssignScript(ScriptUUID, SmartGroupName, SmartGroupUUID, args.TriggerType)
                    if AssignStatus.status_code == 204:
                        print(f"Assigned Script: {Scripts[Num]['name']} to SG: {SmartGroupName}")
                    else:
                        print(f"Failed to assign script {Scripts[Num]['name']} to SG: {SmartGroupName}")

# if args.DeleteAScript: 
#     if args.ScriptUUID:
#         DeleteStatus = DeleteAScript(args.ScriptUUID)
#         if DeleteStatus.status_code == 204:
#             print("Deleted script")
#         else:
#             print("Failed to delete script")
#     else:
#         print("Please provide ScriptUUID to delete")

print("*****************************************************************")
print("                    Import Process Complete")
print("             Please review the status messages above")
print("*****************************************************************")