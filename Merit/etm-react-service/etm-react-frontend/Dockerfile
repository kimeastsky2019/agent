# Development Dockerfile
# For production builds, use: docker build --target production -t etm-react-frontend:prod .
FROM node:18-alpine

WORKDIR /app

# Copy package files first for better layer caching
COPY package*.json ./

# Install dependencies
# Use npm install if package-lock.json doesn't exist, otherwise use npm ci
# Ignore scripts to avoid postinstall issues during build
RUN if [ -f package-lock.json ]; then npm ci --ignore-scripts; else npm install --ignore-scripts; fi

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Start development server with hot reload
# For production, use: CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "3000"]
CMD ["npm", "run", "start"]
