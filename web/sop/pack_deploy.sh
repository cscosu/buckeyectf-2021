#!/usr/bin/env sh

rm -rf out
mkdir out

cd deploy
rsync -avzP . ../out --exclude="node_modules"
cd ..
# sed -i 's/buckeye{.*}/buckeye{this_is_a_fake_flag}/g' out/app/flag.txt

cd out
zip -r out.zip .
mv out.zip ..
cd ..
rm -rf out
mkdir out
name=${PWD##*/}
mv out.zip out/$name.zip
