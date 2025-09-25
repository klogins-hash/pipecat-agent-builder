"""Custom exceptions for Pipecat Agent Builder."""

from typing import Optional, Dict, Any


class PipecatBuilderException(Exception):
    """Base exception for Pipecat Agent Builder."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ConfigurationError(PipecatBuilderException):
    """Raised when configuration is invalid or missing."""
    pass


class APIKeyError(PipecatBuilderException):
    """Raised when API keys are missing or invalid."""
    pass


class VectorizationError(PipecatBuilderException):
    """Raised when documentation vectorization fails."""
    pass


class CodeGenerationError(PipecatBuilderException):
    """Raised when code generation fails."""
    pass


class DeploymentError(PipecatBuilderException):
    """Raised when deployment fails."""
    pass


class MCPConnectionError(PipecatBuilderException):
    """Raised when MCP connection to Windsurf Cascade fails."""
    pass


class ValidationError(PipecatBuilderException):
    """Raised when input validation fails."""
    pass


class ResourceLimitError(PipecatBuilderException):
    """Raised when resource limits are exceeded."""
    pass


class ConversationError(PipecatBuilderException):
    """Raised when conversation interface encounters errors."""
    pass


class KnowledgeSourceError(PipecatBuilderException):
    """Raised when knowledge source processing fails."""
    pass
