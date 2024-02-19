# Init
import argparse
import pwd
import os 
import requests
import json
import base64

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


# Global Vars

URL = args.WorkspaceONEServer + "/API"

AUTH_URL = 'https://apac.uemauth.vmwservices.com/connect/token'

cred = {
    'grant_type': 'client_credentials',
    'client_id':args.WorkspaceONEAdmin,
    'client_secret':args.WorkspaceONEAdminPW
}

TOKEN = requests.post(AUTH_URL,cred)
TOKEN = json.loads(TOKEN.text)['access_token']
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


