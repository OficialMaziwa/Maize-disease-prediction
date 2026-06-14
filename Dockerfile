FROM python:3.11-slim

WORKDIR /app

# Weka zana za mfumo na safisha
RUN apt-get update && apt-get install -y --no-install-recommends gcc && apt-get clean && rm -rf /var/lib/apt/lists/*

# Nakili requirements na usakinishe
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Nakili msimbo wote
COPY . .

# Weka PORT
ENV PORT=10000

# Tumia CMD rahisi kwa ajili ya kuanzisha
CMD gunicorn --bind 0.0.0.0:$PORT run:app
