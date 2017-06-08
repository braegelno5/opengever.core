from ftw.upgrade import UpgradeStep


class TestUpgradeThatReindexes(UpgradeStep):
    """test upgrade that reindexes.
    """

    def __call__(self):
        cata = self.getToolByName('portal_catalog')
        for brain in cata(portal_type='opengever.repository.repositoryfolder'):
            brain.getObject().reindexObject()
