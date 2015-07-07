# -*- coding: utf-8 -*-
from django.core.cache import cache
from cms.sitemaps import CMSSitemap
from django.contrib.sites.models import Site
from django.db.models import Q

from cms.models import Title
from .models import PageSitemapProperties
from .settings import PAGE_SITEMAP_CACHE
from .utils import get_cache_key


class ExtendedSitemap(CMSSitemap):
    default_changefreq = CMSSitemap.changefreq
    default_priority = CMSSitemap.priority

    def priority(self, title):
        ext_key = get_cache_key(title.page)
        properties = cache.get(ext_key)
        if properties:
            return properties.priority
        else:
            try:
                cache.set(ext_key, title.page.pagesitemapproperties, PAGE_SITEMAP_CACHE)
                return title.page.pagesitemapproperties.priority
            except PageSitemapProperties.DoesNotExist:
                return self.default_priority

    def changefreq(self, title):
        ext_key = get_cache_key(title.page)
        properties = cache.get(ext_key)
        if properties:  # pragma: no cover
            return properties.changefreq
        else:
            try:
                cache.set(ext_key, title.page.pagesitemapproperties, PAGE_SITEMAP_CACHE)
                return title.page.pagesitemapproperties.changefreq
            except PageSitemapProperties.DoesNotExist:
                return self.default_changefreq

    def items(self):
        all_titles = Title.objects.public().filter(
                    Q(redirect='') | Q(redirect__isnull=True),
                    Q(page__pagesitemapproperties__exclude=False) | Q(page__pagesitemapproperties__exclude__isnull=True),
                    page__login_required=False,
                    page__site=Site.objects.get_current())
        return all_titles
