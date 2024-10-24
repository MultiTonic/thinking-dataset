from distilabel.llms import InferenceEndpointsLLM
from distilabel.pipeline import Pipeline
from distilabel.steps.tasks import MagpieGenerator, TextGeneration
from globe import REASONING_PROMPT, REFLECTION_SYSTEM_PROMPT

with Pipeline(name="reflection-tuning") as pipeline:
    generate_instructions = MagpieGenerator(
        llm=InferenceEndpointsLLM(
            model_id="meta-llama/Meta-Llama-3.1-70B-Instruct",
            tokenizer_id="meta-llama/Meta-Llama-3.1-70B-Instruct",
            magpie_pre_query_template="llama3",
            generation_kwargs={"temperature": 0.8, "max_new_tokens": 2048},
        ),
        system_prompt=REASONING_PROMPT,
        batch_size=5,
        num_rows=5,
        only_instruction=True,
    )

    response = TextGeneration(
        llm=InferenceEndpointsLLM(
            model_id="meta-llama/Meta-Llama-3.1-70B-Instruct",
            tokenizer_id="meta-llama/Meta-Llama-3.1-70B-Instruct",
            generation_kwargs={"temperature": 0.8, "max_new_tokens": 2048},
        ),
        system_prompt=REFLECTION_SYSTEM_PROMPT,
        input_batch_size=5,
    )

    generate_instructions >> response

if __name__ == "__main__":
    distiset = pipeline.run()
    distiset.push_to_hub(
        "Tonic/thinking", include_script=True
    )
