import csv
from collections import defaultdict
from pathlib import Path

def read_csv(file_path):
    data = defaultdict(int)
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for row in reader:
            url, crawls = row[0], int(row[1])
            data[url] = crawls
    return data

def analyze_crawl_data(data1, data2):
    all_urls = set(data1.keys()) | set(data2.keys())
    analysis = []
    total1, total2 = 0, 0

    for url in all_urls:
        crawls1 = data1.get(url, 0)
        crawls2 = data2.get(url, 0)
        diff = crawls2 - crawls1
        percent_change = (diff / crawls1 * 100) if crawls1 != 0 else float('inf')
        
        analysis.append({
            'URL': url,
            'Period1_Crawls': crawls1,
            'Period2_Crawls': crawls2,
            'Difference': diff,
            'Percent_Change': percent_change
        })
        
        total1 += crawls1
        total2 += crawls2

    analysis.sort(key=lambda x: x['Difference'], reverse=True)
    
    total_diff = total2 - total1
    total_percent_change = (total_diff / total1 * 100) if total1 != 0 else float('inf')
    
    analysis.append({
        'URL': 'Total',
        'Period1_Crawls': total1,
        'Period2_Crawls': total2,
        'Difference': total_diff,
        'Percent_Change': total_percent_change
    })

    return analysis

def write_csv(data, file_path):
    with open(file_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['URL', 'Period1_Crawls', 'Period2_Crawls', 'Difference', 'Percent_Change'])
        writer.writeheader()
        writer.writerows(data)

def generate_report(analysis, file_path):
    total = analysis[-1]
    top_5 = analysis[:5]

    report = f"""# Crawl Analysis Report

## Overview
This report compares crawl data from two periods to analyze changes in crawl rates and URL visibility.

## Key Findings
1. Total Crawls:
   - Period 1: {total['Period1_Crawls']}
   - Period 2: {total['Period2_Crawls']}
   - Difference: {total['Difference']} {'increase' if total['Difference'] > 0 else 'decrease'}
   - Percent Change: {total['Percent_Change']:.2f}% {'increase' if total['Percent_Change'] > 0 else 'decrease'}

2. URL Count:
   - Period 1: {len([item for item in analysis if item['Period1_Crawls'] > 0])}
   - Period 2: {len([item for item in analysis if item['Period2_Crawls'] > 0])}

3. Average Crawls per URL:
   - Period 1: {total['Period1_Crawls'] / (len(analysis) - 1):.2f}
   - Period 2: {total['Period2_Crawls'] / (len(analysis) - 1):.2f}

4. Top 5 URLs with Highest Crawl Change:
"""

    for i, item in enumerate(top_5, 1):
        report += f"   {i}. {item['URL']} ({item['Difference']} {'increase' if item['Difference'] > 0 else 'decrease'})\n"

    report += """
## Analysis
The data shows a significant change in crawl rates across the analyzed URLs. """

    if total['Difference'] > 0:
        report += f"The total number of crawls increased by {total['Percent_Change']:.2f}%, from {total['Period1_Crawls']} in Period 1 to {total['Period2_Crawls']} in Period 2. This substantial growth in crawl activity suggests a major change in search engine behavior or website visibility."
    else:
        report += f"The total number of crawls decreased by {abs(total['Percent_Change']):.2f}%, from {total['Period1_Crawls']} in Period 1 to {total['Period2_Crawls']} in Period 2. This significant reduction in crawl activity suggests a major change in search engine behavior or a decrease in website visibility."

    with open(file_path, 'w') as f:
        f.write(report)

def main():
    period1_file = 'aug-18-25.csv'
    period2_file = 'sep-18-25.csv'
    output_csv = 'crawl_analysis.csv'
    output_report = 'crawl_analysis_report.md'

    data1 = read_csv(period1_file)
    data2 = read_csv(period2_file)

    analysis = analyze_crawl_data(data1, data2)

    write_csv(analysis, output_csv)
    generate_report(analysis, output_report)

    print(f"Analysis complete. Results written to {output_csv} and {output_report}")

if __name__ == "__main__":
    main()