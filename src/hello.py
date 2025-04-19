from google import genai
from pathlib import Path
from PIL import Image
import io
import re
import time
from pydantic import BaseModel

from settings import settings

client = genai.Client(api_key=settings.gemini_token)

class Request(BaseModel):
    name: str
    file: genai.types.File


def extract_number(s: str) -> float:
    pattern = r"(\d+)_(\d+)"
    match = re.match(pattern, s)
    num_int = match.group(1)
    num_float = match.group(2)
    return float(f"{num_int}.{num_float}")


def parse_image(file: Path) -> float:
    image = PIL.Image.open(file)
    client = genai.Client(api_key=settings.gemini_token)
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=[
            "What number is displayed on this device? Give response as a single floating number.",
            image,
        ],
    )
    print(response.text)
    return float(response.text)

def prepare_data(dir: Path) -> list[Request]:
    result = list()
    for file in dir.glob("**.png"):
        name = file.stem
        image = Image.open(file)
        image_bytes = io.BytesIO()
        image.save(image_bytes, format='png')
        file = client.files.upload(file=image_bytes, config={"mime_type": "image/png"})
        result.append(Request(name=name, file=file).__dict__)
    return result

def process_data(data: list[tuple[str, Image]]):
    print(data)
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=[
            "What number is displayed on the device in each image",
            data,
        ],
    )
    print(response.text)


def parse_image_dir(dir: Path):
    count = 0
    err_count = 0
    for file in dir.glob("**.png"):
        print(file)
        name = file.stem
        print(name)
        num = extract_number(name)
        try:
            answer = parse_image(file)
        except genai.errors.ClientError as e:
            if e.code == 429:
                print(e)
                time.sleep(60)
                answer = parse_image(file)

        status = "ok"
        count += 1
        if str(num) != str(answer):
            status = "err"
            err_count += 1
        print(f"wanted: {num:4.1f}, got: {answer:4.1f} | {status} | {file}")
    print(f"err %: {err_count / count * 100}")


def main():
    data_dir = Path("../data/4_type")
    data = prepare_data(data_dir)
    process_data(data)


if __name__ == "__main__":
    main()
