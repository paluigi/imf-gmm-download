import requests
from minio import Minio


def send_telegram_report(
    config: dict, chain: str, records: int, cloud_upload: bool, home_upload: bool
) -> requests.models.Response:
    """Function to send scraping report on Telegram"""
    message = "{}.\nAcquired {} prices.\nMail: {}\nHome upload: {}".format(
        chain, records, cloud_upload, home_upload
    )
    response = requests.post(
        url="https://api.telegram.org/bot{0}/{1}".format(
            config["TELEGRAM"]["token"], "sendMessage"
        ),
        data={"chat_id": config["TELEGRAM"].getint("chat_id"), "text": message},
    ).json()
    return response


def minio_upload(config_dict: dict, filename: str, target: str = "CLOUD") -> bool:
    """
    Function to load a file into Minio

    Parameters:
    config_dict (dict): dictionary with configuration for Minio
                        object storage
    filename (str): string with the local name of the file. It
                    will be the same on Minio
    target (str):   string with information on the dictionary
                    section where to get Minio configuration

    Returns:
    response_h (bool): True if file was uploaded, else False

    """
    mclient = Minio(
        config_dict.get(target).get("minio_url"),
        access_key=config_dict.get(target).get("minio_account"),
        secret_key=config_dict.get(target).get("minio_key"),
    )
    try:
        response_h = mclient.fput_object(
            config_dict.get(target).get("bucket"),
            filename,
            filename
        )
    except:
        response_h = False
    return bool(response_h)
