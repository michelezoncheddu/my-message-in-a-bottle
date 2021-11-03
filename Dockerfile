FROM python:3.9
ADD . /code
WORKDIR /code
#VOLUME /code
RUN pip install -r requirements.txt
ENV FLASK_APP=monolith
ENV FLASK_ENV=development
ENV FLASK_DEBUG=true
EXPOSE 5000
CMD ["flask","run","--host", "0.0.0.0"]