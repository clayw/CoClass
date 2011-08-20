from haystack import indexes
from haystack import site
from models import CourseInfo

class CourseInfoIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    categories = indexes.MultiValueField()
    rating = indexes.FloatField()
    # render
    rendered = indexes.CharField(use_template=True, indexed=False)

    def get_queryset(self):
        return CourseInfo.objects.filter(published=True)

    def prepare_categories(self, obj):
        cats = []
        for cc in obj.coursecategory.all():
            cat = cc.category
            while cat:
                cats.append(cat)
                cat = cat.parent_category
        return cats # meow

    def prepare_rating(self, obj):
        return obj.get_rating()

site.register(CourseInfo, CourseInfoIndex)

