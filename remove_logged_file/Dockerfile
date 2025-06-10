FROM python:3.12-slim

WORKDIR /app

# Copy the log cleaner code
COPY remove_logged_file.py .

# Set CMD to /dev/null to let docker-compose handle the command
CMD ["/dev/null"] 