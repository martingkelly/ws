# Workspace tool
`ws` is a lightweight tool for managing a workspace of code repositories. It is
intended to handle coarse dependencies between projects, building multiple
projects in the right order and passing the correct flags to each (such as
`PKG_CONFIG_PATH` and similar). It is not intended to be a full-fledged build
system, but instead should merely build each project in the right order and with
the right environment glue. Everything it does can be done by-hand, so rather
than a replacing existing build tools, it merely automates the tedious task of
manually specifying `--prefix`, setting env vars, and rebuilding projects in the
right order when they change.

Note that these tools do not directly handle source code syncing. That job is
left to [repo](https://code.google.com/archive/p/git-repo/).

## ws
The `ws` script is the main point of interaction with your workspace. It assumes
you have already synced a bunch of code using the `repo` tool and, unless you
use special options, it assumes you are currently somewhree inside the root of
the source that `repo` manages. Like `repo` however, you can be anywhere inside
the root and do not have to be at the very top.

The normal workflow for `ws` is as follows:

```
repo init -u MANIFEST-REPO-URL
repo sync
ws init
ws build
```

`ws init` will look for a file called `ws-manifest.yml` at the root of the
repository contianing the `git-repo` manifest (the one we passed `-u` into when
we called `repo init`). This file contains dependency and build system
information for the projects that `ws` manages. Note that `ws` does not have to
manage all the same projects that `repo` manages, but it can. The full format
for `ws-manifest.yml` is at the bottom of the README.

## bash-completion
If you like bash-completions and typing things fast, you can do:
```
. bash-completion/ws
```
And get auto-completion for ws commands.

### ws init
When you run `ws init`, ws creates a `.ws` directory in the current working
directory. This directory can contain multiple workspaces, but there is always a
default workspace, which is the one that gets used if you don't specify an
alternate workspace with the `-w` option. You may want to create multiple
workspaces to manage multiple build configurations, such as separate debug and
release builds. However, all workspaces in the same `.ws` directory will still
operate on the same source code (the repositories configured in
`ws-manifest.yml`).

### ws default
`ws default` is used to change the default workspace (the one used when you
don't specify a `-w` option).

### ws build
`ws build` is the main command you run. If you specify no arguments, it will
build every project that repo knows about. If you instead specify a project or
list of projects, it will build only those, plus any dependencies of them.
Additionally, `ws` will checksum the source code on a per-repo basis and avoid
rebuilding anything that hasn't changed. The checksumming logic uses git for
speed and reliability, so source managed by `ws` has to use git.

### ws clean
`ws clean` cleans the specified projects, or all projects if no arguments
are given. By default, it just runs the clean command for the underlying build
system (meson, cmake, etc.). If you also use the `-f/--force` switch, it will
instead remove the entire build directory instead of trusting the underlying
build system.

### ws env
`ws env` allows you to enter the build environment for a given project. If given
no arguments, it gives you an interactive shell inside the build directory for
the project. If given arguments, it instead runs the specified command from that
directory. In both cases, it sets up the right build enviroment so build
commands you might use will work correctly and you can inspect if something
seems wrong.

An example use of `ws env` is to manually build something or to tweak the build
configuration of a given project in a way that `ws` doesn't know how to handle.

## ws manifest
The `ws` manifest is a YAML file specifying a few things about the projects `ws`
manages:
- What build system they use (currently supports `meson` and `cmake`).
- What dependencies they have on other projects managed by `ws`.
- Any special environment variables they need.

The syntax is as follows:
```
some-project:
    build: meson
    deps:
        - gstreamer
        - ...
    env:
        GST_PLUGIN_PATH: ${LIBDIR}/gstreamer-1.0

gstreamer:
    build: meson
    deps:
        - ...
```

In this case, `some-project` builds with `meson`, and requires `gstreamer` and
some other dependencies. In order to find gstreamer plugins, it needs
`GST_PLUGIN_PATH` set. It uses template syntax to refer to `${LIBDIR}`, which will
be filled in with the library path for the project.

Here is the complete list of usable template variables:
```
- ${LIBDIR}: the library path for the project (what `LD_LIBRARY_PATH` will be
  set to for the project's build environment.
- ${PREFIX}: the project's prefix (what you would pass to `--prefix`).
```