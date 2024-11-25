#!/bin/bash

echo "Waiting 2 minutes for the posts to get gotten..."
sleep 120

while true; do
  echo "Notifying Users..."
  python notifier.py
  sleep 120
done