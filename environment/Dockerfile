# hash:sha256:95ae120364f3902c9427a3106b17da9b56c2deaf2c2de0304f4fc25da1e482cb
ARG REGISTRY_HOST
FROM $REGISTRY_HOST/codeocean/py-r:python3.12.4-R4.3.3-JupyterLab4.2.4-RStudiorstudio-server-2024.04.2-764-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive

ARG GIT_ASKPASS
ARG GIT_ACCESS_TOKEN
COPY git-askpass /

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        fzf \
        libdbus-1-3=1.12.20-2ubuntu4.1 \
        libegl1=1.4.0-1 \
        libxcb-icccm4=0.4.1-1.1build2 \
        libxcb-image0=0.4.0-2 \
        libxcb-keysyms1=0.4.0-1build3 \
        libxcb-randr0=1.14-3ubuntu3 \
        libxcb-render-util0=0.3.9-1build3 \
        libxcb-xfixes0=1.14-3ubuntu3 \
        libxcb-xinerama0=1.14-3ubuntu3 \
        libxcb-xinput0=1.14-3ubuntu3 \
        libxkbcommon-x11-0=1.4.0-1 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install -U --no-cache-dir \
    geojson==3.1.0 \
    rioxarray==0.18.1 \
    sopa==1.1.6

COPY postInstall /
RUN /postInstall
