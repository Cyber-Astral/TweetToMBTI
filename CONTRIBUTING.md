# Contributing to TweetToMBTI

First off, thank you for considering contributing to TweetToMBTI! It's people like you that make this tool better for everyone.

## Code of Conduct

By participating in this project, you are expected to uphold our Code of Conduct:
- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive criticism
- Show empathy towards other community members

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples**
- **Include screenshots if applicable**
- **Describe the behavior you observed and expected**
- **Include your environment details** (OS, Python version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear and descriptive title**
- **Provide a detailed description of the proposed enhancement**
- **Explain why this enhancement would be useful**
- **List any alternative solutions you've considered**

### Pull Requests

1. **Fork the repo** and create your branch from `main`
2. **Set up the development environment**:
   ```bash
   pip install -r requirements-dev.txt
   pre-commit install
   ```

3. **Make your changes**:
   - Follow the existing code style
   - Add tests for new functionality
   - Update documentation as needed

4. **Ensure quality**:
   ```bash
   # Run tests
   make test
   
   # Check code style
   make lint
   
   # Format code
   make format
   ```

5. **Commit your changes**:
   - Use clear and meaningful commit messages
   - Follow conventional commits format if possible

6. **Push and create a Pull Request**:
   - Fill in the PR template
   - Link any related issues
   - Ensure all checks pass

## Development Setup

1. Clone your fork:
   ```bash
   git clone https://github.com/your-username/TweetToMBTI.git
   cd TweetToMBTI
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements-dev.txt
   pre-commit install
   ```

4. Set up API keys:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

## Style Guide

### Python Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use [Black](https://github.com/psf/black) for formatting (100 char line length)
- Use [isort](https://pycqa.github.io/isort/) for import sorting
- Write docstrings for all public functions and classes

### Git Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

### Testing

- Write tests for all new functionality
- Maintain or improve test coverage
- Place unit tests in `tests/unit/`
- Place integration tests in `tests/integration/`

## Project Structure

```
TweetToMBTI/
├── scraper/          # Tweet collection module
├── mbti_analyzer/    # MBTI analysis module
├── common/           # Shared utilities
├── tests/            # Test suite
└── docs/             # Documentation
```

## Questions?

Feel free to open an issue with the label "question" if you have any questions about contributing.