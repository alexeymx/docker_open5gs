# Use Ubuntu as base image
FROM ubuntu:22.04 AS builder

# Set architecture (default to amd64)
ARG TARGETARCH=amd64

# Update and install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Clone CGRateS source code
WORKDIR /opt
RUN git clone --depth=1 https://github.com/cgrates/cgrates.git

# Compile CGRateS
WORKDIR /opt/cgrates
RUN make

# Create final container with only the compiled binary
FROM ubuntu:22.04

# Set architecture
ARG TARGETARCH=amd64

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy compiled CGRateS from builder
COPY --from=builder /opt/cgrates /opt/cgrates

# Set working directory
WORKDIR /opt/cgrates

# Expose necessary ports
EXPOSE 2012 2013 2080

# Start CGRateS on container run
CMD ["./cgr-engine"]