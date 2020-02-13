import argparse
import json
import os
import time

import requests
import yaml

SOURCE_EMOJI = 'source_emoji_cache.json'

def request_and_cache_api(file_name, api_request, time_delta=(60 * 2)):
    if os.path.exists(file_name) and time.time() - os.path.getmtime(file_name) < time_delta:
        with open(file_name) as cached_result:
            cached_data = cached_result.read()
            if cached_data:
                print("Reusing cached response from '{0}'.".format(file_name))
                return json.loads(cached_data)
            else:
                print("Found no data in '{0}'.".format(file_name))

    print("Loading data from API call.")
    request_result = api_request()
    # TODO: check that the result is ok before overwriting the cache file
    with open(file_name, 'w+') as cached_result:
        cached_result.write(request_result.text)

    print("API response saved to cache '{0}'.".format(file_name))
    return json.loads(request_result.text)

def emoji_list(token):
    def inner_func():
        print("Calling emoji list API")
        return requests.get('https://slack.com/api/emoji.list?token={0}'.format(token))

    return inner_func

def get_emoji(token):
    return json.loads(emoji_list(token)().text)['emoji']

def get_url(emoji_name, emoji_to_url):
    if emoji_name in emoji_to_url:
        url = emoji_to_url[emoji_name]
        if url[:4] == 'http':
            return url
        if url[:6] == 'alias:':
            return get_url(url[6:], emoji_to_url)
    return None

def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--source-token", help="API token for the source slack", required=True)
    argparser.add_argument("--target-token", help="API token for the target slack", required=True)
    argparser.add_argument("--blacklist", help="Path to blacklist file", default=None)
    argparser.add_argument("--output", help="YAML file to use for output", default="sync.yml")
    args = argparser.parse_args()

    # don't bother trying to sync these problematic ones
    blacklist = set()
    if args.blacklist:
        with open(args.blacklist) as blacklist_file:
            blacklist.update(blacklist_file.read().splitlines())

    source_emoji = request_and_cache_api(SOURCE_EMOJI, emoji_list(args.source_token))['emoji']
    target_emoji = get_emoji(args.target_token)

    missing_emoji = source_emoji.keys() - target_emoji.keys() - blacklist

    # create a yaml file compatible with emojipacks
    result = {
        'title': 'Emoji sync',
        'emojis': []
    }

    for missing in missing_emoji:
        url = get_url(missing, source_emoji)
        if url:
            result['emojis'].append({'name': missing, 'src': url})
        else:
            mapping = source_emoji[missing] if missing in source_emoji else ""
            print("'{0}' can't be synched, consider adding it to the blacklist. [{1}]".format(
                missing, mapping))

    if result['emojis']:
        with open(args.output, 'w') as outfile:
            yaml.dump(result, outfile, default_flow_style=False)


if __name__ == "__main__":
    main()
