import re

from distilabel.llms import InferenceEndpointsLLM
from distilabel.pipeline import Pipeline
from distilabel.steps import (
    LoadDataFromHub,
    StepInput,
    StepOutput,
    step,
    FormatTextGenerationSFT,
    KeepColumns,
)
from distilabel.steps.tasks import TextGeneration
from prompts import QUERY_PROMPT, SYSTEM_PROMPT

from datasets import Dataset, load_dataset
from hugs import UniqueDatasetRepository, BatchCounter
from pdfloader import DatasetGenerator

import os

@step(outputs=["pdf_content"])
def LoadPDFsFromFolder(folder_path: str) -> StepOutput:
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "rb") as file:
                pdf_content = file.read()
            yield [{"pdf_content": pdf_content}]

@step(inputs=["pdf_content"], outputs=["pdf_questions"])
def GenerateQuestionsFromPDF(inputs: StepInput, dataset_generator: DatasetGenerator) -> StepOutput:
    outputs = []
    for input in inputs:
        questions = dataset_generator.generate_from_texts(
            texts=[input["pdf_content"]],
            max_questions=5  # Adjust as needed
        )
        input["pdf_questions"] = questions.items
        outputs.append(input)
    yield outputs

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


@step(inputs=["pdf_content"], outputs=["pdf_questions"])
def GenerateQuestionsFromPDF(inputs: StepInput, dataset_generator: DatasetGenerator) -> StepOutput:
    outputs = []
    for input in inputs:
        questions = dataset_generator.generate_from_texts(
            texts=[input["pdf_content"]],
            max_questions=5  # Adjust as needed
        )
        input["pdf_questions"] = questions.items
        outputs.append(input)
    yield outputs

def load_pdfs_from_folder(folder_path):
    pdf_contents = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "rb") as file:
                pdf_content = file.read()
            pdf_contents.append({"pdf_content": pdf_content})
    return pdf_contents

with Pipeline("Think Tonic") as pipeline:
        repo = ""
        counter = ""
        pdf_folder = "path/to/your/pdf/folder"

        llm = InferenceEndpointsLLM(
            model_id="meta-llama/Meta-Llama-3.1-70B-Instruct",
            tokenizer_id="meta-llama/Meta-Llama-3.1-70B-Instruct",
            magpie_pre_query_template="llama3",
            generation_kwargs={"temperature": 0.8, "max_new_tokens": 4092},
        )

        load_pdfs = LoadPDFsFromFolder(folder_path=pdf_folder)
        
        dataset_generator = DatasetGenerator(model=llm.model_id, api_key="your_api_key_here")
        generate_pdf_questions = GenerateQuestionsFromPDF(dataset_generator=dataset_generator)
        
        dataset = LoadDataFromHub(
            repo_id="openai/gsm8k",
            config="main",
            split="train",
            batch_size=3,
        )

        pdf_data = make_generator_step(
            load_pdfs,
            output_mappings={"pdf_content": "pdf_content"}
        )

        initial_formatting = InitialFormatting()
        create_prompt = CreateGenerationPrompt()
        response = TextGeneration(
            input_batch_size=3,
            use_system_prompt=True,
            llm=llm,
            input_mappings={"instruction": "instruction"},
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
            input_mappings={"instruction": "question"},
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
                "pdf_questions",
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
                "pdf_questions",
            ],
        )

        def save_and_push(step_output):
            if counter.increment():
                dataset = Dataset.from_dict(step_output)
                repo.push_to_hub(dataset, f"Update after {counter.count} batches")
            return step_output

        (
            load_pdfs
            >> generate_pdf_questions
            >> dataset
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

if __name__ == "__main__":

    distiset = pipeline.run(
        use_cache=True,
    )
    distiset.push_to_hub("thesven/gsm8k-reasoning", private=True, include_script=True)