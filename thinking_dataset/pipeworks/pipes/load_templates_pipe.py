# @file thinking_dataset/pipeworks/pipes/load_templates_pipe.py
# @description Pipe for loading templates.
# @version 1.0.10
# @license MIT

import pandas as pd
from .pipe import Pipe
from thinking_dataset.utils.log import Log
from thinking_dataset.template.template_loader import TemplateLoader
from thinking_dataset.template.template_schema import TemplateSchema


class LoadTemplatesPipe(Pipe):
    """
    Pipe to load templates from the specified path.
    """

    def __init__(self, config):
        super().__init__(config)
        self.template_schema = TemplateSchema.GENERATE_CABLE

    def _create_df(self):
        """
        Private method to create the DataFrame with the necessary columns.
        """
        columns = ['template']
        df = pd.DataFrame(columns=columns)
        df.loc[0] = [None]
        return df

    def _get_template_path(self):
        """
        Private method to retrieve the template path from the configuration.
        """
        template = self.config.get("template")
        Log.info(f"Config template path: {template}")

        if template is None:
            raise ValueError("Template path is not set in the configuration")

        return template

    def _load_template(self, template_path):
        """
        Private method to load the template from the specified path.
        """
        loader = TemplateLoader(template_path, self.template_schema)
        template = loader.load()
        return template

    def _populate_template(self, df):
        """
        Private method to populate the DataFrame with the loaded template.
        """
        template_path = self._get_template_path()
        template = self._load_template(template_path)
        df['template'] = [template] * len(df)
        return df

    def flow(self, df, **kwargs):
        Log.info("Starting LoadTemplatesPipe")

        flush = self.config.get("flush", True)
        if flush:
            df = self._create_df()
            Log.info("Flush enabled. Reset DataFrame.")

        df = self._populate_template(df)

        Log.info("Finished LoadTemplatesPipe")

        return df
