from fastapi import status


class CustomAPIException(Exception):
    def __init__(self, name, message, stack_trace=None):
        self.name = name
        self.message = message
        self.stack_trace = stack_trace
        super().__init__(message)


class DatabaseException(CustomAPIException):
    def __init__(self, message="Database transaction error has occurred.", status_code=status.HTTP_400_BAD_REQUEST):
        self.name = "DatabaseException"
        self.message = message
        self.status_code = status_code
        super().__init__(self.name, self.message)


class DefaultUserDeleteException(CustomAPIException):
    def __init__(self, message="Default User Cannot be deleted"):
        self.name = "DefaultUserDeleteException"
        self.message = message
        super().__init__(self.name, self.message)


class ItemNotFoundException(CustomAPIException):
    def __init__(self, db_id=None, db_model=None):
        self.name = "ItemNotFoundException"
        self.status_code = status.HTTP_404_NOT_FOUND
        id_string = "the given id(s) do"
        if db_id is not None:
            id_string = f'id {db_id} does'
        item_string = "database item"
        if db_model:
            item_string = db_model.__name__

        self.message = f"The {item_string} specified by {id_string} not exist"
        super().__init__(self.name, self.message)


class ItemsNotFoundException(CustomAPIException):
    def __init__(self, ids):
        self.name = "ItemsNotFoundException"
        self.status_code = status.HTTP_404_NOT_FOUND
        self.message = f"The database items specified by ids {ids} are not found"
        super().__init__(self.name, self.message)


class DatabaseIntegrityCustomException(CustomAPIException):
    def __init__(self, message):
        self.name = "DatabaseIntegrityException"
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.message = f'{message} does not exist'
        super().__init__(self.name, self.message)


class DatabaseIntegrityException(CustomAPIException):
    def __init__(self, message="The specified reference key does not exist or one or more of the input values are "
                               "duplicate", delete=False, db_model=None):
        self.name = "DatabaseIntegrityException"
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.message = message
        if db_model:
            self.message = f'The {db_model.__name__} specified by this ID already exists'
        if delete:
            self.message = "Cannot delete item as data relating to this item exists"
        super().__init__(self.name, self.message)


class ElasticSearchException(CustomAPIException):
    def __init__(self):
        self.name = "ElasticSearchException"
        self.status_code = status.HTTP_404_NOT_FOUND
        self.message = "Error with ElasticSearch server/indices"
        super().__init__(self.name, self.message)


class FloorPlanNotFoundException(CustomAPIException):
    def __init__(self):
        self.name = "FloorPlanNotFoundException"
        self.status_code = status.HTTP_404_NOT_FOUND
        self.message = "The requested floor plan cannot be found"
        super().__init__(self.name, self.message)


class IncompleteUserObject(CustomAPIException):
    def __init__(self):
        self.name = "IncompleteUserObject"
        self.status_code = status.HTTP_401_UNAUTHORIZED
        self.message = "Some important user information required for proceeding with the request are empty."
        super().__init__(self.name, self.message)


class InvalidTimestampException(CustomAPIException):
    def __init__(self, timestamp=None, message=None):
        self.name = "InvalidTimestampException"
        if message is None:
            self.message = f"Timestamp {timestamp if timestamp is not None else ''} cannot be converted to a valid " \
                           f"datetime object."
        else:
            self.message = message
        super().__init__(self.name, self.message)


class ImageException(CustomAPIException):
    def __init__(self, **kwargs):
        self.name = "ImageException"
        if "status" in kwargs:
            self.status_code: status = kwargs.get("status")
        if "message" in kwargs:
            self.message = kwargs.get("message")
        else:
            self.message = "There is a problem with this image. Try uploading a different image."
        super().__init__(self.name, self.message)


class FileSavingException(CustomAPIException):
    def __init__(self, ):
        self.name = "FileSavingException"
        self.message = "File saving operation failed due to an OS error"
        super().__init__(self.name, self.message)


class InvalidInputException(CustomAPIException):
    def __init__(self, message=None):
        self.name = "InvalidInputException"
        if message:
            self.message = message
        else:
            self.message = "Input fields do not match the required format"
        super().__init__(self.name, self.message)


class InvalidUserGroupException(CustomAPIException):
    def __init__(self):
        self.name = "InvalidUserGroupException"
        self.message = "User roles are required for creating a user group"
        super().__init__(self.name, self.message)


class RequiredParameterException(CustomAPIException):
    def __init__(self):
        self.status_code = status.HTTP_404_NOT_FOUND
        self.name = "RequiredParameterException"
        self.message = "A required parameter is missing in the input fields"
        super().__init__(self.name, self.message)


class ConfigNotFoundException(CustomAPIException):
    def __init__(self, message):
        self.status_code = status.HTTP_404_NOT_FOUND
        self.name = "ConfigNotFoundException"
        self.message = message
        super().__init__(self.name, self.message)


class InvalidTimeFormat(CustomAPIException):
    def __init__(self):
        self.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        self.name = "InvalidTimeFormat"
        self.message = "Invalid time format"
        super().__init__(self.name, self.message)


class CameraNotMappedException(CustomAPIException):
    def __init__(self):
        self.status_code = status.HTTP_404_NOT_FOUND
        self.name = "CameraNotMappedException"
        self.message = "This device is not registered"
        super().__init__(self.name, self.message)


class ParentLocationAlreadyExists(CustomAPIException):
    def __init__(self):
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.name = "ParentLocationAlreadyExists"
        self.message = "Parent location already exists"
        super().__init__(self.name, self.message)


class NoDefaultCameraForTenant(CustomAPIException):
    def __init__(self):
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.name = "NoDefaultCameraForTenant"
        self.message = "No default camera for tenant"
        super().__init__(self.name, self.message)


class InvalidGeometryException(CustomAPIException):
    def __init__(self, message):
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.name = "InvalidGeometryException"
        self.message = message
        super().__init__(self.name, self.message)


class NoAccessException(CustomAPIException):
    def __init__(self, message):
        self.status_code = status.HTTP_403_FORBIDDEN
        self.name = "NoAccessException"
        self.message = message
        super().__init__(self.name, self.message)


class ServerNotAvailableError(CustomAPIException):
    def __init__(self, message):
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.name = "ServerNotAvailableError"
        self.message = message
        super().__init__(self.name, self.message)


class SpoofFaceDetected(CustomAPIException):
    def __init__(self, message):
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.name = "SpoofFaceDetected"
        self.message = message
        super().__init__(self.name, self.message)
