#!/bin/bash

echo "Waiting 5 minutes for the posts to get gotten..."
sleep 300

while true; do
  echo "Notifying Users..."
  python notifier.py
  sleep 120
done