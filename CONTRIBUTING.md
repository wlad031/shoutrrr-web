# Contributing to shoutrrr-web

Thank you for your interest in contributing to shoutrrr-web! We welcome contributions from the community to help make this project better.

## Getting Started

1. Fork the repository and clone it locally
2. Create a new branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes
4. Write or update tests if necessary
5. Run tests locally to ensure everything works
6. Commit your changes with clear, descriptive commit messages
7. Push to your fork and submit a pull request

## Development Setup

1. Install Python 3.x and [Shoutrrr CLI](https://containrrr.dev/shoutrrr/v0.8)
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy and configure example files:
   ```bash
   cp config-example.yml config.yml
   cp keys-example.txt api_keys.txt
   ```
4. Start the development server:
   ```bash
   python shoutrrr-web.py
   ```

## Pull Request Guidelines

- Create a clear, descriptive pull request title
- Include a description of what your changes do and why they should be included
- Reference any related issues
- Update documentation if you're adding or changing features
- Add your changes to CHANGELOG.md under an "Unreleased" section
- Ensure all tests pass

## Code Style

- Follow PEP 8 guidelines for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions focused and concise
- Include type hints where appropriate

## Testing

- Add tests for new features
- Ensure existing tests pass
- Test edge cases and error conditions
- Include both unit tests and integration tests where appropriate

## Documentation

- Update README.md for user-facing changes
- Add docstrings to new functions and classes
- Keep code comments current
- Update configuration examples if needed

## Questions or Problems?

If you have questions or run into problems, please open an issue in the GitHub repository.

## License

By contributing to shoutrrr-web, you agree that your contributions will be licensed under the MIT License.
