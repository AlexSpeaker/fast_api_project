FROM python:3.10
WORKDIR /my_app
ADD requirements.txt /tmp/requirements.txt

RUN pip install -r /tmp/requirements.txt

COPY my_twitter ./my_twitter
COPY manage_utils ./manage_utils
COPY manage.py .
ENV AM_I_IN_A_DOCKER_CONTAINER Yes

CMD ["uvicorn", "my_twitter.main:app", "--host", "0.0.0.0", "--port", "80"]
