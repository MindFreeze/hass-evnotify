from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required('akey'): cv.string,
    vol.Optional('password'): cv.string,
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the sensor platform."""
    add_devices([EVNotify(config['akey'], config['password'])])


class EVNotify(Entity):
    """Representation of a Sensor."""

    def __init__(self, akey, pass):
        """Initialize the sensor."""
        import requests

        self._state = None
        self.RESTURL = 'https://app.evnotify.de/'
        self.session = requests.Session()
        self.login(akey, pass)

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'EVNotify SOC'

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        data = self.getSOC()
        self._state = data['soc_display']

    def login(self, akey, password):
        self.token = self.sendRequest('post', 'login', False, {
            "akey": akey,
            "password": password
        })['token']
        self.akey = akey
        return self.token

    def getSOC(self):
        return self.sendRequest('get', 'soc', True)

    def sendRequest(self, method, fnc, useAuthentication = False, params = {}):
        if useAuthentication:
            params['akey'] = self.akey
            params['token'] = self.token
        try:
            if method == 'get':
                return getattr(self.session, method)(self.RESTURL + fnc, params=params).json()
            else:
                return getattr(self.session, method)(self.RESTURL + fnc, json=params).json()

        except requests.exceptions.ConnectionError:
            raise EVNotify.CommunicationError()
