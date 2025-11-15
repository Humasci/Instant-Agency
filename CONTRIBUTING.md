# Contributing to Instant Agency

Thank you for your interest in contributing to Instant Agency! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/Humasci/Instant-Agency/issues)
2. If not, create a new issue with:
   - Clear, descriptive title
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, versions, etc.)
   - Screenshots if applicable

### Suggesting Features

1. Check existing feature requests
2. Create a new issue with:
   - Clear description of the feature
   - Use cases and benefits
   - Possible implementation approach
   - Any relevant examples or mockups

### Code Contributions

1. **Fork the repository**

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the existing code style
   - Add tests for new features
   - Update documentation as needed
   - Keep commits focused and atomic

4. **Test your changes**
   ```bash
   # Run tests
   pytest tests/

   # Run linting
   flake8 agents/
   black agents/ --check

   # Test Docker build
   docker-compose build
   ```

5. **Commit your changes**
   ```bash
   git commit -m "feat: add new prospecting agent"
   ```

   Use conventional commit messages:
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation changes
   - `test:` Test additions/changes
   - `refactor:` Code refactoring
   - `chore:` Maintenance tasks

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Provide a clear description
   - Reference related issues
   - Include screenshots/examples if applicable

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Humasci/Instant-Agency.git
   cd Instant-Agency
   ```

2. **Run setup**
   ```bash
   ./scripts/setup.sh
   ```

3. **Start development environment**
   ```bash
   docker-compose up -d
   ```

4. **Install Python dependencies**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r agents/requirements.txt
   pip install -r requirements-dev.txt
   ```

## Project Structure

- `agents/` - AI agent implementations
- `workflows/` - n8n workflow templates
- `integrations/` - Third-party integrations
- `infrastructure/` - Deployment configs
- `docs/` - Documentation
- `tests/` - Test suites

## Coding Standards

### Python

- Follow PEP 8
- Use type hints
- Write docstrings for all functions
- Maximum line length: 100 characters
- Use `black` for formatting
- Use `flake8` for linting

### JavaScript/n8n

- Use ES6+ syntax
- Clear variable names
- Add comments for complex logic
- Format with Prettier

### YAML

- 2-space indentation
- Clear key names
- Add comments for configuration options

## Testing Guidelines

### Unit Tests

```python
def test_sales_qualification_agent():
    agent = SalesQualificationAgent()
    result = agent.process({
        'lead_id': 123,
        'responses': {...}
    })
    assert result['overall_score'] > 0
```

### Integration Tests

Test interactions between components:
- Agent ↔ Database
- Agent ↔ CRM
- Workflow ↔ Agent

### End-to-End Tests

Test complete workflows from trigger to completion.

## Documentation

- Update README.md for user-facing changes
- Update docs/ for architecture changes
- Add inline comments for complex logic
- Include examples in docstrings

## Review Process

1. Automated checks run on PR creation
2. Maintainers review code
3. Feedback is provided
4. Changes are requested if needed
5. PR is merged when approved

## Community

- **Discussions**: Use GitHub Discussions for questions
- **Issues**: Use GitHub Issues for bugs and features
- **Pull Requests**: For code contributions

## Recognition

Contributors will be recognized in:
- README.md Contributors section
- Release notes
- Project website (coming soon)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Instant Agency! 🚀
