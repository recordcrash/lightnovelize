import configparser
import json

import ebooklib
import textract
from bs4 import BeautifulSoup
from ebooklib import epub
from openai import OpenAI

# Load configuration
config = configparser.ConfigParser()
config.read('config.ini')

# Initialize the OpenAI client
client = OpenAI(
    api_key=config['DEFAULT']['OPENAI_API_KEY']
)


def split_text_into_sections(text: str, max_chars=20000) -> list:
    """
    Splits the given text into sections based on the max_chars limit, ensuring
    no paragraphs are split in half.
    """
    paragraphs = text.split("\n")
    sections = []
    current_section = ""

    for paragraph in paragraphs:
        if len(current_section) + len(paragraph) < max_chars:
            current_section += paragraph + "\n"
        else:
            sections.append(current_section.strip())
            current_section = paragraph + "\n"
    if current_section:
        sections.append(current_section.strip())

    return sections


def extract_descriptions_from_section(section: str) -> dict:
    """
    Uses GPT-4 to extract character, prop, and location descriptions from the provided section of text.
    """
    # Construct the user prompt
    print("Extracting descriptions from the following section:")
    print(section)
    user_prompt = section

    # System prompt from the saved file
    with open("./prompts/extract_descriptions_system_prompt.txt", "r") as f:
        system_prompt = f.read()

    # Call to GPT-4
    print("Calling GPT-4 for description extraction...")
    completion = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    response_content = json.loads(completion.choices[0].message.content)
    print("Response from GPT-4 for description extraction:")
    print(response_content)
    return response_content


def consolidate_descriptions(descriptions: list) -> dict:
    """
    Combines descriptions for named characters, props, and locations across multiple mentions.
    """
    consolidated_data = {}
    # Logic to consolidate descriptions (this will be expanded further)
    # This is a placeholder for now.
    for description in descriptions:
        for key, value in description.items():
            if key in consolidated_data:
                consolidated_data[key].append(value)
            else:
                consolidated_data[key] = [value]

    return consolidated_data


def enhance_descriptions(data: dict) -> dict:
    """
    Enhances sparse or ambiguous descriptions.
    """
    # Construct the user prompt
    user_prompt = str(data)

    # System prompt from the saved file
    with open("./prompts/consolidate_descriptions_system_prompt.txt", "r") as f:
        system_prompt = f.read()

    # Call to GPT-4
    print("Calling GPT-4 for description enhancement...")
    completion = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    response_content = json.loads(completion.choices[0].message.content)
    print("Response from GPT-4 for description enhancement:")
    print(response_content)
    return response_content


def extract_chapters_from_epub(filepath: str) -> list:
    """
    Extracts chapters from the given EPUB file.
    """
    book = epub.read_epub(filepath)
    chapters = []

    for item in book.items:
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            # Parse the content with BeautifulSoup
            soup = BeautifulSoup(item.content, 'html.parser')

            # Replace <i> and <b> tags with spaces to prevent words from merging
            for tag in soup.find_all(['i', 'b']):
                tag.replace_with(f" {tag.get_text()} ")

            # Extract text from paragraphs
            paragraphs = soup.find_all('p')
            chapter_text = '\n'.join([p.get_text(strip=True) for p in paragraphs])

            # Join broken sentences
            lines = chapter_text.split('\n')
            for i in range(len(lines) - 1):
                if not lines[i].endswith(('.', ',', '!', '?', ';', ':', '-', '”')):
                    lines[i + 1] = lines[i] + ' ' + lines[i + 1]
                    lines[i] = ''
            chapter_text = '\n'.join(filter(None, lines))

            # Only include chapters that exceed 700 words
            if chapter_text and len(chapter_text.split()) > 700:
                chapters.append(chapter_text)

    return chapters


def extract_descriptions_from_file(filepath: str) -> dict:
    """
    Main function to extract character, prop, and location descriptions from the provided file.
    """
    if filepath.endswith('.epub'):
        chapters = extract_chapters_from_epub(filepath)
        all_descriptions = []

        for chapter in chapters:
            sections = split_text_into_sections(chapter)

            for section in sections:
                all_descriptions.append(extract_descriptions_from_section(section))

    else:
        text = textract.process(filepath).decode('utf-8')
        sections = split_text_into_sections(text)

        all_descriptions = []
        for section in sections:
            all_descriptions.append(extract_descriptions_from_section(section))

    consolidated_data = consolidate_descriptions(all_descriptions)
    final_data = enhance_descriptions(consolidated_data)

    return final_data
