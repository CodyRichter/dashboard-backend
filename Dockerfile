FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

WORKDIR /app

COPY requirements.txt /app
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./ /app

RUN chmod +x /app/startup.sh
CMD ["/app/startup.sh"]