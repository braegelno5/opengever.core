from ftw.upgrade import UpgradeStep


class InstallOpengeverOfficeconnector(UpgradeStep):
    """Install opengever officeconnector.
    """

    def __call__(self):
        self.install_upgrade_profile()
