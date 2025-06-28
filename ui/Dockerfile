# Stage 1: Build the Angular application
FROM node:22-slim AS build
WORKDIR /app
COPY package*.json ./
# In the bash session, current directory was /app/ui, so files were created there.
# Docker context will be ui/, so paths in COPY should be relative to ui/
RUN npm install
COPY . .
RUN npm run build -- --configuration production

# Stage 2: Serve the application with Nginx
FROM nginx:alpine
COPY --from=build /app/dist/ui/browser /usr/share/nginx/html

# Copy nginx config for Angular (if any specific, otherwise default works for SPA)
# For this setup, the main nginx.conf will be in the docker-compose setup,
# and it will handle routing to this Angular app or the API.
# This Nginx instance is just for serving the static files of Angular.
# If we were serving Angular directly without a reverse proxy, we'd need a custom nginx.conf here.
# e.g., COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
