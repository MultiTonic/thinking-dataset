import datetime
from huggingface_hub import HfApi
from datasets import Dataset

class UniqueDatasetRepository:
    def __init__(self, project_name):
        self.project_name = project_name
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.repo_name = f"{self.project_name}-{self.timestamp}"
        self.api = HfApi()
        self.create_repo()

    def create_repo(self):
        self.api.create_repo(self.repo_name, private=True)

    def push_to_hub(self, dataset, commit_message):
        dataset.push_to_hub(self.repo_name, commit_message=commit_message)

class BatchCounter:
    def __init__(self, batch_size=100):
        self.count = 0
        self.batch_size = batch_size

    def increment(self):
        self.count += 1
        return self.count % self.batch_size == 0
