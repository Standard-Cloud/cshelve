FROM debian:bookworm

ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Install dependencies
RUN apt-get update \
    && apt-get install -y python3-pip git nodejs npm \
    && pip3 install uv pre-commit --break-system-packages

# Create the vscode user and group
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID --shell /bin/bash --create-home $USERNAME

# Create the build directory with needed subfolders
RUN mkdir -p /build/package && chown -R $USERNAME:$USERNAME /build

# Brutally install the Azure CLI
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash

USER $USERNAME

# Create the virtual environment
RUN uv venv --python 3.9 /build/package/venv
