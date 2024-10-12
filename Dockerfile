FROM python:3.12-slim

WORKDIR /programas/orquestador

# Instalar FastAPI y otras dependencias
RUN pip install --upgrade pip
RUN pip3 install "fastapi[standard]"
RUN pip3 install httpx
RUN pip3 install pydantic

COPY . .

EXPOSE 8010

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8010"]
