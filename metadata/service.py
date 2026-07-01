from metadata import cache
from metadata import tmdb


class MetadataService:

    def lookup(self, title):

        data = cache.load(title)

        if data:
            print(f"[CACHE] {title}")
            return data

        print(f"[TMDB ] {title}")

        data = tmdb.lookup(title)

        if data:
            cache.save(title, data)

        return data
