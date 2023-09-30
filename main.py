import configparser
import os
from datetime import datetime
import requests
from utils import send_telegram_report, minio_upload

config = configparser.ConfigParser()
config.read("secrets.ini")
config_dict = {sect: dict(config.items(sect)) for sect in config.sections()}

pdf_url = "https://www.imfconnect.org/content/dam/imf/News%20and%20Generic%20Content/GMM/latest.pdf"
with requests.get(pdf_url) as res:
    pdf_file = res.content

filename = "IMF_GMM_{}.pdf".format(datetime.now().strftime("%Y-%m-%d"))

mail_result = requests.post(
    "https://api.mailgun.net/v3/{}/messages".format(
        config_dict.get("MAILGUN").get("domain")
    ),
    auth=("api", config_dict.get("MAILGUN").get("apikey")),
    files=[("attachment", (filename, pdf_file))],
    data={
        "from": "Daily IMF GMM report <{}>".format(
            config_dict.get("MAILGUN").get("from")
        ),
        "to": [config_dict.get("MAILGUN").get("mail")],
        "subject": "Daily IMF GMM report",
        "text": "Please find in attachment the latest Global Market Monitor report from IMF.\nBest regards.\n{}".format(
            config_dict.get("MAILGUN").get("message")
        ),
    },
)

# Transfer daily file to Minio
with open(filename, "wb") as f:
    f.write(pdf_file)

home_upload = minio_upload(config_dict, filename, "HOME")

# Send Telegram report
_ = send_telegram_report(config_dict, "IMF GMM", "1", mail_result, home_upload)

os.remove(filename)
