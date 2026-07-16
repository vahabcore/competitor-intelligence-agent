import sys
from pathlib import Path

# Add src directory to path so we can import from src.utils
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from utils import FileHandler, get_logger, FileImportError

# Initialize a logger for this script
logger = get_logger("demo_script")

def main():
    logger.info("Starting demonstration of FileHandler utility.")
    
    # Initialize FileHandler targeted at the 'data' directory
    data_dir = Path(__file__).parent.parent / 'data'
    handler = FileHandler(base_dir=data_dir)

    # 1. JSON Export / Import
    json_filename = "demo_config.json"
    sample_config = {"app_name": "CompetitorIntelligenceAgent", "version": "1.0.0", "active": True}
    logger.info(f"Writing to {json_filename}...")
    handler.write_json(json_filename, sample_config)

    logger.info(f"Reading from {json_filename}...")
    read_config = handler.read_json(json_filename)
    logger.info(f"Read config: {read_config}")

    # 2. CSV Export / Import
    csv_filename = "demo_data.csv"
    sample_data = [
        {"id": 1, "competitor": "Company A", "status": "active"},
        {"id": 2, "competitor": "Company B", "status": "inactive"}
    ]
    logger.info(f"Writing to {csv_filename}...")
    handler.write_csv(csv_filename, sample_data)

    logger.info(f"Reading from {csv_filename}...")
    read_data = handler.read_csv(csv_filename)
    logger.info(f"Read data: {read_data}")

    # 3. Text Export / Import
    text_filename = "demo_notes.txt"
    sample_text = "This is a simple note.\nIt supports multiple lines.\n"
    logger.info(f"Writing to {text_filename}...")
    handler.write_text(text_filename, sample_text)

    logger.info(f"Reading from {text_filename}...")
    read_text = handler.read_text(text_filename)
    logger.info(f"Read text:\n{read_text}")

    # 4. Error Handling Demonstration
    missing_filename = "does_not_exist.json"
    logger.info(f"Attempting to read missing file: {missing_filename}...")
    try:
        handler.read_json(missing_filename)
    except FileImportError as e:
        logger.error(f"Caught expected FileImportError: {e}")

    logger.info("Demonstration completed successfully.")

if __name__ == "__main__":
    main()
