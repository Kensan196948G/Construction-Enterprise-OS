FROM node:20-alpine

WORKDIR /app

COPY package.json ./
RUN npm install --no-audit --no-fund

COPY . .

ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3101
EXPOSE 3101

# Static export mode — serve via dev server for Docker Compose
CMD ["npm", "run", "dev", "--", "-p", "3101", "-H", "0.0.0.0"]
