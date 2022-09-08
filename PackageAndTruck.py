
class Package:

    def __init__(self, id, address, city, state, zip, delivery_deadline, weight, notes, status):
        self.id = id
        self.address = address
        self.city = city
        self.state = state
        self.zip = zip
        self.delivery_deadline = delivery_deadline
        self.weight = weight
        self.notes = notes
        self.status = status
        self.miles_to_deliver = 0
        self.truck_num = 0

    def print_all(self):
        print(self.id, self.address, self.delivery_deadline, self.notes,
              self.status)


class Truck:

    def __init__(self, name, hour, min):
        self.name = name
        self.package_count = 0
        self.package_list = []
        self.package_list_id = []
        self.priority_packages_address = []
        self.package_list_location = []
        self.location_list = set()
        self.package_delivery_list = []
        self.distance_list = []
        self.route_list = []
        self.departure_hr = hour
        self.departure_min = min
        self.location = None
        self.SPEED = 18.0
        self.miles_traveled = 0.0
        self.time_hr = hour
        self.time_min = min
        self.meridian = 'AM'
        self.time = '%.f:%02.f %s' % (self.time_hr, self.time_min, self.meridian)

    def add_to_package_list(self, package):  # Add package to truck
        if self.package_count + 1 <= 16:
            self.package_list.append(package.id)
            self.package_list_id.append(package.id)
            if package.delivery_deadline != 'EOD':  # Maintain list of packages with delivery deadlines
                self.priority_packages_address.append(package.address)
            self.package_list_location.append(package.address)
            self.package_count += 1
            self.location = package.address
            package.truck_num = self.name
            return True
        return False

    # Map delivery route. Start with delivery deadline packages
    # and always visit next closest location in package_list_location
    def map_route(self, package_map_by_location, total_miles, location_map, total_list):
        locations = location_map.search('HUB', 'location_list', 'name')
        if len(self.priority_packages_address) > 0:
            # Track user input package and time to report status at or around input time. show status update based on required times in PA Requirement G
            locations, total_miles, total_list = self.map_timed_packages(locations, package_map_by_location, total_miles,
                                                             location_map, total_list)  # Route delivery deadline packages
        while len(self.package_list_location) > 0:  # Route remaining packages
            package_list = None
            for location in locations:
                if location.name in self.package_list_location:  # Find next closest location
                    package_list = package_map_by_location.search(location.name)
                    break
            for package in package_list:  # Deliver packages
                if package.id in self.package_list_id:
                    self.add_package(package, location)
                    total_list.append((package, self.time_hr, self.time_min, self.meridian, self.name))
            total_miles = total_miles + location.distance
            locations = location_map.search(location.name, 'location_list', 'name')
        if len(self.package_list_location) == 0:  # If all packages on truck are delivered, return to HUB
            for location in locations:
                if location.name == 'HUB':
                    self.return_to_hub(location)
                    total_miles = total_miles + location.distance
                    break
        return total_miles, total_list

    # Route packages with delivery deadline
    def map_timed_packages(self, locations, package_map_by_location, total_miles, location_map, total_list):
        package_list = None
        route_list = None
        while len(self.priority_packages_address) > 0:
            for location in locations:  # Find next closest location
                if location.name in self.priority_packages_address:
                    package_list = package_map_by_location.search(location.name)
                    break
            for package in package_list:  # Add package to delivered if on the truck
                if package.id in self.package_list_id:
                    self.add_package(package, location)
                    total_list.append((package, self.time_hr, self.time_min, self.meridian, self.name))
                    if package.address in self.priority_packages_address:
                        self.priority_packages_address.remove(
                            package.address)  # Remove address from priority package list
            total_miles = total_miles + location.distance
            locations = location_map.search(location.name, 'location_list', 'name')
        return locations, total_miles, total_list  # Return current location list, total miles, track if user input package delivered at user input time,
        # track if appropriate time for status update, route_list for running the route

    # Add package to delivered list, update truck data
    def add_package(self, package, location):
        self.package_delivery_list.append(package)
        self.location_list.add(location.name)
        self.distance_list.append((location.name, location.distance))
        self.package_list_location.remove(package.address)
        self.package_list_id.remove(package.id)
        self.route_list.append((package, self.time_hr, self.time_min, self.meridian))
        old_location = self.location
        self.location = package.address
        if old_location != self.location:  # Only update time and distance traveled if package delivered to new location
            self.miles_traveled = self.miles_traveled + location.distance
            travel_time = (location.distance / self.SPEED) * 60
            self.time_hr = self.time_hr + ((travel_time + self.time_min) // 60)
            self.time_min = (self.time_min + travel_time) % 60
            if self.time_min == 60:
                self.time_min = 0
                self.time_hr = self.time_hr + 1
            if self.time_hr >= 12:
                self.meridian = 'PM'
            if self.time_hr > 12:
                self.time_hr = self.time_hr - 12
            self.time = '%.f:%02.f %s' % (self.time_hr, self.time_min, self.meridian)
        package.miles_to_deliver = location.distance
        return True

    # Return truck to HUB
    def return_to_hub(self, location):
        self.location_list.add(location.name)
        self.distance_list.append((location.name, location.distance))
        self.location = location.name
        self.miles_traveled = self.miles_traveled + location.distance
        travel_time = (location.distance / self.SPEED) * 60
        self.time_hr = self.time_hr + ((travel_time + self.time_min) // 60)
        self.time_min = (self.time_min + travel_time) % 60
        if self.time_min == 60:
            self.time_min = 0
            self.time_hr = self.time_hr + 1
        if self.time_hr >= 12:
            self.meridian = 'PM'
        if self.time_hr > 12:
            self.time_hr = self.time_hr - 12
        self.time = '%.f:%02.f %s' % (self.time_hr, self.time_min, self.meridian)
