from plone.rest import Service


class Attach(Service):

    def render(self):
        # TODO - journal entry
        return self.context.restrictedTraverse(
            'download_file_version').render()


class Download(Service):

    def render(self):
        # TODO - journal entry
        return self.context.restrictedTraverse(
            'download_file_version').render()


class Checkout(Service):

    def render(self):
        self.context.restrictedTraverse('checkout_documents')
        return '{"message": "Checkout"}'


class Checkin(Service):

    def render(self):
        self.context.restrictedTraverse('checkin_documents')
        return '{"message": "Checkin"}'
