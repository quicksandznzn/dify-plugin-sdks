from typing import IO, Optional
from urllib.parse import urljoin

import requests

from dify_plugin.errors.model import (
    CredentialsValidateFailedError,
    InvokeBadRequestError,
)
from dify_plugin.interfaces.model.openai_compatible.common import _CommonOaiApiCompat
from dify_plugin.interfaces.model.speech2text_model import Speech2TextModel


class OAICompatSpeech2TextModel(_CommonOaiApiCompat, Speech2TextModel):
    """
    Model class for OpenAI Compatible Speech to text model.
    """

    def _invoke(self, model: str, credentials: dict, file: IO[bytes], user: Optional[str] = None) -> str:
        """
        Invoke speech2text model

        :param model: model name
        :param credentials: model credentials
        :param file: audio file
        :param user: unique user id
        :return: text for given audio file
        """
        headers = {}

        api_key = credentials.get("api_key")
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        endpoint_url = credentials.get("endpoint_url", "https://api.openai.com/v1/")
        if not endpoint_url.endswith("/"):
            endpoint_url += "/"
        endpoint_url = urljoin(endpoint_url, "audio/transcriptions")

        payload = {"model": credentials.get("endpoint_model_name", model)}
        files = [("file", file)]
        response = requests.post(endpoint_url, headers=headers, data=payload, files=files)  # noqa: S113

        if response.status_code != 200:
            raise InvokeBadRequestError(response.text)
        response_data = response.json()
        return response_data["text"]

    def validate_credentials(self, model: str, credentials: dict) -> None:
        """
        Validate model credentials

        :param model: model name
        :param credentials: model credentials
        :return:
        """
        try:
            audio_file_path = self._get_demo_file_path()

            with open(audio_file_path, "rb") as audio_file:
                self._invoke(model, credentials, audio_file)
        except Exception as ex:
            raise CredentialsValidateFailedError(str(ex)) from ex
