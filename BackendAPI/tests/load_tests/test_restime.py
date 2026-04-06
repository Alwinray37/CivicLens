import httpx
import time
import asyncio

RES_TIME_THRES = .25
RES_FAILED_THRES = .005

BURST_USERS = 100
BURST_DELAY = .05
BURSTS = 15


endpoint = "http://localhost:8000"

async def get_restime(client, route: str):
    start_time = time.perf_counter()
    data: dict[str, float] = { 'failed': 0 }

    try:
        await client.get(endpoint + route)
    except:
        data['success'] = 1

    res_time = time.perf_counter() - start_time
    
    data['time'] = res_time

    return data


async def get_avg_burst_restime(client, route: str):
    actions = [get_restime(client, route) for _ in range(BURST_USERS)]

    gathered = await asyncio.gather(*actions)

    return {
            'avg_time': sum(data['time'] for data in gathered) / BURST_USERS,
            'failed': sum(data['failed'] for data in gathered),
        }
    

async def get_avg_restime(route: str):
    async with httpx.AsyncClient() as client:
        print()
        sum = 0
        failed = 0
        for _ in range(BURSTS):
            burst_data = await get_avg_burst_restime(client, route)
            print(f"burst data: {burst_data}")

            sum += burst_data['avg_time']
            failed += burst_data['failed']

            await asyncio.sleep(BURST_DELAY)

        avg = sum / BURSTS
        pc_failed = failed / (BURST_USERS * BURSTS)
        print(f"avg: {avg}")
        print(f"failed: {pc_failed}%")

        return {
                'avg_time': avg,
                'pc_failed': pc_failed
            }

async def assert_restime(route):
    avg_res = await get_avg_restime(route)

    assert avg_res['avg_time'] <= RES_TIME_THRES
    assert avg_res['pc_failed'] <= RES_FAILED_THRES



def test_get_meetings():
    asyncio.run(assert_restime("/getMeetings"))

def test_get_meeting_info():
    asyncio.run(assert_restime("/getMeetingInfo/2"))
