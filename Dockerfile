FROM node:22-alpine AS web-build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY index.html tsconfig*.json vite.config.ts eslint.config.js ./
COPY src ./src
RUN npm run build

FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend ./backend
COPY --from=web-build /app/dist ./dist
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
