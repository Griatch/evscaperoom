"""
The wind turns

"""
from evennia.utils import interactive
from ..state import BaseState
from .state_001_start import Windows

GREETING = """
    This is the situation, {name}:

    The |rJester|n wants to win your village's yearly |wpie-eating contest|n.
    As it turns out, you are one of her most dangerous opponents.

    Today, the day of the contest, she invited you to her small cabin for a
    'strategy chat'. But she tricked you and now you are |wlocked in|n! If you
    don't get out before the contest starts she'll get to eat all those pies on
    her own and surely win!

    When you get into the cabin, a *book of notes have been read and a bunch of
    disgusting ingredients have just been mixed together to create the
    so-called *childmaker potion mentioned in the book ...

"""

# always drop this hint some time after the childmaker is finished
INTRO1 = """
As the smells of the various ingredients of the *childmaker potion gradually
abate, *Vale makes a sound as if it is sniffing the air:

    |w"Ah, I think the wind's turning."|n
"""

# ------------------------------------------------------------
# windows (possible to cover)
# ------------------------------------------------------------

WINDOWS_DESC = """
The two windows face the sun- and shadow-side of the cabin respectively. But
even though they let in a lot of light, that light enters through a sturdy
metalwork just outside the glass. Intervoven into the metalwork are climbing
roses that further limit the view. Above each window is a wooden bar that might
have held curtains at one point, but none can be seen anymore.
"""

WINDOWS_COVER1 = """
~You ~hang *{obj} over the shadow-side window. It doesn't block all light,
but probably good enough. The room gets a little darker.
"""

WINDOWS_COVER2 = """
~You ~hang *{obj} as a makeshift curtain over the sunside window. Whereas not all
light is blocked out (you can still see to move around), the room is now as
dark as it can be with the tools at hand.
"""


class WindowsCoverable(Windows):

    def at_object_creation(self):
        super().at_object_creation()
        self.set_flag("window_coverable")  # important
        self.db.covering_objects = []

    def at_cover(self, caller, item):
        """ Called by the objects used to cover it (blanket, bathtowel) """
        if item in self.db.covering_objects:
            self.msg_char(caller, "You have already used that.")
            return

        self.db.covering_objects.append(item)
        if len(self.db.covering_objects) > 1:
            self.room.score(2, "covered both windows")
            self.msg_room(caller, WINDOWS_COVER2.format(obj=item.name).strip())
            self.next_state()
        else:
            self.room.log("covered one window")
            self.msg_room(caller, WINDOWS_COVER1.format(obj=item.key).strip())


# ------------------------------------------------------------
# state
# ------------------------------------------------------------

STATE_HINT_LVL1 = """
Listen to *Vale. Which way is the wind turning?
"""

STATE_HINT_LVL2 = """
Go to *window and look outside. You'll spot a *scarecrow that has now turned in
the wind. Look at the scarecrow and read the sign it is holding.
"""

STATE_HINT_LVL3 = """
You were told you should cover the windows. Among the drawers of the closet is
a *blanket. Is there something else of similar size in the room you could use?
"""

STATE_HINT_LVL4 = """
Use the *blanket and *towel on the *windows to cover them.
"""


class State(BaseState):

    hints = [STATE_HINT_LVL1,
             STATE_HINT_LVL2,
             STATE_HINT_LVL3,
             STATE_HINT_LVL4]

    next_state = "state_006_dark_room"

    def character_enters(self, character):
        self.cinematic(GREETING.format(name=character.key),
                       target=character)

    @interactive
    def init(self):
        # replace windows with version that can be covered
        windows = self.create_object(
            WindowsCoverable, key='windows', aliases=["window"])
        windows.db.desc = WINDOWS_DESC.strip()
        yield(10)
        self.msg(INTRO1)

    def clear(self):
        super().clear()
        self.room.progress(43)
