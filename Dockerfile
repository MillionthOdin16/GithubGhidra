FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV GHIDRA_VERSION=11.0.3
ENV GHIDRA_SHA=4434dc6990a84c7e5e9a65a523b4e98c8b5b5c17
ENV GHIDRA_URL=https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_${GHIDRA_VERSION}_build/ghidra_${GHIDRA_VERSION}_PUBLIC_20240410.zip

# Install system dependencies
RUN apt-get update && apt-get install -y \
    openjdk-17-jdk \
    python3 \
    python3-pip \
    wget \
    unzip \
    curl \
    git \
    file \
    aapt \
    zipalign \
    && rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

# Download and install Ghidra
WORKDIR /opt
RUN wget -O ghidra.zip ${GHIDRA_URL} && \
    unzip ghidra.zip && \
    rm ghidra.zip && \
    mv ghidra_${GHIDRA_VERSION}_PUBLIC /opt/ghidra

# Set Ghidra environment
ENV GHIDRA_INSTALL_DIR=/opt/ghidra
ENV PATH="${GHIDRA_INSTALL_DIR}/support:${PATH}"

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir -r /app/requirements.txt

# Copy application files
COPY . /app
WORKDIR /app

# Create directories for analysis
RUN mkdir -p /app/workspace /app/projects /app/tmp

# Expose MCP server port
EXPOSE 8000

# Run the MCP server
CMD ["python3", "mcp_server.py"]