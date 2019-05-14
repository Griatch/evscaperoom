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
        self.msg_room(caller, "~You ~open the front door to freedom!")
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
Almost there now!

The fire sure heated the *cauldron! Maybe time to examine it again?
"""

STATE_HINT_LVL2 = """
Dig around in the *cauldron to find the room *key. Use it to unlock the front
*door and leave! Congrats!
"""


class State(BaseState):

    next_state = "state_012_questions_and_endings"

    hints = [STATE_HINT_LVL1,
             STATE_HINT_LVL2]

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
