FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Clone and install CGRateS
RUN git clone https://github.com/cgrates/cgrates.git /opt/cgrates \
    && cd /opt/cgrates \
    && make

# Set working directory
WORKDIR /opt/cgrates

# Expose necessary ports
EXPOSE 2012 2013 2080

# Start CGRateS
CMD ["./cgr-engine"]