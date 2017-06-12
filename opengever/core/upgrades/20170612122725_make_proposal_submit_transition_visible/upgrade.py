from ftw.upgrade import UpgradeStep


class MakeProposalSubmitTransitionVisible(UpgradeStep):
    """Make proposal submit transition visible.
    """

    def __call__(self):
        self.install_upgrade_profile()
