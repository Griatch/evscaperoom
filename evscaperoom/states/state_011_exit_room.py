"""
Get the key and get out!
"""

from evennia.utils import interactive
from ..state import BaseState
from .. import objects


GREETING = """
    This is the situation, {name}:

    The |rJester|n wants to win your village's yearly |wpie-eating contest|n.
    As it turns out, you are one of her most dangerous opponents.

    Today, the day of the contest, she invited you to her small cabin for a
    'strategy chat'. But she tricked you and now you are |wlocked in|n! If you
    don't get out before the contest starts she'll get to eat all those pies on
    her own and surely win!

    When you get into the cabin, the long-cold fireplace is about to come to
    life ...

"""

INTRO_TEXT1 = """
Small tendrils of |wsmoke|n starts to appear among the dry branches ... then a
small |rfl|ya|rme|n breaks out ...
"""

INTRO_TEXT2 = """
|cW|wOO|cSH!

Within moments the rosebush has burst into |wviolent flames|c. This thing is not
even burning normally - it burns with blue-|wwhite|c flames and a lot hotter than
you'd expect from dry wood.|n

|bThe cauldron above the flames hisses and |csteams|b, a cloud of water vapor
rising from it.|n
"""

INTRO_TEXT3 = """
Only a little while later, the unnatural, violent flames abate. There is
nothing left of the rosebush afterwards, not even ash.
"""

# ------------------------------------------------------------
# door key (to the front door!)
# ------------------------------------------------------------

DOORKEY_DESC = """
After all you have seen, this is a surprisingly normal-looking brass house key.
It has a little wooden plaque attached to it.
"""

DOORKEY_READ = """
The plaque reads:

    |rIf you found me, congratulations!
    Have some |cpie|r on the way out, you've earned it!|n
"""

DOORKEY_APPLY = """
~You ~take the door key over to the cabin door and ~insert it into the key
hole. Slowly ~you ~turn the key in the lock ...
"""

DOORKEY_APPLY_UNLOCK = """
... and there is a loud click as it unlocks!
"""


class DoorKey(objects.Insertable, objects.Readable):

    target_flag = "cabin_door"

    @interactive
    def at_apply(self, caller, action, obj):
        self.room.score(2, "unlocked the door")
        self.msg_room(caller, DOORKEY_APPLY.strip())
        yield(3)
        obj.set_flag("unlocked")  # the important bit
        self.msg_room(caller, DOORKEY_APPLY_UNLOCK.strip())

    def at_read(self, caller, *args, **kwargs):
        self.msg_char(caller, DOORKEY_READ.strip())

    def get_cmd_signatures(self):
        txt = "You can *read the plaque. And of course *insert into <target>."
        return [], txt

# ------------------------------------------------------------
# cauldron (key accessible)
# ------------------------------------------------------------

CAULDRON_DESC = """
The cauldron is steaming and dripping. The ice inside has cracked into
sludge from the heat.
"""

CAULDRON_DIG = """
~You ~dig around in the icy sludge and find the door *key near the bottom!
"""

CAULDRON_DIG_ALREADY = """
You already found the *key, it's right there! Just use it!
"""


class CauldronMelted(objects.EvscaperoomObject):

    def at_focus_dig(self, caller, **kwargs):
        if not self.check_flag("found_key"):
            doorkey = self.room.state.create_object(
                DoorKey, "key", aliases=["door key"])
            doorkey.db.desc = DOORKEY_DESC.strip()
            self.msg_room(caller, CAULDRON_DIG.strip())
            self.set_flag("found_key")
        else:
            self.msg_char(caller, CAULDRON_DIG_ALREADY.strip())


# ------------------------------------------------------------
# outer door
# ------------------------------------------------------------

CABINDOOR_DESC = """
The main door of the Jester's cabin is gaintly painted in red. Its top is
rounded and the door is not very big. But it's sturdy, made from
planks taken in the woods surrounding the cabin.

It's a sunny day outside and tempting light shines in through the key hole.
"""

CABINDOOR_DESC_OPEN = """
The door to the cabin stands wide open!

|gOutside, in the bright sunlight, you see the path heading towards
the river and then back to the village.|n
"""

CABINDOOR_OPEN = """
You open the front door to freedom!

|gBright sunlight shines through the doorway. A warm summer wind sweeps through
the cabin.|n
"""

CABINDOOR_CANNOT_LEAVE = """
The door is closed though ...
"""

CABINDOOR_LEAVE = """
~you ~step out into the sun.
"""


