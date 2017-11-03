# Put Needed Libraries Here
import json
import os
import time
import xmltodict
import sys
from threading import Thread, Lock

# List Global Variables Here
sharedDict = {}                  #The dictionary that all the threads with add to
sharedDictLock = Lock()          #The lock used so only one thread is writing to the sharedDict at a time

# Define Functions Here 
def main():
    scanDict = {
    "deviceScan.xml" : "-sn 192.168.200.* -oX ",                        # Quickly discovers hosts on the network, with their names, and MAC addresses
    "portScan.xml" : "-F 192.168.200.* -oX ",                           # Scan the top 100 common ports
    "serviceScan.xml" : "-sV 192.168.200.* -oX ",                       # Probe open ports to determine service/version info
    "osScan.xml" : "-O 192.168.200.* -oX "}                             # Enable OS detection

    try:
        # Spawn as many threads as in scanDict
        for fileName, argument in scanDict.iteritems():
            thread = Thread(target = runNMAP, args=(fileName, argument))        # Spawn a thread that will execute runNMAP with the given arguments
            thread.daemon = True                                                # Kill the thread automatically when the main thread ends
            thread.start()                                                      # Start the thread

        time.sleep(10)                                                  # Give time to collect some data

        # Periodically convert the shared dictionary to a JSON file
        while True:
            convertDictToJson()
            time.sleep(10)

    except KeyboardInterrupt:
        time.sleep(1)
        print("Shutting down...")
        sys.exit()

def runNMAP(fileName, argument):
    # Defining Variables Needed
    global sharedDict
    global sharedDictLock
    command = "nmap " + argument + fileName + " > /dev/null"

    # Script Actions
    print "Starting... thread running: " + command
    try:
        while True:
            os.system(command)
            with open(fileName, "rb") as xmlBinary:                                             # Reads XML file as binary
                xmlDict = xmltodict.parse(xmlBinary, xml_attribs=True)["nmaprun"]["host"]       # Convert the XML to a dictionary               
                sharedDictLock.acquire()                                                        # Thread grabbing the lock on the sharedDict
                # TODO: Define function to manually update the dictionaries
                sharedDict.update(xmlDict)                                                      # Update the global dictionary with the new results
                sharedDictLock.release()                                                        # Thread releasing the lock on the sharedDict
            time.sleep(10)
    except:
        print "Shutting down thread running: " + command

# Convert dictionary to JSON
def convertDictToJson():
    global sharedDict
    print "Updating Conceirge.json" 
    sharedDictLock.acquire()
    jsonString =  json.dumps(sharedDict, indent=4)
    sharedDictLock.release()
    with open("Conceirge.json", "wb") as jsonFile:
            jsonFile.write(jsonString)

if __name__ == "__main__":
    main()