#!/bin/python

import datetime
import argparse
import sys
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from github import Github

def get_referrers(repo):
    referrers = repo.get_top_referrers()
    values = []
    for referrer in referrers:
        value = [referrer.count, referrer.uniques, referrer.referrer]
        values.append(value)
    print(values)
    return values

def print_referrers(repo, f):
    referrers = repo.get_top_referrers()
    f.write(f'Number of top referrers: {len(referrers)}\n')
    for referrer in referrers:
        f.write(f'{referrer.count} views, {referrer.uniques}, unique views from {referrer.referrer}\n')
    f.write('\n')

def get_paths(repo):
    paths = repo.get_top_paths()
    values = []
    for path in paths:
        value = [path.count, path.uniques, path.path]
        values.append(value)
    print(values)
    return values

def print_paths(repo, f):
    paths = repo.get_top_paths()
    f.write(f'Number of top paths: {len(paths)}\n')
    for path in paths:
        f.write(f'{path.count} views, {path.uniques}, unique views in {path.path}\n')
    f.write('\n')

def get_views(repo):
    daily_views = repo.get_views_traffic()
    weekly_views = repo.get_views_traffic(per="week")
    total_views = daily_views['count']
    total_unique_views = daily_views['uniques']
    values = []
    values.append([total_views, total_unique_views])
    for view in daily_views['views']:
        formatted_time = view.timestamp.strftime("%m/%d/%y")
        values.append([view.count, formatted_time])
    for view in weekly_views['views']:
        week_start = view.timestamp
        week_end = week_start + datetime.timedelta(days=7)
        formatted_start = week_start.strftime("%m/%d/%y")
        formatted_end = week_end.strftime("%m/%d/%y")
        values.append([view.count, formatted_start + '-' + formatted_end])
    return values

def print_views(repo, f):
    daily_views = repo.get_views_traffic()
    weekly_views = repo.get_views_traffic(per="week")
    total_views = daily_views['count']
    total_unique_views = daily_views['uniques']
    f.write(f'Total Views: {total_views}\n')
    f.write(f'Total Unique Views: {total_unique_views}\n')
    for view in daily_views['views']:
        formatted_time = view.timestamp.strftime("%m/%d/%y")
        f.write(f'{view.count} views on {formatted_time}\n')
    for view in weekly_views['views']:
        week_start = view.timestamp
        week_end = week_start + datetime.timedelta(days=7)
        formatted_start = week_start.strftime("%m/%d/%y")
        formatted_end = week_end.strftime("%m/%d/%y")
        f.write(f'{view.count} views on {formatted_start} to {formatted_end}\n')
    f.write('\n')

def get_clones(repo):
    clones = repo.get_clones_traffic()
    total_count = clones['count']
    values = []
    values.append([total_count])
    for clone in clones['clones']:
        formatted_time = clone.timestamp.strftime("%m/%d/%y")
        values.append[clone.count, clone.uniques, formatted_time]
    return values

def print_clones(repo, f):
    clones = repo.get_clones_traffic()
    total_count = clones['count']
    f.write(f'Total clones: {total_count}\n')
    for clone in clones['clones']:
        formatted_time = clone.timestamp.strftime("%m/%d/%y")
        f.write(f'Total clones: {clone.count}, Unique clones: {clone.uniques}, on {formatted_time}\n')
    f.write('\n')

def main():
    parser = argparse.ArgumentParser(description='Retrieve traffice data from iocage plugin repos on Github')
    parser.add_argument('-file', default=True, action='store_true', help='Write to file')
    parser.add_argument('-sheets', default=False, action='store_true', help='Write to Google Sheets (requires credentials.json)')
    parser.add_argument('-i', default=False, action='store_true', help='Create individual files')
    parser.add_argument('-s', default=True, action='store_true', help='Create a single file (default)')
    parser.add_argument('-r', default=True, action='store_true', help='Only get referrers')
    parser.add_argument('-v', default=True, action='store_true', help='Only get views')
    parser.add_argument('-p', default=True, action='store_true', help='Only get paths')
    parser.add_argument('-c', default=True, action='store_true', help='Only get clones')
    parser.add_argument('-verbose', default=False, action='store_true', help='Verbose mode')
    args = parser.parse_args()
    write_file = args.file
    write_sheets = args.sheets
    individual = args.i
    single = args.s
    only_referrers = args.r
    only_views = args.v
    only_paths = args.p
    only_clones = args.c
    verbose = args.verbose

    #Put access token in here
    g = Github("")
    org = g.get_organization("freenas")
    plugin_repos = [repo for repo in org.get_repos() if 'iocage-plugin' in repo.name]

    if verbose:
        print("Total plugins:", len(plugin_repos))

    if write_sheets:
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        #Put the ID of the spreasheet to write to here
        sheet_id = ''
        sheet_range = 'Sheet1'
        creds = None
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
        sheet = service.spreadsheets()
        for repo in plugin_repos:
            if verbose:
                print("Traffic data for", repo.name, end=' ')
            values = get_referrers(repo)
            values.append(get_paths(repo))
            values.append(get_views(repo))
            values.append(get_clones(repo))
            if verbose:
                print(' ')
        body = { 'values' : values } 
        result = sheet.values().update(spreadsheetId=sheet_id, range=sheet_range, valueInputOption='USER_ENTERED', body=body).execute()
    elif write_file:
        f = None
        if single:
            f = open('data_plugins', 'w')
        for repo in plugin_repos:
            if individual:
                f = open('data_'+repo.name, 'w')
            elif single:
                f.write(repo.name+'\n\n')
            if verbose:
                print("Traffic data for", repo.name, end=' ')
            if only_referrers:
                print_referrers(repo, f)
            if only_paths:
                print_paths(repo, f)
            if only_views:
                print_views(repo, f)
            if only_clones:
                print_clones(repo, f)
            if verbose:
                print(' ')
                sys.stdout.flush()
            if individual:
                f.close()
        if single:
            f.close()

if __name__ == "__main__": main()
