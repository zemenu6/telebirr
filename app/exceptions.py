from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from . import schemas


async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=schemas.ErrorResponse(
            success=False,
            message=exc.detail,
            error_code=get_error_code(exc.status_code)
        ).dict()
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=schemas.ErrorResponse(
            success=False,
            message="Validation error",
            error_code="VALIDATION_ERROR"
        ).dict()
    )


async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=schemas.ErrorResponse(
            success=False,
            message="Internal server error",
            error_code="INTERNAL_ERROR"
        ).dict()
    )


def get_error_code(status_code: int) -> str:
    error_codes = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        409: "CONFLICT",
        422: "VALIDATION_ERROR",
        500: "INTERNAL_ERROR"
    }
    return error_codes.get(status_code, "UNKNOWN_ERROR")


class TeleBirrException(Exception):
    def __init__(self, message: str, error_code: str = "BUSINESS_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(message)


class InsufficientFundsException(TeleBirrException):
    def __init__(self):
        super().__init__("Insufficient balance", "INSUFFICIENT_FUNDS")


class InvalidPhoneException(TeleBirrException):
    def __init__(self):
        super().__init__("Invalid phone number format", "INVALID_PHONE")


class EqubNotMatureException(TeleBirrException):
    def __init__(self):
        super().__init__("Equb account not mature for withdrawal", "EQUB_NOT_MATURE")


class MinimumDepositException(TeleBirrException):
    def __init__(self):
        super().__init__("Minimum deposit amount is 500 Birr", "MINIMUM_DEPOSIT")


class UserNotFoundException(TeleBirrException):
    def __init__(self):
        super().__init__("User not found", "USER_NOT_FOUND")


class EqubNotFoundException(TeleBirrException):
    def __init__(self):
        super().__init__("Equb account not found", "EQUB_NOT_FOUND")
