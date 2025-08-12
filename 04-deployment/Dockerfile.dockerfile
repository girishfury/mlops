FROM agrigorev/zoomcamp-model:mlops-2024-3.10.13-slim
WORKDIR /app
COPY ["starter_container.py", "requirements.txt", "./"]
RUN python3 -m pip install --upgrade pip
RUN pip install -r requirements.txt
ENTRYPOINT ["python3", "starter_container.py"]