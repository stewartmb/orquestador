FROM python:3-slim

# Instalar las dependencias del sistema
RUN apt-get update && \
    apt-get install -y gcc libffi-dev libssl-dev && \
    apt-get clean

WORKDIR /programas/orquestador

# Instalar FastAPI y otras dependencias
RUN pip3 install "fastapi[standard]"
RUN pip3 install httpx
RUN pip3 install pydantic

COPY . .

EXPOSE 8010

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8010"]
