import time

class Telemetry:
    """Class for tracking processing telemetry."""
    
    def __init__(self):
        self.start_time = time.time()
        self.total_attempts = 0
        self.successful_generations = 0
        self.failed_generations = 0
        self.errors_by_type = {}
        self.last_log_time = time.time()
        self.total_expected = 0
        
    def reset_stats(self, expected_total=0):
        """Reset the statistics."""
        self.start_time = time.time()
        self.total_attempts = 0
        self.successful_generations = 0
        self.failed_generations = 0
        self.errors_by_type = {}
        self.last_log_time = time.time()
        self.total_expected = expected_total
    
    def log_success(self, split_name, elapsed_time=0.0):
        """Log a successful generation."""
        self.total_attempts += 1
        self.successful_generations += 1
    
    def log_failure(self, split_name, record_id, error_type):
        """Log a failed generation."""
        self.total_attempts += 1
        self.failed_generations += 1
        self.errors_by_type[error_type] = self.errors_by_type.get(error_type, 0) + 1
    
    def get_telemetry_lines(self, total_records):
        """Get summary of telemetry as a list of log lines."""
        elapsed = time.time() - self.start_time
        remaining = max(0, total_records - self.successful_generations)
        
        # Calculate generation rate (generations per minute)
        gpm = (self.total_attempts / elapsed * 60) if elapsed > 0 else 0
        
        # Calculate request-level error rate (percentage of failed attempts)
        request_error_rate = (self.failed_generations / max(1, self.total_attempts) * 100)
        
        # Calculate record-level error rate (percentage of failed records out of processed)
        records_processed = self.successful_generations + self.failed_generations
        record_error_rate = (self.failed_generations / max(1, records_processed) * 100)
        
        # Estimate remaining time
        if gpm > 0 and request_error_rate < 100:
            success_rate = 1 - (request_error_rate / 100)
            est_minutes = remaining / (gpm * success_rate) if success_rate > 0 else float('inf')
            time_remaining = f"{est_minutes:.1f} min" if est_minutes < 60 else f"{est_minutes/60:.1f} hours"
        else:
            time_remaining = "unknown"
        
        # Create telemetry lines
        telemetry_lines = [
            "=== Telemetry ===",
            f"- Progress: {self.successful_generations}/{total_records} complete ({self.successful_generations/max(1,total_records)*100:.1f}%)",
            f"- Status: {self.successful_generations} success, {self.failed_generations} errors ({record_error_rate:.1f}% error rate)",
            f"- Requests: {self.total_attempts} total requests, {self.failed_generations} failed ({request_error_rate:.1f}% request error rate)",
            f"- Performance: {gpm:.1f} req/min",
            f"- Remaining: {remaining} records, Est. time: {time_remaining}"
        ]
        
        return telemetry_lines
    
    def get_telemetry_string(self, total_records):
        """Legacy method that returns all telemetry as a single string."""
        return "\n".join(self.get_telemetry_lines(total_records))