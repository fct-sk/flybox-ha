import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_USERNAME, CONF_PASSWORD

from .const import DOMAIN, DEFAULT_HOST
from .flybox_client import FlyboxClient


class FlyboxConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            client = FlyboxClient(
                user_input[CONF_HOST],
                user_input[CONF_USERNAME],
                user_input[CONF_PASSWORD],
            )

            try:
                await self.hass.async_add_executor_job(
                    client.login
                )
            except Exception:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(
                    user_input[CONF_HOST]
                )
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title="Orange Flybox",
                    data=user_input,
                )

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_HOST,
                    default=DEFAULT_HOST,
                ): str,
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )
