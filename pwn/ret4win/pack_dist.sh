#!/usr/bin/env sh

rm -rf dist
mkdir dist

cd deploy
sudo docker-compose up --build -d
docker cp deploy_app_1:/home/ctf/app/chall .
sudo docker-compose down
rsync -avzP . ../dist --exclude=".gdb_history" --exclude='core'
cd ..
sed -i 's/buckeye{.*}/buckeye{this_is_a_fake_flag}/g' dist/flag.txt

cd dist
zip -r dist.zip .
mv dist.zip ..
cd ..
rm -rf dist
mkdir dist
name=${PWD##*/}
mv dist.zip dist/$name.zip
