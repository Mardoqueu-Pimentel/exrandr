# exrandr

Generate xrandr command adapted to work with gnome scale in mind.

## Instalation

```shell
$ pip install "git+https://github.com/Mardoqueu-Pimentel/exrandr.git"
```

## Usage

```shell
$ exrandr --help

Usage: exrandr [OPTIONS]

Options:
  --scale INTEGER
  --display TEXT   Format: name,resolution,zoom,gamma,rotation,primary
                   [required]
  --help           Show this message and exit.


$ exrandr --scale=2 --display DP-1,1920x1080,,0.9,left --display HDMI-0,3840x2160,1.6,0.9,,p --display eDP-1-1,1920x1080,1.25

xrandr \
	--output DP-1 --mode 1920x1080 --scale 2.0 --pos 0x0 --gamma 0.9 --rotation left \
	--output HDMI-0 --mode 3840x2160 --scale 1.25 --pos 2160x0 --gamma 0.9 --primary \
	--output eDP-1-1 --mode 1920x1080 --scale 1.6 --pos 6960x0 --gamma 1.0 | :
```