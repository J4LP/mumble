
class InvalidUUIDError(Exception):
    pass


class GuestPassExpiredError(Exception):

    model = None

    def __init__(self, *args, **kwargs):
        if args[0]:
            self.model = args[0]
        super(GuestPassExpiredError, self).__init__()



class InvalidCorporationError(Exception):

    corporation = None

    def __init__(self, *args, **kwargs):
        super(InvalidCorporationError, self).__init__()
        if args[0]:
            self.corporation = args[0]

class InvalidAllianceError(Exception):

    alliance = None

    def __init__(self, *args, **kwargs):
        super(InvalidAllianceError, self).__init__()
        if args[0]:
            self.alliance = args[0]
