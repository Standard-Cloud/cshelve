FROM mcr.microsoft.com/devcontainers/python:3.9

# Install uv
RUN pip install uv

# Create the build directory
RUN mkdir -p /build/package && chown vscode:vscode /build/package

# Brutally install the Azure CLI
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash

USER vscode

# Copy the project files then build the virtual environment
COPY --chown=vscode:vscode pyproject.toml uv.lock /build/package
RUN cd /build/package && uv venv --python 3.9 && uv sync --dev

# Copy the project files to the workspace
COPY . /workspaces/package
WORKDIR /workspaces/package
