"""
Pipes Package.

This package contains all pipeline processing pipes for the
Thinking Dataset project.

Functions:
    None

Classes:
    Pipe: Abstract base class for all processing pipes.
    AddIdPipe
    ChunkingPipe
    DropColumnsPipe
    ExportTablesPipe
    FileExtractorPipe
    FileUploadHfApiPipe
    FilterBySizePipe
    HandleMissingValuesPipe
    NormalizeTextPipe
    QueryGenerationPipe
    RemapColumnsPipe
    RemoveDuplicatesPipe
    ResponseGenerationPipe
    SubsetPipe
"""

from .pipe import Pipe
from .add_id_pipe import AddIdPipe
from .chunking_pipe import ChunkingPipe
from .drop_columns_pipe import DropColumnsPipe
from .export_tables_pipe import ExportTablesPipe
from .file_extractor_pipe import FileExtractorPipe
from .file_upload_hf_api_pipe import FileUploadHfApiPipe
from .filter_by_size_pipe import FilterBySizePipe
from .handle_missing_values_pipe import HandleMissingValuesPipe
from .normalize_text_pipe import NormalizeTextPipe
from .query_generation_pipe import QueryGenerationPipe
from .remap_columns_pipe import RemapColumnsPipe
from .remove_duplicates_pipe import RemoveDuplicatesPipe
from .response_generation_pipe import ResponseGenerationPipe
from .subset_pipe import SubsetPipe

__version__ = "0.0.2"
__author__ = "MultiTonic Team"
__copyright__ = "Copyright (c) 2025 MultiTonic Team"
__license__ = "MIT"

__all__ = [
    "Pipe",
    "AddIdPipe",
    "ChunkingPipe",
    "DropColumnsPipe",
    "ExportTablesPipe",
    "FileExtractorPipe",
    "FileUploadHfApiPipe",
    "FilterBySizePipe",
    "HandleMissingValuesPipe",
    "NormalizeTextPipe",
    "QueryGenerationPipe",
    "RemapColumnsPipe",
    "RemoveDuplicatesPipe",
    "ResponseGenerationPipe",
    "SubsetPipe",
]
