#!/usr/bin/env sh

rm -rf dist
mkdir dist

cd deploy
rsync -avzP . ../dist
cd ..
sed -i '' 's/buckeye{.*}/buckeye{this_is_a_fake_flag}/g' dist/flag.txt

cp -r bins/ dist/bins/

mv dist dist-guess-god
cp -r bins/ dist-guess-god/bins/
zip -r dist.zip dist-guess-god/
rm -rf dist-guess-god
mkdir dist
mv dist.zip dist/guess-god.zip
