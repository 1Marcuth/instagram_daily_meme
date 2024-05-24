from configparser import ConfigParser
from pydantic import validate_call
from datetime import datetime, timedelta
import decouple
import time
import os

from utils.file import read_json_file, write_json_file
from models.context import ContextModel
from post_details import create_caption
from settings import VALIDATE_CONFIG
from instagram import Instagram

def check_user_data_dir() -> None:
    if not os.path.exists(".user_data"):
        os.mkdir(".user_data")

def get_context() -> ContextModel:
    context_dict = read_json_file("context.json")
    context = ContextModel(**context_dict)
    return context

@validate_call(config = VALIDATE_CONFIG)
def save_context(context: ContextModel) -> None:
    context_dict = context.model_dump()
    write_json_file("context.json", context_dict)

def get_config() -> dict:
    config = ConfigParser()
    config.read("config.ini")
    config_dict = dict(config)
    return config_dict

def get_credentials() -> tuple[str, str]:
    username: str = decouple.config("INSTA_USERNAME")
    password: str = decouple.config("INSTA_PASSWORD")
    return username, password

def login() -> Instagram:
    username, password = get_credentials()
    instagram = Instagram(".user_data")
    instagram.login(username, password)
    return instagram

@validate_call(config = VALIDATE_CONFIG)
def should_post_check(context: ContextModel) -> bool:
    current_date = datetime.now()
    current_time = int(current_date.timestamp())

    if context.started_at <= 0:
        context.started_at = current_time
        context.days_posted = [current_time]
        return True
    
    interval_between_posts = timedelta(days = 1).total_seconds()
    latest_post_time = max(context.days_posted)
    is_to_post = current_date > datetime.fromtimestamp(latest_post_time + interval_between_posts)

    if is_to_post:
        context.days_posted.append(current_time)
        return True
    
    return False

@validate_call(config = VALIDATE_CONFIG)
def create_daily_post(context: ContextModel, config: dict) -> None:
    current_dir = os.getcwd()
    caption = create_caption(context, config)
    instagram = login()

    video_file_path = os.path.normpath(os.path.join(current_dir, config["main"]["video_file_path"]))
    post_location = config["post"]["location"]
    media_file_paths = [ video_file_path ]

    instagram.create_post(media_file_paths, caption, post_location)

def main() -> None:
    context = get_context()
    config = get_config()
    should_post = should_post_check(context)

    if should_post:
        check_user_data_dir()
        create_daily_post(context, config)
        save_context(context)

if __name__ == "__main__":
    main()