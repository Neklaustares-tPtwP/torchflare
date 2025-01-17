"""Implements notifiers for slack and discord."""
import json
from abc import ABC
from typing import TYPE_CHECKING

import requests

from torchflare.callbacks.callback import Callbacks
from torchflare.callbacks.states import CallbackOrder

if TYPE_CHECKING:
    from torchflare.experiments.experiment import Experiment


def prepare_data(logs: dict):
    """Function to prepare the data according to the type of message.

    Args:
        logs: Dictionary containing the metrics and loss values.

    Returns:
        string in the same format as logs.
    """
    val = [f"{key} : {value}" for key, value in logs.items()]
    text = "\n".join(val)
    return text


class SlackNotifierCallback(Callbacks, ABC):
    """Class to Dispatch Training progress to your Slack channel.

    Args:
        webhook_url : Slack webhook url.

    Examples:
        .. code-block:: python

            import torchflare.callbacks as cbs
            slack_notif = cbs.SlackNotifierCallback(webhook_url="YOUR_SECRET_URL")

    """

    def __init__(self, webhook_url: str):
        """Constructor method for SlackNotifierCallback."""
        super(SlackNotifierCallback, self).__init__(order=CallbackOrder.EXTERNAL)
        self.webhook_url = webhook_url

    def on_epoch_end(self, experiment: "Experiment"):
        """This function will dispatch messages to your Slack channel."""
        data = {"text": prepare_data(experiment.exp_logs)}

        response = requests.post(self.webhook_url, json.dumps(data), headers={"Content-Type": "application/json"})

        if response.status_code != 200:
            raise ValueError(
                "Request to server returned an error {}, the response is:\n{}".format(
                    response.status_code, response.text
                )
            )


class DiscordNotifierCallback(Callbacks, ABC):
    """Class to Dispatch Training progress.

    Args:
        exp_name : The name of your experiment bot. (Can be anything)
        webhook_url : The webhook url of your discord server/channel.

    Examples:
        .. code-block::

            import torchflare.callbacks as cbs

            discord_notif = cbs.DiscordNotifierCallback(
                webhook_url="YOUR_SECRET_URL", exp_name="MODEL_RUN"
            )

    """

    def __init__(self, exp_name: str, webhook_url: str):
        """Constructor method for DiscordNotifierCallback."""
        super(DiscordNotifierCallback, self).__init__(order=CallbackOrder.EXTERNAL)
        self.exp_name = exp_name
        self.webhook_url = webhook_url

    def on_epoch_end(self, experiment: "Experiment"):
        """On epoch end dispatch per epoch metrics."""
        data = {
            "username": self.exp_name,
            "embeds": [{"description": prepare_data(experiment.exp_logs)}],
        }
        response = requests.post(self.webhook_url, json.dumps(data), headers={"Content-Type": "application/json"})
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
