"""Input validation and security for Pipecat Agent Builder."""

import re
import urllib.parse
from typing import List, Dict, Any, Optional
from pathlib import Path

from core.config import AgentRequirements, KnowledgeSourceConfig
from core.exceptions import ValidationError
from core.logger import setup_logger

logger = setup_logger("validators")


class SecurityValidator:
    """Security validation for user inputs."""
    
    # Dangerous patterns to block
    DANGEROUS_PATTERNS = [
        r'__import__',
        r'eval\s*\(',
        r'exec\s*\(',
        r'subprocess',
        r'os\.system',
        r'open\s*\(',
        r'file\s*\(',
        r'input\s*\(',
        r'raw_input\s*\(',
        r'compile\s*\(',
        r'globals\s*\(',
        r'locals\s*\(',
        r'vars\s*\(',
        r'dir\s*\(',
        r'getattr',
        r'setattr',
        r'delattr',
        r'hasattr',
    ]
    
    # Safe characters for names
    SAFE_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9\s\-_\.]+$')
    
    @classmethod
    def validate_agent_name(cls, name: str) -> str:
        """Validate agent name for security and format."""
        if not name or not name.strip():
            raise ValidationError("Agent name cannot be empty")
        
        name = name.strip()
        
        if len(name) > 100:
            raise ValidationError("Agent name too long (max 100 characters)")
        
        if not cls.SAFE_NAME_PATTERN.match(name):
            raise ValidationError("Agent name contains invalid characters")
        
        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, name, re.IGNORECASE):
                raise ValidationError(f"Agent name contains potentially dangerous content")
        
        return name
    
    @classmethod
    def validate_description(cls, description: str) -> str:
        """Validate agent description."""
        if not description or not description.strip():
            raise ValidationError("Agent description cannot be empty")
        
        description = description.strip()
        
        if len(description) > 1000:
            raise ValidationError("Description too long (max 1000 characters)")
        
        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, description, re.IGNORECASE):
                raise ValidationError("Description contains potentially dangerous content")
        
        return description
    
    @classmethod
    def validate_url(cls, url: str) -> str:
        """Validate URL for security."""
        try:
            parsed = urllib.parse.urlparse(url)
            
            # Must have scheme and netloc
            if not parsed.scheme or not parsed.netloc:
                raise ValidationError("Invalid URL format")
            
            # Only allow HTTP/HTTPS
            if parsed.scheme not in ['http', 'https']:
                raise ValidationError("Only HTTP/HTTPS URLs are allowed")
            
            # Block localhost and private IPs
            hostname = parsed.hostname
            if hostname:
                if hostname in ['localhost', '127.0.0.1', '0.0.0.0']:
                    raise ValidationError("Localhost URLs are not allowed")
                
                # Block private IP ranges
                if (hostname.startswith('192.168.') or 
                    hostname.startswith('10.') or 
                    hostname.startswith('172.')):
                    raise ValidationError("Private IP addresses are not allowed")
            
            return url
            
        except Exception as e:
            raise ValidationError(f"Invalid URL: {e}")
    
    @classmethod
    def validate_file_path(cls, file_path: str) -> str:
        """Validate file path for security."""
        # Block path traversal attempts
        if '..' in file_path or file_path.startswith('/'):
            raise ValidationError("Path traversal attempts are not allowed")
        
        # Block system directories
        dangerous_paths = ['/etc', '/usr', '/bin', '/sbin', '/var', '/sys', '/proc']
        for dangerous in dangerous_paths:
            if file_path.startswith(dangerous):
                raise ValidationError(f"Access to {dangerous} is not allowed")
        
        return file_path


class RequirementsValidator:
    """Validate agent requirements for completeness and correctness."""
    
    VALID_CHANNELS = ['phone', 'web', 'mobile', 'whatsapp', 'telegram']
    VALID_LANGUAGES = ['en', 'es', 'fr', 'de', 'it', 'pt', 'zh', 'ja', 'ko', 'ru', 'ar', 'hi']
    VALID_USE_CASES = [
        'customer_service', 'personal_assistant', 'education', 'healthcare',
        'sales', 'support', 'entertainment', 'business', 'creative', 'other'
    ]
    
    @classmethod
    def validate_requirements(cls, requirements: AgentRequirements) -> AgentRequirements:
        """Validate complete agent requirements."""
        logger.info(f"Validating requirements for agent: {requirements.name}")
        
        # Validate basic fields
        requirements.name = SecurityValidator.validate_agent_name(requirements.name)
        requirements.description = SecurityValidator.validate_description(requirements.description)
        
        # Validate use case
        if requirements.use_case not in cls.VALID_USE_CASES:
            logger.warning(f"Unknown use case: {requirements.use_case}")
        
        # Validate channels
        for channel in requirements.channels:
            if channel not in cls.VALID_CHANNELS:
                raise ValidationError(f"Invalid channel: {channel}")
        
        if not requirements.channels:
            requirements.channels = ['web']  # Default to web
        
        # Validate languages
        for lang in requirements.languages:
            if lang not in cls.VALID_LANGUAGES:
                raise ValidationError(f"Unsupported language: {lang}")
        
        if not requirements.languages:
            requirements.languages = ['en']  # Default to English
        
        # Validate knowledge sources
        for ks in requirements.knowledge_sources:
            cls._validate_knowledge_source(ks)
        
        # Validate integrations
        cls._validate_integrations(requirements.integrations)
        
        # Validate deployment config
        cls._validate_deployment_config(requirements.deployment)
        
        logger.info("Requirements validation completed successfully")
        return requirements
    
    @classmethod
    def _validate_knowledge_source(cls, ks: KnowledgeSourceConfig):
        """Validate individual knowledge source."""
        if ks.type == 'web':
            SecurityValidator.validate_url(ks.source)
        elif ks.type == 'document':
            SecurityValidator.validate_file_path(ks.source)
        elif ks.type not in ['web', 'document', 'api', 'database']:
            raise ValidationError(f"Invalid knowledge source type: {ks.type}")
    
    @classmethod
    def _validate_integrations(cls, integrations: List[str]):
        """Validate integration list."""
        valid_integrations = [
            'twilio', 'telnyx', 'plivo', 'exotel',
            'zendesk', 'salesforce', 'hubspot',
            'slack', 'teams', 'discord',
            'whatsapp', 'telegram',
            'google_calendar', 'outlook',
            'notion', 'airtable'
        ]
        
        for integration in integrations:
            if integration not in valid_integrations:
                logger.warning(f"Unknown integration: {integration}")
    
    @classmethod
    def _validate_deployment_config(cls, deployment):
        """Validate deployment configuration."""
        if deployment.scaling_min < 0:
            raise ValidationError("Minimum scaling cannot be negative")
        
        if deployment.scaling_max < deployment.scaling_min:
            raise ValidationError("Maximum scaling cannot be less than minimum")
        
        if deployment.scaling_max > 100:
            raise ValidationError("Maximum scaling too high (limit: 100)")


