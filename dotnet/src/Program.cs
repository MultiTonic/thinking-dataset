#pragma warning disable SKEXP0070
using System;
using System.Threading.Tasks;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Connectors.Ollama;
using Microsoft.SemanticKernel.TextCompletion;
using Microsoft.Extensions.DependencyInjection;
using static System.Console;

namespace ThinkingDataset
{
    class Program
    {
        static async Task Main(string[] args)
        {
            // Use Llama 3.1 model for the test
            var modelId = "llama-3.1";

            // Local Ollama endpoint
            var endpoint = new Uri("http://localhost:11434");

            var kernelBuilder = Kernel.CreateBuilder();
            kernelBuilder.AddOllamaTextCompletion(modelId, endpoint);
            var kernel = kernelBuilder.Build();

            var textCompletionService = kernel.GetRequiredService<ITextCompletionService>();

            // Example prompt for text completion
            string prompt = "Generate a detailed analysis on the impact of market disruption.";

            // Get the text completion result asynchronously
            var result = await textCompletionService.CompleteAsync(new TextCompletionRequest(prompt));

            // Print the result to the console
            Console.WriteLine(result.Completion);
        }
    }
}
