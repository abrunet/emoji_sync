import argparse
import json

import requests

from emoji_sync.emoji_sync import request_and_cache_api
from emoji_sync.emoji_sync import emoji_list
from emoji_sync.emoji_sync import SOURCE_EMOJI

def emoji_admin_list(batch_size, token):
    return lambda x: requests.post('https://slack.com/api/emoji.adminList', data={
        'query': '',
        'page': '1',
        'count': str(batch_size),
        'token': token,
    })

def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--api-token",
                           help="API token for the source slack",
                           required=True)
    argparser.add_argument("--target-token",
                           help="API token for the slack workspace which will receive the message")
    argparser.add_argument("--xoxs-token",
                           help="API token scrapped from slack.com/admin/emoji",
                           required=True)
    argparser.add_argument("--channel",
                           help="Channel ID to send the message to",
                           required=True)
    argparser.add_argument("--last-run-file",
                           help="""
                           File where yesterday's emojis are stored,
                           this file will be overwritten with today's emojis""",
                           required=True)

    args = argparser.parse_args()

    args.target_token = args.target_token if args.target_token else args.api_token

    source_emoji = request_and_cache_api(SOURCE_EMOJI, emoji_list(args.api_token))['emoji']

    previous_emoji = {}
    with open(args.last_run_file) as emoji_file:
        old_emoji_data = emoji_file.read()
        if old_emoji_data:
            previous_emoji = json.loads(old_emoji_data)['emoji']

    with open(args.last_run_file, 'w+') as emoji_file:
        emoji_file.write(json.dumps(source_emoji))

    added_emoji = source_emoji.keys() - previous_emoji.keys()
    deleted_emoji = previous_emoji.keys() - source_emoji.keys()

    if not added_emoji and not deleted_emoji:
        exit()

    batch_size = len(source_emoji) + 1
    data = request_and_cache_api('admin_list_cache.json',
                                 emoji_admin_list(batch_size, args.source_token))

    emoji_to_author = {}
    if 'custom_emoji_total_count' not in data or data['custom_emoji_total_count'] > batch_size:
        print("Error retrieving emojis from the adminList API.\n{0}".format(json.dumps(data)))

    if 'emoji' in data:
        emoji_to_author = {emoji['name']: emoji['user_display_name'] for emoji in data['emoji']}

    added = []
    for emoji_name in added_emoji:
        author = emoji_to_author.get(emoji_name)
        author = " added by " + author if author else ""
        added.append(":{0}: `{0}`{1}".format(emoji_name, author))

    removed = [":{0}: `{0}`".format(emoji_name) for emoji_name in deleted_emoji]

    message = "Added:\n" + "\n".join(added) if added else ""
    if removed:
        message += "\n" if message else ""
        message += "Removed:\n" + "\n".join(removed)

    payload = {
        'channel': args.channel,
        'text': 'Emoji Report',
        'attachments': [
            {
                'text': message
            }
        ]
    }

    headers = {
        'Content-type': 'application/json; charset=utf-8',
        'Authorization': 'Bearer ' + args.target_token
    }
    resp = requests.post('https://slack.com/api/chat.postMessage', json=payload, headers=headers)
    print(json.dumps(resp.json(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
