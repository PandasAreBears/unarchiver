from pathlib import Path
from unarchiver.unarchiver import Unarchiver

RESOURCES = Path(__file__).parent / "resources"


class TestUnarchiver:
    def test_unarchive_simple_custom_type(self):
        file = RESOURCES / "simple_custom_type.plist"

        object = Unarchiver(file).parse()

        assert "root" in object

        root = object["root"]
        assert root["$type"] == "ArchiverType"
        assert root["value"] == 0
        assert root["name"] == "Panda"
