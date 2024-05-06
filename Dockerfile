FROM python:3.10.11-slim
WORKDIR /app
ENV BOT_TOKEN, ADMIN_ID, BOT_ID
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY *.py .
ENTRYPOINT [ "python3" ]
CMD [ "nami.py" ]