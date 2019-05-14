"""
The windows have been covered, turning the room dark.

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

    When you get into the cabin, the *windows have been covered to block out
    most light ...

"""

INTRO1 = """
Vale chirps from over by the door:

    |w"Eeep! What happened to the light? I don't wanna get eaten by a grue!"

"""


ROOM_DESC = """
|CThe |RJester's cabin|C is thrown into a dark gloom now that the windows are
covered.

By the door is a nicely smelling *hintberry |Cpie. *Vale|C stands next to the
pie. It chatters to itself and waves its arms above its head, excitedly.
Behind the monkey, the light from the keyhole lights the back of its hands,
making them cast long shadows into the cabin and onto the *fireplace|C across
the room.

"""

# ------------------------------------------------------------
# windows (covered)
# ------------------------------------------------------------

WINDOWS_DESC = """
The windows have been covered so as to only let in a little light around their
edges - it's not much, but enough light to allow you to still move around without
bumping into things.

"""

# ------------------------------------------------------------
# fireplace (shadows cast onto it)
# ------------------------------------------------------------

FIREPLACE_DESC = """
The shadows from *Vale's moving hands dance over the surface of the fireplace.
It turns out the thing has been doing something akin to a shadow theatre show
this whole time!

As you watch, the fingers form the mishappen sillhouette of a man (or is it a
monkey?) reaching up and whacking the chimney with its hands. The figure then
falls down and out of sight only to return and do the same thing again, over
and over and over.

You notice that the shadow-figure always hits the same *stone high up on the
chimney, much above the *painting that hangs in the center of the fireplace.
"""

# ------------------------------------------------------------
# stone (spot on chimney, have to stand to chair to reach)
# ------------------------------------------------------------

STONE_DESC = """
The stone pointed out by Vale sits high up on the chimney. On closer
inspection, it looks a little loose.
"""

STONE_PUSH_DAMPER_CLOSED = """
~You ~push at the *stone. It sinks a little bit into the surface before it hits
some sort of blocker. Inside the chimney there is the brief sound of something
metallic grinding against stone. ~You ~push again but it's stuck.
"""

STONE_PUSH_DAMPER_CLOSED_PERSON = """
It feels like this stone should be possible to push further. Maybe you need to
change the fireplace in some other way before you can continue?
"""

STONE_PULL = """
~You ~pull at the stone, but it's not coming out.
"""

STONE_CANNOT_REACH = """
The spot *Vale shows you is too high up. You cannot reach it.
"""


class Stone(objects.EvscaperoomObject):

    must_stand_on_flag = "reach_stone"

    def _can_reach(self, caller):
        pos = self.get_position(caller)
        obj, position = pos
        return position == "climb" and obj.check_flag(self.must_stand_on_flag)

    def at_focus_pull(self, caller, **kwargs):
        if self._can_reach(caller):
            self.room.score(1, "tried to pull stone")
            self.msg_char(caller, STONE_PULL.strip())
        else:
            self.msg_char(caller, STONE_CANNOT_REACH.strip())

    @interactive
    def at_focus_push(self, caller, **kwargs):
        if self._can_reach(caller):
            damper = self.room.state.get_object("damper knob")
            if damper and damper.check_flag("open"):
                self.room.score(2, "push stone in fireplace")
                self.next_state()
            else:
                self.msg_room(caller, STONE_PUSH_DAMPER_CLOSED.strip())
                self.msg_char(caller, STONE_PUSH_DAMPER_CLOSED_PERSON.rstrip())
        else:
            self.msg_char(caller, STONE_CANNOT_REACH.strip())


# ------------------------------------------------------------
# state
# ------------------------------------------------------------

STATE_HINT_LVL1 = """
The shadows from *Vale's hand motions are pointing something out on the *fireplace.
"""

STATE_HINT_LVL2 = """
You need to climb something to get to the *stone. The *table is too far away.
"""

STATE_HINT_LVL3 = """
Move *chair to the *fireplace and climb up on it. Push the *stone and hope something happens.
"""

STATE_HINT_LVL4 = """
If the *stone is blocked, examine *picture and turn it over to find the fireplace *damper.
Turn the *damper knob and you should now be able to push *stone all the way in.

"""


class State(BaseState):

    hints = [STATE_HINT_LVL1,
             STATE_HINT_LVL2,
             STATE_HINT_LVL3,
             STATE_HINT_LVL4]

    next_state = "state_007_chest_lever"

    def character_enters(self, character):
        self.cinematic(GREETING.format(name=character.key),
                       target=character)

    @interactive
    def init(self):

        fireplace = self.get_object("fireplace")
        if fireplace:
            fireplace.db.desc = FIREPLACE_DESC.strip()
        windows = self.get_object("windows")
        if windows:
            windows.db.desc = WINDOWS_DESC.strip()
        stone = self.create_object(
            Stone, key="stone")
        stone.db.desc = STONE_DESC.strip()
        self.room.db.desc = ROOM_DESC.strip()
        yield(4)
        self.msg(INTRO1.strip())

    def clean(self):
        super().clean()
        self.room.progress(52)

        # clean up
        stone = self.get_object("stone")
        if stone:
            stone.delete()
        # reset all positions (get off chair/table etc)
        for char in self.room.get_all_characters():
            self.room.set_position(char, None)
