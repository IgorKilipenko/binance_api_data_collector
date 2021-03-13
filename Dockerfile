FROM python:3.9

EXPOSE 8080

WORKDIR /src

COPY requirements.txt requirements.txt
#RUN py -m pip install -r requirements.txt
RUN pip install -r requirements.txt

COPY ./src /src

# update PATH environment variable
#ENV PATH=/root/.local:$PATH

CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8085"]