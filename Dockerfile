FROM python:3.6.0-slim

RUN pip3 install japronto
RUN pip3 install requests
RUN pip install uvloop==0.8.1
RUN pip install backoff
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["japronto"]
