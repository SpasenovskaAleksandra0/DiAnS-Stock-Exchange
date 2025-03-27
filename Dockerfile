FROM python:3.9-slim-bullseye

WORKDIR app

COPY requirements.txt .
COPY . .

RUN pip install -r requirements.txt

EXPOSE 5000

#CMD ["flask", "run", "--host=0.0.0.0"]
#CMD ["python", "flask_app/app.py"]