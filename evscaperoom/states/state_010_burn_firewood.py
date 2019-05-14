"""
Time to melt some ice!

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

    When you get into the cabin, a new super-fertilizer recipe is just being
    tested ...

"""

INTRO_TEXT1 = """
|GThe stem of the rose splits into two and then into four and eight. New leaves
unfold and push out of the plant so quickly that it looks like the thing is
exploding!|n
"""

INTRO_TEXT2 = """
|gThe rose stickling bursts out of its pot, shooting off more and more branches
and leaves in all directions. Long thorns grow. Ping rose-blooms unfold withing
moments open, several per branch. The thing is taking over the table.|n
"""

INTRO_TEXT3 = """
|G... Then the plant starts to wither. The dirt has turned to sand and there is
just not enough water and nutrients in the pot to sustain the growth.|n
"""

INTRO_TEXT4 = """
|YThe leaves turn yellow and for a moment |Gnew leaves|Y sprout to take their
place. But they can't keep up.|n
"""

INTRO_TEXT5 = """
|RAnd just as suddenly, it's over. On the table stands the completely dried-out husk
of a *rosebush|R, grown to several times its original size.|n
"""

# ------------------------------------------------------------
# Dried rosebush
# ------------------------------------------------------------

ROSEBUSH_DESC = """
The rosebush is impressively large, but is so dried out that it's brown-black
in color. The roses are frozen in place, rapidly mummified.
"""

ROSEBUSH_FEEL = """
The thing crackles like parchment. Even the thorns are dry and brittle.
"""

ROSEBUSH_MOVE = """
Carefully ~you ~move the brittle bush to *{location}. It looks big
but it doesn't actually weigh very much.
"""

ROSEBUSH_BURN_FAIL = """
You try to focus the light on the bush over on the {location} but it's not
working. Maybe it's too far away.
"""

ROSEBUSH_BURN = """
~You ~hold up the looking glass between the rosebush and the glaring sun from the
window. A bright spot appears among the dry leaves and branches.

"""


class Rosebush(objects.Feelable, objects.Movable):

    move_positions = {"table": "to_table",
                      "fireplace": "to_fireplace"}
    start_position = "table"

    def at_object_creation(self):
        super().at_object_creation()
        # this makes it so we can use the looking glass on it
        self.set_flag("burnable")
        self.set_flag("looking_glass_sun")

    def get_cmd_signatures(self):
        txt = ("You can *feel and also carefully *move to <location>. "
               f"The bush is currently at the *{self.db.position}.")
        return [], txt

    def at_focus_feel(self, caller, **kwargs):
        self.msg_char(caller, ROSEBUSH_FEEL.strip())

    def at_cannot_move(self, caller):
        self.msg_char(caller, "There's no place for it there.")

    def to_table(self, caller):
        self.room.achievement(caller, "Where to put this?", "Moved the plant back and forth")
        self.msg_room(caller, ROSEBUSH_MOVE.format(location="the table"))

    def to_fireplace(self, caller):
        self.room.score(2, "moved rosebush to fireplace")
        self.msg_room(caller, ROSEBUSH_MOVE.format(location="fireplace, propping it up inside"))

    def handle_burn(self, caller, igniter):
        "Called by object checking for the burnable flag"
        location = self.db.position
        if location != "fireplace":
            self.msg_char(caller, ROSEBUSH_BURN_FAIL.format(location=location).strip())
        else:
            self.room.score(2, "burned rosebush")
            self.msg_room(caller, ROSEBUSH_BURN.lstrip())
            self.next_state()


# ------------------------------------------------------------
# state
# ------------------------------------------------------------

STATE_HINT_LVL1 = """
That *rosebush looks very dry. It would likely burn well.
"""

STATE_HINT_LVL2 = """
Move *rosebush to *fireplace, then use *monocular on *rosebush
to start a fire.
"""


class State(BaseState):

    next_state = "state_011_exit_room"

    hints = [STATE_HINT_LVL1,
             STATE_HINT_LVL2]

    def character_enters(self, character):
        self.cinematic(GREETING.format(name=character.key),
                 target=character)

    @interactive
    def init(self):

        # the plant is no more
        plant = self.get_object("plant")
        if plant:
            plant.delete()
        rosebush = self.create_object(
            Rosebush, key="rosebush", aliases="rose bush")
        rosebush.db.desc = ROSEBUSH_DESC.strip()

        self.msg(INTRO_TEXT1.rstrip())
        yield(4)
        self.msg(INTRO_TEXT2.rstrip())
        yield(4)
        self.msg(INTRO_TEXT3.rstrip())
        yield(4)
        self.msg(INTRO_TEXT4.rstrip())
        yield(4)
        self.msg(INTRO_TEXT5.rstrip())

    def clean(self):
        super().clean()
        self.room.progress(93)
