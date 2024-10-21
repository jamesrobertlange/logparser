import csv
from collections import defaultdict
from pathlib import Path
import os
import shutil

from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from markupsafe import Markup
import markdown
import imgkit

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a real secret key

# Create log_uploads directory if it doesn't exist
os.makedirs("log_uploads", exist_ok=True)

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

def format_number(num):
    return f"{num:,}"

def generate_report(analysis, file_path):
    total = analysis[-1]
    top_20_increase = sorted([item for item in analysis[:-1] if item['Difference'] > 0], key=lambda x: x['Difference'], reverse=True)[:20]
    top_20_decrease = sorted([item for item in analysis[:-1] if item['Difference'] < 0], key=lambda x: x['Difference'])[:20]
    top_20_percent_increase = sorted([item for item in analysis[:-1] if item['Percent_Change'] != float('inf')], key=lambda x: x['Percent_Change'], reverse=True)[:20]
    top_20_percent_decrease = sorted([item for item in analysis[:-1] if item['Percent_Change'] < 0], key=lambda x: x['Percent_Change'])[:20]

    report = f"""# Crawl Analysis Report

## Overview
This report compares crawl data from two periods to analyze changes in crawl rates and URL visibility.

## Key Findings
1. Total Crawls:
   - Period 1: {format_number(total['Period1_Crawls'])}
   - Period 2: {format_number(total['Period2_Crawls'])}
   - Difference: {format_number(total['Difference'])} {'increase' if total['Difference'] > 0 else 'decrease'}
   - Percent Change: {total['Percent_Change']:.2f}% {'increase' if total['Percent_Change'] > 0 else 'decrease'}

2. URL Count:
   - Period 1: {format_number(len([item for item in analysis if item['Period1_Crawls'] > 0]))}
   - Period 2: {format_number(len([item for item in analysis if item['Period2_Crawls'] > 0]))}

3. Average Crawls per URL:
   - Period 1: {format_number(int(total['Period1_Crawls'] / (len(analysis) - 1)))}
   - Period 2: {format_number(int(total['Period2_Crawls'] / (len(analysis) - 1)))}

## Top 20 URLs with Highest Crawl Increase:
"""

    for i, item in enumerate(top_20_increase, 1):
        report += f"{i}. {item['URL']} ({format_number(item['Difference'])} increase)\n"

    report += "\n## Top 20 URLs with Highest Crawl Decrease:\n"

    for i, item in enumerate(top_20_decrease, 1):
        report += f"{i}. {item['URL']} ({format_number(abs(item['Difference']))} decrease)\n"

    report += "\n## Top 20 URLs with Highest Crawl Increase Percentage:\n"

    for i, item in enumerate(top_20_percent_increase, 1):
        report += f"{i}. {item['URL']} ({item['Percent_Change']:.2f}% increase)\n"

    report += "\n## Top 20 URLs with Highest Crawl Decrease Percentage:\n"

    for i, item in enumerate(top_20_percent_decrease, 1):
        report += f"{i}. {item['URL']} ({abs(item['Percent_Change']):.2f}% decrease)\n"

    report += """
## Analysis
The data shows a significant change in crawl rates across the analyzed URLs. """

    if total['Difference'] > 0:
        report += f"The total number of crawls increased by {total['Percent_Change']:.2f}%, from {format_number(total['Period1_Crawls'])} in Period 1 to {format_number(total['Period2_Crawls'])} in Period 2. This substantial growth in crawl activity suggests a major change in search engine behavior or website visibility."
    else:
        report += f"The total number of crawls decreased by {abs(total['Percent_Change']):.2f}%, from {format_number(total['Period1_Crawls'])} in Period 1 to {format_number(total['Period2_Crawls'])} in Period 2. This significant reduction in crawl activity suggests a major change in search engine behavior or a decrease in website visibility."

    with open(file_path, 'w') as f:
        f.write(report)

    return report

def generate_png(markdown_content, output_path):
    try:
        # Convert Markdown to HTML
        html_content = markdown.markdown(markdown_content)
        
        # Add some basic styling
        styled_html = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    background-color: #1e1e1e;
                    color: #b19cd9;
                    padding: 20px;
                }}
                h1, h2 {{
                    color: #d7bfdc;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }}
                th {{
                    background-color: #2d2d2d;
                }}
            </style>
        </head>
        <body>
        {html_content}
        </body>
        </html>
        """
        
        # Convert HTML to PNG
        imgkit.from_string(styled_html, output_path)
        return True
    except Exception as e:
        print(f"PNG generation failed: {str(e)}")
        return False

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        period1 = request.files['period1']
        period2 = request.files['period2']

        period1_path = Path("log_uploads") / period1.filename
        period2_path = Path("log_uploads") / period2.filename

        period1.save(period1_path)
        period2.save(period2_path)

        data1 = read_csv(period1_path)
        data2 = read_csv(period2_path)

        analysis = analyze_crawl_data(data1, data2)

        output_csv = Path("log_uploads") / "crawl_analysis.csv"
        output_report = Path("log_uploads") / "crawl_analysis_report.md"
        output_png = Path("log_uploads") / "crawl_analysis_report.png"

        write_csv(analysis, output_csv)
        report_content = generate_report(analysis, output_report)

        # Generate PNG
        png_generated = generate_png(report_content, str(output_png))
        if not png_generated:
            flash("PNG generation failed. Please check the logs for more information.")

        # Convert Markdown to HTML
        html_content = markdown.markdown(report_content)

        return render_template('result.html', report=Markup(html_content), png_generated=png_generated)

    return render_template('index.html')

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(Path("log_uploads") / filename, as_attachment=True)

@app.route('/delete_files', methods=['POST'])
def delete_files():
    try:
        for file in os.listdir("log_uploads"):
            file_path = os.path.join("log_uploads", file)
            if os.path.isfile(file_path):
                os.unlink(file_path)
        return redirect(url_for('index'))
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == '__main__':
    app.run(debug=True)