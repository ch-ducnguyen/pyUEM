# pyUEM
Script for automatically import Windows 10 and macOS scripts as Workspace ONE Scripts into the Workspace ONE UEM Console.  

# Issues 
- ~~'EVENT' and 'SCHEDULE' TriggerType doesn't work (Unknown Error)~~

# Usage 
```
usage: uem.py [-h] -ws WORKSPACEONESERVER -wa WORKSPACEONEADMIN -wpw WORKSPACEONEADMINPW [-GN ORGANIZATIONGROUPNAME] [-GID ORGANIZATIONGROUPID] [-d SCRIPTSDIRECTORY] [-sGID SMARTGROUPID] [-sGN SMARTGROUPNAME] [-suuid SCRIPTUUID] [-D]
              [-U] [-E] [-P] [-ds] [-Tt {SCHEDULE,EVENT,SCHEDULE_AND_EVENT}] [-S {FOUR_HOURS,SIX_HOURS,EIGHT_HOURS,TWELVE_HOURS,TWENTY_FOUR_HOURS}] [-Li] [-Lo] [-Su] [-R] [-Nc]

options:
  -h, --help            show this help message and exit

Mandatory Arguments:
  -ws WORKSPACEONESERVER, --WorkspaceONEServer WORKSPACEONESERVER
                        Server URL for the Workspace ONE UEM API Server
  -wa WORKSPACEONEADMIN, --WorkspaceONEAdmin WORKSPACEONEADMIN
                        Client ID for OAuth Token
  -wpw WORKSPACEONEADMINPW, --WorkspaceONEAdminPW WORKSPACEONEADMINPW
                        Client Secret for OAuth Token

Optional Arguments:
  -GN ORGANIZATIONGROUPNAME, --OrganizationGroupName ORGANIZATIONGROUPNAME
                        The display name of the Organization Group. You can find this at the top of the console, normally your company's name. Required to provide OrganizationGroupName or OrganizationGroupID.
  -GID ORGANIZATIONGROUPID, --OrganizationGroupID ORGANIZATIONGROUPID
                        The Group ID for your organization group. You can find this at the top of the console by hovering over the company name. Required to provide OrganizationGroupName or OrganizationGroupID.
  -d SCRIPTSDIRECTORY, --ScriptsDirectory SCRIPTSDIRECTORY
                        The directory your script samples are located, default location is the current directory of this script.
  -sGID SMARTGROUPID, --SmartGroupID SMARTGROUPID
                        If provided, imported scripts will be assigned to this Smart Group. Exisiting assignments will be overwritten. If wanting to assign, you are required to provide SmartGroupID or SmartGroupName. This option will
                        prompt to select the correct Smart Group if multiple Smart Groups are found with a similar name.
  -sGN SMARTGROUPNAME, --SmartGroupName SMARTGROUPNAME
                        If provided, imported scripts will be assigned to this Smart Group. Exisiting assignments will be overwritten. If wanting to assign, you are required to provide SmartGroupID or SmartGroupName. This option will
                        prompt to select the correct Smart Group if multiple Smart Groups are found with a similar name.
  -suuid SCRIPTUUID, --ScriptUUID SCRIPTUUID
                        ScriptUUID to delete

Toggle Arguments:
  -D, --DeleteScripts   If enabled, all scripts in your environment will be deleted. This action cannot be undone. Ensure you are targeting the correct Organization Group.
  -U, --UpdateScripts   If enabled, imported scripts will update matched scripts found in the Workspace ONE UEM Console.
  -E, --ExportScripts   If enabled, all scripts will be downloaded locally, this is a good option for backuping up scripts before making updates.
  -P, --Platform        Keep disabled to import all platforms. If enabled, determines what platform's scripts to import. Supported values are "Windows" or "macOS".
  -ds, --DeleteAScript  Delete single script. Require script UUID

Schedule Arguments:
  -Tt {SCHEDULE,EVENT,SCHEDULE_AND_EVENT}, --TriggerType {SCHEDULE,EVENT,SCHEDULE_AND_EVENT}
                        Required when using 'SmartGroupID' or 'SmartGroupName' parameters. Specify the trigger type: 'SCHEDULE', 'EVENT', or 'SCHEDULE_AND_EVENT'
  -S {FOUR_HOURS,SIX_HOURS,EIGHT_HOURS,TWELVE_HOURS,TWENTY_FOUR_HOURS}, --SCHEDULE {FOUR_HOURS,SIX_HOURS,EIGHT_HOURS,TWELVE_HOURS,TWENTY_FOUR_HOURS}
                        Required when using 'SCHEDULE' or 'SCHEDULE_AND_EVENT' as TriggerType. Provide the schedule interval.
  -Li, --LOGIN          Optional: Specify to use the 'LOGIN' event as a trigger. Required when 'EVENT' or 'SCHEDULE_AND_EVENT' is chosen as TriggerType.
  -Lo, --LOGOUT         Optional: Specify to use the 'LOGOUT' event as a trigger. Required when 'EVENT' or 'SCHEDULE_AND_EVENT' is chosen as TriggerType.
  -Su, --STARTUP        Optional: Specify to use the 'STARTUP' event as a trigger. Required when 'EVENT' or 'SCHEDULE_AND_EVENT' is chosen as TriggerType.
  -R, --RUN_IMMEDIATELY
                        Optional: Specify to use the 'RUN_IMMEDIATELY' event as a trigger. Required when 'EVENT' or 'SCHEDULE_AND_EVENT' is chosen as TriggerType.
  -Nc, --NETWORK_CHANGE
                        Optional: Specify to use the 'NETWORK_CHANGE' event as a trigger. Required when 'EVENT' or 'SCHEDULE_AND_EVENT' is chosen as TriggerType.
```

# Script Format 
Check /scripts folder for samples
