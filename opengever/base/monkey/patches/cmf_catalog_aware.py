from opengever.base.monkey.patching import MonkeyPatch
from zope.globalrequest import getRequest
from zope.interface import alsoProvides
from zope.interface import Interface
from zope.interface import noLongerProvides


class IDisableCatalogIndexing(Interface):
    """Marker-interface to disable the catalog
    indexing functions.

    If this interface is provided by the request, all the
    catalog-index-methods will be disabled.

    Use the DeactivatedCatalogIndexing contextmanager to
    get in use of this functionality.
    """


class DeactivatedCatalogIndexing(object):
    """Contextmanager: Deactivates catalog-indexing
    """
    def __enter__(self):
        alsoProvides(getRequest(), IDisableCatalogIndexing)

    def __exit__(self, exc_type, exc_val, exc_tb):
        noLongerProvides(getRequest(), IDisableCatalogIndexing)


class PatchCMFCatalogAware(MonkeyPatch):
    """Patch the Products.CMFCore.CMFCatalogAware indexObject, reindexObject
    and unindexObject methods.

    This patch is deactivated by default and can be activated through
    the DeactivatedCatalogIndexing context manager:

    >>> with DeactivatedCatalogIndexing():
    ...     object.reindexObject  # Does nothing
    ...     object.unindexObject  # Does nothing
    ...     object.indexObject  # Does nothing

    If the patch is activated, it skips the catalog index-methods.

    What's the motivation behind this patch?

    While creating an object, the object will be reindexed up to 4 times.
    This behavior takes a lot of time and is not performance-friendly. Creating
    one object through the web might be not a performance issue. But in several
    parts of the GEVER-system we're creating a lot of content programatically
    (i.e. dossiertemplates).

    To improve the performance in that case, you can decativate the index-methods
    and do it manually at the end of your tasks.
    """

    def __call__(self):

        def _is_indexing_disabled():
            return IDisableCatalogIndexing.providedBy(getRequest())

        def indexObject(self):
            if _is_indexing_disabled():
                # do nothing if indexing is disabled
                return
            return original_indexObject(self)

        def unindexObject(self):
            if _is_indexing_disabled():
                # do nothing if indexing is disabled
                return
            return original_unindexObject(self)

        def reindexObject(self, idxs=[]):
            if _is_indexing_disabled():
                # do nothing if indexing is disabled
                return
            return original_reindexObject(self, idxs)

        from Products.CMFCore.CMFCatalogAware import CMFCatalogAware
        __patch_refs__ = False
        original_indexObject = CMFCatalogAware.indexObject
        original_unindexObject = CMFCatalogAware.unindexObject
        original_reindexObject = CMFCatalogAware.reindexObject
        self.patch_refs(CMFCatalogAware, 'indexObject', indexObject)
        self.patch_refs(CMFCatalogAware, 'unindexObject', unindexObject)
        self.patch_refs(CMFCatalogAware, 'reindexObject', reindexObject)
