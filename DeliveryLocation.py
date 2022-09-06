# This class is used in two distinct ways. A Delivery Location can be a location with a certain distance to get there,
# or a location with a list of all available locations to visit next
class DeliveryLocation:

    def __init__(self, name, distance = None, location_list = None):
        self.name = name
        self.distance = distance
        self.location_list = location_list

