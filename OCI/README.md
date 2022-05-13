# Dockerfiles

## Base defender image
The Dockerfile in `base` is intended to be the base image used for all of the other bases. Build it as follows:
```
$ cd OCI/base
$ docker build -t defender-base .
```