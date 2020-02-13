import argparse
import json
import os

import requests

def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--api-token",
                           help="API token for the source slack",
                           required=True)
    argparser.add_argument("--target-token",
                           help="API token for the slack workspace which will receive the message")
    argparser.add_argument("--channel",
                           help="Channel ID to send the message to",
                           required=True)
    argparser.add_argument("--last-run-file",
                           help="File where the last user list was saved.",
                           required=True)

    args = argparser.parse_args()

    args.target_token = args.target_token if args.target_token else args.api_token

    source_users_resp = requests.get(
        'https://slack.com/api/users.list?token={0}'.format(args.api_token))
    source_users = json.loads(source_users_resp.text)["members"]

    previous_users = {}
    if os.path.exists(args.last_run_file):
        with open(args.last_run_file) as users_file:
            old_users_data = users_file.read()
            if old_users_data:
                previous_users = json.loads(old_users_data)["members"]

    with open(args.last_run_file, 'w+') as emoji_file:
        emoji_file.write(source_users_resp.text)

    deleted_users_now = {user["id"]:user for user in source_users if user["deleted"]}
    previous_deleted_users = {user["id"]:user for user in previous_users if user["deleted"]}

    deleted_users = deleted_users_now.keys() - previous_deleted_users.keys()

    if not deleted_users:
        exit()

    section_count = 1
    user_string = ' is' if len(deleted_users) == 1 else 's are'
    payload = {
        'channel': args.channel,
        'text': 'The following user' + user_string + ' now inactive.',
        'attachments': [
            {
                'blocks': []
            }
        ]
    }

    blocks = payload['attachments'][0]['blocks']
    for idx, user_id in enumerate(deleted_users):
        profile = deleted_users_now[user_id]['profile']
        blocks += [{'type':'divider'}] if idx != 0 else []
        blocks += [
            {
                'type': 'section',
                'block_id': 'section' + str(section_count),
                'text': {
                    'type': 'mrkdwn',
                    'text':  profile['real_name_normalized'] +
                             ' (@' + deleted_users_now[user_id]['name'] + ')'
                },
                'accessory': {
                    'type': 'image',
                    'image_url': profile['image_192'],
                    'alt_text': 'Profile Picture'
                }
            }
        ]
        section_count += 1

    headers = {
        'Content-type': 'application/json; charset=utf-8',
        'Authorization': 'Bearer ' + args.target_token
    }
    resp = requests.post('https://slack.com/api/chat.postMessage', json=payload, headers=headers)
    print(json.dumps(resp.json(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
