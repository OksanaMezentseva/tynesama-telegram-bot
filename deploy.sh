#!/bin/bash

# Path to your SSH private key
KEY_PATH=~/Documents/aws/tynesama-key.pem

# Remote server credentials
REMOTE_USER=ubuntu
REMOTE_IP=56.228.30.8

# Remote path on the EC2 instance
REMOTE_DIR=/home/ubuntu/tynesama-telegram-bot

# Local project directory path
LOCAL_PROJECT_DIR=~/VSCode_Projects/tynesama-telegram-bot

# Sync files using rsync and exclude unnecessary ones
rsync -avz -e "ssh -i $KEY_PATH" \
  --exclude 'venv' \
  --exclude '.env' \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  --exclude '.git' \
  --exclude '.gitignore' \
  --exclude 'deploy.sh' \
  --exclude 'bot_local.py' \
  --exclude '.DS_Store' \
  --exclude '*.log' \
  $LOCAL_PROJECT_DIR/ $REMOTE_USER@$REMOTE_IP:$REMOTE_DIR

# 3. Copy .env file separately (it’s in .gitignore and not copied by rsync)
scp -i $KEY_PATH $LOCAL_PROJECT_DIR/.env $REMOTE_USER@$REMOTE_IP:$REMOTE_DIR/.env

echo "✅ Project deployed successfully!"
