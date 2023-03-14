#!/usr/bin/env python3

from pathlib import Path
import re
import time
import requests
import base64
import datetime
import configparser
import click
from humanfriendly import parse_date


from typing import Any, List, Tuple, Dict, Optional

APP_DIR = "sfin_ynab4"
CONFIG_FILE = Path.home() / APP_DIR / "settings.ini"

config = configparser.ConfigParser()
config.read(CONFIG_FILE)


def update_config() -> None:
    """
    write out current config and read it back in.
    create config file if not exist.
    """

    if not CONFIG_FILE.exists():
        # create missing config
        if not CONFIG_FILE.parent.exists():
            CONFIG_FILE.parent.mkdir()

        config["simplefin"] = {"last_access_time": "0"}
        config["ynab"] = {"output_dir": "logs"}

    with open(CONFIG_FILE, "wt") as c:
        config.write(c)
    config.read(CONFIG_FILE)


def setup(setup_token: str) -> None:
    """ """
    # 2. Claim an Access URL
    claim_url = base64.b64decode(bytes(setup_token, "utf-8"))
    response = requests.post(claim_url)
    access_url = response.text

    config["auth"] = {"url": access_url}

    update_config()


def get_url() -> str:
    return config["auth"]["url"]


def get_accounts(
    start_date: Optional[int] = None, end_date: Optional[int] = None
) -> Dict[str, Any]:
    payload: Dict[str, int] = {}
    if start_date:
        payload["start-date"] = start_date
    if end_date:
        payload["end-date"] = end_date

    url = get_url() + "/accounts"
    response = requests.get(url, params=payload)
    data = response.json()
    return data


def ts_to_date(ts: int) -> str:
    return datetime.datetime.fromtimestamp(ts).strftime("%m/%d/%Y")


def to_csv(transactions: List[Dict[str, Any]]) -> List[str]:
    """
    convert an array of transaction to an array of csv lines for ynab4

    example data:
    Date,Payee,Category,Memo,Outflow,Inflow
    07/25/10,Sample Payee,,Sample Memo for an outflow,100.00,
    07/26/10,Sample Payee 2,,Sample memo for an inflow,,500.00

    """
    # start with header
    csv_lines = ["Date,Payee,Category,Memo,Outflow,Inflow\n"]
    for t in transactions:
        date = ts_to_date(t["posted"])
        payee = t["description"]
        amount = float(t["amount"])
        memo = t.get("extra") or ""

        inflow = ""
        outflow = ""
        if amount < 0:
            outflow = abs(amount)
        else:
            inflow = abs(amount)

        csv_lines.append(f'"{date}","{payee}",,"{memo}","{outflow}","{inflow}"' + "\n")

    return csv_lines


@click.command("import")
@click.option("--start-time", help="override start time to import transactions form")
def import_transactions(start_time: str) -> None:
    if "auth" not in config:
        setup_token = input("Setup Token? ")
        setup(setup_token)

    now = int(time.time())

    if start_time:
        last_access = int(datetime.datetime(*parse_date(start_time)).timestamp())
    else:
        last_access = int(config["simplefin"]["last_access_time"]) or now - (
            7 * 24 * 60 * 60
        )

    data = get_accounts(start_date=last_access, end_date=now)

    if data.get("errors"):
        raise Exception(data.get("errors"))

    count = 0
    for account in data["accounts"]:
        name = account["name"]
        name = re.sub(r"[^\w\s-]", "", name.lower())
        name = re.sub(r"[-\s]+", "-", name).strip("-_")

        csv_lines = to_csv(account["transactions"])
        count += len(csv_lines) - 1  # do not count the header

        if len(csv_lines) < 2:
            # skip accounts with no transactions
            continue

        csv_path = Path.home() / config["ynab"]["output_dir"] / f"{name}.csv"
        if not csv_path.parent.exists():
            csv_path.parent.mkdir()
        with open(csv_path, "wt") as file:
            file.writelines(csv_lines)

    print(f"{count} transactions downloaded from {ts_to_date(last_access)} to now.")
    config["simplefin"]["last_access_time"] = str(now)
    update_config()


if __name__ == "__main__":
    import_transactions()
