from ftw.upgrade import UpgradeStep


class UpgradeThatFlushes(UpgradeStep):
    """Upgrade that flushes.
    """

    def __call__(self):
        cata = self.getToolByName('portal_catalog')
        cata(portal_type='opengever.repository.repositoryfolder')
