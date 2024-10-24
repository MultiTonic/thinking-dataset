
# 8. **Run each pipeline script separately:**
#    ```
#    python reasoning_pipeline.py
#    python financial_pipeline.py
#    python medical_pipeline.py
#    ```

# 2. **run the combine_datasets script:**
#    ```
#    python combine_datasets.py
#    ```

# This will create and push the individual datasets for each domain, and then combine them into a final multi-domain dataset.
    


import os
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
    make_generator_step,
)
from distilabel.steps.tasks import TextGeneration, Magpie, EvolInstruct, EvolQuality, EvolComplexity
from globe import QUERY_PROMPT, SYSTEM_PROMPT, REASONING_PROMPT, FINANCIAL_PROMPT, MEDICAL_PROMPT
from datasets import Dataset, load_dataset
from hugs import UniqueDatasetRepository, BatchCounter
from pdfloader import DatasetGenerator

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

@step(inputs=["financial_data"], outputs=["formatted_financial_data"])
def FormatFinancialData(inputs: StepInput) -> StepOutput:
    outputs = []
    for input in inputs:
        formatted_data = f"Financial data: {input['financial_data']}"
        input["formatted_financial_data"] = formatted_data
        outputs.append(input)
    yield outputs

@step(inputs=["medical_record"], outputs=["formatted_medical_data"])
def FormatMedicalData(inputs: StepInput) -> StepOutput:
    outputs = []
    for input in inputs:
        formatted_data = f"Medical record: {input['medical_record']}"
        input["formatted_medical_data"] = formatted_data
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

def create_reasoning_pipeline(llm, repo, counter, pdf_folder):
    with Pipeline("Math Reasoning Pipeline") as pipeline:
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
            load_pdfs_from_folder(pdf_folder),
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

        dataset_generator = DatasetGenerator(model=llm.model_id, api_key="your_api_key_here")
        generate_pdf_questions = GenerateQuestionsFromPDF(dataset_generator=dataset_generator)

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

    return pipeline

def create_financial_pipeline(llm, repo, counter, pdf_folder):
    with Pipeline("Financial Data Pipeline") as pipeline:
        load_pdfs = LoadPDFsFromFolder(folder_path=pdf_folder)
        
        dataset_generator = DatasetGenerator(model=llm.model_id, api_key="your_api_key_here")
        generate_pdf_questions = GenerateQuestionsFromPDF(dataset_generator=dataset_generator)
        
        financial_data = make_generator_step(
            load_dataset("financial_dataset_placeholder"),
            output_mappings={"financial_data": "raw_data"}
        )

        pdf_data = make_generator_step(
            load_pdfs_from_folder(pdf_folder),
            output_mappings={"pdf_content": "pdf_content"}
        )

        format_financial = FormatFinancialData()
        financial_generation = TextGeneration(
            input_batch_size=3,
            use_system_prompt=True,
            llm=llm,
            input_mappings={"instruction": "formatted_financial_data"},
        )
        financial_magpie = Magpie(
            llm=llm,
            system_prompt=FINANCIAL_PROMPT,
            n_turns=1,
            only_instruction=False,
            input_batch_size=3,
        )
        
        dataset_generator = DatasetGenerator(model=llm.model_id, api_key="your_api_key_here")
        generate_pdf_questions = GenerateQuestionsFromPDF(dataset_generator=dataset_generator)

        keep_columns_financial = KeepColumns(
            columns=[
                "financial_data",
                "formatted_financial_data",
                "generation",
                "magpie_response",
                "pdf_questions",
            ],
        )

        def save_and_push_financial(step_output):
            if counter.increment():
                dataset = Dataset.from_dict(step_output)
                repo.push_to_hub(dataset, f"Financial update after {counter.count} batches")
            return step_output

        (
            load_pdfs
            >> generate_pdf_questions
            >> financial_data
            >> format_financial
            >> financial_generation
            >> financial_magpie
            >> keep_columns_financial
            >> save_and_push_financial
        )

    return pipeline

