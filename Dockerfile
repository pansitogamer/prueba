FROM python:3.11-slim

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instala dependencias del sistema mínimas necesarias
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libffi-dev \
    libssl-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libglib2.0-dev \
    git \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Crea el directorio de trabajo
WORKDIR /app

# Copia e instala dependencias
COPY requirements.txt .

# Instala pip y herramientas de compilación
RUN pip install --upgrade pip setuptools wheel

# Instala las dependencias del proyecto
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código fuente
COPY . .

# Comando por defecto
CMD ["python", "start.py"]
