#!/usr/bin/env bash

set -e

echo ""
echo "=========================================="
echo "   GHOSTHEART DEPLOY HELPER"
echo "=========================================="
echo ""

if [ ! -d ".git" ]; then
  echo "This folder is not a Git repo yet."
  echo "Run these first:"
  echo ""
  echo "git init"
  echo "git branch -M main"
  echo "git remote add origin YOUR_GITHUB_REPO_URL"
  echo ""
  exit 1
fi

git add .
git commit -m "Update GhostHeart website"
git push origin main

echo ""
echo "Deploy push complete."
echo "Now enable GitHub Pages in your repo settings."
echo ""
