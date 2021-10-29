#!/usr/bin/env sh

name="piss"

rm -rf dist
mkdir dist

cd deploy
rsync -avzP . ../dist
cd ..
sed -i  '' 's/buckeye{.*}/buckeye{this_is_a_fake_flag}/g' dist/flag[12].txt

mv dist dist-$name
zip -r dist.zip dist-$name/
rm -rf dist-$name/
mkdir dist
mv dist.zip dist/dist-$name.zip
