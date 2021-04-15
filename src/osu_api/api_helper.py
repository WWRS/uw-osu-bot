# library imports
import asyncio
import aiohttp

# file imports
import api_request
import token_handler
from ..utils.sanitizer import sanitize
from ..utils import modes

URL = "https://osu.ppy.sh/api/v2/"


async def regen_token():
    with api_request.get_token() as token:
        token_handler.set_token(token)


async def _get_ranked_beatmapsets(mode_num, *sql_dates):
    all_maps = []
    async with aiohttp.ClientSession() as session:
        for date in sql_dates:
            cur_page = 1
            while True:
                async with session.get(URL + f"beatmapsets/search",
                        params={
                            "m": mode_num,
                            "s": "ranked",
                            "q": f"created={date}",
                            "page": cur_page
                        },
                        headers=api_request.headers()) as response:
                    res = await response.json()
                    all_maps.extend(res["beatmapsets"])
                    cur_page += 1
                    if len(res["beatmapsets"]) < 50: # last page
                        break
    return all_maps


async def get_good_sets(mode: str, months: list[str]):
    sql_dates = []
    for month in months:
        date_month, date_year = month.split("/")
        if len(date_month) == 1:
            date_month = "0" + date_month
        sql_dates.append(f"20{date_year}-{date_month}")

    mode_id = modes.get_id(mode)

    beatmapsets = await _get_ranked_beatmapsets(mode_id, *sql_dates)

    # maps beatmapset_id to a list of the difficulty of each map
    bms_diffs = {bms["id"]: [bm["difficulty_rating"] for bm in bms["beatmaps"]] for bms in beatmapsets}
    bms_diffs = {k: v for (k, v) in bms_diffs.items() if len(v) >= 5 and max(v) >= 6}
    return list(bms_diffs.keys())


async def get_rank_username_id(username):
    url = URL + f"users/{username}/osu"
    async with api_request.get(url, {"key": "username"}) as user:
        user_rank = int(user["statistics"]["global_rank"])
        user_username = user["username"]
        user_id = user["id"]
        return user_rank, user_username, user_id


async def get_username(id):
    url = URL + f"users/{id}"
    async with api_request.get(url, {"key": "id"}) as user:
        username = user["username"]
        return sanitize(username)


async def get_recent(id):
    async with aiohttp.ClientSession() as session:
        async with session.get(URL + f"users/{id}/scores/recent", headers=api_request.headers()) as response:
            scores = await response.json()
            return scores


async def get_beatmap_names(*ids):
    to_return = []
    async with aiohttp.ClientSession() as session:
        for id in ids:
            async with session.get(URL + f"beatmapsets/{id}", headers=api_request.headers()) as response:
                map = await response.json()
                to_return.append(map["title"])
    return to_return

if __name__ == "__main__":
    asyncio.run(regen_token())
    # maps = asyncio.run(get_good_sets("standard", ["1/21", "2/21"]))
    print(asyncio.run(get_beatmap_names(294227, 480669)))
