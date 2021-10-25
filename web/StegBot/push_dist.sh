#!/usr/bin/env bash

cd dist
git init
git remote add origin git@github.com:qxxxb/StegBot.git
git add .
git commit -m "Initial commit"
git push -fu origin master
