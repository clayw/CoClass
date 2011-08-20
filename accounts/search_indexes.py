from haystack import indexes
from haystack import site
from models import Expert

class ExpertIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    lat = indexes.FloatField(model_attr='place__latitude')
    lng = indexes.FloatField(model_attr='place__longitude')
    # render
    rendered = indexes.CharField(use_template=True, indexed=False)

    def get_queryset(self):
        return Expert.objects.filter(privacy='a')


site.register(Expert, ExpertIndex)

