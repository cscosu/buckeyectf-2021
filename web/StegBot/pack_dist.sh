#!/usr/bin/env sh

rm -rf dist
mkdir dist

cd deploy
rsync -avzP . ../dist --exclude='node_modules' --exclude='dist' --exclude=".env" --exclude="app.log"
cd ..
