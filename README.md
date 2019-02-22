# iocage_plugin_analytics
Short Python script to retrieve traffic data from Github's API with regards to iocage plugins

# Options
* -file: Write data to files
* -sheets: Write to a Google Sheets spreadsheet
* -i: When writing to a file, put each repo in its own file
* -s: When writing to a file, put all data in a single file
* -r: Only get data on referrers
* -v: Only get data on views
* -p: Only get data on paths
* -c: Only get data on clones
* -verbose: Print how many plugins and which is being examined as the script runs
* -h: View all argument options

# Setup
First edit stats.py and put the Github access token in:

`g = Github("")`

Must have push access to the repositories. Only repo access needed.

If using Google Sheets:

Authorize the Google account from which the sheet will be created by going to:

https://developers.google.com/sheets/api/quickstart/python

and enabling the API. Then save the created credentials.json file in the directory of the script.

Then edit

`sheet_id = ''`

and put the ID of the spreadsheet to be written. A future update will automatically create the spreadsheet.

# Requirements
py-github

If using Google Sheets:

google-api-python-client

google-auth-httplib2

google-auth-oauthlib
