# @file thinking_dataset/pipeworks/pipes/seed_template_pipe.py
# @description Pipe for seeding templates with data.
# @version 1.0.0
# @license MIT

import time
from .pipe import Pipe
from thinking_dataset.utils.log import Log


class SeedTemplatesPipe(Pipe):
    """
    Pipe to seed templates with specific values.
    """

    def flow(self, df, **kwargs):
        Log.info("Starting SeedTemplatesPipe")

        # TODO load 3 random seeds from db table

        time.sleep(1)

        # TODO inject 3 seeds into template in df

        Log.info("Finished SeedTemplatesPipe")
        return df
