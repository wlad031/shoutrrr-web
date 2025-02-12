import subprocess
import os
import json
import yaml
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
        config_path = os.getenv("CONFIG_PATH")
    if config_path and not os.path.exists(config_path):
        app.logger.error(f"Config file {config_path} does not exist")
        exit(1)
    if not config_path:
        app.logger.debug("No config file specified")
        return {}
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        app.logger.info(f"Loaded configuration: {config}")
        return config
    except Exception as e:
        app.logger.error(f"Failed to load configuration from {config_path}: {str(e)}")
        exit(1)


def verify_shoutrrr_installed(shoutrrr):
    """Verify that the shoutrrr binary is installed."""
    try:
        subprocess.run(
            [shoutrrr, "--help"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        app.logger.error(f"Shoutrrr binary check failed: {e.stderr.strip()}")
        exit(1)


def verify_urls(shoutrrr, config):
    """Verify all URLs in the configuration."""
    urls = [c.get("url") for name, c in config.items() if c.get("url")]
    if not urls:
        app.logger.error("No Shoutrrr URLs found. Exiting.")
        exit(1)
    for url in urls:
        try:
            app.logger.debug(f"Verifying URL: {url}")
            output = subprocess.run(
                [shoutrrr, "verify", "--url", url],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
            )
            app.logger.info(f"Verification successful for {url}:\n{output.stdout}")
        except subprocess.CalledProcessError as e:
            app.logger.error(
                f"Verification failed for URL: {url}. Error: {e.stderr.strip()}"
            )
            exit(1)


def get_shoutrrr_binary():
    """Return the shoutrrr binary path."""
    return os.getenv("SHOUTRRR_BINARY", "shoutrrr")


def send_notification(shoutrrr, config, message, tags=None):
    """Send a notification using the shoutrrr binary based on tags."""
    res = []
    if not tags:
        for name, c in config.items():
            if not c.get("is_default", False):
                continue
            url = c.get("url")
            if not url:
                continue
            try:
                app.logger.info(f"Sending message to {name}: {message}")
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
        if not res:
            app.logger.error("No default URLs found. Check configuration.")
    else:
        requested_tags = [tag.lower() for tag in tags]
        for name, c in config.items():
            item_tags = c.get("tags", [])
            item_tags_lower = [t.lower() for t in item_tags]
            if not any(rt in item_tags_lower for rt in requested_tags):
                continue
            url = c.get("url")
            if not url:
                continue
            try:
                app.logger.info(
                    f"Sending message to {name} (tags: {item_tags}): {message}"
                )
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
        if not res:
            app.logger.error(
                f"Requested tags: {tags}, but no matching configuration found"
            )
    return res


def build_message(data):
    """Build the message string from the incoming data."""
    if "message" in data:
        return data["message"]
    else:
        return f"Unknown message:\n{json.dumps(data)}"


@app.route("/send", methods=["POST"])
@require_api_key
def send():
    shoutrrr = get_shoutrrr_binary()
    config = load_config()
    data = request.json or {}
    message = build_message(data)
    tags = data.get("tags", None)
    send_result = send_notification(shoutrrr, config, message, tags)
    len_success = len([r for r in send_result if r["success"]])
    if send_result and len_success == len(send_result):
        return jsonify({"status": "success", "message": "Notification sent"}), 200
    elif send_result and len_success > 0:
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
    else:
        return jsonify({"status": "error", "message": "Notification failed"}), 500


def main():
    shoutrrr = get_shoutrrr_binary()
    config = load_config()
    verify_shoutrrr_installed(shoutrrr)
    verify_urls(shoutrrr, config)


if __name__ == "__main__":
    main()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 80)))
