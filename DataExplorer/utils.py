# utils.py
from Dataleakage.detection import AdvancedDataLeakDetector
import pandas as pd
from pathlib import Path


def read_file_content(file):
    """Reads the content of a file and returns it as a string or pandas DataFrame."""
    file_path = Path(file)
    if file_path.suffix == '.csv':
        return pd.read_csv(file_path)  # Return content as a DataFrame for CSV
    elif file_path.suffix in ['.xls', '.xlsx']:
        return pd.read_excel(file_path)  # Return content as a DataFrame for Excel
    else:
        with open(file_path, 'r') as f:
            return f.read()  # Return content as a string for text files


def scan_file_for_sensitivity(file):
    """Scans a file for sensitive data and returns the sensitivity score."""
    detector = AdvancedDataLeakDetector()
    # Read the content of the file
    content = read_file_content(file)
    metadata = {'filename': file.name}  # Add filename metadata
    # Perform the analysis using the detector
    scan_result = detector.analyze_file(content, metadata)
    return scan_result.score
