# library_server/Dockerfile
FROM python:latest

# We set a working directory for our container
WORKDIR /api_server

COPY api.py ./
COPY requirements.txt ./

# Install needed dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Command for executing our script
CMD ["python", "api.py"]