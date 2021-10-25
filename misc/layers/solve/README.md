```
$ docker pull qxxxb/layers
$ dooker run -it qxxxb/layers
/ # id
uid=0(root) gid=0(root) groups=0(root),1(bin),2(daemon),3(sys),4(adm),6(disk),10(wheel),11(floppy),20(dialout),26(tape),27(video)
/ # ls
Dockerfile   dev          home         media        mnt          proc         run          srv          tmp          var
bin          etc          lib          message.txt  opt          root         sbin         sys          usr
/ # cat Dockerfile
FROM alpine:latest
COPY flag.png Dockerfile /
RUN rm flag.png
RUN echo "Sorry, the flag has been deleted :(" > /message.txt
/ # exit
$ docker save qxxxb/layers > layers.tar
```

Then you can find `flag.png` in one of the layers
