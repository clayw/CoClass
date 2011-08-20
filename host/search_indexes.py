from haystack import indexes
from haystack import site
from models import HostClass

class HostClassIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    lat = indexes.FloatField(model_attr='place__latitude')
    lng = indexes.FloatField(model_attr='place__longitude')
    start_date = indexes.DateField(model_attr='disp_start_date')
    # render
    rendered = indexes.CharField(use_template=True, indexed=False)

    def get_queryset(self):
        return HostClass.objects.filter(privacy='a')

site.register(HostClass, HostClassIndex)
