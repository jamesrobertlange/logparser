# Log Analyzer

This Flask application analyzes log data from two periods and generates a report comparing crawl rates and URL visibility.

## Features

- Upload two CSV files containing log data
- Generate a detailed analysis report
- Create CSV, Markdown, and PNG versions of the report
- Dark mode UI with purple text
- Option to delete all uploaded and generated files

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/log-analyzer.git
   cd log-analyzer
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Install wkhtmltoimage:
   - On macOS: `brew install wkhtmltopdf`
   - On Ubuntu: `sudo apt-get install wkhtmltopdf`
   - For other systems, check the [wkhtmltopdf downloads page](https://wkhtmltopdf.org/downloads.html)

   Note: wkhtmltoimage is typically included with wkhtmltopdf.

## Usage

1. Run the Flask application:
   ```
   python app.py
   ```

2. Open a web browser and go to `http://localhost:5000`

3. Upload two CSV files containing log data for different periods

4. View the generated report and download CSV, Markdown, or PNG versions

5. Use the "Delete All Files" button to clean up uploaded and generated files when done

## Troubleshooting

If you encounter issues with PNG generation, ensure that `wkhtmltoimage` is properly installed and accessible in your system's PATH. You may need to specify the path to the `wkhtmltoimage` executable in the `app.py` file:

```python
import imgkit
config = imgkit.config(wkhtmltoimage='/path/to/wkhtmltoimage')

# In the generate_png function:
imgkit.from_string(styled_html, output_path, config=config)
```

Replace `/path/to/wkhtmltoimage` with the actual path on your system.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)