import configparser
import os

from modules import description_extractor

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
    # Show the list of files to be processed
    print("The following files will be processed:")
    for path in filepaths:
        print(f"- {path}")

    # Ask for confirmation
    confirmation = input("\nDo you want to continue? (yes/no): ").strip().lower()
    if confirmation not in ('yes', ''):
        print("Operation aborted.")
        return

    for filepath in filepaths:
        print(f"\nProcessing {filepath}...")
        descriptions = description_extractor.extract_descriptions_from_file(filepath)
        print(descriptions)
        # Further processing or saving the descriptions as needed


if __name__ == "__main__":
    main()
