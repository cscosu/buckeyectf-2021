#!/usr/bin/env sh

name="sozu"
rm -rf dist
mkdir dist

cd deploy
rsync -avzP . ../dist --exclude=".env"
cd ..

mv dist dist-$name
zip -r dist.zip dist-$name/
rm -rf dist-$name
mkdir dist
mv dist.zip dist/$name.zip
