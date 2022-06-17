"""SIRI sensors"""
from datetime import datetime, time, timedelta

import logging
import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.components.geo_location import PLATFORM_SCHEMA, GeolocationEvent
from homeassistant.helpers.entity import Entity
from homeassistant.const import CONF_TOKEN, CONF_URL, CONF_ID, CONF_NAME

from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .api import SIRIApi

from .const import (
    DOMAIN,
    SENSOR_NAME
)

NAME = DOMAIN
ISSUEURL = "https://github.com/codyc1515/hacs_siri/issues"

STARTUP = f"""
-------------------------------------------------------------------
{NAME}
This is a custom component
If you have any issues with this you need to open an issue here:
{ISSUEURL}
-------------------------------------------------------------------
"""

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_TOKEN): cv.string,
    vol.Required(CONF_URL): cv.string,
    vol.Required(CONF_ID): cv.string,
    vol.Optional(CONF_NAME): cv.string
})

SCAN_INTERVAL = timedelta(seconds=30)

async def async_setup_platform(hass, config, async_add_entities,
                               discovery_info=None):
    token = config.get(CONF_TOKEN)
    url = config.get(CONF_URL)
    stop = config.get(CONF_ID)
    name = config.get(CONF_NAME)
    
    api = SIRIApi(token, url, stop)

    _LOGGER.debug('Setting up sensor(s)...')

    sensors = []
    sensors .append(SIRIStopSensor(name, api, stop))
    async_add_entities(sensors, True)

class SIRIStopSensor(Entity):
    def __init__(self, name, api, stop):
        self._name = name
        self._icon = "mdi:bus"
        self._state = ""
        self._state_attributes = {}
        self._unit_of_measurement = None
        self._device_class = "running"
        self._unique_id = stop
        self._api = api

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the sensor."""
        return self._state_attributes

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def unique_id(self):
        """Return the unique id."""
        return self._unique_id
    
    def update(self):
        _LOGGER.debug('Fetching SIRI stops')
        response = self._api.get_stops()
        if response:
            _LOGGER.debug(response)
            
            time_delta = (datetime.strptime(response['eta'], "%Y-%m-%dT%H:%M:%S+12:00") - datetime.now())
            total_seconds = time_delta.total_seconds()
            calc = total_seconds/60
            
            minutes = calc % 60
            seconds = (calc*60) % 60

            if minutes > 0:
            	eta = "%d min %ds" % (minutes, seconds)
            else:
                eta = "%ds" % (seconds)
            
            self._state = response['route'] + " in " + eta
            
            self._state_attributes['Latitude'] = str(response['latitude'])
            self._state_attributes['Longitude'] = str(response['longitude'])
        else:
            _LOGGER.error('Unable to fetch SIRI stops')
