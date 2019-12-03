FROM python:3.7-slim

ADD . .

RUN pip3 install -r requirements.txt
RUN pip3 install sklearn

CMD ["python3","-u","/src/api.py"]