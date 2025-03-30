# Build stage
FROM python:3.12-slim-bullseye AS builder

# Set working directory
WORKDIR /app

# Install uv and necessary tools
RUN pip install uv && apt-get update && apt-get install -y grep

# Copy the source code
COPY . .

# Extract version from pyproject.toml
RUN VERSION=$(grep -oP 'version = "\K[^"]+' pyproject.toml) && \
    echo "Package version: $VERSION" && \
    echo "export VERSION=$VERSION" > /app/version.env

# Build the package
RUN uv build

# Run stage
FROM python:3.12-alpine AS runner

# Set working directory
WORKDIR /app

# Copy version environment variable
COPY --from=builder /app/version.env /app/version.env

# Copy the built package from the builder stage (using a wildcard to match any version)
COPY --from=builder /app/dist/ /app/dist/

# Install the package and its dependencies, clean up, and add non-root user
RUN . /app/version.env && \
    echo "Installing inmobi-$VERSION.tar.gz" && \
    pip install --no-cache-dir /app/dist/inmobi-$VERSION.tar.gz && \
    rm -rf /app/dist/ /app/version.env && \
    adduser -D appuser

# Switch to non-root user
USER appuser

# Set the command to run the MCP service
CMD ["inmobi"]