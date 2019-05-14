# EvscapeRoom

Griatch 2019

Created for the MUD Coders Guild game Jam, April 14-May 15 2019. The theme for
the jam was "One Room".

> Please note that this is a bit hard-coded for the sake of the jam; I plan to
> break out the 'engine' bits later and make an Evennia contribution out of it later.

# Introduction

There is a pie-eating contest in town. The tricky village Jester has trapped
you - her greatest pie-eating rivals - in her quirky cabin. If you don't get
out she'll win by default!

Evscaperoom is, as it sounds, an escaperoom in text form. You start locked into
the cabin of the Jester and have to figure out how to get out. There is no
timer, but surely everyone knows that the greater your pie-eating skills the
better you'll do ...

# Installation

The Evscaperoom is installed by adding the `evscaperoom` command to your game.
When you run that command in-game you're ready to play!

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
