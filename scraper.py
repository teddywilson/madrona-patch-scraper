#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import json
import os
import re
import requests
import time
import urllib.request
from bs4 import BeautifulSoup
from sys import exit

BASE_FORUM_THREAD_URL = "https://madronalabs.com/topics/357-sticky-aalto-patch-thread" 

HTML_PATCH_REGEX = re.compile("&lt[;]Aalto.*\/&gt", re.DOTALL)
HTML_PRESET_NAME_REGEX = re.compile('presetName=\\"[^\\"]*\\"')
JSON_PATCH_REGEX = re.compile('{.*}', re.DOTALL)

# Sanity threshold for page fetching
PAGE_INDEX_THRESHOLD = 300

def fail(message):
    print(message)
    exit(1)


def scrape_patches():
    html_patches = []
    json_patches = []

    page_index = 1
    while True and page_index < PAGE_INDEX_THRESHOLD:
        url = BASE_FORUM_THREAD_URL + "?page=%d" % page_index
        page_index += 1

        response = requests.get(url)
        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.text, "html.parser")
        forum_posts = soup.find_all("div", class_="forum-post")

        # Take into account the sticky post
        if len(forum_posts) <= 1:
            break

        for forum_post in forum_posts:
            html_result = re.findall(HTML_PATCH_REGEX, str(forum_post))
            for html_match in html_result:
                html_patches.append(html_match)

            json_result = re.findall(JSON_PATCH_REGEX, str(forum_post))
            for json_match in json_result:
                json_patches.append(json_match)

    return html_patches, json_patches


def sanitize_html_preset_name(html_preset_name):
    if not html_preset_name.startswith('presetName="'):
        fail('Found html preset name with invalid prefix: %s' % html_preset_name)
    if not html_preset_name.endswith('"'):
        fail('Found html preset name with invalid suffix: %s' % html_preset_name)
    return html_preset_name[12:-1].replace('/', '_')


def sanitize_html_patch(html_patch):
    if not html_patch.startswith('&lt;Aalto'):
        fail('Found html patch with invalid prefix: %s' % html_patch)
    if not html_patch.endswith('/&gt'):
        fail('Found html patch with invalid suffix: %s' % html_patch)
    return "<" + html_patch[4:-3] + ">"


def sanitize_json_preset_name(json_preset_name):
    return json_preset_name.replace('/', '_')


def sanitize_json_patch(json_patch):
    return json_patch.replace('<br/>', '')


def write_patches_to_output_dir(html_patches, json_patches, output_dir):
    for html_patch in html_patches:
        preset_name = re.search(HTML_PRESET_NAME_REGEX, html_patch)
        if preset_name is None:
            fail('Could not parse html preset name: %s' % match)
        f = open(os.path.join(output_dir, sanitize_html_preset_name(preset_name.group())), "w")
        f.write(sanitize_html_patch(html_patch))
        f.close()

    for json_patch_str in json_patches:
        json_patch = json.loads(sanitize_json_patch(json_patch_str))
        f = open(os.path.join(output_dir, sanitize_json_preset_name(json_patch['preset'])), "w")
        f.write(json.dumps(json_patch))
        f.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--output_dir', required=True)
    args = parser.parse_args()

    # Create the output directory if it doesn't already exist
    if not os.path.exists(args.output_dir):
        print('Creating directory %s' % args.output_dir)
        os.makedirs(args.output_dir)

    html_patches, json_patches  = scrape_patches()
    write_patches_to_output_dir(html_patches, json_patches, args.output_dir)
