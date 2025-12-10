# coding=utf-8
#from __future__ import absolute_import

### (Don't forget to remove me)
# This is a basic skeleton for your plugin's __init__.py. You probably want to adjust the class name of your plugin
# as well as the plugin mixins it's subclassing from. This is really just a basic skeleton to get you started,
# defining your plugin as a template plugin, settings and asset plugin. Feel free to add or remove mixins
# as necessary.
#
# Take a look at the documentation on what other plugin mixins are available.

import octoprint.plugin
import octoprint.util
import octoprint.printer

heating = False
timer = None

class PreventmintempPlugin(octoprint.plugin.StartupPlugin,
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.TemplatePlugin,      
):

    def check_temp(self):
        global heating
        heat_thresh = self._settings.get_float(["heat_thresh"]) #10.0 #settings.preventMINTEMP.heat_thresh
        ignore_thresh = self._settings.get_float(["ignore_thresh"])
        heat_target = self._settings.get_float(["heat_target"])
        check_period = self._settings.get_int(["check_period"])
         
        #count += 1
        print(f"Checking temperature. heat_thresh={heat_thresh}, heat_target={heat_target}, check_period={check_period}, ignore_thresh={ignore_thresh}")
        pstate = self._printer.get_state_id()
        if(pstate != "PRINTING"):  #Don't do monitoring if we're printing
            tdict = self._printer.get_current_temperatures()
            all_at_target = True
            for x in tdict:
                #print(x, ": ", tdict[x])
                if(x[:4] == "tool" or x == "bed"):
                    elt_name = x
                    T = tdict[x]["actual"]
                    Ttarg = tdict[x]["target"]
                    if(Ttarg == 0 and T > ignore_thresh and T < heat_thresh):
                            self._logger.info(f"Element {x} is below {heat_thresh}C temperature threshold. Heating element {x}.")
                            all_at_target = False
                            heating = True
                            self._printer.set_temperature(elt_name,heat_target)
                    else:
                        # If we're heating this element and we reached target, then turn it off
                        if(Ttarg != 0.0 and (T >= heat_target or T < ignore_thresh)):
                            if(T > ignore_thresh):
                                self._logger.info(f"Element {elt_name} reached {heat_target}C target. Turning off heater.")
                            else:
                                self._logger.info(f"Element {elt_name} is below error temperature.")
                            self._printer.set_temperature(elt_name, 0.0)
                        elif(Ttarg != 0.0):
                            all_at_target = False
            if(all_at_target and heating):
                self._logger.info("All elements above temperature target.")
                heating = False
        else:
            self._logger.info("Ignoring temperature check because printer is printing,")
            heating = False
    
    def on_after_startup(self):
        global timer
        check_period = self._settings.get_int(["check_period"])
        self._logger.info("Prevent MINTEMP plugin started.")
        timer = octoprint.util.RepeatedTimer(check_period,self.check_temp)
        timer.start()

    ##~~ SettingsPlugin mixin

    def get_settings_defaults(self):
        return dict(
            heat_thresh=13.0,		#lower temperature threshold to start heating
            ignore_thresh=10.0,	#temperature below which we are in MINTEMP error, so will not heat
            heat_target=50.0,		#target temperture to which to heat elements
            check_period=10.0		#how often to check temperature in seconds
        )
    
    def on_settings_save(self, data):
        global timer
        s = self._settings
        if "heat_thresh" in data.keys():
            s.set_float(["heat_thresh"], data["heat_thresh"])
        if "ignore_thresh" in data.keys():
            s.set_float(["ignore_thresh"], data["ignore_thresh"])
        if "heat_target" in data.keys():
            s.set_float(["heat_target"], data["heat_target"])
        if "check_period" in data.keys():
            # If check period changes, then cancel and re-start timer
            if s.get_int(["check_period"]) != data["check_period"]:
                check_period = int(data["check_period"])
                s.set_int(["check_period"], check_period)
                timer.cancel()
                timer = octoprint.util.RepeatedTimer(check_period,self.check_temp)
                timer.start()
        s.save()

    def get_template_configs(self):
        return [
            dict(type="settings", custom_bindings=False)
        ]
    
    def is_template_autoescaped(self):
        return True

    ##~~ AssetPlugin mixin

    #def get_assets(self):
        # Define your plugin's asset files to automatically include in the
        # core UI here.
    #    return {
    #        "js": ["js/preventMINTEMP.js"],
    #        "css": ["css/preventMINTEMP.css"],
    #        "less": ["less/preventMINTEMP.less"]
    #    }

    ##~~ Softwareupdate hook

    #def get_update_information(self):
        # Define the configuration for your plugin to use with the Software Update
        # Plugin here. See https://docs.octoprint.org/en/main/bundledplugins/softwareupdate.html
        # for details.
      #  return {
      #      "preventMINTEMP": {
      #          "displayName": "Preventmintemp Plugin",
      #          "displayVersion": self._plugin_version,

                # version check: github repository
      #          "type": "github_release",
      #          "user": "mdaneman@yahoo.com",
      #          "repo": "PreventMinTEMP",
      #          "current": self._plugin_version,

                # update method: pip
      #          "pip": "https://github.com/mdaneman@yahoo.com/PreventMinTEMP/archive/{target_version}.zip",
      #      }
      #  }


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "Prevent MINTEMP"


# Set the Python version your plugin is compatible with below. Recommended is Python 3 only for all new plugins.
# OctoPrint 1.4.0 - 1.7.x run under both Python 3 and the end-of-life Python 2.
# OctoPrint 1.8.0 onwards only supports Python 3.
__plugin_pythoncompat__ = ">=3,<4"  # Only Python 3

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = PreventmintempPlugin()
#
#    global __plugin_hooks__
#    __plugin_hooks__ = {
#        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
#    }
