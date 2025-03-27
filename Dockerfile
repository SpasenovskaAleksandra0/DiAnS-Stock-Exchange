FROM python:3.13

WORKDIR app

COPY requirements.txt .
COPY . .

RUN pip install -r requirements.txt

EXPOSE 5000

#CMD ["python", "flask_app/app.py"]
