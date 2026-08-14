from django.conf import settings
from elasticsearch import Elasticsearch

elasticsearch_client = Elasticsearch(
    settings.ELASTICSEARCH_URL,
    request_timeout=5,
)
