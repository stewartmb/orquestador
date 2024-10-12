FROM python:3-slim

# Instalar las herramientas necesarias para compilar los paquetes
RUN apt-get update && \
    apt-get install -y gcc build-essential libffi-dev libssl-dev make && \
    apt-get clean

WORKDIR /programas/orquestador

# Instalar FastAPI y otras dependencias
RUN pip install --upgrade pip
RUN pip3 install "fastapi[standard]"
RUN pip3 install httpx
RUN pip3 install pydantic

COPY . .

EXPOSE 8010

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8010"]
