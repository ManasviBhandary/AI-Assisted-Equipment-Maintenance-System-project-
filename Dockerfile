# Use lightweight official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy application files
COPY . /app

# Run ETL pipeline on image build
RUN python etl/etl_pipeline.py

# Expose server port
EXPOSE 8000

# Environment variables
ENV PYTHONUNBUFFERED=1

# Command to run backend HTTP server
CMD ["python", "backend/server.py", "8000"]
