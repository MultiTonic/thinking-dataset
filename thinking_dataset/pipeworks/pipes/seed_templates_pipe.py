# @file thinking_dataset/pipeworks/pipes/seed_templates_pipe.py
# @description Pipe for seeding templates with data.
# @version 1.0.2
# @license MIT

from .pipe import Pipe
from thinking_dataset.utils.log import Log


class SeedTemplatesPipe(Pipe):
    """
    Pipe to seed templates with specific values.
    """

    def flow(self, df, **kwargs):
        Log.info("Starting SeedTemplatesPipe")

        table = self.config.get("table")
        seed_amount = self.config.get("seed_amount")
        Log.info(f"Table: {table}, Seed Amount: {seed_amount}")

        Log.info(f"Incoming DataFrame: {df}")

        Log.info("Finished SeedTemplatesPipe")
        return df
