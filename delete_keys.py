import os
import json


BASE_DIR = os.getenv("BASE_DIR", "./output/")
INPUT_DIR = os.getenv("INPUT_DIR", "decode_json_outputs/")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "clean_json/")
DELETE_KEYS = os.getenv("DELETE_KEY_LIST").split(',')


def scrub(obj, del_key="del_key"):
    if isinstance(obj, dict):
        for key in list(obj.keys()):
            if key == del_key:
                del obj[key]
            else:
                scrub(obj[key], del_key)
    elif isinstance(obj, list):
        for i in reversed(range(len(obj))):
            if obj[i] == del_key:
                del obj[i]
            else:
                scrub(obj[i], del_key)
    else:
        pass


def main():
    path = f"{BASE_DIR}{INPUT_DIR}"
    files = os.listdir(path)
    output_path = f"{BASE_DIR}{OUTPUT_DIR}"
    os.makedirs(output_path, exist_ok=True)

    for f in files:
        try:
            with open(f"{path}{f}", 'r') as data_file:
                data = json.load(data_file)

            for key in DELETE_KEYS:
                scrub(data, key)

            with open(f'{output_path}{f}.json', 'w') as output_file:
                json.dump(data, output_file, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))
        except Exception:
            print(f"error filename:{f}")
            continue


if __name__ == "__main__":
    main()
