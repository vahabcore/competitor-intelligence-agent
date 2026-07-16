class FileIOError(Exception):
    """Base exception for file input/output errors."""
    pass

class FileImportError(FileIOError):
    """Raised when there is an error importing a file."""
    pass

class FileExportError(FileIOError):
    """Raised when there is an error exporting to a file."""
    pass