class APIKeyValidator:
    """Validate API keys and service configurations."""
    
    @classmethod
    def validate_api_keys(cls, settings) -> Dict[str, bool]:
        """Validate all configured API keys."""
        results = {}
        
        # Required keys
        required_keys = {
            'openai_api_key': 'sk-',
            'deepgram_api_key': None,  # No standard prefix
            'cartesia_api_key': None,
        }
        
        for key_name, prefix in required_keys.items():
            key_value = getattr(settings, key_name, None)
            if not key_value:
                results[key_name] = False
                continue
            
            if prefix and not key_value.startswith(prefix):
                results[key_name] = False
                continue
            
            if len(key_value) < 10:  # Minimum reasonable length
                results[key_name] = False
                continue
            
            results[key_name] = True
        
        return results
    
    @classmethod
    def validate_service_compatibility(cls, requirements: AgentRequirements) -> List[str]:
        """Validate service compatibility and return warnings."""
        warnings = []
        
        # Check language support
        if requirements.stt_service and requirements.languages:
            primary_lang = requirements.languages[0]
            if primary_lang not in ['en', 'es', 'fr', 'de'] and requirements.stt_service.provider == 'deepgram':
                warnings.append(f"Deepgram may have limited support for language: {primary_lang}")
        
        # Check channel compatibility
        if 'phone' in requirements.channels:
            if not any(integration in requirements.integrations for integration in ['twilio', 'telnyx', 'plivo']):
                warnings.append("Phone channel requires telephony integration (Twilio, Telnyx, or Plivo)")
        
        return warnings


class ResourceValidator:
    """Validate resource usage and limits."""
    
    MAX_KNOWLEDGE_SOURCES = 10
    MAX_INTEGRATIONS = 5
    MAX_LANGUAGES = 3
    
    @classmethod
    def validate_resource_limits(cls, requirements: AgentRequirements):
        """Validate resource usage against limits."""
        
        if len(requirements.knowledge_sources) > cls.MAX_KNOWLEDGE_SOURCES:
            raise ValidationError(f"Too many knowledge sources (max: {cls.MAX_KNOWLEDGE_SOURCES})")
        
        if len(requirements.integrations) > cls.MAX_INTEGRATIONS:
            raise ValidationError(f"Too many integrations (max: {cls.MAX_INTEGRATIONS})")
        
        if len(requirements.languages) > cls.MAX_LANGUAGES:
            raise ValidationError(f"Too many languages (max: {cls.MAX_LANGUAGES})")
    
    @classmethod
    def estimate_resource_usage(cls, requirements: AgentRequirements) -> Dict[str, Any]:
        """Estimate resource usage for the agent."""
        
        # Base resource usage
        cpu_units = 1.0
        memory_mb = 512
        storage_mb = 100
        
        # Adjust based on features
        cpu_units += len(requirements.languages) * 0.2
        cpu_units += len(requirements.knowledge_sources) * 0.3
        cpu_units += len(requirements.integrations) * 0.1
        
        memory_mb += len(requirements.knowledge_sources) * 100
        memory_mb += len(requirements.languages) * 50
        
        storage_mb += len(requirements.knowledge_sources) * 200
        
        # Adjust for channels
        if 'phone' in requirements.channels:
            cpu_units += 0.5
            memory_mb += 200
        
        return {
            'estimated_cpu_units': round(cpu_units, 2),
            'estimated_memory_mb': int(memory_mb),
            'estimated_storage_mb': int(storage_mb),
            'complexity_score': cls._calculate_complexity(requirements)
        }
    
    @classmethod
    def _calculate_complexity(cls, requirements: AgentRequirements) -> str:
        """Calculate complexity score for the agent."""
        score = 0
        
        score += len(requirements.channels)
        score += len(requirements.languages) * 2
        score += len(requirements.knowledge_sources) * 3
        score += len(requirements.integrations) * 2
        
        if score <= 5:
            return "simple"
        elif score <= 15:
            return "moderate"
        else:
            return "complex"
