from pydantic import validate_call
import time

from models.context import ContextModel
from settings import VALIDATE_CONFIG

ONE_DAY_IN_SECONDS = 86400

@validate_call(config = VALIDATE_CONFIG)
def get_current_day(started_time: int) -> int:
    current_time = time.time()
    time_difference = current_time - started_time
    current_day = int(time_difference / ONE_DAY_IN_SECONDS) + 1
    return current_day

@validate_call(config = VALIDATE_CONFIG)
def create_caption(context: ContextModel, config: dict) -> str:
    main_config = config["main"]
    meme_name = main_config["meme_name"]
    post_config = config["post"]
    base_caption: str = post_config["base_caption"]
    hashtags: str = post_config["hashtags"]

    current_day = get_current_day(context.started_at)
    caption = base_caption.format(day = current_day, meme_name = meme_name)
    hashtags_text = "#" + " #".join(hashtags.split(","))
    caption += f"\n{hashtags_text}" 

    return caption