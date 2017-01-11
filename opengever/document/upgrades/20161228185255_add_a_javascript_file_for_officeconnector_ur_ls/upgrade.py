from ftw.upgrade import UpgradeStep


class AddAJavascriptFileForOfficeconnectorURLs(UpgradeStep):
    """Add a javascript file for officeconnector URLs.
    """

    def __call__(self):
        self.install_upgrade_profile()
