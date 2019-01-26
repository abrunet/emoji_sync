import argparse
import json

import requests
import yaml

def get_emoji(token):
    r = requests.get('https://slack.com/api/emoji.list?token={0}'.format(token))
    return json.loads(r.text)['emoji']

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

    source_emoji = get_emoji(args.source_token)
    target_emoji = get_emoji(args.target_token)

    # don't bother trying to sync these problematic ones
    blacklist = set()
    if args.blacklist:
        with open(args.blacklist) as blacklist_file:
            blacklist.update(blacklist_file.read().splitlines())

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
