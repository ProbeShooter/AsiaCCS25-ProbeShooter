FROM python:3.13.1-slim

# Metadata
LABEL authors="Daehyeon Bae <dh_bae@korea.ac.kr>"
LABEL description="ProbeShooter artifacts (ASIA CCS '25)."
LABEL url="https://github.com/ProbeShooter/AsiaCCS25-ProbeShooter"
LABEL license="MIT"

# Vim installation
RUN apt update && \
    apt install -y vim && \
    rm -rf /var/lib/apt/lists/*

# Python package installation
RUN pip install --upgrade pip && \
    pip install --no-cache-dir setuptools numpy matplotlib scikit-learn scipy tqdm

# Copy files
RUN mkdir -p /root/ProbeShooter
WORKDIR /root/ProbeShooter
COPY . .
RUN pip install --no-cache-dir . && \
    rm -rf build dist source/*.egg-info && \
    find . -type d -name "__pycache__" -exec rm -rf {} + && \
    chmod +x ./scripts/* && \
    mkdir -p ./scripts/output

# Finalize
WORKDIR /root/ProbeShooter
CMD ["/bin/bash"]
