import voluptuous as vol

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

    def __init__(self, akey, password):
        """Initialize the sensor."""
        import requests

        self._state = None
        self.RESTURL = 'https://app.evnotify.de/'
        self.session = requests.Session()
        self.login(akey, password)

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'EVNotify SOC'

    @property
    def unit_of_measurement(self):
        """Return the unit_of_measurement of the device."""
        return '%'

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return 'mdi:battery'

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state['soc_display']

    @property
    def device_state_attributes(self):
        """Return the devices' state attributes."""
        from datetime import datetime

        attrs = {
            'battery_level': self._state['soc_bms'],
            'last_seen': datetime.fromtimestamp(self._state['last_soc']).strftime('%Y-%m-%d %H:%M:%S')
        }
        return attrs

    def update(self):
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """
        self._state = self.getSOC()

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
