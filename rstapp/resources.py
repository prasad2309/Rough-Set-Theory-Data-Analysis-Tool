from import_export import resources
from .models import Document

class DocumentResource(resources.ModelResource):
    class Meta:
        model = Document
