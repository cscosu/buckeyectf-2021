#!/usr/bin/env sh

rm -rf dist
mkdir dist

cd deploy
rsync -avzP . ../dist --exclude="node_modules" --exclude=".env"
cd ..

cd dist
zip -r dist.zip .
mv dist.zip ..
cd ..
rm -rf dist
mkdir dist
name=${PWD##*/}
mv dist.zip dist/$name.zip
