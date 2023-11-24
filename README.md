# slack-kubernetes-bot
This project implements a Slack bot using the Slack Bolt framework to interact with Kubernetes clusters. The bot allows users to perform various operations on Kubernetes nodes and pods directly from Slack.

## Prerequisites

Before running the bot, ensure you have the following dependencies installed:

- Python 3.x
- [Slack Bolt](https://slack.dev/bolt-python/concepts) library
- [Slack SDK](https://slack.dev/python-slack-sdk/) library
- [Kubernetes Python Client](https://github.com/kubernetes-client/python) library
- [dateutil](https://pypi.org/project/python-dateutil/) library

## Setup

1. Clone this repository:

    ```bash
    git clone https://github.com/vivek-raj1/slack-kubernetes-bot.git
    cd slack-kubernetes-bot
    ```

2. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Set up environment variables:

    - `SLACK_BOT_TOKEN`: Your Slack bot token.
    - `SLACK_SIGNING_SECRET`: Your Slack app's signing secret.

4. Run the bot:

    ```bash
    python main.py
    ```

## Bot Commands

- **/kubebot**: Main command to interact with the Kubernetes bot.
- **/node**: Command to get information about Kubernetes nodes. Use `list`, `count`, or `describe`.
- **/podlist**: List pods in a given namespace and context.

## Additional Information

- The bot uses the Slack Bolt framework for handling Slack events and commands.
- Kubernetes information is fetched using the Kubernetes Python client.
- Feel free to extend the bot by adding more commands or features based on your requirements.