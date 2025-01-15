# @file thinking_dataset/pipeworks/pipes/load_templates_pipe.py
# @description Pipe for loading templates.
# @version 1.0.1
# @license MIT

from .pipe import Pipe
from thinking_dataset.utils.log import Log
from thinking_dataset.templates.template_loader import TemplateLoader


class LoadTemplatesPipe(Pipe):
    """
    Pipe to load templates from the specified path.
    """

    def flow(self, df, **kwargs):
        Log.info("Starting LoadTemplatesPipe")

        try:
            # Retrieve template path
            template_path = self.config.get("template")
            Log.info(f"Config template path: {template_path}")

            # Check if template path is correctly set
            if template_path is None:
                Log.info("Template path is not set in the configuration")
                raise ValueError(
                    "Template path is not set in the configuration")

            schema = {
                # Define your JSON schema here
            }

            # Load the template
            loader = TemplateLoader(template_path, schema)
            template = loader.load()
            df['template'] = [template] * len(df)

            Log.info("Finished LoadTemplatesPipe")
            return df
        except Exception as e:
            Log.info(f"An error occurred in LoadTemplatesPipe: {str(e)}")
            raise
