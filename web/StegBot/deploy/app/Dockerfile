FROM ubuntu:20.04 AS nsjail

# Install nsjail

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get -y update && apt-get install -y \
autoconf \
bison \
flex \
gcc \
g++ \
git \
libprotobuf-dev \
libnl-route-3-dev \
libtool \
make \
pkg-config \
protobuf-compiler \
uidmap

RUN git clone https://github.com/google/nsjail --branch 3.0 && \
cd nsjail && \
make -j8 && \
mv nsjail /bin && \
cd / && \
rm -rf nsjail

FROM node:16.11.1-buster-slim AS build
WORKDIR /app

COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile && yarn cache clean

COPY app.ts package.json tsconfig.json yarn.lock ./
RUN yarn build

FROM node:16.11.1-buster-slim AS run

COPY --from=nsjail /usr/bin/nsjail /usr/bin/

RUN apt-get update && \
apt-get install -y libprotobuf17 libnl-route-3-200 && \
rm -rf /var/lib/apt/lists/*

RUN useradd -m ctf && \
mkdir /chroot/ && \
chown root:ctf /chroot && \
chmod 770 /chroot

RUN apt-get update && \
apt-get install -y curl steghide libjpeg62 libmcrypt4 libmhash2 zlib1g && \
rm -rf /var/lib/apt/lists/*

WORKDIR /home/ctf/app
COPY --from=build /app/yarn.lock /app/package.json ./

ENV NODE_ENV production
RUN yarn install --prod --frozen-lockfile && yarn cache clean

COPY --from=build /app/dist ./dist
COPY bof.jpg ./

COPY jail.cfg /

RUN chown -R ctf:ctf .
USER ctf

ENTRYPOINT ["nsjail", "--config", "/jail.cfg", "--"]
CMD ["/usr/local/bin/node", "/app/dist/app.js"]
