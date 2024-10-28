import os
from distilabel.llms import InferenceEndpointsLLM
from distilabel.pipeline import Pipeline
from distilabel.steps import (
    StepInput,
    StepOutput,
    step,
    KeepColumns,
    make_generator_step,
)
from distilabel.steps.tasks import TextGeneration, Magpie
from prompts import FINANCIAL_PROMPT
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
            max_questions=5
        )
        input["pdf_questions"] = questions.items
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

def create_financial_pipeline(llm, repo, counter, pdf_folder):
    with Pipeline("Financial Data Pipeline") as pipeline:
        load_pdfs = LoadPDFsFromFolder(folder_path=pdf_folder)
        
        dataset_generator = DatasetGenerator(model=llm.model_id, api_key="your_api_key_here")
        generate_pdf_questions = GenerateQuestionsFromPDF(dataset_generator=dataset_generator)
        
        financial_data = make_generator_step(
            load_dataset("financial_dataset_placeholder"),
            output_mappings={"financial_data": "raw_data"}
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

if __name__ == "__main__":
    llm = InferenceEndpointsLLM(
        model_id="meta-llama/Meta-Llama-3.1-70B-Instruct",
        tokenizer_id="meta-llama/Meta-Llama-3.1-70B-Instruct",
        magpie_pre_query_template="llama3",
        generation_kwargs={"temperature": 0.8, "max_new_tokens": 4092},
    )

    financial_repo = UniqueDatasetRepository("tonic-thinking-dataset-financial")
    financial_counter = BatchCounter()
    financial_pdf_folder = "path/to/financial/pdf/folder"

    financial_pipeline = create_financial_pipeline(llm, financial_repo, financial_counter, financial_pdf_folder)
    financial_distiset = financial_pipeline.run(use_cache=True)
    financial_repo.push_to_hub(financial_distiset, "Final financial dataset")