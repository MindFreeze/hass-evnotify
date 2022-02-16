import time
import voluptuous as vol
import requests
from datetime import timedelta

from homeassistant.helpers.entity import Entity
from homeassistant.helpers.icon import icon_for_battery_level
from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required('akey'): cv.string,
    vol.Optional('password'): cv.string,
})

SCAN_INTERVAL = timedelta(minutes=5)


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the sensor platform."""
    add_devices([EVNotify(config['akey'], config['password'])])


class EVNotify(Entity):
    """Representation of a Sensor."""

    def __init__(self, akey, password):
        """Initialize the sensor."""

        self.RESTURL = 'https://app.evnotify.de/'
        self.session = requests.Session()
        self.login(akey, password)
        self.update()

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'EVNotify SOC'

    @property
    def unit_of_measurement(self):
        """Return the unit_of_measurement of the device."""
        return '%'

    @property
    def device_class(self):
        return 'battery'

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return icon_for_battery_level(battery_level=int(self._state['soc_display'] or self._state['soc_bms']),
                                          charging=False)

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state['soc_display'] or self._state['soc_bms']

    @property
    def extra_state_attributes(self):
    # def device_state_attributes(self):
        """Return the devices' state attributes."""
        from datetime import datetime

        attrs = {
            'battery_level': self._state.get('soc_bms'),
            'last_seen': datetime.fromtimestamp(self._state.get('last_soc')).strftime('%Y-%m-%d %H:%M:%S'),
            'soh': self._state.get('soh'),
            'charging': self._state.get('charging'),
            'rapid_charge_port': self._state.get('rapid_charge_port'),
            'normal_charge_port': self._state.get('normal_charge_port'),
            'slow_charge_port': self._state.get('slow_charge_port'),
            'aux_battery_voltage': self._state.get('aux_battery_voltage'),
            'dc_battery_voltage': self._state.get('dc_battery_voltage'),
            'dc_battery_current': self._state.get('dc_battery_current'),
            'dc_battery_power': self._state.get('dc_battery_power'),
            'cumulative_energy_charged': self._state.get('cumulative_energy_charged'),
            'cumulative_energy_discharged': self._state.get('cumulative_energy_discharged'),
            'battery_min_temperature': self._state.get('battery_min_temperature'),
            'battery_max_temperature': self._state.get('battery_max_temperature'),
            'battery_inlet_temperature': self._state.get('battery_inlet_temperature'),
            'external_temperature': self._state.get('external_temperature'),
            'odo': self._state.get('odo'),
            'last_extended': datetime.fromtimestamp(self._state.get('last_extended')).strftime('%Y-%m-%d %H:%M:%S')
        }
        return attrs

    def update(self):
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """
        # self._state = self.getSOC() | self.getStats()
        self._state = {**self.getSOC(), **self.getStats()}
        self.extra_state_attributes

    def login(self, akey, password):
        self.token = self.sendRequest('post', 'login', False, {
            "akey": akey,
            "password": password
        })['token']
        self.akey = akey
        return self.token

    def getSOC(self):
        return self.sendRequest('get', 'soc', True)

    def getStats(self):
        return self.sendRequest('get', 'extended', True)

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
