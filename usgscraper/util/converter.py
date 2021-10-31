import json
from functools import wraps


def jsonify(journal: str, volume: int, issue: int, data: dict) -> None:
    """The jsonify function converts the argument `data` to a JSON file.

    Args:
        journal (str): the journal name
        volume (int): the volume of a journal
        issue (int): the issue of a volume
        data (dict): the target data

    Returns:
        a json file
    """
    if issue:
        with open(f"{journal} - {volume} - {issue}.json", "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False)
    else:
        with open(f"{journal} - {volume}.json", "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False)


def convert(datatype):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            data = list(self.extract_data())
            if datatype == "json":
                jsonify(self.__class__.__name__, self.volume, self.issue, data)

        return wrapper

    return decorator
  
