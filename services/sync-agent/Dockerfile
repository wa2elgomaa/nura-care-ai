FROM node:22-alpine AS build
WORKDIR /app
COPY package.json tsconfig.json ./
RUN npm install
COPY src ./src
RUN npm run build

FROM node:22-alpine
WORKDIR /app
ENV NODE_ENV=production
COPY --from=build /app/dist ./dist
COPY package.json ./
RUN mkdir -p /var/lib/nura && chown -R node:node /var/lib/nura
USER node
EXPOSE 7070
CMD ["node", "dist/index.js"]
