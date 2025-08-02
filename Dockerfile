# Use the official SQL Server 2019 image as the base
FROM mcr.microsoft.com/mssql/server:2019-latest

# Install prerequisites for mssql-tools
RUN apt-get update && \
        apt-get install -y curl gnupg && \
        curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
        curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
        apt-get update && \
        ACCEPT_EULA=Y apt-get install -y mssql-tools unixodbc-dev

# Add mssql-tools to PATH
ENV PATH="$PATH:/opt/mssql-tools/bin"

# Copy entrypoint script (optional, for custom startup)
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose SQL Server port
EXPOSE 1433

# Set entrypoint to start SQL Server
ENTRYPOINT ["/entrypoint.sh"]
