import datetime
from haystack import indexes
from rango.models import Page, Category


class PageIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, model_attr='title', use_template=False)

    def get_model(self):
        return Page

    def index_queryset(self, using=True):
        return self.get_model().objects.all()

class CategoryIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, model_attr='name', use_template=False)

    def get_model(self):
        return Category
    def index_queryset(self, using=True):
        return self.get_model().objects.all()
