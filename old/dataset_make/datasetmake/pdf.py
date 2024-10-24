import json
from typing import List
from io import BytesIO

import requests
from PyPDF2 import PdfReader
from langchain_text_splitters import TokenTextSplitter
from tqdm import tqdm

from distilabel.llms import InferenceEndpointsLLM
from distilabel.pipeline import Pipeline
from distilabel.steps import StepInput, StepOutput, step, make_generator_step
from distilabel.steps.tasks import TextGeneration

@step(outputs=["pdf_content"])
def LoadPDFFromURL(url: str) -> StepOutput:
    response = requests.get(url)
    pdf_file = BytesIO(response.content)
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    text = text.replace("\n", " ")
    yield [{"pdf_content": text}]

@step(inputs=["pdf_content"], outputs=["chunks"])
def ChunkText(inputs: StepInput, chunk_size: int = 1024, chunk_overlap: int = 100) -> StepOutput:
    token_splitter = TokenTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    for input in inputs:
        chunks = token_splitter.split_text(input["pdf_content"])
        yield [{"chunks": chunks}]

@step(inputs=["chunks"], outputs=["questions"])
def GenerateQuestions(inputs: StepInput, llm: InferenceEndpointsLLM, max_questions: int = 10) -> StepOutput:
    for input in inputs:
        questions = []
        for chunk in input["chunks"]:
            response = llm.generate(
                [{"role": "user", "content": f"Generate a question based on this text: {chunk}"}]
            )
            question = response.generations[0][0].text
            questions.append(question)
            if len(questions) >= max_questions:
                break
        yield [{"questions": questions[:max_questions]}]

@step(inputs=["questions", "chunks"], outputs=["qa_pairs"])
def GenerateAnswers(inputs: StepInput, llm: InferenceEndpointsLLM) -> StepOutput:
    for input in inputs:
        qa_pairs = []
        for question, chunk in zip(input["questions"], input["chunks"]):
            response = llm.generate(
                [{"role": "user", "content": f"Answer this question based on the given context:\nQuestion: {question}\nContext: {chunk}"}]
            )
            answer = response.generations[0][0].text
            qa_pairs.append({"question": question, "answer": answer, "context": chunk})
        yield [{"qa_pairs": qa_pairs}]

class DatasetGenerator:
    def __init__(self, model: str, api_key: str):
        self.llm = InferenceEndpointsLLM(
            model_id=model,
            tokenizer_id=model,
            generation_kwargs={"temperature": 0.7, "max_new_tokens": 512},
        )

    def generate_from_texts(self, texts: List[str], max_questions: int = 10, **kwargs) -> List[dict]:
        with Pipeline("Text QA Generation") as pipeline:
            text_input = make_generator_step([{"pdf_content": text} for text in texts])
            chunk_text = ChunkText()
            generate_questions = GenerateQuestions(llm=self.llm, max_questions=max_questions)
            generate_answers = GenerateAnswers(llm=self.llm)

            text_input >> chunk_text >> generate_questions >> generate_answers

        result = pipeline.run()
        return [item for batch in result for item in batch["qa_pairs"]]

    def generate_from_pdf(self, url: str, max_questions: int = 10, **kwargs) -> List[dict]:
        with Pipeline("PDF QA Generation") as pipeline:
            load_pdf = LoadPDFFromURL(url=url)
            chunk_text = ChunkText()
            generate_questions = GenerateQuestions(llm=self.llm, max_questions=max_questions)
            generate_answers = GenerateAnswers(llm=self.llm)

            load_pdf >> chunk_text >> generate_questions >> generate_answers

        result = pipeline.run()
        return result[0]["qa_pairs"]

if __name__ == "__main__":
    generator = DatasetGenerator(
        model="meta-llama/Meta-Llama-3.1-70B-Instruct",
        api_key="your_api_key_here"
    )
    qa_pairs = generator.generate_from_pdf("https://example.com/sample.pdf", max_questions=5)
    print(json.dumps(qa_pairs, indent=2))