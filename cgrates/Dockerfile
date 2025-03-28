FROM dkr.cgrates.org/master/cgr-engine:latest

# Install PostgreSQL client
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

# Copy initialization scripts
COPY init_scripts /init_scripts
RUN chmod +x /init_scripts/*.sh

# Create entrypoint script
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["/usr/bin/cgr-engine", "-config_path", "/etc/cgrates", "-logger", "*stdout"]