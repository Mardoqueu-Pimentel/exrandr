# exrandr

The Gnome display "Scale" feature is very useful. It allows the desktop interface on a 4K monitor to appear the same "size" as a 1080p one.

But what if you're using a 32-inch monitor and only want a 50% zoom? This is known as fractional scaling. In Gnome, you can achieve this using `xrandr` to instruct `X` to render the desktop at a higher resolution and then downscale this virtual resolution to the monitor's native resolution.

The `xrandr` parameters for this aren't very intuitive. Let's say you have a 4K monitor and want your desktop to appear 50% zoomed in without blurriness.

1.  Your monitor's native resolution is 3840x2160.
2.  To avoid blur, you set Gnome's "Scale" to 200%.
3.  To accommodate this, `X` must render the virtual desktop at 7640x4320.
4.  With a 50% zoom applied, this virtual resolution becomes 5120x2880.
5.  Since 2880 is approximately 1.33 times 2160, the `xrandr` command would be something like: `$ xrandr ... --mode 3840x2160 --scale 1.3333333333333333 ...`.

Now, what if you need to account for the monitor's PPI (pixels per inch) or rotation? What about a second monitor? I've found that `$ xrandr ... --right-of ...` doesn't work well with `$ xrandr ... --scale ...`, making it necessary to use `$ xrandr ... --pos ...` instead.

This small tool can help with these challenges.
```
$ exrandr -v -a --scale 2 \
          display -n HDMI-0 -i 32 -r 3840x2160 -z 2 -g 0.85 -p \
          display -n eDP-1-1 -i 15.6 -r 1920x1080 -z 1.5 -g 0.95 --below HDMI-0
```
## Installation

```
$ pip install "git+https://github.com/Mardoqueu-Pimentel/exrandr.git"
```

## Usage

```
$ exrandr --help
Usage: exrandr [OPTIONS] COMMAND1 [ARGS]... [COMMAND2 [ARGS]...]...

Options:
  -s, --scale FLOAT  The desktop Scale to use. 1 for 100%, 2 for 200%, 3 for
                     300%. Only Gnome is supported.  [default: 1.0]
  -p, --ppi FLOAT    Force this ppi instead of choosing the lowest one of a
                     monitor. If 0 no ppi scaling will be made.
  -a, --apply        Call xrandr.
  -v, --verbose      Verbose output.
  --help             Show this message and exit.

Commands:
  completion  Output shell completions.
  display     Configure a xrandr display.

$ exrandr display --help
Usage: exrandr display [OPTIONS]

  Configure a xrandr display.

Options:
  -n, --name [HDMI-0|eDP-1-1]     Name of the monitor on xrandr.  [required]
  -i, --inches FLOAT              The size of the diagonal of the monitor in
                                  inches.  [required]
  -r, --resolution RESOLUTION     The true resolution of the monitor.
  -g, --gamma FLOAT               The gamma of the monitor.  [default: 1.0]
  -z, --zoom FLOAT                The zoom you want to apply.  [default: 1.0]
  -o, --rotation [normal|inverted|left|right]
                                  If the monitor should be rotated.  [default:
                                  normal]
  -p, --primary                   Whether the monitor is primary.
  --default-ppi                   Mark this monitor as the default ppi for ppi
                                  scaling.
  --above TEXT                    The monitor which this monitor is above.
  --below TEXT                    The monitor which this monitor is below.
  --left TEXT                     The monitor which this monitor is left
  --right TEXT                    The monitor which this monitor is right
  --off                           Turn off this monitor.
  --help                          Show this message and exit.
```
