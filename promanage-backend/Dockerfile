# Dockerfile con Rust para Pydantic 2.x
FROM rust:1.75-slim as rust-base

# Instalar Python y dependencias del sistema
FROM python:3.11-slim

# Copiar Rust desde la imagen base
COPY --from=rust-base /usr/local/cargo /usr/local/cargo
COPY --from=rust-base /usr/local/rustup /usr/local/rustup

# Configurar variables de entorno para Rust
ENV RUSTUP_HOME=/usr/local/rustup \
    CARGO_HOME=/usr/local/cargo \
    PATH=/usr/local/cargo/bin:$PATH

# Instalar dependencias del sistema necesarias para compilación
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    libc6-dev \
    libffi-dev \
    libssl-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements y instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY main.py .

# Exponer puerto
EXPOSE 8000

# Variables de entorno para la aplicación
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Comando por defecto (sin reload para evitar problemas de multiprocessing)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Para desarrollo con reload usar:
# docker run -p 8000:8000 -v $(pwd):/app promanage-backend-rust uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Metadata
LABEL maintainer="ProManage Team"
LABEL description="ProManage Backend API with FastAPI and Pydantic 2.x"
LABEL version="1.0.0"