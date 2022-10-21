# Delivery-Service-Routing
Greedy Algorithm implementation for truck routing

A Python script to route delivery trucks efficiently while adhering to package constraints.
<br>
The script parses delivery loaction file and maps each location to an array of all other locations and distances from the key to the desired locaion, sorted by distance.
<br>
The script also parses package data file and adds each package to a list. It then iterates through the list to sort out the packages amongst the available trucks based on a set of conditions and package restrictions.
<br>
To route each truck, the closest locaion is picked from the unvisited locations the truck must deliver to, until all packages are delivered
<br>
A time tracking mechanism is used to allow for detailed reports at any given time in the day. The time for the report is supplied by the user in the command line.
<br>
Implementation of Chaining HashTable and Linear Position HashTable to store package and delivery locaion data.
