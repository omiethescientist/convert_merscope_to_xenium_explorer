# hash:sha256:ff395cfd3396c3c8dc2e387d8bc6410f266c9490344820d4888f44bb1a535c6c
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/py-r:python3.12.4-R4.3.3-JupyterLab4.2.4-RStudiorstudio-server-2024.04.2-764-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive

ARG GIT_ASKPASS
ARG GIT_ACCESS_TOKEN
COPY git-askpass /

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        fzf=0.29.0-1ubuntu0.1 \
        wget=1.21.2-2ubuntu1.1 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install -U --no-cache-dir \
    geojson==3.1.0 \
    rioxarray==0.18.1 \
    ruff==0.8.5 \
    sopa==1.1.6

COPY postInstall /
RUN /postInstall
