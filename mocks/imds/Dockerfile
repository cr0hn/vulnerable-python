FROM python:3.13-slim
WORKDIR /srv
RUN pip install --no-cache-dir flask==3.1.0
COPY server.py .
EXPOSE 8090
CMD ["python", "server.py"]
