FROM ubuntu
RUN apt-get update && apt-get install python3 -y && apt-get install python3-pip -y
RUN  apt-get install python3-virtualenv -y && apt-get install python3-pip -y 
RUN mkdir /django_proj 
WORKDIR /django_proj
EXPOSE 8000
RUN cd /django_proj 
ADD . /django_proj
RUN virtualenv django_env 
CMD source django_env/bin/activate 
RUN pip3 install django 
RUN django-admin startproject djp . 
RUN mv settings.py /django_proj/djp
RUN python3 manage.py migrate
CMD python3 manage.py runserver 0.0.0.0:8000
