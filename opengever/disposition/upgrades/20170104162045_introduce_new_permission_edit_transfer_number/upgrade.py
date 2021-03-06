from ftw.upgrade import UpgradeStep


class IntroduceNewPermissionEditTransferNumber(UpgradeStep):
    """Introduce new permission edit transfer number.
    """

    def __call__(self):
        self.install_upgrade_profile()

        self.update_workflow_security(
            ['opengever_disposition_workflow'], reindex_security=False)
