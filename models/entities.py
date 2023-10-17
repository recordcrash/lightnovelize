class Entity:
    def __init__(self, name: str):
        self.name = name
        self.descriptions = []  # List to store descriptions sequentially
        self.summary = ""  # Concise summary of the entity

    def add_description(self, desc: str, chapter: int):
        # Each description is associated with a chapter to maintain a timeline
        self.descriptions.append({"chapter": chapter, "description": desc})

    def generate_summary(self):
        # Logic to generate a concise summary for the entity, can be done with GPT-4 if needed
        pass

    def get_description_for_chapter(self, chapter: int) -> str:
        # Returns the most recent description up to the given chapter
        for desc in reversed(self.descriptions):
            if desc["chapter"] <= chapter:
                return desc["description"]
        return self.summary  # Fallback to the summary if no specific description found

    def merge(self, other_entity):
        # Logic to merge two entities
        self.descriptions.extend(other_entity.descriptions)
        # Sort descriptions by chapter to maintain the timeline
        self.descriptions.sort(key=lambda x: x['chapter'])


class Chapter:
    def __init__(self, chapter_number: int, text: str):
        self.chapter_number = chapter_number
        self.text = text
        self.entities = []  # List of entities (characters/props/locations) that appear in this chapter


class Book:
    def __init__(self, title: str):
        self.title = title
        self.chapters = []  # List of Chapter objects
        self.global_entities = {}  # Dictionary with entity names as keys and Entity objects as values

    def add_chapter(self, chapter: Chapter):
        self.chapters.append(chapter)

    def add_global_entity(self, entity: Entity):
        self.global_entities[entity.name] = entity

    def get_entities_for_chapter(self, chapter_number: int) -> list:
        return [entity for chapter in self.chapters if chapter.chapter_number == chapter_number for entity in
                chapter.entities]

    def merge_entities(self, old_entity_name: str, new_entity_name: str):
        if old_entity_name in self.global_entities and new_entity_name in self.global_entities:
            self.global_entities[new_entity_name].merge(self.global_entities[old_entity_name])
            del self.global_entities[old_entity_name]
