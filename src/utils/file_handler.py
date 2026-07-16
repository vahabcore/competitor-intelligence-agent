import json
import csv
from pathlib import Path
from typing import Any, List, Dict, Union

from .logger import get_logger
from .exceptions import FileImportError, FileExportError

logger = get_logger(__name__)

class FileHandler:
    """
    An Object-Oriented utility for handling file imports and exports.
    Provides methods to read and write JSON, CSV, and text files robustly.
    """
    def __init__(self, base_dir: Union[str, Path] = "."):
        """
        Initialize the FileHandler.
        
        Args:
            base_dir (Union[str, Path]): The root directory for file operations. 
                                         Defaults to the current working directory.
        """
        self.base_dir = Path(base_dir)
        # Ensure the base directory exists
        try:
            self.base_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to initialize base directory {self.base_dir}: {e}")
            raise

    def _get_full_path(self, filename: str) -> Path:
        """Resolve the full path given a filename relative to the base directory."""
        return self.base_dir / filename

    def read_json(self, filename: str) -> Any:
        """
        Reads a JSON file.
        
        Args:
            filename (str): The name of the file to read.
            
        Returns:
            Any: The parsed JSON data.
            
        Raises:
            FileImportError: If reading or parsing fails.
        """
        path = self._get_full_path(filename)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Successfully read JSON file: {path}")
            return data
        except Exception as e:
            msg = f"Failed to read JSON file at {path}: {e}"
            logger.error(msg)
            raise FileImportError(msg) from e

    def write_json(self, filename: str, data: Any, indent: int = 4) -> None:
        """
        Writes data to a JSON file.
        
        Args:
            filename (str): The name of the file to write.
            data (Any): The data to serialize to JSON.
            indent (int): Formatting indent.
            
        Raises:
            FileExportError: If writing or serialization fails.
        """
        path = self._get_full_path(filename)
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent)
            logger.info(f"Successfully wrote JSON file: {path}")
        except Exception as e:
            msg = f"Failed to write JSON file at {path}: {e}"
            logger.error(msg)
            raise FileExportError(msg) from e

    def read_csv(self, filename: str) -> List[Dict[str, str]]:
        """
        Reads a CSV file into a list of dictionaries.
        
        Args:
            filename (str): The name of the file to read.
            
        Returns:
            List[Dict[str, str]]: The rows of the CSV file.
            
        Raises:
            FileImportError: If reading fails.
        """
        path = self._get_full_path(filename)
        try:
            with open(path, 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                data = list(reader)
            logger.info(f"Successfully read CSV file: {path} ({len(data)} rows)")
            return data
        except Exception as e:
            msg = f"Failed to read CSV file at {path}: {e}"
            logger.error(msg)
            raise FileImportError(msg) from e

    def write_csv(self, filename: str, data: List[Dict[str, Any]], fieldnames: List[str] = None) -> None:
        """
        Writes a list of dictionaries to a CSV file.
        
        Args:
            filename (str): The name of the file to write.
            data (List[Dict[str, Any]]): The data to write.
            fieldnames (List[str], optional): The column headers. 
                                              If None, inferred from the first row.
            
        Raises:
            FileExportError: If writing fails.
        """
        path = self._get_full_path(filename)
        try:
            if not data and not fieldnames:
                logger.warning(f"No data or fieldnames provided for {filename}. Writing empty file.")
                with open(path, 'w', encoding='utf-8', newline='') as f:
                    pass
                return

            if not fieldnames:
                fieldnames = list(data[0].keys())

            with open(path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            logger.info(f"Successfully wrote CSV file: {path}")
        except Exception as e:
            msg = f"Failed to write CSV file at {path}: {e}"
            logger.error(msg)
            raise FileExportError(msg) from e

    def read_text(self, filename: str) -> str:
        """
        Reads a plain text file.
        
        Args:
            filename (str): The name of the file to read.
            
        Returns:
            str: The contents of the file.
            
        Raises:
            FileImportError: If reading fails.
        """
        path = self._get_full_path(filename)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.info(f"Successfully read text file: {path}")
            return content
        except Exception as e:
            msg = f"Failed to read text file at {path}: {e}"
            logger.error(msg)
            raise FileImportError(msg) from e

    def write_text(self, filename: str, content: str) -> None:
        """
        Writes a string to a plain text file.
        
        Args:
            filename (str): The name of the file to write.
            content (str): The text content to write.
            
        Raises:
            FileExportError: If writing fails.
        """
        path = self._get_full_path(filename)
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Successfully wrote text file: {path}")
        except Exception as e:
            msg = f"Failed to write text file at {path}: {e}"
            logger.error(msg)
            raise FileExportError(msg) from e
