#!/bin/bash

WORK_DIR=
VIRTUAL_ENV_DIR=
SOURCE_TOKEN=
TARGET_TOKEN=
BLACKLIST_PATH=
WORKSPACE_NAME=
UPLOAD_ACCOUNT_EMAIL=
UPLOAD_ACCOUNT_PASSWORD=

cd $WORK_DIR
source $VIRTUAL_ENV_DIR/bin/activate
emoji-sync "$SOURCE_TOKEN" "$TARGET_TOKEN" --blacklist "$BLACKLIST_PATH"

sync_file=sync.yml
if [ -e $sync_file ]; then
    date >> emoji_sync.log
    node_modules/emojipacks/bin/emojipacks -s $WORKSPACE_NAME -e $UPLOAD_ACCOUNT_EMAIL -p '$UPLOAD_ACCOUNT_PASSWORD' -y $sync_file >> emoji_sync.log 2>&1
    rm $sync_file
fi
