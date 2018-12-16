import sys, datetime, pytz, requests, json, simplejson

from astral import *
from error import hiveError
from pprint import pprint

# Payload constants
ON_PAYLOAD = \
    '{"nodes":[{"attributes":{"state":{"targetValue":"ON"}}}]}'
OFF_PAYLOAD = \
    '{"nodes":[{"attributes":{"state":{"targetValue":"OFF"}}}]}'
API_ADDR = "https://api-prod.bgchprod.info/omnia/"

# Escaped so value can be formatted
BRIGHTNESS_PAYLOAD = \
    '{{"nodes":[{{"attributes":{{"brightness":{{"targetValue":"{}"}}}}}}]}}'
TEMPERATURE_PAYLOAD = \
 '{{"nodes":[{{"attributes":{{"colourTemperature":{{"targetValue":"{}"}}}}}}]}}'

class hive:
    """Hive device control class\
    \
    This class controls hive devices. Currently, this only supports lights and groups of\
    lights.\
    
    """
    def __init__(self):
        """Initiliase hive class
    
        Initialises the hive class, sets variables and initialises the devices

        :param self: Instance of hive class
        :raises ValueError: Nothing yet
        :return: None:
        :rtype: None:\
        """
        #global vars
        self.username = None
        self.password = None
        self.apikey = None
        self.DEBUG = False
        self.l = Location(info=("London","UK",51.5074, 0.1278, "Europe/London"))
        self.data = None
        self.now = None
        self.buttons = None

        self.arrDevices = {}
        
        #Initialise data
        self.hive_main()
        
        #Initialise list of lights
        self._getDevices(True)
        self._initCustomGroups()
        self._initGroupStatus()

    def getButtonsSetting(self):
        return self.buttons

    #sends the username/password combo to get an apikey
    def getApiKey(self, force = False):
        """Obtains the Api key
        
        Sends the username and password from the configuration file to obtain the api key.
        
        :param self: Instance of hive class
        :param force: Boolean that forces the Api key to be reobtained
        :raises ValueError: Nothing yet
        :return: Api Key
        :rtype: str\
        """
        try:
            if (self.apikey is None or force):
                #gets a new apikey
                keys = {'username':self.username,'password':self.password,'caller':'web'}
                r = requests.post("https://api-prod.bgchprod.info:8443/api/login",params=keys)
                self.apikey= r.json()['ApiSession']
            
                if (r.status_code is not 200):
                    raise hiveError(r.status_code)

        except hiveError as hE:
            print("An exception occured: ", hE.value)

        except:
            print("Unexpected exception in hive._sendDeviceValue():" + \
                  "{} - {}".format(sys.exc_info()[0], sys.exc_info()[1]))

        else:
            return self.apikey

    def getLights(self, force = False):
        """Gets a list of the lights
        
        Gets a list of Hive light devices.
        
        :param self: Instance of hive class
        :param force: Boolean that forces a refresh of devices with the server
        :raises ValueError: Nothing yet
        :return: List of lights
        :rtype: dictionary\
        """
        self._getDevices(force)
        arrLights = {}
        for id, device in self.arrDevices.items():
            if (device['type'] == 'light'):
                arrLights[id] = device
        return arrLights
        
    def getGroups(self, force = False):
        """Gets a list of the groups
        
        Gets a list of Hive group devices.
        
        :param self: Instance of hive class
        :param force: Boolean that forces a refresh of devices with the server
        :raises ValueError: Nothing yet
        :return: List of groups
        :rtype: dictionary\
        """
        self._getDevices(force)
        arrGroups = {}
        for id, device in self.arrDevices.items():
            if (device['type'] == 'group'):
                arrGroups[id] = device
        return arrGroups
        
    def getDevices(self, force = False):
        """Gets a list of the devices
        
        Gets a list of Hive devices.
        
        :param self: Instance of hive class
        :param force: Boolean that forces a refresh of devices with the server
        :raises ValueError: Nothing yet
        :return: List of devices
        :rtype: dictionary\
        """
        self._getDevices(force)
        return self.arrDevices

    def _getDevices(self, force = False):
        """Gets a list of the devices
        
        Gets a list of Hive devices. Currently, this only supports groups and lights.
        This should not be called directly from outside the class.
        
        :param self: Instance of hive class
        :param force: Boolean that forces a refresh of devices with the server
        :raises ValueError: Nothing yet
        :return: None
        :rtype: None
        
        .. seealso:: modules :py:func:`getLights`, :py:func:`getGroups`\
        """
        try:
            if (len(list(self.arrDevices)) <= 0 and force == True):
                #sends the request to get the list of devices
                headers= {
                    'X-Omnia-Access-Token':self.getApiKey(),
                    'X-AlertMe-Client':'Web',
                    'Accept':'application/vnd.alertme.zoo-6.4+json',
                    'Content-Type':'application/json'
                }
                r = requests.get(API_ADDR+"nodes/",headers=headers)

                if (r.status_code is not 200):
                    raise hiveError(r.status_code)
        
                temp = r.json()['nodes']
                for rt in temp:
                    # We only want lights here
                    if (rt['attributes']['nodeType']['reportedValue'].find("class.light") > 0
                          or rt['attributes']['nodeType']['reportedValue'].find("class.tunable.light") > 0):
                        self.arrDevices[rt['id']] = {}
                        self.arrDevices[rt['id']]['id'] = rt['id']
                        self.arrDevices[rt['id']]['name'] = rt['name']
                        self.arrDevices[rt['id']]['brightness'] = \
                            rt['attributes']['brightness']['reportedValue']
                        if (rt['attributes']['state']['reportedValue'] =='OFF'):
                            self.arrDevices[rt['id']]['status'] = False
                        else:
                            self.arrDevices[rt['id']]['status'] = True
                        if (rt['attributes']['nodeType']['reportedValue'].find("class.tunable.light") > 0):
                            self.arrDevices[rt['id']]['colourTemp'] = \
                                rt['attributes']['colourTemperature']['reportedValue']
                        # Store device type for quicker checking later
                        self.arrDevices[rt['id']]['type'] = 'light'
                    elif (rt['attributes']['nodeType']['reportedValue'].find("class.synthetic.group") > 0):
                        self.arrDevices[rt['id']] = {}
                        #This makes it easier when calling from outside the class for generic devices
                        self.arrDevices[rt['id']]['id'] = rt['id']
                        self.arrDevices[rt['id']]['name'] = rt['name']
                        self.arrDevices[rt['id']]['lights'] = {}
                        self.arrDevices[rt['id']]['lights'] = \
                            self.getGroupLights(rt['id'])
                        # Store device type for quicker checking later
                        self.arrDevices[rt['id']]['type'] = 'group'
        except hiveError as hE:
            print("An exception occured: ", hE.value)

        except:
            print("Unexpected exception in hive._getDevices():" + \
                  "{} - {}".format(sys.exc_info()[0], sys.exc_info()[1]))
                    
    def _initGroupStatus(self):
        try:
            for id, device in self.arrDevices.items():
                if device['type'] == 'group':
                    self.isLightOn(id)
            #[self.isLightOn(group) for group in self.arrDevices.items() if group['type'] == 'group']
        except hiveError as hE:
            print("An exception occured: ", hE.value)

        except:
            print("Unexpected exception in hive._initGroupStatus():" + \
                  "{} - {}".format(sys.exc_info()[0], sys.exc_info()[1]))
            
    def _initCustomGroups(self):
        try:
            listLen = len(self.data['custom_groups'])
            for i in range(0, listLen):
                id = self.data['custom_groups'][i]['id']
                self.arrDevices[id] = {}
                self.arrDevices[id]['id'] = id
                self.arrDevices[id]['name'] = \
                    self.data['custom_groups'][i]['name']
                self.arrDevices[id]['lights'] = \
                    list(self.data['custom_groups'][i]['lights'].values())
                self.arrDevices[id]['type'] = 'group'
        except hiveError as hE:
            print("An exception occured: ", hE.value)

        except:
            print("Unexpected exception in hive._initCustomGroups():" + \
                  "{} - {}".format(sys.exc_info()[0], sys.exc_info()[1]))

    def getGroupLights(self, group_id):
        """Gets a list of the lights associated with a group
        
        Gets a list of Hive light devices associated with a group.
        
        :param self: Instance of hive class
        :param group_id: String representing ID of the group
        :raises ValueError: Nothing yet
        :return: List of groups
        :rtype: dictionary\
        """
        try:
            arrGroupLights = {}
            headers= {
                'X-Omnia-Access-Token':self.getApiKey(),
                'X-AlertMe-Client':'Web',
                'Accept':'application/vnd.alertme.zoo-6.4+json',
                'Content-Type':'application/json'
            }
            r = requests.get("https://api.prod.bgchprod.info/omnia/bindings?syntheticNodeId=" + group_id,headers=headers)
            
            if (r.status_code is not 200):
                raise hiveError(r.status_code)
                
            temp = r.json()['bindings']
            arrGroupLights = [rt['boundNodeId'] for i, rt in enumerate(temp)]
            
        except hiveError as hE:
            print("An exception occured: ", hE.value)
            
        except:
            print("Unexpected exception in hive.getGroupLights():" + \
                  "{} - {}".format(sys.exc_info()[0], sys.exc_info()[1]))
            
        else:   
            return arrGroupLights

    #queries the hive api to get whether the specifed light is on or not
    def isLightOn(self, device_id, force = False):
        try:
            if (force):
                #sends the request to get the light's status
                headers= {
                    'X-Omnia-Access-Token':self.getApiKey(),
                    'X-AlertMe-Client':'Web',
                    'Accept':'application/vnd.alertme.zoo-6.4+json',
                    'Content-Type':'application/json'
                }
                r = requests.put(API_ADDR+"nodes/"+device_id,headers=headers)

                #presumes light is on
                lightOn = True

                #gets the light's status from the returned JSON and tests if it is off or not.
                if str(r.json()['nodes'][0]['attributes']['state']['reportedValue']) == 'OFF':
                    lightOn= False
                else:
                    lightOn = True

                self.updateLightValue(device_id, "status", lightOn)
                return lightOn
            else:
                if (device_id in self.arrDevices and "status" in self.arrDevices[device_id]):
                    return self.arrDevices[device_id]['status']
                elif (device_id in self.arrDevices):
                    if (self.arrDevices[device_id]['type'] == "group"):
                        isOn = False
                        listLen = len(self.arrDevices[device_id]['lights'])
                        for i in range(0, listLen):
                            isOn = self.isLightOn(self.arrDevices[device_id]['lights'][i])
                        self.updateLightValue(device_id, "status", isOn)
                        return isOn
                return -1
        except hiveError as hE:
            print("An exception occured: ", hE.value)

        except:
            print("Unexpected exception in hive.isLightOn():" + \
                  "{} - {}".format(sys.exc_info()[0], sys.exc_info()[1]))
        
    def updateLightValue(self, device_id, key, value):
        if (device_id in self.arrDevices):
            self.arrDevices[device_id][key] = value

    #work out whether the current time is after sunrise but before sunset
    def isDayTime(self):
        #now = now.replace(hour=23, minute=10)
        daytime= False

        #extract the sunrise/sunset times adds/substracts 30 minutes from these times to account for dawn/dusk
        sunrise= self.getSunrise()
        sunset= self.getSunset()

        #if the current time is between sunrise and sunset then its daytime
        if self.now >= sunrise and self.now <= sunset:
            daytime=True

        return daytime

    #calculates the sunrise time and adds 30 minutes to account for it still being dark
    def getSunrise(self):
        return self.l.sunrise() + datetime.timedelta(minutes=30)

    #calculates the sunset time and substracts 30 minutes to account for it getting dark
    def getSunset(self):
        return self.l.sunset() - datetime.timedelta(minutes=30)

    #gets the time the device was last modified from the server
    def getRemoteModifiedTime(self, light_id):
        #sends the request to get the light's status
        headers= {
            'X-Omnia-Access-Token':self.getApiKey(),
            'X-AlertMe-Client':'Web',
            'Accept':'application/vnd.alertme.zoo-6.4+json',
            'Content-Type':'application/json'
        }
        r = requests.put(API_ADDR+"nodes/"+light_id,headers=headers)

        #presumes light is on
        return r.json()['nodes'][0]['attributes']['state']['reportReceivedTime']

    #saves the reported time from the server locally
    def saveModifiedTime(self, light_id, timestamp, lightOn):
        # now write output to a file
        lightFile = open(light_id+".json", "w")
        # magic happens here to make it pretty-printed
        output= {'id':light_id,'modified':timestamp, 'lightOn':lightOn}
        self.data= json.dumps(output)
        lightFile.write(simplejson.dumps(simplejson.loads(self.data), indent=4, sort_keys=True))
        lightFile.close()

    #reads the time the script last modified the device
    def getLocalModifiedTime(self, light_id):
        try:
            with open(light_id+'.json') as json_data:
                d = json.load(json_data)
                return d['modified']
        except IOError:
            return self.getRemoteModifiedTime(light_id)

    #returns true if the device was modified outside of this script and someone has turned the light on/off with via the app or dashboard
    def isOverridden(self, light_id):
        #gets the time the device was last modified by the script
        local_update = datetime.datetime.fromtimestamp(self.getLocalModifiedTime(light_id)/1000.0)

        #gets the time the device was last modified by anything
        remote_update = datetime.datetime.fromtimestamp(self.getRemoteModifiedTime(light_id)/1000.0)

        #if device has been modified since this script last modified it
        if remote_update > local_update:
            print("isOverridden")
            return True

        return False

    #sends the request to turn the specified light on or off (contained within the payload provided)
    def _sendDeviceValue(self, device_id, payload):
        try:
            headers= {
                'X-Omnia-Access-Token':self.getApiKey(),
                'X-AlertMe-Client':'Web',
                'Accept':'application/vnd.alertme.zoo-6.4+json',
                'Content-Type':'application/json'
            }
            r = requests.put(
                    API_ADDR+"nodes/"+device_id,headers=headers,data=payload
                )
            #modifiedTime= self.getLocalModifiedTime(light_id)
            #self.saveModifiedTime(light_id,modifiedTime, True)
            if (r.status_code is not 200):
                raise hiveError(r.status_code)

        except hiveError as hE:
            print("An exception occured: ", hE.value)

        except:
            print("Unexpected exception in hive._sendDeviceValue():" + \
                  "{} - {}".format(sys.exc_info()[0], sys.exc_info()[1]))

        else:
            return (r.status_code)
    
    # Toggles light between on and off
    def toggleDevice(self, device_id):
        """Toggles a device
        
        Toggles that status of a device to either off if currently on, or on if
        currently off
        
        This works with individual lights and groups.
        
        :param self: Instance of hive class
        :param device_id: String representing ID of the device
        :raises hiveError: See hiveError for more info
        :return: True if device has been turned on, False if device has been 
                 turned off. Returns None if neither of these actions has                 
                 happened.
        :rtype: Boolean or None\
        """
        try:
            if (device_id not in self.arrDevices):
                raise hiveError(1)
            
            if (self.arrDevices[device_id]['type'] == 'light'):
                if (self.isLightOn(device_id)):
                    self._sendDeviceValue(device_id, OFF_PAYLOAD)
                    self.updateLightValue(device_id, "status", False)
                    return False
                else:
                    self._sendDeviceValue(device_id, ON_PAYLOAD)
                    self.updateLightValue(device_id, "status", True)
                    return True
            elif (self.arrDevices[device_id]['type'] == 'group'):
                status = False
                listLen = len(self.arrDevices[device_id]['lights'])
                for i in range(0, listLen):
                    if ("status" in self.arrDevices[device_id]):
                        if (self.arrDevices[device_id]['status']):
                            self._sendDeviceValue(self.arrDevices[device_id]['lights'][i], OFF_PAYLOAD)
                            self.updateLightValue(self.arrDevices[device_id]['lights'][i], "status", False)
                            status = False
                        else:
                            self._sendDeviceValue(self.arrDevices[device_id]['lights'][i], ON_PAYLOAD)
                            self.updateLightValue(self.arrDevices[device_id]['lights'][i], "status", True)
                            status = True
                    else:
                        self._sendDeviceValue(self.arrDevices[device_id]['lights'][i], ON_PAYLOAD)
                        self.updateLightValue(self.arrDevices[device_id]['lights'][i], "status", True)
                        status = True
                self.updateLightValue(device_id, "status", status)
                return status
            else:
                return
                
        except hiveError as hE:
            print("An exception occured: ", hE.value)
            
        except:
            print("Unexpected exception in hive.toggleDevice():" + \
                  "{} - {}".format(sys.exc_info()[0], sys.exc_info()[1]))
    
    # Toggles all lights, 0 = off, 1 = on, 2 = toggle all to reverse state
    def toggleAllLights(self, status = 2):
        """Toggles all light devices
        
        Toggles that status of all lights to either on, off, or the reverse of 
        their current state.
        
        :param self: Instance of hive class
        :param status: Integer representing the state to set devices to
                       0 is off, 1 is on, 2 is the reverse of current state
        :raises ValueError: Nothing yet
        :return: Nothing yet
        :rtype: None\
        """
        try:
            for id, device in self.arrDevices.items():
                if (status == 0):
                    if (device['status']):
                            self._sendDeviceValue(device['id'], OFF_PAYLOAD)
                            self.updateLightValue(device['id'], "status", False)
                    elif (status == 1):
                        if (device['status'] == False):
                            self._sendDeviceValue(device['id'], ON_PAYLOAD)
                            self.updateLightValue(device['id'], "status", True)
                    else:
                        self.toggleDevice(device['id'])

        except hiveError as hE:
            print("An exception occured: ", hE.value)

        except:
            print("Unexpected exception in hive.toggleAllLights():" + \
                  "{} - {}".format(sys.exc_info()[0], sys.exc_info()[1]))

    def getBrightness(self, device_id):
        """Get the brightness of a light
        
        Get the brightness of a light. If a group is specified, it will return 
        the average of the groups values.
        
        :param self: Instance of hive class
        :param light_id: String representing ID of the light
        :raises ValueError: Nothing yet
        :return: Nothing yet
        :rtype: None\
        """
        try:
            brightness = 0
            if (self.arrDevices[device_id]['type'] == "light"):
                brightness = self.arrDevices[device_id]['brightness']
            elif (self.arrDevices[device_id]['type'] == "group"):
                brightness = 0
                listLen = len(self.arrDevices[device_id]['lights'])
                for i in range(0, listLen):
                    brightness += self.getBrightness(self.arrDevices[device_id]['lights'][i])
                brightness /= listLen
        except hiveError as hE:
            print("An exception occured: ", hE.value)

        except:
            print("Unexpected exception in hive.getBrightness():" + \
                  "{} - {}".format(sys.exc_info()[0], sys.exc_info()[1]))

        else:
            return brightness

    def _setBrightness(self, device_id, brightness):
        """Change the brightness of a light
        
        Change the brightness of a light. If the value is below the minimum 
        value of 100 or the maximum value of 0, the minimum or maximum value 
        respectively will be used.
        
        :param self: Instance of hive class
        :param light_id: String representing ID of the light
        :param brightness: Integer of value to set brightness (Min 0, Max 100)
        :raises ValueError: Nothing yet
        :return: Nothing yet
        :rtype: None\
        """
        try:
            if (brightness < 0):
                brightness = 0
            elif (brightness > 100):
                brightness = 100
        
            if (self.arrDevices[device_id]['type'] == "light"):
                self._sendDeviceValue(device_id,
                                      BRIGHTNESS_PAYLOAD.format(brightness))
                self.updateLightValue(device_id, "brightness", brightness)
            elif (self.arrDevices[device_id]['type'] == "group"):
                listLen = len(self.arrDevices[device_id]['lights'])
                for i in range(0, listLen):
                    self._setBrightness(self.arrDevices[device_id]['lights'][i],
                                        brightness)
                    self.updateLightValue(self.arrDevices[device_id]['lights'][i],
                                          "brightness", brightness)

        except hiveError as hE:
            print("An exception occured: ", hE.value)

        except:
            print("Unexpected exception in hive._setBrightness():" + \
                  "{} - {}".format(sys.exc_info()[0], sys.exc_info()[1]))

        else:
            return brightness
        
    def increaseBrightness(self, device_id, brightness):
        try:
            brightnessVal = 0
        
            if (self.arrDevices[device_id]['type'] == "light"):
                brightnessVal = self.getBrightness(device_id) + brightness
                self._setBrightness(device_id, brightnessVal)
            elif (self.arrDevices[device_id]['type'] == "group"):
                listLen = len(self.arrDevices[device_id]['lights'])
                for i in range(0, listLen):
                    brightnessVal = \
                        self.getBrightness(self.arrDevices[device_id]['lights'][i]) + brightness

                    self._setBrightness(self.arrDevices[device_id]['lights'][i],
                                        brightnessVal)
                    self.updateLightValue(self.arrDevices[device_id]['lights'][i],
                                          "brightness", brightnessVal)

        except hiveError as hE:
            print("An exception occured: ", hE.value)

        except:
            print("Unexpected exception in hive.increaseBrightness():" + \
                  "{} - {}".format(sys.exc_info()[0], sys.exc_info()[1]))

        else:
            return brightnessVal
    
    def decreaseBrightness(self, device_id, brightness):
        try:
            brightnessVal = 0
        
            if (self.arrDevices[device_id]['type'] == "light"):
                brightnessVal = self.getBrightness(device_id) - brightness
                self._setBrightness(device_id, brightnessVal)
            elif (self.arrDevices[device_id]['type'] == "group"):
                listLen = len(self.arrDevices[device_id]['lights'])
                for i in range(0, listLen):
                    brightnessVal = \
                        self.getBrightness(self.arrDevices[device_id]['lights'][i]) - brightness
                        
                    self._setBrightness(self.arrDevices[device_id]['lights'][i],
                                        brightnessVal)
                    self.updateLightValue(self.arrDevices[device_id]['lights'][i],
                                          "brightness", brightnessVal)
                                          
        except hiveError as hE:
            print("An exception occured: ", hE.value)

        except:
            print("Unexpected exception in hive.decreaseBrightness():" + \
                  "{} - {}".format(sys.exc_info()[0], sys.exc_info()[1]))

        else:
            return brightnessVal

    def getColourTemperature(self, light_id):
        try:
            cTemp = 0
            if ("colourTemp" in self.arrDevices[light_id]):
                if (self.arrDevices[light_id]['type'] == "light"):
                    cTemp = self.arrDevices[light_id]['colourTemp']
                '''elif (self.arrDevices[device_id]['type'] == "group"):
                    listLen = len(self.arrDevices[device_id]['lights'])
                    for i in range(0, listLen):
                        cTemp += self.getColourTemp(self.arrDevices[device_id]['lights'][i])
                    cTemp /= listLen'''
        except hiveError as hE:
            print("An exception occured: ", hE.value)

        except:
            print("Unexpected exception in hive.getColourTemperature():" + \
                  "\n{} - {}".format(sys.exc_info()[0], sys.exc_info()[1]))
            #pprint(sys.exc_info())
        else:
            return cTemp

    def setColourTemperature(self, light_id, temperature):
        """Set the colour temperature of a tunable light
        
        Set the colour temperature of a tunable light. If the value is below the
        minimum value of 2700 or the maximum value of 6533, the minimum or 
        maximum value respectively will be used.
        
        :param self: Instance of hive class
        :param light_id: String representing ID of the light
        :param temperature: Integer to set temperature value (Min 2700,Max 6533)
        :raises ValueError: Nothing yet
        :return: Nothing yet
        :rtype: None\
        """
        try:
            if (temperature < 2700):
                temperature = 2700
            elif (temperature > 6533):
                temperature = 6533
            
            self._sendDeviceValue(light_id, \
                                  TEMPERATURE_PAYLOAD.format(temperature))
            self.updateLightValue(light_id, "colourTemp", temperature)
            
        except hiveError as hE:
            print("An exception occured: ", hE.value)

        except:
            print("Unexpected exception in hive.setColourTemperature():" + \
                  "{} - {}".format(sys.exc_info()[0], sys.exc_info()[1]))

        else:
            return temperature
            
    def increaseColourTemperature(self, light_id, temperature):
        cTemp = self.getColourTemperature(light_id)
        cTemp += temperature
        
        return self.setColourTemperature(light_id, cTemp)
        
    def decreaseColourTemperature(self, light_id, temperature):
        cTemp = self.getColourTemperature(light_id)
        cTemp -= temperature
        
        return self.setColourTemperature(light_id, cTemp)
    
    #load all the global values from the json config and return the schedule array fro processing
    def loadJSON(self):
        try:
            self.now = datetime.datetime.now(pytz.timezone('Europe/London'))
            #reads in the JSON array containing the lights schedule
            json_data=open("config/schedule.json").read()
            self.data = json.loads(json_data)
            self.username = self.data['username']
            self.password = self.data['password']
            self.buttons = self.data['buttons']

        except hiveError as hE:
            print("An exception occured: ", hE.value)

        except:
            print("Unexpected exception in hive.loadJSON():" + \
                  "{} - {}".format(sys.exc_info()[0], sys.exc_info()[1]))

        else:
            return self.data['schedule']
                
    def hive_main(self):
        schedule = self.loadJSON()
