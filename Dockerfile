# Use an official Python image
FROM python:3.13

# Set the working directory
WORKDIR app

# Copy project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the application
CMD ["python", "novo.py"]
