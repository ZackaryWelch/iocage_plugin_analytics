#!/bin/python

import fileinput
import argparse
import sys
import pickle
import os.path
import json
import time
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from os import listdir

from github import Github

#def replace_id(body, sheet_id):
#    for k in body.keys():
#        if k == "sheetId" and body[k] == "":
#            body[k] = sheet_id
#        if isinstance(body, dict) and isinstance(body[k], dict):
#            replace_id(body[k], sheet_id)
#        elif isinstance(body, dict) and isinstance(body[k], list):
#            replace_id(body[k][0], sheet_id)

def send_request(file_name, sheet, sheet_id):
    with open(file_name, 'r') as f:
        body = json.load(f)
        #replace_id(body['requests'][0], sheet_id)
        sheet.batchUpdate(spreadsheetId=sheet_id,body=body).execute()

def get_referrers(repo):
    referrers = repo.get_top_referrers()
    values = []
    values.append(['referrers'])
    for referrer in referrers:
        values.append(['', referrer.count, referrer.uniques, '', referrer.referrer])
    return values

def print_referrers(repo, f):
    referrers = repo.get_top_referrers()
    f.write(f'Number of top referrers: {len(referrers)}\n')
    for referrer in referrers:
        f.write(f'    \"count\" : {referrer.count},\n    \"uniques\" : {referrer.uniques},\n    \"referrer\" : {referrer.referrer}\n')
    f.write('\n')

def get_paths(repo):
    paths = repo.get_top_paths()
    values = []
    values.append(['paths'])
    for path in paths:
        values.append(['', path.count, path.uniques, '', path.path])
    return values

def print_paths(repo, f):
    paths = repo.get_top_paths()
    f.write(f'Number of top paths: {len(paths)}\n')
    for path in paths:
        f.write(f'    \"count\" : {path.count},\n    \"uniques\" : {path.uniques},\n    \"path\" : {path.path}\n')
    f.write('\n')

def get_views(repo):
    daily_views = repo.get_views_traffic()
    total_views = daily_views['count']
    total_unique_views = daily_views['uniques']
    values = []
    values.append(['views: total_count', total_views, total_unique_views])
    for view in daily_views['views']:
        formatted_time = view.timestamp.strftime("%m/%d/%y")
        values.append(['', view.count, '', formatted_time])
    return values

def print_views(repo, f):
    daily_views = repo.get_views_traffic()
    total_views = daily_views['count']
    total_unique_views = daily_views['uniques']
    f.write(f'    \"total_views\" : {total_views},\n')
    f.write(f'    \"total_uniques\" : {total_unique_views},\n')
    for view in daily_views['views']:
        f.write(f'    \"count\" : {view.count},\n    \"time_t\" : {view.timestamp}\n')
    f.write('\n')

def get_clones(repo):
    clones = repo.get_clones_traffic()
    total_count = clones['count']
    values = []
    #Adds a row with the total count of all clones
    values.append(['clones: total_count', total_count])
    for clone in clones['clones']:
        formatted_time = clone.timestamp.strftime("%m/%d/%y")
        values.append(['', clone.count, clone.uniques, formatted_time])
    return values

def print_clones(repo, f):
    clones = repo.get_clones_traffic()
    total_count = clones['count']
    f.write(f'    \"total_count\" : {total_count},\n')
    for clone in clones['clones']:
        f.write(f'    \"count\" : {clone.count},\n    \"uniques\" : {clone.uniques},\n    \"time_t\" : {clone.timestamp}\n')
    f.write('\n')

def get_simple_clones(repo):
    clones = repo.get_clones_traffic()
    total_count = clones['count']
    total_uniques = clones['uniques']
    return [repo.name[14:], total_count, total_uniques]

def print_simple_clones(repo, f):
    clones = repo.get_clones_traffic()
    total_count = clones['count']
    total_uniques = clones['uniques']
    f.write(f'    \"count\" : {total_count},\n    \"uniques\" : {total_uniques}\n')

