"""
@file thinking_dataset/datasets/operations/get_whoami.py
@description Retrieves information about the authenticated user.
@version 1.0.0
@license MIT
@author Kara Rawson
@see {@link https://github.com/MultiTonic|GitHub Repository}
@see {@link https://huggingface.co/DataTonic|GitHub Organization}
"""

from .base_operation import BaseOperation
from ...utilities.log import Log


class GetWhoami(BaseOperation):
    """
    A class to retrieve information about the authenticated user.

    Methods
    -------
    execute()
        Retrieves information about the authenticated user.
    """

    def execute(self):
        """
        Retrieves information about the authenticated user.

        Returns
        -------
        dict
            User information.
        """
        try:
            user_info = self.data_tonic.api.whoami()
            Log.info(self.log, f"Retrieved user info: {user_info}")
            return user_info
        except Exception as e:
            Log.error(self.log, f"Error retrieving user info: {e}")
            return None
