# iocage_plugin_analytics
Short Python script to retrieve traffic data from Github's API with regards to iocage plugins

# Options
* -format: Sets the output format for the script, either as a (*f*ile) or (*s*sheets). (File) is default.
* -file_type: If file is chosen, write either to (*i*ndividual) files or a (*s*ingle) file. (Single) file is default
* -sheet_id: Id of the spreadsheet to be written to. By default this is blank and a new spreadsheet will be created with the title 'GitHub Data'. Must have write access to the spreadsheet
* -grabs: List which data is desired. By default all is given, which is (*r*eferrers), (*v*iews), (*p*aths), and (*c*lones). For example, if only views and paths are desired, then use '-grabs v p'
* -token: GitHub access token. Must have push access to repo. Only repo scope needed. Blank by default and is required.
* -v: Print total plugin count and which is being examined as the script runs
* -h: View all argument options

# Setup
Only '-token' argument is requiered. Must first create an access token with repo scope and have push access to the repos from which data is desired.

## If using Google Sheets:

Authorize the Google account from which the sheet will be created by going to:

https://developers.google.com/sheets/api/quickstart/python

and enabling the API. Then save the created credentials.json file in the directory of the script.

Then either input the id of a spreadsheet to be written to, or one will be created for you with the title 'GitHub Data'. The default sheet range is all of Sheet1, and if no 'Sheet1' exists the script will fail.

# Requirements
* py-github

## If using Google Sheets:

* google-api-python-client
* google-auth-httplib2
* google-auth-oauthlib
