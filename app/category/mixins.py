from pydantic import computed_field

class CategoryParserMixin:
    @computed_field
    @property
    def parsed_categories(self) -> str:
        if hasattr(self, 'categories'):
            return '\n'.join([f'{category.name}: {category.description}' for category in self.categories])

    def parsed_category(self) -> str:
        if hasattr(self, 'category'):
            return f'{self.category.name}: {self.category.description}'
