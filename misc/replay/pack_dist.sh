#!/usr/bin/env sh

rm -rf out
mkdir out

cd deploy
rsync -avzP . ../out --exclude=".gdb_history" --exclude='core'
cd ..

cd out
zip -r out.zip .
mv out.zip ..
cd ..
rm -rf out
mkdir out
name=${PWD##*/}
mv out.zip out/$name.zip
