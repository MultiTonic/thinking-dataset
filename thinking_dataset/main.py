from distilabel.llms import OllamaLLM

def main():
    print("Thinking Dataset Application")

    # Initialize Ollama model using Distilabel
    ollama = OllamaLLM(model="llama3.1")
    ollama.load()

    # Example prompt
    prompt = "Generate a detailed analysis on the impact of market disruption."

    # Call the model
    output = ollama.generate(inputs=[[{"role": "user", "content": prompt}]])
    print("Response from Ollama:", output)

    # Process and use the generated output
    # Example: Save to file, further analysis, etc.
    with open("output.txt", "w") as file:
        file.write(str(output))

if __name__ == "__main__":
    main()
