class AppError(Exception):
    def __init__(self, message: str, code: int = 4000) -> None:
        super().__init__(message)
        self.message = message
        self.code = code


class UnsupportedFileError(AppError):
    def __init__(self, message: str = "Unsupported file type") -> None:
        super().__init__(message, 4001)
