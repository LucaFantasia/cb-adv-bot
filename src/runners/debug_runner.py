from container import build_services


def main() -> None:
    services = build_services()

    print(services.product_api.get_product("BTC-USD"))
