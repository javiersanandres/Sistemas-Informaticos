# library_server/Dockerfile
FROM python:latest

# We set a working directory for our container
WORKDIR /library_service

COPY library_server/file.py ./
COPY utils.py ./
COPY requirements.txt ./

# Install needed dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Command for executing our script
CMD ["python", "library_service/file.py"]
