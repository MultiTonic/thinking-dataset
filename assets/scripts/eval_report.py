import os
import json
import glob
import numpy as np
import matplotlib.pyplot as plt

def load_result_files(results_dir="./results"):
    """Load all latest_*_results.json files from the results directory."""
    pattern = os.path.join(results_dir, "latest_*_results.json")
    result_files = glob.glob(pattern)
    
    if not result_files:
        print(f"No result files found matching pattern {pattern}")
        return []
    
    print(f"Found {len(result_files)} result files")
    
    results = []
    for file_path in result_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                filename = os.path.basename(file_path)
                data['filename'] = filename
                results.append(data)
                print(f"Loaded {filename}")
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    
    return results

def extract_metrics(results):
    """Extract ROUGE and BLEU metrics along with language information."""
    metrics_data = []
    
    for result in results:
        try:
            # Extract language info
            source_lang = result['metadata']['source_language']
            target_lang = result['metadata']['target_language']
            source_code = result['metadata']['source_code']
            target_code = result['metadata']['target_code']
            
            # Create language pair label
            lang_pair = f"{source_code}-{target_code}"
            lang_full = f"{source_lang} → {target_lang}"
            
            # Extract metrics
            rouge1 = result['rouge'].get('rouge1', 0)
            rouge2 = result['rouge'].get('rouge2', 0)
            rougeL = result['rouge'].get('rougeL', 0)
            bleu = result['bleu'].get('bleu', 0)
            
            # Create a record
            record = {
                'lang_pair': lang_pair,
                'lang_full': lang_full,
                'source_lang': source_lang,
                'target_lang': target_lang,
                'rouge1': rouge1,
                'rouge2': rouge2,
                'rougeL': rougeL,
                'bleu': bleu,
                'filename': result['filename']
            }
            metrics_data.append(record)
            
        except KeyError as e:
            print(f"Missing key in result data: {e}")
            continue
    
    # Sort by language pair for consistency
    metrics_data.sort(key=lambda x: x['lang_pair'])
    return metrics_data

def create_comparison_chart(metrics_data, output_dir="./results", run_id=None):
    """Create a bar chart comparing ROUGE and BLEU metrics across languages."""
    if not metrics_data:
        print("No metrics data to visualize")
        return
    
    # Prepare data for plotting
    lang_pairs = [d['lang_pair'] for d in metrics_data]
    lang_full_names = [d['lang_full'] for d in metrics_data]
    rouge1_scores = [d['rouge1'] for d in metrics_data]
    rougeL_scores = [d['rougeL'] for d in metrics_data]
    bleu_scores = [d['bleu'] for d in metrics_data]
    
    # Set up the chart with adjusted dimensions - wider rather than tall
    fig, ax = plt.subplots(figsize=(max(12, len(lang_pairs) * 0.8), 8))  # Prioritize width over height
    
    # Set position of bars on y-axis
    y_pos = np.arange(len(lang_pairs))
    bar_height = 0.25
    
    # Create horizontal bars
    ax.barh(y_pos - bar_height, rouge1_scores, height=bar_height, label='ROUGE-1', color='skyblue')
    ax.barh(y_pos, rougeL_scores, height=bar_height, label='ROUGE-L', color='lightgreen')
    ax.barh(y_pos + bar_height, bleu_scores, height=bar_height, label='BLEU', color='salmon')
    
    # Add grid lines for reference
    ax.xaxis.grid(True, linestyle='--', alpha=0.7, color='lightgrey')
    
    # Add labels, title, and legend
    ax.set_ylabel('Language Pair', fontweight='bold', fontsize=12)
    ax.set_xlabel('Score (0-1)', fontweight='bold', fontsize=12)
    ax.set_title('ROUGE and BLEU Metrics by Language Pair', fontweight='bold', fontsize=14)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(lang_pairs)
    
    # Ensure x-axis starts at 0 and caps at 1.0 (scores are normalized)
    ax.set_xlim(0, 1.0)
    
    # Add a legend
    ax.legend(loc='lower right')
    
    # Adjust layout and save
    plt.tight_layout()
    
    # Create filename with run_id if available
    if run_id:
        output_filename = f'translation_metrics_comparison_{run_id}.png'
    else:
        output_filename = 'translation_metrics_comparison.png'
    
    output_path = os.path.join(output_dir, output_filename)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_path}")
    
    # Remove plt.show() to avoid displaying in console
    plt.close(fig)

