#!/usr/bin/env python3
import subprocess
import sys
import secrets
import string
import time

PROJECT_NAME = "openproject"


def generate_clear_password(length=100):
    ambiguous = {'O', '0', 'I', 'l', '1'}
    alphabet = ''.join(c for c in (string.ascii_letters + string.digits) if c not in ambiguous)
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def parse_args(argv):
    args = {}
    key = None
    for item in argv:
        if item.startswith("--"):
            key = item.lstrip("-")
            args[key] = True  # default if no value provided
        elif key:
            args[key] = item
            key = None
    return args


def up():
    """Start docker compose services"""
    subprocess.run(["docker", "compose", "-p", PROJECT_NAME, "up", "-d"], check=True)
    time.sleep(120)
    cmd = [
        "docker", "compose", "run", "--rm", "openproject",
        "bash", "-c",
        "RAILS_ENV=production bundle exec rake db:migrate db:seed"
    ]
    subprocess.run(cmd, check=True)


def down():
    """Stop docker compose services and remove volumes"""
    subprocess.run(["docker", "compose", "-p", PROJECT_NAME, "down", "-v"])


class ComposeApp:

    def __init__(self, action, user, host, protocol):
        self.action = action
        self.user = user
        self.host = host
        self.protocol = protocol
        self.env_variables = {
            'POSTGRES_USER': "postgres_postgres_users",
            'POSTGRES_PASSWORD': generate_clear_password(),
            'POSTGRES_DB': "postgres",
            'OPENPROJECT_HOST__NAME': f"{PROJECT_NAME}.{self.user}.{self.host}",
            'OPENPROJECT_SECRET_KEY_BASE': generate_clear_password(),
            'OGNA_USER':user,
            'OGNA_HOST':host,
            'OGNA_PROTOCOL':protocol
        }

    def configure(self):
        with open('.env', 'w+') as env_file:
            for key, value in self.env_variables.items():
                env_file.write(f"{key}={value}")
                env_file.write("\n")

    def deploy(self):
        self.configure()
        if self.action == "up":
            up()
        elif self.action == "down":
            down()
        else:
            print(f"Unknown command: {self.action}")
            print("Available commands: up, down")
            sys.exit(1)


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])

    app = ComposeApp(
        action=args.get("action"),
        user=args.get("user", 'user'),
        host=args.get("host", 'localhost'),
        protocol=args.get("protocol", 'http')
    )

    app.deploy()
