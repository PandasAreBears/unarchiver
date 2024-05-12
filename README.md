# Unarchiver

Unarchive an NSKeyedArchive into python.

## Installation

```sh
pip install unarchiver
```

## Command-line usage

```sh
Usage: unarchiver.py [OPTIONS] KEYED_ARCHIVE

  Unarchive an NSKeyedArchiver file.

Options:
  -o, --to-file PATH  A file to dump unarchived content into.
  --help              Show this message and exit.
```

``` sh
$ poetry run unarchive ~/Library/News/actionQueue
{
    "root": {
        "$type": "NSMutableDictionary",
        "NS.keys": [
            "FCFileCoordinatedAccountActionQueueLocalDataHintKey",
            "FCFileCoordinatedAccountActionQueueActionTypesKey"
        ],
        "NS.objects": [
            true,
            {
                "$type": "NSMutableArray",
                "NS.objects": []
            }
        ]
    }
}
```

## Library Usage

```py
from unarchiver.unarchiver import Unarchiver

unarchiver = Unarchiver(path_to_archive)

obj = unarchiver.parse()
```