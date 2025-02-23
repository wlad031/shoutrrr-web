# shoutrrr-web

[![GitHub release (latest by date)](https://img.shields.io/github/v/release/wlad031/shoutrrr-web)](https://github.com/wlad031/shoutrrr-web/releases)
[![Docker Pulls](https://img.shields.io/docker/pulls/wlad031/shoutrrr-web)](https://hub.docker.com/r/wlad031/shoutrrr-web)
[![License](https://img.shields.io/github/license/wlad031/shoutrrr-web)](https://github.com/wlad031/shoutrrr-web/blob/master/LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/wlad031/shoutrrr-web)](https://github.com/wlad031/shoutrrr-web/issues)

A Flask-based web interface for the [Shoutrrr](https://containrrr.dev/shoutrrr/) notification router, enabling HTTP-based access to various notification services.

[Docker Hub](https://hub.docker.com/r/wlad031/shoutrrr-web) | [Changelog](CHANGELOG.md) | [Contributing](CONTRIBUTING.md)

## Motivation

Shoutrrr is a powerful notification router that supports multiple services like Slack, Discord, Email, and more. However, it's primarily designed as a CLI tool. shoutrrr-web bridges this gap by providing a RESTful API interface to Shoutrrr, making it easy to:

- Send notifications from any application that can make HTTP requests
- Route notifications based on tags
- Configure multiple notification services with different purposes
- Manage notification routing through simple YAML configuration

## Installation

### Prerequisites

- Python 3.x
- [Shoutrrr CLI](https://containrrr.dev/shoutrrr/v0.8) installed and available in PATH

### Security

The application requires API key authentication. All requests must include an `X-Api-Key` header with a valid API key. API keys are stored in a text file (default: `api_keys.txt`), with one key per line.

Example `api_keys.txt`:
```text
your-api-key-1
your-api-key-2
```

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/username/shoutrrr-web.git
   cd shoutrrr-web
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up API keys:
   ```bash
   cp keys-example.txt api_keys.txt
   # Edit api_keys.txt to add your API keys (one per line)
   ```

4. Create a configuration file based on the example:
   ```bash
   cp config-example.yml config.yml
   ```

4. Edit `config.yml` to add your notification services:
   ```yaml
   service1:
     url: "your-shoutrrr-url"
     is_default: true
     tags:
       - alert
       - notification
   ```

## Usage

### Docker Compose

You can run shoutrrr-web using Docker Compose. Here's a basic example:

```yaml
version: '3'
services:
  shoutrrr-web:
    image: ghcr.io/wlad031/shoutrrr-web:0.2.3
    environment:
      - PORT=80
      - CONFIG_PATH=/config/config.yml
      - API_KEYS_FILE=/config/api_keys.txt
    volumes:
      - ./config:/config
    ports:
      - "80:80"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:80/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

Make sure to create a `config` directory with your `config.yml` and `api_keys.txt` files before starting the container.

### Starting the Server (Manual)

```bash
export CONFIG_PATH=my_config.yml # Optional: defaults to config.yml
export API_KEYS_FILE=my_api_keys.txt  # Optional: defaults to api_keys.txt
python shoutrrr-web.py
```

The server will start on port 80 by default. You can change this using the `PORT` environment variable.

### API Endpoints

#### Health Check
```bash
curl http://localhost:80/health
```
Returns `200 OK` with `{"status": "healthy"}` when the service is running properly. This endpoint does not require authentication and is useful for monitoring and container orchestration.

#### Notifications

Send a notification to default services:
```bash
curl -X POST http://localhost:80/send \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: your-api-key" \
  -d '{"message": "Hello, World!"}'
```

Send a notification to services with specific tags:
```bash
curl -X POST http://localhost:80/send \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: your-api-key" \
  -d '{
    "message": "Alert: System CPU usage high",
    "tags": ["alert"]
  }'
```

### Configuration

The application uses a YAML configuration file to define notification services:

- `url`: The Shoutrrr URL for the service
- `is_default`: (boolean) Whether to send to this service when no tags are specified
- `tags`: (list) Tags for selective notification routing

Example configuration:
```yaml
service1:
  url: "slack://token@channel"
  is_default: true
  tags:
    - alert
    - monitoring

service2:
  url: "discord://token@channel"
  is_default: false
  tags:
    - logs
    - debug
```

### Environment Variables

- `CONFIG_PATH`: Path to the YAML configuration file
- `API_KEYS_FILE`: Path to the API keys file (default: "api_keys.txt")
- `PORT`: Server port (default: 80)
- `SHOUTRRR_BINARY`: Path to the Shoutrrr binary (default: "shoutrrr")

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.md)  file for details.
