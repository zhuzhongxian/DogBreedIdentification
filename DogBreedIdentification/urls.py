from apps.users import urls as user_urls
from apps.search import urls as search_urls
urlpattern = []

urlpattern += user_urls.urlpattern
urlpattern += search_urls.urlpattern