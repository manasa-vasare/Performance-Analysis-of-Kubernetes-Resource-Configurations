import os
import pandas as pd
import matplotlib.pyplot as plt

def generate_comparison_charts():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    results_dir = os.path.join(base_dir, "results")
    analysis_dir = os.path.join(base_dir, "analysis")

    baseline_csv = os.path.join(results_dir, "baseline_requests.csv")
    restricted_csv = os.path.join(results_dir, "restricted_requests.csv")

    if not os.path.exists(baseline_csv) or not os.path.exists(restricted_csv):
        print("CSV files not found in results directory.")
        return

    df_base = pd.read_csv(baseline_csv)
    df_rest = pd.read_csv(restricted_csv)

    # Filter out Aggregated row for endpoint breakdown
    df_base_ep = df_base[df_base['Name'] != 'Aggregated'].set_index('Name')
    df_rest_ep = df_rest[df_rest['Name'] != 'Aggregated'].set_index('Name')

    endpoints = df_base_ep.index.tolist()

    # 1. Latency Comparison Chart (Median Response Time in ms)
    fig, ax = plt.subplots(figsize=(8, 5))
    x = range(len(endpoints))
    width = 0.35

    base_latencies = [df_base_ep.loc[ep, 'Median Response Time'] for ep in endpoints]
    rest_latencies = [df_rest_ep.loc[ep, 'Median Response Time'] for ep in endpoints]

    ax.bar([p - width/2 for p in x], base_latencies, width, label='Baseline (500m CPU)', color='#2b5c8f')
    ax.bar([p + width/2 for p in x], rest_latencies, width, label='Restricted (100m CPU)', color='#c0392b')

    ax.set_ylabel('Median Response Time (ms)')
    ax.set_title('Endpoint Median Latency: Baseline vs Restricted')
    ax.set_xticks(list(x))
    ax.set_xticklabels(endpoints)
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    plt.tight_layout()
    latency_chart_path = os.path.join(analysis_dir, "latency_comparison.png")
    plt.savefig(latency_chart_path, dpi=300)
    plt.close()
    print(f"Saved latency comparison to {latency_chart_path}")

    # 2. Aggregated Throughput & Total Requests Comparison
    base_agg = df_base[df_base['Name'] == 'Aggregated'].iloc[0]
    rest_agg = df_rest[df_rest['Name'] == 'Aggregated'].iloc[0]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5))

    # Throughput
    ax1.bar(['Baseline', 'Restricted'], [base_agg['Requests/s'], rest_agg['Requests/s']], color=['#2b5c8f', '#c0392b'])
    ax1.set_ylabel('Requests / Second')
    ax1.set_title('Throughput (req/s)')
    ax1.grid(axis='y', linestyle='--', alpha=0.7)

    # Total completed requests
    ax2.bar(['Baseline', 'Restricted'], [base_agg['Request Count'], rest_agg['Request Count']], color=['#2b5c8f', '#c0392b'])
    ax2.set_ylabel('Total Completed Requests')
    ax2.set_title('Request Count (2 min test)')
    ax2.grid(axis='y', linestyle='--', alpha=0.7)

    plt.tight_layout()
    throughput_chart_path = os.path.join(analysis_dir, "throughput_comparison.png")
    plt.savefig(throughput_chart_path, dpi=300)
    plt.close()
    print(f"Saved throughput comparison to {throughput_chart_path}")

if __name__ == '__main__':
    generate_comparison_charts()
