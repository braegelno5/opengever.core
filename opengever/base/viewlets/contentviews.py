from plone.app.layout.viewlets.common import ContentViewsViewlet


class ModelContentViewsViewlet(ContentViewsViewlet):
    """Provide correct edit links for a SQL-model based view.

    For plone content fall-back to default content views.
    """

    def prepareObjectTabs(self, default_tab='view', sort_first=('folderContents',)):
        """Prepare the object tabs by determining their order and working
        out which tab is selected. Used in global_contentviews.pt
        """

        if getattr(self.view, 'is_model_view', False):
            return self.prepare_model_tabs()
        else:
            return super(ModelContentViewsViewlet, self).prepareObjectTabs(
                default_tab, sort_first)

    def prepare_model_tabs(self):
        model = self.view.model
        return ({
            'category': 'object',
            'available': True,
            'description': u'',
            'icon': '',
            'title': u'Edit',
            'url': model.get_edit_url(),
            'selected': self.view.is_model_edit_view,
            'visible': True,
            'allowed': True,
            'link_target': None,
            'id': 'edit'
        },)