def main():
    print_dict = {'referrers': print_referrers,
                  'paths': print_paths,
                  'views': print_views,
                  'clones': print_clones}
    get_dict = {'referrers': get_referrers,
                'paths': get_paths,
                'views': get_views,
                'clones': get_clones}

    parser = argparse.ArgumentParser(description='Retrieve traffic data from iocage plugin repos on Github')
    parser.add_argument('-format', default='sheets', help='Output format (file or sheets)')
    parser.add_argument('-collect_json', default=False, action='store_true', help='Bring all data_plugin files together into one file with objects of arrays')
    parser.add_argument('-sheet_id', default='', help='The ID of the spreadsheet to be written to. By default a new spreadsheet is created. Must have write access to the sheet.')
    parser.add_argument('-grabs', nargs="+", default=list(print_dict), help=f'Choose which data points to retrieve, default all: {" ".join(list(print_dict))}')
    parser.add_argument('-v', default=False, action='store_true', help='Verbose mode')
    parser.add_argument('-token', default='', help='Access token for GitHub. Must have push access to repo')
    parser.add_argument('-all', default=False, action='store_true', help='Only show total clone count for repos')
    args = parser.parse_args()
    format_type = args.format
    collect_json = args.collect_json
    grabs = args.grabs
    verbose = args.v
    inputted_id = args.sheet_id
    access_token = args.token
    all_data = args.all

    if collect_json:
        jsonfiles = [f for f in listdir('.') if 'data_plugin' in f and f != 'data_plugins_all.json']
        if len(jsonfiles) > 0:
            open('data_plugins_all.json', 'w')
            for json in jsonfiles:
                with open(json, 'r') as f:
                    pass
            sys.exit('Finished combining json files')
        else:
            sys.exit('No data files present')

    if access_token == '':
        sys.exit("No token inputted. Cannot connect to GitHub.")

    #Explicitly grab all iocage-plugin repos from the freenas org
    #Possibly could provide organization name or repo name as args
    g = Github(access_token)
    org = g.get_organization("freenas")
    plugin_repos = [repo for repo in org.get_repos() if 'iocage-plugin' in repo.name]

    if verbose:
        print("Total plugins:", len(plugin_repos))

    #Accept shorter arguments and check for invalid input
    grab_names = [name for name in grabs]
    total_grabs = []
    #Grab options not available in simplified mode
    if all_data:
        for grab in grab_names:
            if grab == 'r' or grab == 'referrers':
                total_grabs.append('referrers')
            elif grab == 'v' or grab == 'views':
                total_grabs.append('views')
            elif grab == 'p' or grab == 'paths':
                total_grabs.append('paths')
            elif grab == 'c' or grab == 'clones':
                total_grabs.append('clones')
            else:
                print(f'Unknown grab function {grab}, skipping')
    if format_type == 's':
        format_type = 'sheets'
    if format_type == 'f':
        format_type = 'file'
    if format_type != 'sheets' and format_type != 'file':
        print(f'Invalid output format {format_type}')

    if format_type=='sheets':
        #R/W scope. Full scope list on Google API docs
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        sheet_id = ''
        #Sheet and range for the spreadsheet. This script uses all of Sheet1
        sheet_range = 'Sheet1'
        sheet = None
        creds = None
        #Loads credentials from the token if the script has ran before
        #Otherwise they are loaded from credentials.json, then a token is created
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', scopes)
                creds = flow.run_local_server()
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('sheets', 'v4', credentials=creds)
        if inputted_id == '':
            #Creates a spreadsheet with the title GitHub Data if no id is given
            title = ''
            if all_data:
                title = 'GitHub Data'
            else:
                title = 'GitHub Total Clones'
            body = {'properties': { 'title': title } }
            sheet = service.spreadsheets().create(body=body, fields='spreadsheetId').execute()
            sheet_id = sheet.get('spreadsheetId')
        else:
            sheet_id = inputted_id
        #Create a header row on the spreadsheet
        if all_data:
            values = [['repo', 'count', 'uniques', 'date', 'name']]
        else:
            values = [['repo', 'count', 'uniques']]
        for repo in plugin_repos:
            #Add the name as a row for each plugin repo
            if all_data:
                values.append([repo.name])
            if verbose:
                print("Traffic data for", repo.name[14:], end=' ')
            if all_data:
                for name in total_grabs:
                    #Generate rows of data from api calls in the get functions
                    value_list = get_dict[name](repo)
                    for value in value_list:
                        values.append(value)
            else:
                values.append(get_simple_clones(repo))
            if verbose:
                print(' ')
                sys.stdout.flush()
        sheet = service.spreadsheets()
        body = { 'values' : values }
        #Send the cell values to the sheet
        sheet.values().update(spreadsheetId=sheet_id, range=sheet_range, valueInputOption='USER_ENTERED', body=body).execute()
        send_request('sort.json', sheet, sheet_id)
        send_request('chart.json', sheet, sheet_id)
    else:
        #Writes json files with the name data_REPO if individual format
        #Otherwise data_plugins for a single file
        f = None
        ts = int(time.time())
        f = open('data_plugins_'+str(ts)+'.json', 'w')
        f.write('{\n')
        for repo in plugin_repos:
            f.write('  \"'+repo.name[14:]+'\" : {\n')
            if verbose:
                print("Traffic data for", repo.name[14:], end=' ')
            if all_data:
                for name in total_grabs:
                    print_dict[name](repo, f)
            else:
                print_simple_clones(repo, f)
            if verbose:
                print(' ')
                sys.stdout.flush()
            f.write('  },\n')
        f.write('  \"time_t\" : '+str(ts)+'\n')
        f.write('}')
        f.close()

if __name__ == "__main__": main()
