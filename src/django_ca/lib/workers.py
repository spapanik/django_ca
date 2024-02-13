from uvicorn.workers import UvicornWorker as BaseUvicornWorker


class UvicornWorker(BaseUvicornWorker):
    CONFIG_KWARGS = BaseUvicornWorker.CONFIG_KWARGS.copy() | {"lifespan": "off"}
