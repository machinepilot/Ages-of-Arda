FROM node:18-slim as base

# Install dependencies
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Copy source code
COPY services ./services
COPY shared ./shared
COPY gateway ./gateway
COPY config ./config

# Environment setup
ENV NODE_ENV=production
ENV MCP_PORT=8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD node ./shared/scripts/healthcheck.js

# Start the MCP server
CMD ["node", "gateway/server.js"] 