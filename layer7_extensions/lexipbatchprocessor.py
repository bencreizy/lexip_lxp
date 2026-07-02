# lexipbatchprocessor.py
# Batch Processor Module for structural compilation of entire directories of Lexip curves

from pathlib import Path
from .lexip_batch_processor import LexipBatchProcessor as CoreProcessor

class LexipBatchProcessor:
    """
    High-level automation interface managing directory-scale pipeline conversions.
    Integrates raw vector ingestion, geometric optimization, and structural reporting.
    """
    def __init__(self, input_dir: str, output_dir: str):
        self.processor = CoreProcessor(input_dir, output_dir)

    def execute_video_pipeline(self, smooth: bool = True, simplify: bool = True, max_frames: int = None):
        """
        Scan input workspace to unpack raw temporal tracking paths out of compressed containers
        and compile clean, spatial .lxp coordinate files.
        """
        self.processor.batch_convert_videos(smooth=smooth, simplify=simplify, max_frames=max_frames)

    def execute_geometric_simplification(self, epsilon: float = 2.0):
        """
        Execute precision spatial boundary compression over existing asset states within
        the monitored path, reducing processing overhead.
        """
        self.processor.batch_resimplify(epsilon=epsilon)

    def compile_structural_metrics(self, report_filename: str = "analysis.json"):
        """
        Perform exhaustive multi-file geometric inspection passes to generate localized 
        spatial metrics, including tracking counts, lengths, and centroids.
        """
        self.processor.batch_analyze(report_name=report_filename)
