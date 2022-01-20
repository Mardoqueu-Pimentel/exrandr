import string

gsettings_set_xsettings = string.Template(
    "gsettings "
    "set "
    "org.gnome.settings-daemon.plugins.xsettings "
    "overrides "
    "\"[{'Gdk/WindowScalingFactor', <2>}]\""
).substitute

gsettings_set_interface_scaling_factor = string.Template(
    "gsettings set org.gnome.desktop.interface scaling-factor $int_scale"
).substitute
