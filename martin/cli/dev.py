import uvicorn


def run_dev(host: str, port: int):
    print(f"\n🚀 MARTIN Dev Server")
    print(f"   http://{host}:{port}\n")

    uvicorn.run(
        "martin.runtime_asgi.dev_entry:app",
        host=host,
        port=port,
        reload=True,
    )