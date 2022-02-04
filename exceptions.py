class CustomException(Exception):
    def __init__(self, status, message):
        self.status = status
        self.message = message
        print(message)
        super().__init__(message)


class UnauthorizedError(CustomException):
    def __init__(self, *args, **kwargs):
        super().__init__(status='401', message="Не авторизован!")


class NotFoundError(CustomException):
    def __init__(self, *args, **kwargs):
        super().__init__(status='404', message="Не найдено!")


class DeletedError(CustomException):
    def __init__(self, *args, **kwargs):
        super().__init__(status='410', message="Уже удалено!")


class InternalServerError(CustomException):
    def __init__(self, *args, **kwargs):
        super().__init__(status='500', message="Внутренняя ошибка сервера!")
