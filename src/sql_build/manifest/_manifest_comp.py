
from dataclasses import dataclass

from ._script import Script
from .exception import SqlBuildParseError


@dataclass
class Group:
    group: str
    scripts: list[Script]
    execution_order: int

    def get_parse_errors(self):
        parse_errors: list[SqlBuildParseError] = []
        for script in self.scripts:
            if script.parse_errors:
                parse_errors.extend(script.parse_errors)

        if parse_errors:
            return parse_errors
        else:
            return None


@dataclass
class Options:
    allow_drop_tables: bool
    allow_drop_catalogs: bool

    def __str__(self):
        values = [f"\n\t{a}: {v}" for a, v in self.__dict__.items()]
        values = "".join(values)
        return f"Manifest options:{values}"
