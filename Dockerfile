FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
# copy project files and folders to the current working directory (i.e. 'app' folder)
#COPY . .
RUN pip install -r requirements.txt
ADD . /code/

#server
EXPOSE 8000
STOPSIGNAL SIGINT
ENTRYPOINT ["python", "manage.py"]
CMD ["runserver", "0.0.0.0:8000"]
