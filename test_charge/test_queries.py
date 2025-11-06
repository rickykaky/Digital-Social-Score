import asyncio, aiohttp, time
API_URL = "http://34.38.214.124/docs#/AI%20Analysis/analyze_toxicity_analyze_post"
#API_URL = "http://34.145.51.226/docs#/default/get_social_score_score_post"
async def test(session, text):
    async with session.post(API_URL, json={"text": text}) as r:
        return await r.json()

async def load_test(n_users=10000):
    start = time.time()
    async with aiohttp.ClientSession() as session:
        tasks = [test(session,"Hello world!") for _ in range(n_users)]
        await asyncio.gather(*tasks)
    print(f"{n_users} requêtes exécutées en {time.time()-start:.2f}s")
asyncio.run(load_test())

