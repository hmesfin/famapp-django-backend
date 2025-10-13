# Frontend Dockerfile for DjVue Orchestra 🎭
# Ham Dog & TC's masterpiece for local development

FROM node:20-alpine AS base

# Set working directory
WORKDIR /app

# Install dependencies for hot-reload and development
RUN apk add --no-cache \
    git \
    && rm -rf /var/cache/apk/*

# Development stage - the main show for local dev
FROM base AS development

# Set environment
ENV NODE_ENV=development

# Copy package files first for better caching
COPY frontend/package*.json ./

# Install all dependencies (including dev dependencies)
RUN npm install

# Copy the rest of the frontend code
# Note: This will be overridden by the volume mount in docker-compose
COPY frontend/ .

# Expose Vite's default port
EXPOSE 5173

# Start the development server
# --host 0.0.0.0 is crucial for Docker networking
# --port 5173 ensures we're on the right port
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]