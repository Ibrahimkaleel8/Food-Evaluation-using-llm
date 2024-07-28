FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

RUN mkdir /backend

COPY ./requirements.txt /backend/requirements.txt

RUN pip install -r /backend/requirements.txt

COPY . /backend 

EXPOSE 3000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000", "--reload"]