class CabinDoorOpenable(objects.Openable):

    start_open = False

    def at_object_creation(self):
        super().at_object_creation()
        # required for key to work with this
        self.set_flag("cabin_door")

    def at_open(self, caller):
        # this will be the end of the game!
        self.msg_room(caller, CABINDOOR_OPEN.strip())
        self.db.desc = CABINDOOR_DESC_OPEN.strip()

    def at_close(self, caller):
        self.msg_char(caller, "The door is closed.")
        self.db.desc = CABINDOOR_DESC.strip()

    @interactive
    def at_focus_leave(self, caller, **kwargs):
        if self.check_flag("open"):
            self.room.score(1, "left the cabin")
            for char in self.room.get_all_characters():
                self.msg_room(char, CABINDOOR_LEAVE.strip())
            yield(3)
            # set it explicitly here for debugging and if
            self.next_state("state_012_questions_and_endings")
        else:
            self.msg_char(caller, CABINDOOR_CANNOT_LEAVE.strip())


# ------------------------------------------------------------
# state
# ------------------------------------------------------------


STATE_HINT_LVL1 = """
You heated the cauldron, maybe time to look inside it?

... what, you thought it was more complex than that?

But the NEXT piece of pie will have something REALLY interesting.
"""

STATE_HINT_LVL2 = """
Open the door with *key you found in the *cauldron.

Yep, there is no more trick to it.

The next piece of pie will be more informative though.
"""

STATE_HINT_LVL3 = """
Open the door and step outside.

Yeah, that's usually how doors work. Enjoy the sunshine!

On the other hand, the piece of pie you eat after this one will bring the
really juicy intel.
"""

STATE_HINT_LVL4 = """
Actually not not this one, but the next one for sure.
"""

STATE_HINT_LVL5 = """
This pie gives you no further insight. But you can't be SURE the next pie is
not giving you the answer to the FINAL MYSTERY, can you.
"""

STATE_HINT_LVL6 = """
So here's the big secret, finally:

Every pie you eat makes it harder for you to beat the Jester in the pie-eating
contest. That's pretty obvious when you think about it.

... So, no, that was not really the secret. Have one more slice and uncle pie
will tell you.

"""

STATE_HINT_LVL7 = """
... or not. The pie has got you good. We could be doing this all day.
"""

STATE_HINT_LVL8 = """
There really is no reward at the end of this. Just a very aching tummy. This
is the final hint you are gonna get, promise.
"""

STATE_HINT_LVL9 = """
So that was a lie. But THIS is the last one.
"""

STATE_HINT_LVL10 = """
Hey, how many slices are IN this pie anyway ... ?
"""

STATE_HINT_LVL11 = """
The pie is just messin' with you, you know. Wobble out of here now.
"""

STATE_HINT_LVL12 = """
At least you are really, really full of pie!
"""

STATE_HINT_LVL13 = """
This is the thirteenth piece of pie you've eaten just to figure out how to open
a door. Congratulations.
"""


class State(BaseState):

    next_state = "state_012_questions_and_endings"

    hints = [STATE_HINT_LVL1,
             STATE_HINT_LVL2,
             STATE_HINT_LVL3,
             STATE_HINT_LVL4,
             STATE_HINT_LVL5,
             STATE_HINT_LVL6,
             STATE_HINT_LVL7,
             STATE_HINT_LVL8,
             STATE_HINT_LVL9,
             STATE_HINT_LVL10,
             STATE_HINT_LVL11,
             STATE_HINT_LVL12,
             STATE_HINT_LVL13]

    def character_enters(self, character):
        self.room.achievement(
            character, "Latecomer", "Joined a room more than 90% complete")
        self.cinematic(GREETING.format(name=character.key),
                       target=character)

    @interactive
    def init(self):
        rosebush = self.get_object("rosebush")
        if rosebush:
            rosebush.delete()
        door = self.get_object("door to the cabin")
        if door:
            door.delete()
        door = self.create_object(
            CabinDoorOpenable, key="door to the cabin", aliases=["door"])
        door.db.desc = CABINDOOR_DESC.strip()

        yield(3)
        self.msg(INTRO_TEXT1.rstrip())
        yield(4)
        self.msg(INTRO_TEXT2.rstrip())
        yield(4)
        self.msg(INTRO_TEXT3.rstrip())

        cauldron = self.create_object(
            CauldronMelted, key="cauldron")
        cauldron.db.desc = CAULDRON_DESC.strip()

    def clean(self):
        super().clean()
        chars = self.room.get_all_characters()
        for obj in self.room.contents:
            if obj not in chars:
                obj.delete()

        # We are done - show questions and end cinematics
        self.room.progress(100)
