class Obs:
    def __init__(self,date, event, identifier, value, server):
        self.date = date
        self.event = event
        self.identifier = identifier
        self.value = value
        self.server = server        
        self.encounterUUID = None   
        self.isSentinelEvent = True
        self.isFirstCD4 = False

    def __hash__(self):
        return hash(self.date, self.event, self.identifier, self.value, self.server)

    def __eq__(self, other):
        return (self.date, self.event, self.identifier, self.value, self.server) == (other.date, other.event, other.identifier, other.value, other.server)

    def __ne__(self, other):
        # Not strictly necessary, but to avoid having both x==y and x!=y
        # True at the same time
        return not(self == other)