# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster AS base
RUN  apt update && apt install -y git
RUN  python -m pip install --upgrade git+https://github.com/vmware/vsphere-automation-sdk-python.git

FROM python:3.8-slim-buster AS release
WORKDIR /app
COPY --from=base /usr/local/lib/python3.8/site-packages/ /usr/local/lib/python3.8/site-packages
RUN  python -m pip install requests
RUN  python -m pip install --upgrade pip setuptools==60.10.0
COPY FolderOps/config.ini /app/
COPY FolderOps/folderOps.py /app/
COPY TagOps/tagops.py /app/
