# library_server/Dockerfile
FROM python:latest

# We set a working directory for our container
WORKDIR /user_service

COPY users_server/user.py ./
COPY requirements.txt ./
COPY utils.py ./

# Install needed dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Command for executing our script
CMD ["python", "user.py"]