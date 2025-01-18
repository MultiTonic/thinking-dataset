# @file thinking_dataset/pipeworks/pipes/load_templates_pipe.py
# @description Pipe for loading templates.
# @version 1.0.17
# @license MIT

import pandas as pd
from .pipe import Pipe
from thinking_dataset.utils.log import Log
from thinking_dataset.template.template_loader import TemplateLoader
from thinking_dataset.template.template_schema import TemplateSchema


class LoadTemplatesPipe(Pipe):

    def __init__(self, config):
        super().__init__(config)
        self.template_schema = TemplateSchema.GENERATE_CABLE
        self.column_name = "template"

    def _create_df(self) -> pd.DataFrame:
        columns = ['id', self.column_name]
        df = pd.DataFrame(columns=columns)
        df.loc[0] = [None, None]
        return df

    def _get_template_path(self) -> str:
        template = self.config.get(self.column_name)
        Log.info(f"Template path: {template}")

        if template is None:
            raise ValueError("Template path is not set in the configuration")

        return template

    def _load_template(self, template_path: str) -> str:
        loader = TemplateLoader(template_path, self.template_schema)
        template = loader.load()
        return template

    def _populate_template(self, df: pd.DataFrame) -> pd.DataFrame:
        path = self._get_template_path()
        template = self._load_template(path)
        df[self.column_name] = [template] * len(df)
        df['id'] = range(1, len(df) + 1)
        return df

    def flow(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        Log.info("Starting LoadTemplatesPipe")

        flush = self.config.get("flush", True)
        if flush:
            df = self._create_df()
            Log.info("Flush enabled. Reset DataFrame.")

        df = self._populate_template(df)

        Log.info("Finished LoadTemplatesPipe")

        return df
