class SqlBuildCatalogNameError(Exception):
    def __init__(self, message):
        super().__init__(message)

class SqlBuildError(Exception):
    def __init__(self, message):
        super().__init__(message)

class SqlBuildParameterError(Exception):
    def __init__(self, message):
        super().__init__(message)

class SqlBuildRuntimeError(Exception):
    def __init__(self, group: str, file: str, error: str):
        self.group = group
        self.file = file
        self.error = error
        self.message = f"Group: {self.group}, File: {self.file}, Error: {self.error}"
        super().__init__(self.message)

class SqlBuildParseError(Exception):
    def __init__(self, parse_error: dict, file: str, sql: str):
        self.parse_error = parse_error
        self.sql = sql
        self.file = file
        try:
            self.error = parse_error["error"]
            self.error_class = self.error["errorClass"]
            self.message_template = self.error["messageTemplate"]
            self.message_parameters = self.error["messageParameters"]
            self.message_formatted = self._format_message(self.message_template, self.message_parameters)
            self.line = self.error["line"]
            self.pos = self.error["position"]
            query_context = self.error.get("queryContext")
            if isinstance(query_context, list) and query_context:
                self.sql = query_context[0].get("fragment", self.sql)
            self.message = f"Error: {self.error_class} \n\tFile: {self.file}  \n\tMessage: {self.message_formatted} On line {self.line} at position {self.pos} \n\tSQL:\n\t{self.sql.replace("\n","\n\t")}\n"
        except (KeyError, ValueError):
            self.message = str(self.parse_error)

        super().__init__(self.message)

    def _format_message(self, message_template: str, message_parameters: dict[str, str]):
        for p, v in message_parameters.items():
            message_template = message_template.replace(f"<{p}>", v)
        return message_template
