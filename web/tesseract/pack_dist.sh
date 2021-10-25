#!/usr/bin/env sh

name=${PWD##*/}
rm -rf dist
mkdir dist

cd deploy
rsync -avzP . ../dist --exclude=".env"
cd ..
sed -i '' 's/buckeye{.*}/buckeye{this_is_a_fake_flag}/g' dist/flag.txt

mv dist dist-$name
zip -r dist.zip dist-$name/
rm -rf dist-$name
mkdir dist
mv dist.zip dist/$name.zip
