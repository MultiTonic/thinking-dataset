
# Configure logging to use UTF-8 encoding
# Set up logging to use UTF-8 encoding
# logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.StreamHandler(sys.stdout)])

# # Ensure sys.stdout uses UTF-8 encoding
# sys.stdout.reconfigure(encoding='utf-8')
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load environment variables from .env file
# load_dotenv()

# # Retrieve OneAI API key from environment variables
# oneai_api_key = os.getenv("ONEAI_API_KEY", "e75810fc0c96453eb15c865e00edea24")


    # def dump(self, **kwargs):
    #     dump = super().dump(**kwargs)
    #     dump['cable_sample'] = []  
    #     return dump



# # Prepare Messages Step
# class PrepareMessagesStep(Step):
#     @property
#     def inputs(self) -> List[str]:
#         return ["prepared_content"]

#     @property
#     def outputs(self) -> List[str]:
#         return ["messages"]

#     def process(self, inputs: StepInput) -> StepOutput:
#         for batch in inputs:
#             output_batch = []
#             for item in batch:
#                 if "prepared_content" in item:
#                     messages = [
#                         {"role": "system", "content": SITREPPROMPT},
#                         {"role": "user", "content": item["prepared_content"]}
#                     ]
#                     output_batch.append({"messages": messages})
#                 else:
#                     logging.warning(f"Missing 'prepared_content' in item: {item}")
#             yield output_batch



        # format_summary_sft = FormatChatGenerationSFT(
        #     name="format_summary_sft",
        #     input_batch_size=32
        # )

        # format_comparison_sft = FormatChatGenerationSFT(
        #     name="format_comparison_sft",
        #     input_batch_size=32
        # )

        # Define the pipeline flow