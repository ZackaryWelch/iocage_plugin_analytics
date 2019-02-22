#!/bin/python

import datetime
import argparse
import sys
from github import Github

def print_referrers(repo, f):
    referrers = repo.get_top_referrers()
    f.write(f'Number of top referrers: {len(referrers)}\n')
    for referrer in referrers:
        f.write(f'{referrer.count} views, {referrer.uniques}, unique views from {referrer.referrer}\n')
    f.write('\n')

def print_paths(repo, f):
    paths = repo.get_top_paths()
    f.write(f'Number of top paths: {len(paths)}\n')
    for path in paths:
        f.write(f'{path.count} views, {path.uniques}, unique views in {path.path}\n')
    f.write('\n')

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
    parser.add_argument('-i', default=False, action='store_true', help='Create individual files')
    parser.add_argument('-s', default=False, action='store_true', help='Create a single file')
    parser.add_argument('-r', default=True, action='store_true', help='Only get referrers')
    parser.add_argument('-v', default=True, action='store_true', help='Only get views')
    parser.add_argument('-p', default=True, action='store_true', help='Only get paths')
    parser.add_argument('-c', default=True, action='store_true', help='Only get clones')
    args = parser.parse_args()
    individual = args.i
    single = args.s
    only_referrers = args.r
    only_views = args.v
    only_paths = args.p
    only_clones = args.c
    if not individual and not single:
        sys.exit('Specifiy individual (-i) or single (-s) for file output')
    #Put access token in here
    g = Github("")
    org = g.get_organization("freenas")
    plugin_repos = [repo for repo in org.get_repos() if 'iocage-plugin' in repo.name]
    print("Total plugins:", len(plugin_repos))
    if single:
        f = open('data_plugins', 'w')
    for repo in plugin_repos:
        if individual:
            f = open('data_'+repo.name, 'w')
        elif single:
            f.write(repo.name+'\n\n')
        print("Traffic data for", repo.name, end=' ')
        if only_referrers:
            print_referrers(repo, f)
        if only_paths:
            print_paths(repo, f)
        if only_views:
            print_views(repo, f)
        if only_clones:
            print_clones(repo, f)
        print(' ')
        if individual:
            f.close()
        sys.stdout.flush()
    if single:
        f.close()

if __name__ == "__main__": main()
