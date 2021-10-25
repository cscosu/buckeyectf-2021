#!/usr/bin/env sh

rm -rf out
mkdir out

cd deploy
rsync -avzP . ../out --exclude="__pycache__" --exclude="node_modules" --exclude="env"
cd ..

cd out
zip -r out.zip .
mv out.zip ..
cd ..
rm -rf out
mkdir out
name=${PWD##*/}
mv out.zip out/$name.zip
