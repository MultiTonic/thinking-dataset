from datasets import Dataset
from hugs import UniqueDatasetRepository

def load_dataset(repo_name):
    repo = UniqueDatasetRepository(repo_name)
    return repo.load_from_hub()

def combine_datasets():
    reasoning_dataset = load_dataset("tonic-thinking-dataset-reasoning")
    financial_dataset = load_dataset("tonic-thinking-dataset-financial")
    medical_dataset = load_dataset("tonic-thinking-dataset-medical")

    combined_dataset = Dataset.from_dict({
        "reasoning": reasoning_dataset,
        "financial": financial_dataset,
        "medical": medical_dataset
    })
    
    combined_repo = UniqueDatasetRepository("tonic-thinking-dataset-combined")
    combined_repo.push_to_hub(combined_dataset, "Final combined multi-domain dataset")

if __name__ == "__main__":
    combine_datasets()