def create_telemetry_chart(metrics_data, output_dir="./results", run_id=None):
    """Create charts visualizing model telemetry (prediction time and rate)."""
    if not metrics_data:
        print("No metrics data to visualize")
        return
    
    # Extract telemetry data
    telemetry_data = []
    for d in metrics_data:
        try:
            filename = d['filename']
            result_file = os.path.join(output_dir, filename)
            with open(result_file, 'r', encoding='utf-8') as f:
                full_data = json.load(f)
                if 'telemetry' in full_data:
                    telemetry = full_data['telemetry']
                    telemetry['lang_pair'] = d['lang_pair']
                    telemetry['lang_full'] = d['lang_full']
                    telemetry_data.append(telemetry)
        except Exception as e:
            print(f"Error loading telemetry from {filename}: {e}")
    
    if not telemetry_data:
        print("No telemetry data found")
        return
    
    # Sort by language pair for consistency
    telemetry_data.sort(key=lambda x: x['lang_pair'])
    
    # Prepare data for plotting
    lang_pairs = [d['lang_pair'] for d in telemetry_data]
    avg_pred_times = [d['avg_pred_time'] for d in telemetry_data]
    pred_rates = [d['pred_rate'] for d in telemetry_data]
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 12))
    
    # First chart: Average Prediction Time
    y_pos = np.arange(len(lang_pairs))
    ax1.barh(y_pos, avg_pred_times, height=0.5, color='cornflowerblue')
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(lang_pairs)
    ax1.set_xlabel('Time (seconds)', fontweight='bold')
    ax1.set_ylabel('Language Pair', fontweight='bold')
    ax1.set_title('Average Prediction Time by Language Pair', fontweight='bold')
    ax1.xaxis.grid(True, linestyle='--', alpha=0.7, color='lightgrey')
    
    # Second chart: Prediction Rate
    ax2.barh(y_pos, pred_rates, height=0.5, color='mediumseagreen')
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(lang_pairs)
    ax2.set_xlabel('Rate (predictions/minute)', fontweight='bold')
    ax2.set_ylabel('Language Pair', fontweight='bold')
    ax2.set_title('Prediction Rate by Language Pair', fontweight='bold')
    ax2.xaxis.grid(True, linestyle='--', alpha=0.7, color='lightgrey')
    
    # Adjust layout
    plt.tight_layout()
    
    # Create filename with run_id if available
    if run_id:
        output_filename = f'translation_telemetry_{run_id}.png'
    else:
        output_filename = 'translation_telemetry.png'
    
    output_path = os.path.join(output_dir, output_filename)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Telemetry chart saved to {output_path}")
    plt.close(fig)
    
    # Create an additional chart comparing runtime across language pairs
    fig, ax = plt.subplots(figsize=(12, 8))
    runtimes = [d['runtime'] for d in telemetry_data]
    
    # Create horizontal bars for runtime
    ax.barh(y_pos, runtimes, height=0.5, color='coral')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(lang_pairs)
    ax.set_xlabel('Total Runtime (seconds)', fontweight='bold')
    ax.set_ylabel('Language Pair', fontweight='bold')
    ax.set_title('Total Processing Time by Language Pair', fontweight='bold')
    ax.xaxis.grid(True, linestyle='--', alpha=0.7, color='lightgrey')
    
    plt.tight_layout()
    
    # Save runtime chart
    if run_id:
        output_filename = f'translation_runtime_{run_id}.png'
    else:
        output_filename = 'translation_runtime.png'
    
    output_path = os.path.join(output_dir, output_filename)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Runtime chart saved to {output_path}")
    plt.close(fig)

def extract_run_id(results):
    """Extract the run_id from the results data."""
    if not results:
        return None
    
    # Try to get a consistent run_id from all results
    run_ids = set()
    for result in results:
        if 'metadata' in result and 'run_id' in result['metadata']:
            run_ids.add(result['metadata']['run_id'])
    
    if len(run_ids) == 1:
        # All results have the same run_id
        return next(iter(run_ids))
    elif len(run_ids) > 1:
        # Multiple run_ids found, use the most common one
        print(f"Warning: Multiple run IDs found: {run_ids}")
        return next(iter(run_ids))  # Just use the first one
    else:
        # No run_id found
        print("Warning: No run ID found in results")
        return None

def main():
    print("Loading translation evaluation results...")
    results = load_result_files()
    
    if not results:
        print("No results found. Exiting.")
        return
    
    print("Extracting metrics...")
    metrics_data = extract_metrics(results)
    
    # Extract run_id from the results
    run_id = extract_run_id(results)
    if run_id:
        print(f"Using run ID: {run_id}")
    
    print("Creating comparison chart...")
    create_comparison_chart(metrics_data, run_id=run_id)
    
    print("Creating telemetry charts...")
    create_telemetry_chart(metrics_data, run_id=run_id)
    
    print("Done!")

if __name__ == "__main__":
    main()
