import os
from pathlib import Path
from distilabel.distiset import create_distiset
from huggingface_hub import HfApi
import datasets
from datasets import Dataset

def find_pipeline_folders(cache_dir):
    return list(cache_dir.glob("*/*"))

def choose_folder(folders):
    print("Available pipeline folders:")
    for i, folder in enumerate(folders):
        print(f"{i}: {folder}")
    while True:
        try:
            choice = int(input("Enter the number of the pipeline folder you want to use: "))
            if 0 <= choice < len(folders):
                return folders[choice]
        except ValueError:
            pass
        print("Invalid choice. Please try again.")

def find_data_folder(pipeline_folder):
    data_folder = pipeline_folder / "data"
    if not data_folder.exists():
        raise FileNotFoundError(f"Data folder not found in {pipeline_folder}")
    return data_folder

def create_dataset_from_cache(data_folder):
    try:
        distiset = create_distiset(data_folder)
        if not distiset:
            raise ValueError("No data found in the cache")
        
        print("\nAvailable steps:")
        steps = list(distiset.keys())
        for i, step in enumerate(steps):
            print(f"{i}: {step}")
        
        step_choice = int(input("Enter the number of the step you want to use: "))
        step_name = steps[step_choice]
        
        return distiset[step_name]["train"]
    except Exception as e:
        print(f"Error creating dataset: {e}")
        return None

def prepare_dataset_for_hub(dataset):
    # Convert to standard Dataset format if it's not already
    if not isinstance(dataset, Dataset):
        dataset = Dataset.from_dict(dataset.to_dict())
    
    # Ensure the dataset has at least one string column for the viewer
    if not any(isinstance(dataset.features[col], datasets.features.Value) and 
               dataset.features[col].dtype == 'string' for col in dataset.features):
        dataset = dataset.add_column("text", ["Sample text" for _ in range(len(dataset))])
    
    return dataset

def push_to_hub(dataset, repo_name, token):
    try:
        is_public = input("Do you want to make the dataset public? (yes/no): ").lower() == 'yes'
        
        dataset = prepare_dataset_for_hub(dataset)
        
        dataset.push_to_hub(
            repo_name, 
            token=token, 
            private=not is_public,
            embed_external_files=True
        )
        print(f"Dataset successfully pushed to {repo_name}")
        print(f"You can view your dataset at: https://huggingface.co/datasets/{repo_name}")
    except Exception as e:
        print(f"Error pushing to Hugging Face Hub: {e}")

def main():
    cache_dir = Path(os.path.expanduser("~")) / ".cache" / "distilabel" / "pipelines"
    
    pipeline_folders = find_pipeline_folders(cache_dir)
    if not pipeline_folders:
        print("No pipeline folders found in the cache directory.")
        return

    pipeline_folder = choose_folder(pipeline_folders)
    
    try:
        data_folder = find_data_folder(pipeline_folder)
        dataset = create_dataset_from_cache(data_folder)
        
        if dataset is not None:
            repo_name = input("Enter the repository name (e.g., 'your-username/your-dataset-name'): ")
            token = input("Enter your Hugging Face API token: ")
            push_to_hub(dataset, repo_name, token)
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()