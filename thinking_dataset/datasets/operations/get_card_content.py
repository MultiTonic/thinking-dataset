# @file thinking_dataset/datasets/operations/get_card_content.py
# @description Operation to retrieve dataset card content.
# @version 1.0.0
# @license MIT

from .base_operation import Operation


class GetCardContent(Operation):
    """
    Operation class to retrieve dataset card content.
    """

    def execute(self, dataset_id):
        """
        Retrieves card content of the dataset.
        """
        dataset_info = self.data_tonic.get_dataset_info(dataset_id)
        card_content = dataset_info.card_data
        self.log_info(f"Dataset card data: {card_content}")
        return card_content
