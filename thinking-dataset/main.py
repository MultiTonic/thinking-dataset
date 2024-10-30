import sys
from ollama import Ollama
from distillabel import Distillabel

def main():
    print("Thinking Dataset Application")

    # Initialize Ollama
    ollama = Ollama(model="llama-3.1")

    # Example prompt
    prompt = "Generate a detailed analysis on the impact of market disruption."

    # Generate response using Ollama
    response = ollama.complete(prompt)
    print(response)

    # Additional logic for Distillabel and other processes

if __name__ == "__main__":
    main()
