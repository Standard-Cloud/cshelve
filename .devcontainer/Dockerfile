FROM debian:bookworm

ARG NODE_VERSION=20
ARG USER_UID=1000
ARG USER_GID=$USER_UID
ARG USERNAME=vscode

# Install dependencies
RUN apt-get update \
    && apt-get install -y python3-pip git curl \
    && pip3 install uv pre-commit --break-system-packages

# Create the vscode user and group
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID --shell /bin/bash --create-home $USERNAME

# Create the build directory with needed subfolders
RUN mkdir -p /build/package && chown -R $USERNAME:$USERNAME /build

# Brutally install the Azure CLI
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash

USER $USERNAME

#region Install Node.js
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
ENV NVM_DIR=/home/$USERNAME/.nvm
RUN bash -c "source $NVM_DIR/nvm.sh && nvm install $NODE_VERSION"
#endregion

# Create the virtual environment
RUN uv venv --python 3.9 /build/package/venv

# Update git config
RUN git config --global push.autoSetupRemote true
