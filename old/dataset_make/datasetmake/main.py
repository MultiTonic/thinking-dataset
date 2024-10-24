import re
from datetime import datetime
from distilabel.llms import InferenceEndpointsLLM
from distilabel.pipeline import Pipeline
from distilabel.steps import (
    LoadDataFromHub,
    StepInput,
    StepOutput,
    step,
    FormatTextGenerationSFT,
    KeepColumns,
    GroupColumns,
)
from distilabel.steps.tasks import TextGeneration, Magpie, EvolInstruct, EvolQuality, EvolComplexity
from globe import QUERY_PROMPT, SYSTEM_PROMPT, REASONING_PROMPT
from datasets import Dataset
from hugs import UniqueDatasetRepository, BatchCounter


@step(
    inputs=["question", "answer", "short_answer"],
    outputs=["instruction", "system_prompt"],
)
def CreateGenerationPrompt(inputs: StepInput) -> StepOutput:
    outputs = []
    for input in inputs:
        prompt = QUERY_PROMPT.format(
            question=input["question"],
            long_answer=input["answer"],
            short_answer=input["short_answer"],
        )
        input["instruction"] = prompt
        input["system_prompt"] = SYSTEM_PROMPT
        outputs.append(input)
    yield outputs

@step(inputs=["answer"], outputs=["short_answer", "answer"])
def InitialFormatting(inputs: StepInput) -> StepOutput:
    outputs = []
    for input in inputs:
        pattern_short = r"####\s*(\d+)"
        pattern_long = r"(.*?)\s*####"
        match_short = re.search(pattern_short, input["answer"])
        match_long = re.search(pattern_long, input["answer"])
        if match_short is not None and match_long is not None:
            input["short_answer"] = match_short.group(1)
            input["answer"] = match_long.group(1)
            outputs.append(input)
    yield outputs

@step(inputs=["generation"], outputs=["generation"])
def FilterNull(inputs: StepInput) -> StepOutput:
    outputs = []
    for input in inputs:
        if input["generation"] is not None or input["generation"] != "":
            outputs.append(input)
    yield outputs

def create_pipeline(repo, counter):
    with Pipeline("Thinking Multi-Domain Dataset") as pipeline:
        llm = InferenceEndpointsLLM(
            model_id="meta-llama/Meta-Llama-3.1-70B-Instruct",
            tokenizer_id="meta-llama/Meta-Llama-3.1-70B-Instruct",
            magpie_pre_query_template="llama3",
            generation_kwargs={"temperature": 0.8, "max_new_tokens": 4092},
        )

        dataset = LoadDataFromHub(
            repo_id="openai/gsm8k",
            config="main",
            split="train",
            batch_size=3,
        )

        initial_formatting = InitialFormatting()
        create_prompt = CreateGenerationPrompt()
        response = TextGeneration(
            input_batch_size=3,
            use_system_prompt=True,
            llm=llm,
            input_mappings={
                "instruction": "instruction",
            },
        )
        magpie_step = Magpie(
            llm=llm,
            system_prompt=REASONING_PROMPT,
            n_turns=1,
            only_instruction=False,
            input_batch_size=3,
        )
        null_filter = FilterNull()
        evol_instruct = EvolInstruct(
            llm=llm,
            num_evolutions=2,
            store_evolutions=True,
            generate_answers=True,
        )
        evol_quality = EvolQuality(
            llm=llm,
            num_evolutions=2,
            store_evolutions=True,
        )
        evol_complexity = EvolComplexity(
            llm=llm,
            num_instructions=2,
            generate_answers=True,
        )
        format_sft = FormatTextGenerationSFT(
            input_mappings={
                "instruction": "question",
            }
        )
        group_responses = GroupColumns(
            columns=[
                "generation",
                "magpie_response",
                "evolved_instructions",
                "answers",
                "evolved_responses",
                "evolved_instruction",
                "answer",
            ],
            output_columns=["grouped_responses"],
        )
        keep_columns = KeepColumns(
            columns=[
                "system_prompt",
                "question",
                "answer",
                "short_answer",
                "grouped_responses",
                "messages",
                "model_name",
            ],
        )

        def save_and_push(step_output):
            if counter.increment():
                dataset = Dataset.from_dict(step_output)
                repo.push_to_hub(dataset, f"Update after {counter.count} batches")
            return step_output

        (
            dataset
            >> initial_formatting
            >> create_prompt
            >> response
            >> magpie_step
            >> null_filter
            >> evol_instruct
            >> evol_quality
            >> evol_complexity
            >> format_sft
            >> group_responses
            >> keep_columns
            >> save_and_push
        )

    return pipeline

if __name__ == "__main__":
    repo = UniqueDatasetRepository("tonic-thinking-dataset")
    counter = BatchCounter()
    pipeline = create_pipeline(repo, counter)
    
    distiset = pipeline.run(
        use_cache=True,
    )

    # Final push of the complete dataset
    repo.push_to_hub(distiset, "Multi-Thinking-Dataset")