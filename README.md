# EvscapeRoom

A free single/multiplayer escape-room 'MUD', using Python and [Evennia](https://github.com/evennia/evennia)!

Created for the *MUD Coders Guild game Jam*, April 14-May 15 2019. The theme for
the jam was "One Room". This ended up as the winning entry! 

- [Evscaperoom Dev blog (part 1)](http://evennia.blogspot.com/2019/05/creating-evscaperoom-part-1.html)
- [Evscaperoom Dev blog (part 2)](http://evennia.blogspot.com/2019/05/creating-evscaperoom-part-2.html)


## Live demo

While you can easily set up and run this with your own Evennia install, the Evscaperoom 
is also playable in full on the [official Evennia demo server](https://demo.evennia.com/).
Just make an account, log in and write `evscaperoom` in the first location!

 > Note: The version in the Evennia demo is more up-to-date than the one in this repo since that's the live place
 where people find bugs - and I can't be arsed to set up a git subrepo inside the other repo - I always 
 mess those up. So if you really want the latest version with latest bug fixes you are better off looking at
 the code embedded into the demo at https://github.com/evennia/evdemo/tree/master/evdemo/evscaperoom.

# Introduction

![The Jester being jesterly](world/grin_in_the_shadows_by_griatch_art_small.jpg)

There is a pie-eating contest in town. The tricky village Jester has trapped
you - her greatest pie-eating rivals - in her quirky cabin. If you don't get
out she'll win by default! 

Evscaperoom is, as it sounds, an escaperoom in text form. You start locked into
the cabin of the Jester and have to figure out how to get out. There is no
timer, but surely everyone knows that the greater your pie-eating skills the
better you'll do ...

# Installation 

## Short: 

This comes as an Evennia game folder and makes use of Evennia `master` branch (using Python 3.7). 
If you are an existing Evennia user, that's all the info you need! 

## Running through docker

- `git clone https://github.com/Griatch/evscaperoom.git`
- `cd evscaperoom`
- `docker run -it --rm -p 4000:4000 -p 4001:4001 -p 4002:4002 -v $PWD:/usr/src/game evennia/evennia:develop`

(If your platform does not have `$PWD` replace with the the path to your
 current dir). You should end up in a shell inside the `evscaperoom` repo (it's mounted
into the container)

- `evennia migrate`  (only first time)
- `evennia start`  (create a superuser. The email can be blank)

You can now connect your browser to `http://localhost:4001` or your mud client
to `localhost`, port `4000`. To play and enjoy the game, best is to *not* log
in as the superuser you created, but to make a new, normal player account.

Enjoy!

## Full installation (non-docker)

You need the [Evennia](https://github.com/evennia/evennia) engine to run. You need Python3.7 and GIT to
fetch Evennia. Below are copyable instructions for an apt-able
Linux (tested on Linux Mint), but you can install on Windows and Mac too, see Evennia's [Getting Started](https://github.com/evennia/evennia/wiki/Getting-Started)
instructions where this is explained in more detail (in those instructions you
don't need to create the `mygame` folder since this repo replaces that). Note however that this uses the 
develop-branch of Evennia which may not be fully stable at all times.

- `sudo apt-get update && sudo apt-get install python3.7 python3.7-dev git python-pip python-virtualenv gcc`
- `mkdir evscaperoom && cd evscaperoom`
- `git clone https://github.com/evennia/evennia.git`
- `git clone https://github.com/Griatch/evscaperoom.git`
- `virtualenv --python /usr/bin/python3.7 vienv`
- `source vienv/bin/activate`

Make sure the last `source` command makes your terminal prompt change to `(vienv)`. This you
need to re-run if you start a new terminal later, since we are installing Python stuff into 
this virtual Python environment.

- `cd evennia && git checkout develop && cd ..` 
- `pip install -e evennia`

You should now have switched to Evennia's `develop` branch and installed
Evennia in the virtualenv. 

- `cd evscaperoom`
- `evennia migrate` (create a superuser when asked, email can be blank)
- `evennia start`

You can now browse to http://localhost:4001 to play the game. Or connect your
mud-client to `localhost`, port `4000`. To play and enjoy the game, best is to
*not* log in as the superuser you created, but to make a new, normal player
account.

Enjoy!

# Playing the game

You should start by `look`ing around and at objects in the Jester's cabin. Read the
descriptions carefully, there may be hints in there! Note also that some things
may subtly change over time. 

The `examine <object>` command allows you to 'focus' on an object. When you do
you'll learn actions you could try for the object you are focusing on, such as
turning it around, read text on it or use it with some other object. Note that
more than one player can focus on the same object, so you won't block anyone
when you focus. Focusing on another object or use `examine` again will remove
focus.

The Jester has provided hintberry-pies for if you get stuck. They are very
tasty and will give you insight. But if you eat too many pies now, how are you
going to be able to best her in the pie-eating contest later ...?

# Technical 

The Jester's cabin is a single Evennia room of a custom typeclass. The game
commands are defined on the room itself and thus only work there.  The objects
have `at_focus_<action>` hooks, where the name of the hook defines what kind of
action can be performed when focusing on this object. This moves all logic onto
each object instead of being in the command.

When connecting to the game, the user has the option to join an existing room
(which may already be in some state of ongoing progress), or may create a fresh
room for them to start solving on their own (but anyone may still join them later).

The room will go through a series of 'states' as the players progress through
its challenges. These states are describes as modules in .states/ and the 
room will load and execute the State-object within each module to set up
and transition between states as the players progress. This allows for isolating
the states from each other and will hopefully make it easier to track 
the logic and (in principle) inject new puzzles later.

Once no players remain in the room, the room and its state will be wiped.

# Design Philosophy

Some basic premises inspired the design of this.

- You should be able to resolve the room alone. So no puzzles should require the
  collaboration of multiple players. This is simply because there is no telling
  if others will actually be online at a given time (or stay online throughout).
- You should never be held up by the actions/inactions of other players. This
  is why you cannot pick up anything (no inventory system) but only
  focus/operate on items. This avoids the annoying case of a player picking up
  a critical piece of a puzzle and then logging off.
- A room's state changes for everyone at once. My first idea was to have a given 
  room have different states depending on who looked (so a chest could be open
  and closed to two different players at the same time). But not only does this
  add a lot of extra complexity, it also defeats the purpose of having multiple
  players. This way people can help each other and collaborate like in a 'real'
  escape room. For people that want to do it all themselves I instead made it
  easy to start "fresh" rooms for them to take on.

All other design decisions flowed from these. 
