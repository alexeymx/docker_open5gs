FROM debian:10

# Install dependencies
RUN apt update && apt install -y \
    osmo-cbc \
    osmo-stp \
    osmo-hlr \
    osmo-mgw \
    osmo-mme \
    osmo-sgsn \
    iproute2 \
    iptables \
    && rm -rf /var/lib/apt/lists/*

# Copy configuration files
COPY osmo-cbc.cfg /etc/osmocom/osmo-cbc.cfg

# Expose required ports
EXPOSE 4239  5700  29118

# Start CBC
CMD ["osmo-cbc", "-c", "/etc/osmocom/osmo-cbc.cfg"]