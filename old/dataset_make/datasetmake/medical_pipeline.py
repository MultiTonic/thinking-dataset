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
from globe import MEDICAL_PROMPT
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

@step(inputs=["medical_record"], outputs=["formatted_medical_data"])
def FormatMedicalData(inputs: StepInput) -> StepOutput:
    outputs = []
    for input in inputs:
        formatted_data = f"Medical record: {input['medical_record']}"
        input["formatted_medical_data"] = formatted_data
        outputs.append(input)
    yield outputs

def create_medical_pipeline(llm, repo, counter, pdf_folder):
    with Pipeline("Medical Data Pipeline") as pipeline:
        load_pdfs = LoadPDFsFromFolder(folder_path=pdf_folder)
        
        dataset_generator = DatasetGenerator(model=llm.model_id, api_key="your_api_key_here")
        generate_pdf_questions = GenerateQuestionsFromPDF(dataset_generator=dataset_generator)
        
        medical_data = make_generator_step(
            load_dataset("medical_dataset_placeholder"),
            output_mappings={"medical_record": "raw_data"}
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

    medical_repo = UniqueDatasetRepository("tonic-thinking-dataset-medical")
    medical_counter = BatchCounter()
    medical_pdf_folder = "path/to/medical/pdf/folder"

    medical_pipeline = create_medical_pipeline(llm, medical_repo, medical_counter, medical_pdf_folder)
    medical_distiset = medical_pipeline.run(use_cache=True)
    medical_repo.push_to_hub(medical_distiset, "Final medical dataset")