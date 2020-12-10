class Patient:
    def __init__(self,identifier, givenName, middleName, familyName, gender, birthdate):
        self.identifier = identifier
        self.givenName = givenName
        self.middleName = middleName
        self.familyName = familyName
        self.gender = gender
        self.birthdate = birthdate
        self.serverPatientUUID = {}
        self.serverPatientIdentifier = {}
        self.obs = []
        self.shrPatientUUID = None    
        self.fhirPatientUUID = None    

    def __hash__(self):
        return hash(self.identifier)

    def __eq__(self, other):
        return (self.identifier, self.givenName, self.middleName, self.familyName, self.gender, self.birthdate) == (other.identifier, other.givenName, other.middleName, other.familyName, other.gender, other.birthdate)

    def __ne__(self, other):
        # Not strictly necessary, but to avoid having both x==y and x!=y
        # True at the same time
        return not(self == other)

