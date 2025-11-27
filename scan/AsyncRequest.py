import asyncio
import random
from typing import Optional, Dict, Any
import httpx

from scan.LogManager import write_error_log


def make_async_client(
        timeout: Optional[httpx.Timeout] = None,
        limits: Optional[httpx.Limits] = None,
        proxies: Optional[Dict[str, str]]  = None
)-> httpx.AsyncClient:
    """创建异步客户端"""
    if timeout is None:
        timeout = httpx.Timeout(connect=5, read=10, write=10, pool=10)
    if limits is None:
        limits = httpx.Limits(max_connections=100, max_keepalive_connections=10)
    return httpx.AsyncClient(timeout=timeout, limits=limits,proxies=proxies)

async def request_with_tactics(
        client: httpx.AsyncClient,
        method: str,
        url: str,
        log_path: Optional[str],
        *,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Any = None,
        json: Any = None,
        max_attempts: int = 3,
        backoff: bool = False,
        TimeoutConfig: Optional[Dict[str, Any]] = None,
        retry_tatics: Optional[Dict[str, Any]] = None,
) -> httpx.Response:
    """发起异步请求"""
    attempt = 0
    common_args = {
            "method": method,
            "url": url,
            "headers": headers,
            "params": params,
            "data": data,
            "json": json
        }
    if TimeoutConfig is not None:
        timeout = httpx.Timeout(**TimeoutConfig)
        common_args["timeout"] = timeout
    # print(f"Requesting {common_args}")
    while True:
        attempt += 1
        try:
            request = client.build_request(**common_args)
            resp = await client.send(
                request,
                follow_redirects=False,
            )
            if resp.status_code in retry_tatics['StatusCodes']:
                await write_error_log(log_path, f"Retryable status {resp.status_code}", url)
                raise httpx.HTTPStatusError(
                    f"Retryable status code: {resp.status_code}",
                    request=request,
                    response=resp
                )
            return resp
        except Exception as e:
            if attempt >= max_attempts:
                # print(f"Max retries exceeded: {e}")
                # await write_error_log(log_path, f"Max retries exceeded({attempt}): {e}", url)
                return None
            if backoff:
                sleep = (2 ** (attempt - 1)) * retry_tatics['BaseDelaySeconds']
                sleep += random.random()
                await asyncio.sleep(sleep)  