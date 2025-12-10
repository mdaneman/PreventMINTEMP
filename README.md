## PreventMINTEMP

I have a Prusa MK3S sitting in a cold garage. When the printer is sitting idle and the garage temperature drops below 10C, the printer tiggers a MINTEMP error and needs to be re-started to work again.
This error is meant to detect a bad thermister (which would typically report a negative temperature), but it tiggers unncessarily (in my view) even when the printer is not printing, just due to sitting in a cold environment.
This simple plugin monitors the tool and bed temperatures and re-heats them to a set target temperature (40C by default) when they drop below a pre-set threshold temperature (12C by default). It will not trigger re-heating if the printer is printing or if the tool temperatures are already below the MINTEMP alarm threshold. This threshold is generally determined by the printer firmware and should be set by adjusting the "Don't Trigger Below" parameter to match the printer setting. It's set to 10C by default, which is the default setting for Prusal MKx printers.

Setup
-----

Install via the bundled [Plugin Manager](https://docs.octoprint.org/en/main/bundledplugins/pluginmanager.html)
or manually using this URL:

    https://github.com/mdaneman@yahoo.com/PreventMinTEMP/archive/main.zip


Configuration
-------------

This plugin has 4 adjustable parameters:

- **Heating Threshold** 	- this is temperature below which re-heating will be triggered.
- **Reheat Target** 	- target temperature to which the tools will be re-heated.
- **Monitor Period** 	- frequency of temperature monitoring in seconds.
- **Don't Trigger Below** - temperature below which re-heating will not be triggered. This should be lower than the **Heating Threshold** and would generally be the temperature at which your printer tiggers the MINTEMP alarm.
