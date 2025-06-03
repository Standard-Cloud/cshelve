FROM debian:bookworm

ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID
ARG USER_GID=$USER_UID
ARG VCPKG_VERSION=2025.04.09

# Install dependencies
RUN apt-get update \
    && apt-get install -y python3-pip git nodejs npm cmake g++ ninja-build curl \
    && pip3 install uv pre-commit --break-system-packages

# Create the vscode user and group
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID --shell /bin/bash --create-home $USERNAME

# Create the build directory with needed subfolders
RUN mkdir -p /build/{package, vcpkg} && chown -R $USERNAME:$USERNAME /build

# Brutally install the Azure CLI
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash
RUN apt install -y libcurl4-openssl-dev
USER $USERNAME

# Install vcpkg
RUN git clone --branch $VCPKG_VERSION --depth 1 https://github.com/microsoft/vcpkg.git /build/vcpkg

# Create the virtual environment
RUN uv venv --python 3.9 /build/package/venv

USER root
RUN apt install -y zip pkg-config linux-libc-dev
USER $USERNAME
