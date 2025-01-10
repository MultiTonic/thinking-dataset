"""
@file thinking_dataset/datasets/operations/get_whoami.py
@description Retrieves information about the authenticated user.
@version 1.0.0
@license MIT
"""

from .operation import Operation
from thinking_dataset.utils.log import Log


class GetWhoami(Operation):
    """
    A class to retrieve information about the authenticated user.
    """

    def execute(self):
        """
        Retrieves information about the authenticated user.
        """
        try:
            user_info = self.data_tonic.api.whoami()
            Log.info(f"Retrieved user info: {user_info}")
            return user_info
        except Exception as e:
            Log.error(self.log, f"Error retrieving user info: {e}")
            return None
