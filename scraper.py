#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import requests
import urllib.request
import os
import re
import time
from bs4 import BeautifulSoup
from sys import exit

BASE_FORUM_THREAD_URL = "https://madronalabs.com/topics/357-sticky-aalto-patch-thread" 
PATCH_REGEX = re.compile("&lt[;]Aalto.*\/&gt", re.DOTALL)

# Sanity threshold for page fetching
PAGE_INDEX_THRESHOLD = 300

# TODO(teddywilson) scrape other patch types
def scrape_html_patches():
    html_patches = []
    page_index = 1

    while True and page_index < PAGE_INDEX_THRESHOLD:
        url = BASE_FORUM_THREAD_URL + "?page=%d" % page_index
        page_index += 1

        response = requests.get(url)
        if response.status_code != 200:
            return html_patches

        soup = BeautifulSoup(response.text, "html.parser")
        forum_posts = soup.find_all("div", class_="forum-post")

        # Take into account the sticky post
        if len(forum_posts) < 1:
            return html_patches

        for forum_post in forum_posts:
            result = re.findall(PATCH_REGEX, str(forum_post))
            for match in result:
                html_patches.append(match)

    return html_patches

def sanitize_html_patch(html_patch):
    if not html_patch.startswith('&lt;Aalto'):
        print('Found html_patch with invalid prefix: %s' % html_patch)
        exit(1)
    if not html_patch.endswith('/&gt'):
        print('Found html_patch with invalid suffix: %s' % html_patch)
        exit(1)
    return "<" + html_patch[4:-3] + ">"

def write_patches_to_output_dir(html_patches, output_dir):
    for idx, html_patch in enumerate(html_patches):
        filename = 'html_patch_%d' % idx
        f = open(os.path.join(output_dir, filename), "w")
        f.write(sanitize_html_patch(html_patch))
        f.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--output_dir', required=True)
    args = parser.parse_args()

    # Create the output directory if it doesn't already exist
    if not os.path.exists(args.output_dir):
        print('Creating directory %s' % args.output_dir)
        os.makedirs(args.output_dir)

    html_patches = scrape_html_patches()
    write_patches_to_output_dir(html_patches, args.output_dir)
