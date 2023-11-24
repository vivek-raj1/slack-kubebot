import os
from datetime import datetime
from slack_bolt import App
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from kubernetes import client, config
import datetime
from dateutil import parser
import logging

# Configure logging to display debug messages
# logging.basicConfig(level=logging.DEBUG)

app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)
slack_client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))


command_descriptions = {
    "/kubebot": "Main command to interact with the Kubernetes bot.",
    "/node": "Command to get information about Kubernetes nodes. cmd - list, count, describe",
    "/your_custom_command": "Description of your custom command.",
    "help": "Display a list of available commands and their descriptions."
    # Add more commands as needed
}


def create_options_attachment(contexts):
    options = [
        {
            "text": {
                "type": "plain_text",
                "text": f"`{context['name']}`",
                "emoji": True
            },
            "value": f"context_{context['name']}"
        } for context in contexts
    ]

    return {
        "blocks": [
            {
                "type": "input",
                "element": {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select a cluster",
                        "emoji": True
                    },
                    "options": options,
                    "action_id": "static_select-action"
                },
                "label": {
                    "type": "plain_text",
                    "text": "Clusters",
                    "emoji": True
                }
            }
        ]
    }


def create_options_attachment():
    return {
        "text": "Select an option:",
        "fallback": "You are unable to choose an option",
        "callback_id": "kubebot_options",
        "attachment_type": "default",
        "actions": [
            {
                "name": "option",
                "text": "Clusters",
                "type": "button",
                "value": "context_list"
            },
            {
                "name": "option",
                "text": "Help",
                "type": "button",
                "value": "help"
            }
        ]
    }


def get_kubernetes_context():
    config.load_kube_config()
    contexts, active_context = config.list_kube_config_contexts()
    return contexts

def get_kubernetes_nodes(context_name):
    config.load_kube_config(context=context_name)
    v1 = client.CoreV1Api()
    nodes = v1.list_node()
    return nodes

def get_kubernetes_pods(namespace, context_name):
    config.load_kube_config(context=context_name)
    v1 = client.CoreV1Api()
    pods = v1.list_namespaced_pod(namespace)
    return pods


def display_help(ack, body, say):
    ack()
    user_id = body["user"]["id"]

    help_text = "Here are the available commands and their descriptions:\n"
    for command, description in command_descriptions.items():
        help_text += f"`{command}`: {description}\n"

    say(f"Sure, <@{user_id}>! {help_text}")

@app.command("/kubebot")
def kubebot_command(ack, say, command):
    ack()
    user_id = command["user_id"]
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"Hi <@{user_id}>! What can I help you with?"
    options_attachment = create_options_attachment()
    try:
        response = slack_client.chat_postMessage(
            channel=command["channel_id"],
            text=message,
            attachments=[options_attachment]
        )
        print(f"Message sent: {response}")
    except SlackApiError as e:
        print(f"Error sending message: {e.response['error']}")

@app.action("kubebot_options")
def handle_options_action(ack, body, say):
    selected_option = body["actions"][0]["value"]
    user_id = body["user"]["id"]
    
    ack()
    
    if selected_option == "pod_logs":
        say(f"Sure, <@{user_id}>! Executing command `/podlogs`.")
        # You can implement the logic to execute the '/podlogs' command here.
        # You might want to use the Slack WebClient to send messages or execute commands.
    elif selected_option == "context_list":
        contexts = get_kubernetes_context()
        context_list = ""
        for context in contexts:
            context_list += f"`{context['name']}`\n"

        say(f"Sure, <@{user_id}>! Listing context \n{context_list}")
    elif selected_option == "help":
        display_help(ack, body, say)
        

@app.command("/node")
def node_command(ack, say, command):
    """
    Handle the "/node" command.

    Parameters:
    - ack: A function to acknowledge the command request.
    - say: A function to send a response message.
    - command: The command object containing user input.

    Returns:
        None
    """
    ack()
    user_id = command["user_id"]
    text = command["text"].split()  # Split the command text into words
    if len(text) == 2:
        context_name = text[1]
        if text[0] == "count" and context_name:
            nodes = get_kubernetes_nodes(context_name)
            count = len(nodes.items)
            say(f"Sure, <@{user_id}>! Counting Node in context `{context_name}` \nNode Count: {count}.")
        elif text[0] == "list" and context_name:
            say(f"Sure, <@{user_id}>! Listing nodes in context `{context_name}`... :mag:")  # Implement logic to list nodes here.
            nodes = get_kubernetes_nodes(context_name)
            # node_info = "```NAME\tINTERNAL-IP\tAGE\tVERSION\n"
            # node_info = "```\n"
            node_info = f"`{'NAME':<55}{'INTERNAL-IP':<15}{'AGE':<7}{'VERSION':<10}`\n"
            for node in nodes.items:
                internal_ip = next((address.address for address in node.status.addresses if address.type == "InternalIP"), "-")
                naive_datetime = node.metadata.creation_timestamp.replace(tzinfo=None)
                age = str((datetime.datetime.now() - naive_datetime).days) + "d"
                version = node.status.node_info.kubelet_version if node.status.node_info else "-"
                node_info += f"`{node.metadata.name:<55}{internal_ip:<15}{age:<7}{version:<10}`\n"
            # node_info += "```"
            say(f"Hi <@{user_id}>! nodes in context list `{context_name}`:\n{node_info}")
    else:
        say(f"Hi <@{user_id}>! What can I help you with regarding nodes? Options: `/node count contextname`, `/node list contextname`.")



@app.command("/podlist")
def pod_list_command(ack, say, command):
    """
    Command to list pods in a given namespace and context.

    Args:
        ack: A function to acknowledge the command.
        say: A function to send a response message.
        command: The command object containing user input.

    Returns:
        None
    """
    ack()
    user_id = command["user_id"]
    text = command["text"].split()  # Split the command text into words
    if len(text) == 2:
        namespace = text[0]
        context_name = text[1]
        if namespace and context_name:
            say(f"Sure, <@{user_id}>! Listing pods in namespace `{namespace}` and context `{context_name}`")
            pods = get_kubernetes_pods(namespace, context_name)
            pod_info = f"`{'NAME':<55}{'STATUS':<10}{'AGE':<7}{'POD IP':<15}{'NODE':<20}`\n"
            for pod in pods.items:
                status = pod.status.phase if pod.status.phase else "-"
                naive_datetime = pod.metadata.creation_timestamp.replace(tzinfo=None)
                age = str((datetime.datetime.now() - naive_datetime).days) + "d"
                pod_ip = pod.status.pod_ip if pod.status.pod_ip else "-"
                node_name = pod.spec.node_name if pod.spec.node_name else "-"
                pod_info += f"`{pod.metadata.name:<55}{status:<10}{age:<7}{pod_ip:<15}{node_name:<20}`\n"
            
            say(f"Hi <@{user_id}>! Pods in namespace `{namespace}` and context `{context_name}`:\n{pod_info}")
        else:
            say(f"Please provide both namespace and context name.")
    else:
        say(f"Hi <@{user_id}>! What can I help you with regarding pod list? Options: `/podlist namespace context`.")



if __name__ == "__main__":
    # Start the bot
    app.start(port=3000) 
    