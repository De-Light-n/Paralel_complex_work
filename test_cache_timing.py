"""
Simple cache timing demo for asset-service.

Flow:
1) clear cache via POST /assets/cache/clear
2) call GET /assets/{id} first time (cache miss)
3) call GET /assets/{id} second time (cache hit)
"""

import argparse
import json
import sys
import time
from urllib import error, request


def http_request(url: str, method: str = "GET"):
    req = request.Request(url=url, method=method)
    req.add_header("Content-Type", "application/json")
    started = time.perf_counter()
    try:
        with request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8")
            elapsed_ms = (time.perf_counter() - started) * 1000
            return resp.status, body, elapsed_ms
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        elapsed_ms = (time.perf_counter() - started) * 1000
        return exc.code, body, elapsed_ms


def resolve_asset_id(base_url: str, preferred_id: int) -> int:
    """Try preferred asset id first; fallback to first asset from listing."""
    status, _, _ = http_request(f"{base_url}/assets/{preferred_id}", method="GET")
    if status < 400:
        return preferred_id

    list_status, list_body, _ = http_request(f"{base_url}/assets?skip=0&limit=1", method="GET")
    if list_status >= 400:
        raise RuntimeError("Cannot fetch assets list from service")

    payload = json.loads(list_body)
    assets = payload.get("assets", [])
    if not assets:
        raise RuntimeError("No assets found. Create one asset first, then rerun test")

    return int(assets[0]["id"])


def main():
    parser = argparse.ArgumentParser(description="Measure cache hit/miss timing for asset-service")
    parser.add_argument("--base-url", default="http://localhost:8001", help="Asset service base URL")
    parser.add_argument("--asset-id", type=int, default=1, help="Asset ID for GET request")
    args = parser.parse_args()

    try:
        asset_id = resolve_asset_id(args.base_url, args.asset_id)
    except Exception as exc:
        print(f"Failed to resolve asset id: {exc}")
        sys.exit(1)

    clear_url = f"{args.base_url}/assets/cache/clear"
    get_url = f"{args.base_url}/assets/{asset_id}"
    print(f"Using asset_id={asset_id}")

    print("Clearing cache...")
    status, body, clear_ms = http_request(clear_url, method="POST")
    print(f"  clear status: {status}, time: {clear_ms:.2f} ms")
    if status >= 400:
        print("  clear response:", body)

    print("\nFirst request (expected cache MISS)...")
    status1, body1, t1 = http_request(get_url, method="GET")
    print(f"  status: {status1}, time: {t1:.2f} ms")
    if status1 >= 400:
        print("  response:", body1)
        print("\nTip: make sure asset with this ID exists, or pass --asset-id")
        sys.exit(1)

    print("\nSecond request (expected cache HIT)...")
    status2, body2, t2 = http_request(get_url, method="GET")
    print(f"  status: {status2}, time: {t2:.2f} ms")

    diff = t1 - t2
    if t2 > 0:
        ratio = t1 / t2
    else:
        ratio = 0

    print("\nResult:")
    print(f"  first call : {t1:.2f} ms")
    print(f"  second call: {t2:.2f} ms")
    print(f"  saved      : {diff:.2f} ms")
    print(f"  speedup    : {ratio:.2f}x")


if __name__ == "__main__":
    main()
