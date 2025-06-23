from typing import Dict, List, Set

from google import genai
from google.genai import types

import os
from os import getenv
from dotenv import load_dotenv
load_dotenv()

from pdf2image import convert_from_path
from PIL import Image

import httpx

from ast import literal_eval as leval

import json

client = genai.Client(api_key = getenv("API_KEY"))

def pdf_get_pages(pdf_path: str):
    return convert_from_path(pdf_path)

def pdf_save_pages(pdf_path, test_folder: str) -> List[str]:
    output_folder = f"{test_folder}/pages"

    pages = pdf_get_pages(pdf_path)

    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    paths = []

    for i, image in enumerate(pages):
        path = f"{output_folder}/page_{i}.jpeg"
        image.save(path)
        paths.append(path)

    return paths

def get_tags(test_pdf: str) -> Set[str]:
    with open(test_pdf, "rb") as file:
        prompt = "You are part of an app for drilling Regents questions indexed from past tests. Respond only with a comma separated (no space after the comma) list of question types / tags present. Don't say where they are or anything else, just the types present."
        response = client.models.generate_content(
            model = "gemini-2.5-flash",
            contents = [
                types.Part.from_bytes(
                    data=file.read(),
                    mime_type="application/pdf"
                ),
                prompt
            ]
        )
        tags = response.text.split(",")
    return set(tags)

def get_questions(pages_folder, test_folder: str):
    pages_paths = list(os.listdir(pages_folder))

    page_question_data = {}

    tags = get_tags(f"{pages_folder}/test.pdf")

    for i, page_file in enumerate(sorted(pages_paths, key=lambda x: '{0:0>16}'.format(x).lower())):
        page_path = f"{pages_folder}/{page_file}"

        with open(page_path, "rb") as file:
            prompt = \
            """You are part of an app for drilling Regents questions indexed from past tests. Your task is to help extract the questions from the attached scan JPEG of a page from a test book. Answer in the following format:"""+\
            """[{"question_number":42,"bounds":((62,254),(100,500)),"question_type":"free_response",tags:["tag1","tag2"]},...]"""+\
            """Bounds is the coordinates in the pixel grid of the top left and bottom right corners of the bounding box which encloses the question and its answers, for cropping. Question type can either be "free_response" for the later free response questions, or "multiple_choice" for the standard multiple choice questions. The tags are these: """ + ", ".join(tags) +\
            """Only answer with this information in this structured format and no extraneous or additional information."""
            response = client.models.generate_content(
                model = "gemini-2.5-flash",
                contents = [
                    types.Part.from_bytes(
                        data=file.read(),
                        mime_type="image/jpeg"
                    ),
                    prompt
                ]
            )
            question_info = leval(response.text)

        page_question_data[str(i)] = question_info

        questions = []

        for page, page_data in page_question_data:
            question_datas = page_data

            for question_data in question_datas:
                question_data["page_number"] = page
                questions.append(question_data)

        with open(f"{test_folder}/question_crop.json", "w") as file:
            file.write(json.dumps(questions))

# TODO: Add crop_questions() to take each question and get the page and crop the bounding box and save each question to folder 'questions' in its own folder just named the question number, with the image + the cropped just of the question itself and just of the answer choices (if its a multiple choice), also if its free response check if it has sub-questions and save those, and save some jsons for these to store all the info

def analyze_test(test_folder: str) -> Dict[int, Dict]:
    # work in progress
    pages_paths = pdf_save_pages(f"{test_folder}/test.pdf", f"{test_folder}/pages")

    tags = get_tags(f"{test_folder}/test.pdf")
