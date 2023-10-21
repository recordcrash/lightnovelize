import configparser
import os
from models import entities
from modules import description_extractor, scene_generator

# Load configurations from config.ini
config = configparser.ConfigParser()
config.read('config.ini')

# Check if config.ini exists
if not os.path.exists('config.ini'):
    raise FileNotFoundError("config.ini not found. Please ensure it exists in the root directory.")

# Check for mandatory options
if (not config.has_option('DEFAULT', 'OPENAI_API_KEY') or not config['DEFAULT']['OPENAI_API_KEY'] or
        config['DEFAULT']['OPENAI_API_KEY'] == 'YOUR_API_KEY_HERE'):
    raise ValueError("OPENAI_API_KEY is not set in config.ini.")
if not config.has_option('DEFAULT', 'INPUT_FOLDER') or not config['DEFAULT']['INPUT_FOLDER']:
    raise ValueError("INPUT_FOLDER is not set in config.ini.")
if not config.has_option('DEFAULT', 'TARGET_FOLDER') or not config['DEFAULT']['TARGET_FOLDER']:
    raise ValueError("TARGET_FOLDER is not set in config.ini.")

# Check if INPUT_FOLDER exists and has valid files
input_folder = config['DEFAULT']['INPUT_FOLDER']
if not os.path.exists(input_folder):
    raise FileNotFoundError(f"Input folder '{input_folder}' not found.")
file_exts = ['.txt', '.docx', '.odt', '.pdf', '.epub', '.rtf', '.html']
filepaths = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if
             os.path.splitext(f)[-1].lower() in file_exts]
if not filepaths:
    raise ValueError("No valid files found in the input folder.")

# Check if TARGET_FOLDER exists, if not, create it
target_folder = config['DEFAULT']['TARGET_FOLDER']
if not os.path.exists(target_folder):
    os.makedirs(target_folder)


def main():
    local_mode = False
    # Show the list of files to be processed
    print("The following files will be processed:")
    for path in filepaths:
        print(f"- {path}")

    # Ask for confirmation
    confirmation = input("\nDo you want to continue? (yes/no): ").strip().lower()
    if confirmation not in ('yes', ''):
        print("Operation aborted.")
        return

    # get title from first file
    book_title = os.path.splitext(os.path.basename(filepaths[0]))[0]
    book = entities.Book(book_title)

    chapters = []
    for filepath in filepaths:
        chapters.extend(description_extractor.extract_content_as_chapters(filepath))

    print(f"Processing {len(chapters)} chapters...")
    current_description = {}
    for chapter_number, chapter_content in enumerate(chapters, start=1):
        print(f"\nProcessing chapter {chapter_number}...")

        # Dividing chapter into sections
        sections = description_extractor.split_text_into_sections(chapter_content)
        all_descriptions = [description_extractor.extract_descriptions_from_section(section, local_mode=local_mode)
                            for section in sections]

        # Combine sections in one
        if len(all_descriptions) > 1:
            single_description = description_extractor.enhance_descriptions(all_descriptions, local_mode=local_mode)
        else:
            single_description = all_descriptions[0]

        # Combine chapters in one
        if chapter_number > 1:
            current_description = description_extractor.enhance_descriptions([single_description, current_description],
                                                                             local_mode=local_mode)
        else:
            current_description = single_description

    # Second loop, this time to get a scene per chapter/chapter section that we can draw with DALL·E
    for chapter_number, chapter_content in enumerate(chapters, start=1):
        scene_prompt = scene_generator.generate_dalle_prompt_from_chapter_and_data(chapter_content, current_description,
                                                                                   local_mode=local_mode)
        print(scene_prompt)


if __name__ == "__main__":
    main()
