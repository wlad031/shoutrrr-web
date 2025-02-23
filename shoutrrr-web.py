import subprocess
import os
import json
import yaml
import re
from flask import Flask, request, jsonify
from common_python import (
    configure_logging,
    require_api_key,
    create_health_blueprint,
    log_request_info,
)

app = Flask("Shoutrrr Web")
configure_logging(app)
health_bp = create_health_blueprint()
app.register_blueprint(health_bp)
app.before_request(log_request_info)


def load_config(config_path=None):
    """Load the notification configuration from a YAML file."""
    if not config_path:
        config_path = os.getenv("CONFIG_PATH", "config.yml")
    if not os.path.exists(config_path):
        app.logger.error(f"Config file {config_path} does not exist")
        exit(1)
    try:
        app.logger.info(f"Loading configuration from {config_path}")
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        config_with_service_names = {}
        for name, service in config.items():
            config_with_service_names[name] = {
                    "name": name,
                    "url": service.get("url"),
                    "is_default": service.get("is_default", False),
                    "tags": service.get("tags", []),
            }
        config_string = yaml.dump(config_with_service_names, default_flow_style=False)
        app.logger.info(f"Loaded configuration:\n{config_string}")
        return config_with_service_names
    except Exception as e:
        app.logger.error(f"Failed to load configuration from {config_path}: {str(e)}")
        exit(1)


def get_shoutrrr_binary():
    """Return the shoutrrr binary path."""
    return os.getenv("SHOUTRRR_BINARY", "shoutrrr")


config = load_config()
shoutrrr = get_shoutrrr_binary()


def verify_shoutrrr_installed(shoutrrr):
    """Verify that the shoutrrr binary is installed."""
    try:
        output = subprocess.run(
            [shoutrrr, "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        app.logger.info(f"Detected shoutrrr:{shoutrrr}\n{output.stdout}")
    except subprocess.CalledProcessError as e:
        app.logger.error(f"Shoutrrr binary check failed: {e.stderr.strip()}")
        exit(1)


def verify_urls(shoutrrr, config):
    """Verify all URLs in the configuration."""
    for service in config.values():
        url = service.get("url", None)
        if not service.get("url", None):
            app.logger.error(f"Service {service.get('name')} has no URL")
            exit(1)
        try:
            app.logger.info(f"Verifying URL:\n{url}")
            output = subprocess.run(
                [shoutrrr, "verify", "--url", url],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
            )
            app.logger.info(f"Verification successful:\n{output.stdout}")
        except subprocess.CalledProcessError as e:
            app.logger.error(
                f"Verification failed for URL: {url}. Error: {e.stderr.strip()}"
            )
            exit(1)


def prepare_message(message, service):
    """Prepare the message for sending to a particular URL."""
    url = service.get("url")
    if url.startswith("telegram:"):
        app.logger.debug(f"Service: Telegram: {service.get('name')}")
        if "parseMode=MarkdownV2" in url:
            app.logger.debug(f"Service: Telegram MarkdownV2: {service.get('name')}")
            message = re.sub(r"([!\.\-#\(\)])", r"\\\1", message)
            app.logger.debug(f"Escaped message for Telegram MarkdownV2:\n{message}")
    return message


def choose_services(config, tags=None):
    result = []
    if not tags:
        app.logger.debug(f"No tags requested, looking for default services...")
        result = [
            (name, service)
            for name, service in config.items()
            if service.get("is_default", False)
        ]
        if not result:
            app.logger.error("No default URLs found. Check configuration.")
    else:
        requested_tags = [tag.lower() for tag in tags]
        result = [
            (name, service)
            for name, service in config.items()
            if any(rt in service.get("tags", []) for rt in requested_tags)
        ]
        if not result:
            app.logger.error(
                f"Requested tags: {tags}, but no matching configuration found"
            )
    return result


def send_notification(shoutrrr, config, message, tags=None):
    """Send a notification using the shoutrrr binary based on tags."""

    target_services = choose_services(config, tags)

    res = []
    for name, service in target_services:
        url = service.get("url")
        try:
            app.logger.info(f"Sending message to {name}:\n{message}")
            message = prepare_message(message, service)
            subprocess.run(
                [shoutrrr, "send", "--url", url, "--message", message],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
            )
            app.logger.info(f"Message sent successfully to {name}")
            res.append({"url": url, "success": True})
        except subprocess.CalledProcessError as e:
            app.logger.error(f"Error sending message to {url}: {e.stderr.strip()}")
            res.append({"url": url, "success": False})
    return res


def build_message(data):
    """Build the message string from the incoming data."""
    if "message" in data:
        return data["message"]
    return f"Unknown message:\n{json.dumps(data)}"


@app.route("/send", methods=["POST"])
@require_api_key
def send():
    data = request.json or {}
    message = build_message(data)
    tags = data.get("tags", None)
    send_result = send_notification(shoutrrr, config, message, tags)
    len_success = len([r for r in send_result if r["success"]])
    if send_result and len_success == len(send_result):
        return jsonify({"status": "success", "message": "Notification sent"}), 200
    if send_result and len_success > 0:
        return (
            jsonify(
                {
                    "status": "partial_success",
                    "message": "Notification sent",
                    "success": len_success,
                    "failed": len(send_result) - len_success,
                }
            ),
            200,
        )
    return jsonify({"status": "error", "message": "Notification failed"}), 500


def main():
    verify_shoutrrr_installed(shoutrrr)
    verify_urls(shoutrrr, config)


if __name__ == "__main__":
    main()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 80)))
