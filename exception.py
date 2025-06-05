class JobMatcherError(Exception):
    """Base class for exceptions in Job Resume Matcher project."""
    pass

class APIQuotaExceededError(JobMatcherError):
    """Exception raised when API quota is exceeded."""
    def __init__(self, message="API quota exceeded. Please check your plan and billing details."):
        self.message = message
        super().__init__(self.message)

class ModelNotFoundError(JobMatcherError):
    """Exception raised when requested model is not found."""
    def __init__(self, message="Requested model not found or unsupported."):
        self.message = message
        super().__init__(self.message)

class InvalidInputError(JobMatcherError):
    """Exception raised for invalid inputs."""
    def __init__(self, message="Invalid input provided."):
        self.message = message
        super().__init__(self.message)
