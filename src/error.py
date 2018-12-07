class hiveError(Exception):
    errors = {
        1:   "Unknown device ID",
        400: "One or more parameters invalid or missing",
        401: "User is not authorized",
        403: "You do not have the right permissions to perform this call",
        404: "Response data unavailable",
        405: "API method not allowed",
        415: "Error with headers submitted",
        503: "Unable to contact event service"
    }
    
    def __init__(self, value):
        if (value in self.errors):
            self.value = self.errors[value]
        else:
            self.value = "Unknown error {}".format(value)
    def __str__(self):
        return repr(self.value)