import sys, requests, json, argparse
from dateutil.parser import parse
from collections import defaultdict
from datetime import datetime

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--token", help="API token", required=True)
    argparser.add_argument("--channel", help="Channel ID to send the message to", required=True)
    argparser.add_argument("--logfile", help="Log file to parse", default="emoji_sync.log")
    args = argparser.parse_args()

    results = defaultdict(set)
    parsed_date = None

    with open(args.logfile) as f:
        for line in f:
            line = line.strip()
            if (line.startswith(('Mon ', 'Tue ', 'Wed ', 'Thu ', 'Fri ', 'Sat ', 'Sun '))):
                parsed_date = parse(line.split(" - ")[0]).date()
            elif (line.startswith("Uploaded emojis:")):
                for uploaded_emoji in line.split():
                    if uploaded_emoji[0] == ':' and uploaded_emoji[-1] == ':':
                        results[parsed_date].add(uploaded_emoji)

    today = datetime.now().date()
    if today in results and results[today]:
        payload = {
            'channel': args.channel,
            'text': 'New emoji today' if len(results[today]) == 1 else 'New emojis today',
            'attachments': [
                {
                    'text': ' '.join(results[today])
                }
            ]
        }

        headers = {
            'Content-type': 'application/json; charset=utf-8',
            'Authorization': 'Bearer ' + args.token
        }
        r = requests.post('https://slack.com/api/chat.postMessage', json=payload, headers=headers);
        print(json.dumps(r.json(), indent=2, sort_keys=True))