def create_medical_pipeline(llm, repo, counter, pdf_folder):
    with Pipeline("Medical Data Pipeline") as pipeline:
        load_pdfs = LoadPDFsFromFolder(folder_path=pdf_folder)
        
        dataset_generator = DatasetGenerator(model=llm.model_id, api_key="your_api_key_here")
        generate_pdf_questions = GenerateQuestionsFromPDF(dataset_generator=dataset_generator)
        
        medical_data = make_generator_step(
            load_dataset("medical_dataset_placeholder"),
            output_mappings={"medical_record": "raw_data"}
        )

        pdf_data = make_generator_step(
            load_pdfs_from_folder(pdf_folder),
            output_mappings={"pdf_content": "pdf_content"}
        )

        format_medical = FormatMedicalData()
        medical_generation = TextGeneration(
            input_batch_size=3,
            use_system_prompt=True,
            llm=llm,
            input_mappings={"instruction": "formatted_medical_data"},
        )
        medical_magpie = Magpie(
            llm=llm,
            system_prompt=MEDICAL_PROMPT,
            n_turns=1,
            only_instruction=False,
            input_batch_size=3,
        )
        
        dataset_generator = DatasetGenerator(model=llm.model_id, api_key="your_api_key_here")
        generate_pdf_questions = GenerateQuestionsFromPDF(dataset_generator=dataset_generator)

        keep_columns_medical = KeepColumns(
            columns=[
                "medical_record",
                "formatted_medical_data",
                "generation",
                "magpie_response",
                "pdf_questions",
            ],
        )

        def save_and_push_medical(step_output):
            if counter.increment():
                dataset = Dataset.from_dict(step_output)
                repo.push_to_hub(dataset, f"Medical update after {counter.count} batches")
            return step_output

        (
            load_pdfs
            >> generate_pdf_questions
            >> medical_data
            >> format_medical
            >> medical_generation
            >> medical_magpie
            >> keep_columns_medical
            >> save_and_push_medical
        )

    return pipeline

if __name__ == "__main__":
    llm = InferenceEndpointsLLM(
        model_id="meta-llama/Meta-Llama-3.1-70B-Instruct",
        tokenizer_id="meta-llama/Meta-Llama-3.1-70B-Instruct",
        magpie_pre_query_template="llama3",
        generation_kwargs={"temperature": 0.8, "max_new_tokens": 4092},
    )

    reasoning_repo = UniqueDatasetRepository("tonic-thinking-dataset-reasoning")
    financial_repo = UniqueDatasetRepository("tonic-thinking-dataset-financial")
    medical_repo = UniqueDatasetRepository("tonic-thinking-dataset-medical")

    reasoning_counter = BatchCounter()
    financial_counter = BatchCounter()
    medical_counter = BatchCounter()

    # Use different PDF folders for each pipeline
    reasoning_pdf_folder = "path/to/reasoning/pdf/folder"
    financial_pdf_folder = "path/to/financial/pdf/folder"
    medical_pdf_folder = "path/to/medical/pdf/folder"

    reasoning_pipeline = create_reasoning_pipeline(llm, reasoning_repo, reasoning_counter, reasoning_pdf_folder)
    financial_pipeline = create_financial_pipeline(llm, financial_repo, financial_counter, financial_pdf_folder)
    medical_pipeline = create_medical_pipeline(llm, medical_repo, medical_counter, medical_pdf_folder)

    reasoning_distiset = reasoning_pipeline.run(use_cache=True)
    financial_distiset = financial_pipeline.run(use_cache=True)
    medical_distiset = medical_pipeline.run(use_cache=True)

    reasoning_repo.push_to_hub(reasoning_distiset, "Final reasoning dataset")
    financial_repo.push_to_hub(financial_distiset, "Final financial dataset")
    medical_repo.push_to_hub(medical_distiset, "Final medical dataset")

    combined_dataset = Dataset.from_dict({
        "reasoning": reasoning_distiset,
        "financial": financial_distiset,
        "medical": medical_distiset
    })
    
    combined_repo = UniqueDatasetRepository("tonic-thinking-dataset-combined")
    combined_repo.push_to_hub(combined_dataset, "Final combined multi-domain dataset")
