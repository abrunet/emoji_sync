import requests, json, yaml, argparse
from collections import defaultdict

def get_emoji(token):
    r = requests.get('https://slack.com/api/emoji.list?token={0}'.format(token))
    return json.loads(r.text)['emoji']

if __name__ == "__main__":
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
    aliases = defaultdict(list)

    for missing in missing_emoji:
        url = source_emoji[missing]
        if url[:4] == 'http':
            result['emojis'].append({'name': missing, 'src': url})
        elif url[:6] == 'alias:':
            aliases[source_emoji[missing][6:]].append(missing)

    for key, values in aliases.items():
        result['emojis'].append({'name': key, 'aliases': values})

    if result['emojis']:
        with open(args.output, 'w') as outfile:
            yaml.dump(result, outfile, default_flow_style=False)
