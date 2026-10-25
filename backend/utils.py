from starlette.responses import Response


class ErrorResponse(Response):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.status_code < 400:
            raise ValueError("Response is not an error")

    def __str__(self):
        return f"{self.__dict__}"