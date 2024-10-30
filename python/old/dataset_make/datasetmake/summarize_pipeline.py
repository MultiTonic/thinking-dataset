import os
from distilabel.llms import OneAI #, AzureOpenAILLM, 
from distilabel.pipeline import Pipeline
from distilabel.steps import LoadDataFromHub
from distilabel.steps.tasks import TextGeneration

# Ensure you have set your OpenAI API key in the environment variables
# os.environ["01AI_API_KEY"] = "your-openai-api-key-here"

# Custom prompt template
CASE_STUDY_PROMPT = """
{pdf_content}

the text above is MIT licensed. Produce a complete fictional case study with several for the given text 
"""

with Pipeline(
    name="cablegate-summary-pipeline",
    description="A pipeline to summarize diplomatic cables from the Cablegate dataset"
) as pipeline:
    load_dataset = LoadDataFromHub(
        name="load_cablegate_dataset",
        output_mappings={"prompt": "pdf_content"}
    )

    summarize_cable = TextGeneration(
        name="summarize_cable",
        llm=OneAI(),
        system_prompt="You are an expert in analyzing diplomatic communications. Provide clear and concise summaries of the given content.",
    )

    load_dataset >> summarize_cable

if __name__ == "__main__":
    distiset = pipeline.run(
        parameters={
            load_dataset.name: {
                "repo_id": "DataTonic/cablegate-pdf-dataset",
                "split": "cables",  # Adjust if needed
            },
            summarize_cable.name: {
                "llm": {
                    "generation_kwargs": {
                        "temperature": 0.7,
                        "max_new_tokens": 150,
                    }
                },
                "prompt_template": CUSTOM_PROMPT,
            },
        },
    )
    
    # Push the results to the Hugging Face Hub
    distiset.push_to_hub(repo_id="your-username/cablegate-summaries")
    print("Pipeline execution completed and results pushed to the Hub.")