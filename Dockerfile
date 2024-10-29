FROM runpod/pytorch:2.0.1-py3.10-cuda11.7.1-devel

# Install Ollama
RUN curl https://ollama.ai/install.sh | sh

# Copy application code
COPY . /app
WORKDIR /app

# Install requirements
RUN pip install -r requirements.txt

# Start script
CMD ["python", "app.py"]