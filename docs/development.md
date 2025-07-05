# Development Guide

## Project Structure

```
arweave-today-ai-podcaster/
├── arweave_podcaster/          # Main package
│   ├── __init__.py            # Package initialization
│   ├── core/                  # Core functionality
│   │   ├── __init__.py
│   │   └── podcast_generator.py
│   ├── services/              # External service integrations
│   │   ├── __init__.py
│   │   ├── data_service.py
│   │   ├── gemini_service.py
│   │   └── video_service.py
│   └── utils/                 # Utility functions
│       ├── __init__.py
│       ├── audio_utils.py
│       ├── config.py
│       ├── file_utils.py
│       └── text_utils.py
├── tests/                     # Test suite
├── scripts/                   # Utility scripts
├── docs/                      # Documentation
├── data/                      # Data storage
├── output/                    # Generated outputs
├── main.py                    # CLI entry point
├── setup.py                   # Package setup
├── pyproject.toml            # Modern packaging config
├── requirements.txt          # Dependencies
└── README.md                 # Project documentation
```

## Development Setup

1. **Clone and setup virtual environment:**
```bash
git clone <repository>
cd arweave-today-ai-podcaster
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install in development mode:**
```bash
pip install -e .
pip install -e .[dev]  # Include development dependencies
```

3. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your API keys
```

## Code Style

The project follows PEP 8 with additional conventions:

### Formatting
- Line length: 88 characters (Black default)
- Use Black for code formatting: `black .`
- Use isort for import sorting: `isort .`

### Type Hints
- All public functions must have type hints
- Use `Optional[T]` for nullable types
- Use `Dict[str, Any]` for JSON-like data

### Docstrings
- Use Google-style docstrings
- Include Args, Returns, and Raises sections
- Provide examples for complex functions

Example:
```python
def process_data(data: Dict[str, Any], option: str = "default") -> Optional[str]:
    """
    Process input data according to the specified option.
    
    Args:
        data: Dictionary containing input data
        option: Processing option, defaults to "default"
        
    Returns:
        Processed string or None if processing failed
        
    Raises:
        ValueError: If data format is invalid
        
    Example:
        >>> result = process_data({"key": "value"}, "advanced")
        >>> print(result)
        "processed_value"
    """
    pass
```

## Testing

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=arweave_podcaster

# Run specific test file
pytest tests/test_text_utils.py

# Run with verbose output
pytest -v
```

### Writing Tests
- Use pytest framework
- Place tests in `tests/` directory
- Name test files `test_*.py`
- Use descriptive test names
- Include both unit and integration tests

Example test:
```python
def test_format_news_topics():
    """Test news topics formatting with multiple items."""
    topics = [
        {"nature": "funding", "headline": "Grant", "body": "Details"},
        {"nature": "event", "headline": "Hackathon", "body": "Info"}
    ]
    
    result = format_news_topics(topics)
    
    assert "First up, in funding news:" in result
    assert "And finally, in event news:" in result
    assert len(result.split("\n\n")) == 2
```

## Architecture Patterns

### Service Layer Pattern
- Services handle external integrations (APIs, file systems)
- Core logic remains independent of external dependencies
- Services are injected into core classes

### Factory Pattern
- Use factory functions for service creation
- Enables easy configuration and testing
- Example: `create_gemini_service()`

### Error Handling Strategy
- Return `None` or `False` for expected failures
- Raise exceptions only for unexpected errors
- Log errors with context information
- Provide user-friendly error messages

## Adding New Features

### Adding a New Service

1. Create service file in `services/` directory
2. Implement service class with clear interface
3. Add factory function for service creation
4. Update `__init__.py` with exports
5. Add configuration options if needed
6. Write comprehensive tests

Example service structure:
```python
class NewService:
    def __init__(self, config_param: str):
        self.config = config_param
    
    def process(self, data: Any) -> Optional[Result]:
        try:
            # Service logic here
            return result
        except Exception as e:
            print(f"Service error: {e}")
            return None

def create_new_service() -> Optional[NewService]:
    if not config.NEW_SERVICE_CONFIGURED:
        return None
    return NewService(config.NEW_SERVICE_PARAM)
```

### Adding Utilities

1. Add function to appropriate utility module
2. Include comprehensive docstring
3. Add type hints
4. Handle errors gracefully
5. Write unit tests

### Extending Configuration

1. Add new config parameter to `Config` class
2. Update `.env.example` with documentation
3. Add validation if required
4. Update documentation

## Release Process

1. **Update version numbers:**
   - `setup.py`
   - `pyproject.toml`
   - `arweave_podcaster/__init__.py`

2. **Run full test suite:**
   ```bash
   pytest
   black --check .
   isort --check-only .
   mypy arweave_podcaster
   ```

3. **Update documentation:**
   - Update README.md
   - Update CHANGELOG.md
   - Review API documentation

4. **Create release:**
   - Tag version: `git tag v1.0.0`
   - Push tags: `git push --tags`
   - Create GitHub release

## Performance Considerations

- Use lazy loading for heavy dependencies (Whisper model)
- Cache expensive operations when possible
- Stream large files rather than loading into memory
- Implement connection pooling for HTTP requests
- Consider async/await for I/O bound operations

## Security Best Practices

- Never commit API keys or secrets
- Use environment variables for configuration
- Validate all user inputs
- Use secure HTTP (verify SSL certificates when possible)
- Sanitize file paths to prevent directory traversal
