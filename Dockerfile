FROM python:3.9
ADD . /code
WORKDIR /code
#VOLUME /code
RUN pip install -r requirements.txt
ENV FLASK_APP=monolith
ENV FLASK_ENV=development
ENV FLASK_DEBUG=true
ENV CELERY_BROKER_URL=redis://redis:6379/0
ENV CELERY_RESULT_BACKEND=redis://redis:6379/0
EXPOSE 5000
EXPOSE 5555
CMD ["flask","run","--host", "0.0.0.0"]
