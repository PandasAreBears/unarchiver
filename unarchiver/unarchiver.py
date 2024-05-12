from pathlib import Path
import builtins
import plistlib
from typing import Any
import base64
import click
import click_pathlib
from pydantic import BaseModel, Field
import json


class Archive(BaseModel):
    version: int = Field(validation_alias="$version")
    archiver: str = Field(validation_alias="$archiver")
    top: dict[str, Any] = Field(validation_alias="$top")
    objects: list[Any] = Field(validation_alias="$objects")


class Unarchiver:
    def __init__(self, path: Path) -> None:
        self.archive = self._parse_archive(path)
        self.cache: dict[plistlib.UID, Any] = {}

    def print(self) -> None:
        print(
            json.dumps(
                self.parse(),
                indent=4,
                default=self._invalid_type_warning,
            )
        )

    def write(self, path: Path) -> None:
        with open(path, "w") as f:
            json.dump(self.parse(), f, indent=4, default=self._invalid_type_warning)

    def parse(self) -> dict[str, Any]:
        return {k: self._value_for_uid(v) for k, v in self.archive.top.items()}

    def _invalid_type_warning(self, obj: Any) -> str:
        return f"<ERROR: encountered invalid type while parsing: {type(obj).__class__.__name__}>\nPlease report a github issue."

    def _top_uid(self) -> plistlib.UID:
        root_uid: plistlib.UID | None = self.archive.top.get("root")
        if root_uid is None:
            raise ValueError("Missing root object")

        return root_uid

    def _parse_archive(self, path: Path) -> Archive:
        with open(path, "rb") as f:
            plist = plistlib.load(f)

        return Archive.model_validate(plist)

    def _class_for_uid(self, uid: plistlib.UID) -> str:
        target = self.archive.objects[uid]

        if not isinstance(target, dict) or "$classname" not in target:
            raise ValueError(f"Object {uid} is not class metadata")

        return target["$classname"]

    def _value_for_uid(self, uid: plistlib.UID) -> Any:
        # UID 0 is always nil
        if uid == 0:
            return None

        # Check the cache
        if uid in self.cache:
            return self.cache[uid]

        # catch self-references
        self.cache[uid] = "..."

        obj: Any = None
        match type(self.archive.objects[uid]):
            case builtins.dict:
                obj = self._handle_uid_as_dict(uid)
            case builtins.bytes:
                obj = self._handle_uid_as_bytes(uid)
            case _:
                obj = self._handle_uid_as_primitive(uid)

        self.cache[uid] = obj
        return obj

    def _handle_uid_as_bytes(self, uid: plistlib.UID) -> str:
        return base64.b64encode(self.archive.objects[uid]).decode("utf-8")

    def _handle_uid_as_primitive(self, uid: plistlib.UID) -> Any:
        return self.archive.objects[uid]

    def _handle_uid_as_dict(self, uid: plistlib.UID) -> dict[str, Any]:
        target = self.archive.objects[uid]
        assert isinstance(target, dict)

        class_uid = target["$class"]
        if class_uid is None:
            raise ValueError("Missing class name for dict target.")

        obj: dict[str, Any] = {"$type": self._class_for_uid(class_uid)}
        for key, value in target.items():
            if key.startswith("$"):
                continue

            match type(value):
                case plistlib.UID:
                    obj[key] = self._value_for_uid(value)
                case builtins.list:
                    obj[key] = [self._value_for_uid(v) for v in value]
                case _:
                    obj[key] = value

        return obj


@click.command()
@click.argument(
    "keyed-archive",
    type=click_pathlib.Path(exists=True),
)
@click.option(
    "--to-file",
    "-o",
    help="A file to dump unarchived content into.",
    type=click_pathlib.Path(exists=True),
)
def cli(keyed_archive: Path, to_file: Path | None):
    """Unarchive an NSKeyedArchiver file."""
    unarchiver = Unarchiver(keyed_archive)
    if to_file is not None:
        unarchiver.write(to_file)
    else:
        unarchiver.print()


if __name__ == "__main__":
    cli()
