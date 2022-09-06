import sys
from PackageAndTruck import Package, Truck
from HashTable import LPHashTable, ChainingHashTable
from DeliveryLocation import DeliveryLocation
import csv
from operator import attrgetter
import gc

# Name: Avraham Gross
# Student ID: 009965073

# Read Delivery Location file, parse data to individual locations with all associated locations and distance
filename = input('PLease input delivery location file path: ')
if filename == "":
    filename = 'C:\\Users\Avramie\Downloads\WGUPS Distance Table.csv'
csvfile = open(filename, 'r')  # Input correct file path here
csvreader = csv.reader(csvfile)
rows = []
i = 0
# Skip lines in file that do not contain location data
for row in csvreader:
    if row[0] == '':
        continue
    if row[0] == 'DISTANCE BETWEEN HUBS IN MILES':  # Skipping header row
        continue
    rows.append(row)
del row
# Parse individual location data
location_map = LPHashTable(len(rows))
delivery_location_distance_list_length = None
for i in range(len(rows)):
    current_location_name = rows[i][1].split('\n')[0].lstrip()
    delivery_location_distance_list = []
    for j in range(2, len(rows) + 2):  # In order to properly parse correct location distance data,
        if i <= j - 2:                 # change from iterating through row to iterating through column
            for k in range(i, len(rows)):
                next_delivery_location = DeliveryLocation(rows[k][1].split('\n')[0].lstrip(), float(rows[k][j]))    # Create Delivery location with name and distance of location
                delivery_location_distance_list.append(next_delivery_location)
            break
        else:  # Continue iterating through row until reaching column of current_location_name's distance
            next_delivery_location = DeliveryLocation(rows[j - 2][1].split('\n')[0].lstrip(), float(rows[i][j]))     # Create Delivery location with name and distance of location
            delivery_location_distance_list.append(next_delivery_location)
    # Sort location distance data from closest to furthest, create Delivery Location object with current location,
    # associated distances, and add to location map
    delivery_location_distance_list.sort(key=attrgetter('distance'))
    delivery_location = DeliveryLocation(current_location_name, None, delivery_location_distance_list)
    location_map.insert(current_location_name, delivery_location)
delivery_location_distance_list_length = len(delivery_location_distance_list)
csvfile.close()
del delivery_location_distance_list
gc.collect()

# Read Package file, parse data to create all packages
filename = input('PLease input package file path: ')
if filename == '':
    filename = 'C:\\Users\Avramie\Downloads\WGUPS Package File.csv'
open_csv = open(filename)  # Input correct file path here
for i in range(11):  # Skip lines in file that do not contain package data
    rows = open_csv.readline()
rows = open_csv.readlines()
delivery_deadlines = set()
package_map_by_location = ChainingHashTable(delivery_location_distance_list_length)
package_map_by_id = LPHashTable(len(rows))
for i in rows:
    rows = i.split(',')
    note = rows[7] + rows[8]
    package = Package(int(rows[0]), rows[1], rows[2], rows[3], int(rows[4]), rows[5], int(rows[6]), note)
    package_map_by_location.insert(package.address, package)    # Insert package into package map using address as key
    package_map_by_id.insert(package.id - 1, package)      # Insert package into package map using id as key
    delivery_deadlines.add(rows[5])
open_csv.close()
delivery_deadlines = list(delivery_deadlines)
delivery_deadlines.sort(reverse=True)
del rows
gc.collect()

