class APIError(Exception):
    desc: str
    status: int
    headers: dict
    def __init__(self, *args) -> None:
        super().__init__(*args)
        self.desc = args[0]
        self.status = args[1]
        self.headers = args[2]