import aiohttp

async def ACNH_Call(index,item) -> dict:
    async with aiohttp.ClientSession() as session:
        if index == "fish":
            async with session.get(f"https://acnhapi.com/v1/fish/{item}") as resp:
                return await resp.json()
        elif index == "sea":
            async with session.get(f"https://acnhapi.com/v1/sea/{item}") as resp:
                return await resp.json()
        elif index == "bug":
            async with session.get(f"https://acnhapi.com/v1/bugs/{item}") as resp:
                return await resp.json()
        elif index == "fossil":
            async with session.get(f"https://acnhapi.com/v1/fossils/{item}") as resp:
                return await resp.json()
        