# Divide packages between trucks based on logical conditions
truck1 = Truck(1, 8.0, 0.0)  # Truck Parameters: name, hour, minute of departure
truck2 = Truck(2, 9.0, 5.0)
truck3 = Truck(3, 10.0, 20.0)
truck_list = [truck1, truck2, truck3]
previous_address = 'HUB'
locations = location_map.search(previous_address, 'location_list', 'name')  # Get location_list of distances from HUB
same_truck = set()
same_truck_item = None
for location in locations:  # Retrieve packages in list based on location
    packages = package_map_by_location.search(location.name)
    if packages is not None:
        packages.sort(key=attrgetter('notes', 'delivery_deadline'),
                      reverse=True)  # Sort packages by notes and delivery deadline to meet constraints
        for package in packages:
            success = False  # Track if package was successfully added to a truck
            if package.id in same_truck:  # If a package must be delivered with other packages, but does not have a note i.e. package 19
                same_truck_item.add_to_package_list(package)
            elif package.delivery_deadline != delivery_deadlines[
                0] and package.notes == '':  # If there is a delivery deadline and no notes
                success = truck1.add_to_package_list(package)
            elif package.address == previous_address:  # If an address is already being visited by a truck
                for truck in truck_list:
                    if truck.location == package.address:
                        success = truck.add_to_package_list(package)
            elif package.notes[0:3] == 'Can':  # If a package can only be on a specific number truck
                correct_truck = getattr(sys.modules[__name__], 'truck' + package.notes[-1])
                success = correct_truck.add_to_package_list(package)
            elif package.notes[0: 7] == 'Delayed':  # If a package cannot leave the HUB until a delayed time
                # Set truck 2 departure time to delivery time
                if package.delivery_deadline != delivery_deadlines[0]:  # If there is a delivery deadline
                    success = truck2.add_to_package_list(package)
                    temp = package.notes.split('until ')
                    truck2.time = temp[1]
                    temp = temp[1].split()[0].split(':')
                    truck2.time_hr = int(temp[0])
                    truck2.time_min = int(temp[1])
                else:  # If there is no delivery deadline
                    success = truck3.add_to_package_list(package)
                    temp = package.notes.split('until ')
                    truck3.time = temp[1]
                    temp = temp[1].split()[0].split(':')
                    truck3.time_hr = int(temp[0])
                    truck3.time_min = int(temp[1])
            elif package.notes[
                 0: 5] == 'Wrong':  # If wrong address is listed correct address and add correct value to map
                package_map_by_location.remove(location.name, package)
                package.address = '410 S State St'
                package.city = 'Salt Lake City'
                package.state = "Utah"
                package.zip = 84111
                success = truck3.add_to_package_list(package)
                package_map_by_location.insert(package.address, package)
            # If there is a delivery deadline
            elif package.delivery_deadline != delivery_deadlines[0]:
                # If package must be on same truck as other packages
                if package.notes[0: 4] == 'Must':
                    associated_package = package.notes.split('Must be delivered with ')[1].split()
                    for i in range(len(associated_package)):
                        same_truck.add(int(associated_package[i]))
                    same_truck.add(package.id)
                    flag = False
                    for truck in truck_list:  # Check if one of the associated packages is already set to a truck
                        if same_truck.intersection(truck.package_list):
                            success = truck.add_to_package_list(package)
                            same_truck_item = truck
                            flag = True
                            break
                    if not flag:  # If not, set to truck 1
                        success = truck1.add_to_package_list(package)
                        same_truck_item = truck1
            elif not success:  # If a package has no note or delivery deadline, put on truck with the fewest packages.
                count = 16
                best_truck_index = -1
                for i, truck in enumerate(truck_list):
                    if truck.package_count <= count:
                        count = truck.package_count
                        best_truck = i
                truck_list[best_truck].add_to_package_list(package)
        previous_address = package.address

total_miles = 0
user_input_int = []
user_input = input(
    'Please input a time (24hr format 23:59): ')  # Take user input to search specific package information
if user_input != '':
    user_input = user_input.split(':')
    for i in range(len(user_input)):
        user_input_int.append(int(user_input[i]))
total_list = []
for truck in truck_list:  # Map route for each truck
    total_miles, total_list = truck.map_route(package_map_by_location, total_miles, location_map, total_list)
    # Set truck 3 departure time at truck 1 return time if later than
    if (truck1.meridian == 'AM' and truck1.time_hr >= truck3.time_hr and truck1.time_min > truck3.time_min) or (
            truck1.meridian == 'PM'):
        truck3.time_hr, truck3.time_min, truck3.time = truck1.time_hr, truck1.time_min, truck1.time
    else:
        truck3.departure_hr, truck3.departure_min, truck3.time = 10, 20, '10:20 AM'

# Run truck routes, print status update at input time
total_list.sort(key=lambda x: (x[1], x[2]))
truck1_distance = 0
truck2_distance = 0
truck3_distance = 0
truck_distance_list = [truck1_distance, truck2_distance, truck3_distance]
if user_input != '':   # If user input time, print status update at that specified time
    for item in total_list:
        hour = item[1]
        if item[3] == 'PM' and item[1] > 12:
            hour = item[1] - 12
        if (item[1] == user_input_int[0] and item[2] <= 45) or item[1] < user_input_int[0]:
            item[0].status = 'delivered at %.f:%02.f %s' % (
            hour, item[2], item[3])  # Mark package as delivered if before or at time of status update
            truck_distance_list[item[4] - 1] += item[0].miles_to_deliver
        elif truck.departure_hr < user_input_int[0] or (
                truck.departure_hr == user_input_int[0] and truck.departure_min <= user_input_int[1]):
            item[0].status = 'en route'  # Mark package 'en route' if truck left depot
# Print total distance driven by each truck at time of status update, print status update
    print('\nTruck 1: %f\nTruck 2: %f\nTruck 3: %f \n' % (truck_distance_list[0], truck_distance_list[1], truck_distance_list[2]))
    meridian = 'AM'
    if user_input_int[0] > 12:
        user_input_int[0] = user_input_int[0] - 12
        meridian = 'PM'
    print('Status Update at %s:%s %s' % (user_input[0], user_input[1], meridian))
else:     # If user did not specify time for status update, print update of final status after all trucks run route
    for item in total_list:
        hour = item[1]
        if item[3] == 'PM' and item[1] > 12:
            hour = item[1] - 12
        item[0].status = 'delivered at %.f:%02.f %s' % (hour, item[2], item[3])
package_map_by_id.print_all()
print('\nTotal miles driven:', total_miles, '\n')
