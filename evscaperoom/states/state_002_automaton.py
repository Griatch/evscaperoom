"""
The monkey automaton

This state does not need to add as much new stuff since it was all added
in the first state; rather we just need to add the new things happening
in this state.

Once the monkey has gotten its name, this moves to the next state since it will
change the room.

"""

from evennia.utils import interactive
from ..state import BaseState
from .. import objects
from .state_001_start import Rafters, RAFTERS_DESC

GREETING = """
    This is the situation, {name}:

    The |rJester|n wants to win your village's yearly |wpie-eating contest|n.
    As it turns out, you are one of her most dangerous opponents.

    Today, the day of the contest, she invited you to her small cabin for a
    'strategy chat'. But she tricked you and now you are |wlocked in|n! If you
    don't get out before the contest starts she'll get to eat all those pies on
    her own and surely win!

    When you get into the cabin, a *coin was found up in the rafters. It was
    inserted into the mouth of a strange monkey *statue ...
"""

# ------------------------------------------------------------
# rafters (no more coin)
# ------------------------------------------------------------

# This desc shows if the watcher stands on something (bed, chair) and
# can thus see more (coin removed)

RAFTERS_STAND_DESC = """
The cabin's sloping roof is held up by thick criss-crossing wooden rafters,
several of which reaches across the room just above your head. They are great
for hanging and storing things just within reach. You can see that there's
a lot of grime and dust on top of them - the Jester is really a bit of a slob.

Over the rafter closest to the *door, just over the *bed, the Jester has hung
her *laundry. On the same rafter but across the room and over the table, hangs
a series of decorative *chimes, gently swinging to and fro.

Over by the fireplace hangs what looks like a old *saddle. On top of the saddle
something is written.

"""


class RaftersNoCoin(Rafters):

    def return_appearance(self, caller, **kwargs):
        # we will show different results depending on
        # if the player stands on something or not
        obj, pos = self.get_position(caller)
        if pos == 'climb':
            return super().return_appearance(caller, desc=RAFTERS_STAND_DESC.strip(), **kwargs)
        else:
            return super().return_appearance(caller, desc=RAFTERS_DESC.strip(), **kwargs)


# ------------------------------------------------------------
# monkey statue (active)
# ------------------------------------------------------------

STATUE_DESC = """
On the floor by the window on the shadow-side stands the strange little
monkey-statue. It's dressed in a red jacket and a conical hat.

It's also winking at you.
"""

STATUE_AWAKENING_1 = """
... nothing is happening.
"""

STATUE_AWAKENING_2 = """
... Then suddenly a shudder goes through the monkey and it turns its head! The
tail takes a slow turn and its fingers flex. The black orbs that are its eyes
look you up and down. From the wooden lips comes a squeaky voice:

    |w"If you know ma name, I'll tell you a secret."|n
"""

STATUE_NO_NAME = """
The monkey statue winks at ~you, shaking its wooden head:

    |w"That's not a name at all."|n
"""

STATUE_WRONG_NAME = """
As ~you ~give a name suggestion, the statue makes a little jump up and down,
flexing those long arms.

    |w"'{name}' eh? Nah, that's not ma name!"|n
"""

STATUE_YOUR_NAME = """
As ~you ~give '{name}' as a suggestion, the statue shakes its head in confusion and
replies,

    |w"... That's ... wait. Hold on now, that's YOUR name!|n
"""

STATUE_RIGHT_NAME_1 = """
... The strange wooden animal makes a loud chirp-noise as you make the
suggestion.  It is as if the thing is laughing an inhuman laugh.

    |w"Yes! Yes! VALE is my name! None other! VALE! VALE!

    My mistress asked Master Warwick to make me from her instructions.

    The man cried when he put the face on me, but he didn't tell me why."|n
"""

STATUE_RIGHT_NAME_2 = """
With a series of creaks and groans, 'Vale' hobbles over towards the *door and
stands in front of it. For a moment you hope that this thing has the means to
open the door. But instead Vale turns around and waves his hands above his
head, excitedly:

    |w"Now listen up and let me tell you the secret ...!"

"""


class StatueActive(objects.CodeInput):

    code = "Vale"
    case_insensitive = True

    def at_focus_speak(self, caller, **kwargs):
        super().at_focus_code(caller, **kwargs)

    def get_cmd_signatures(self):
        txt = "You might try to *speak <name> to the strange thing."
        return [], txt

    def at_no_code(self, caller):
        self.msg_room(caller, "~You ~give the monkey a name suggestion.", True)
        self.msg_room(caller, STATUE_NO_NAME.strip())

    def at_code_incorrect(self, caller, code_tried):
        if code_tried.lower() == caller.key.lower():
            self.room.achievement(caller, "Messing with your head", "Trying to confuse Vale")
            self.msg_room(caller, STATUE_YOUR_NAME.format(name=caller.key).strip())
        else:
            self.msg_room(caller, STATUE_WRONG_NAME.format(name=code_tried.lower().capitalize()))

    @interactive
    def at_code_correct(self, caller, code_tried):
        self.room.score(2, "named Vale")
        self.msg_room(caller, "~You ~give the monkey a name suggestion.", True)
        self.msg_room(caller, STATUE_RIGHT_NAME_1.strip())
        yield(3)
        self.msg_room(caller, STATUE_RIGHT_NAME_2.rstrip())
        yield(3)
        self.next_state()


# ------------------------------------------------------------
# base state
# ------------------------------------------------------------

STATE_HINT_LVL1 = """
Maybe the name of the monkey is written somewhere.
"""
STATE_HINT_LVL2 = """
On the *door is a strange text that looks useful. But how to read it?  Maybe if
one changed the order of the letters?
"""

STATE_HINT_LVL3 = """
Use *mirror on the *door. The message is just written backwards
and without spaces between the words.
"""

STATE_HINT_LVL4 = """
The text reads START BY FEEDING VALE. The monkey's name is 'Vale'.
"""


class State(BaseState):

    next_state = "state_003_locked_closet"

    hints = [STATE_HINT_LVL1,
             STATE_HINT_LVL2,
             STATE_HINT_LVL3,
             STATE_HINT_LVL4]

    def character_enters(self, character):
        self.cinematic(GREETING.format(name=character.key),
                       target=character)

    @interactive
    def init(self):
        # the coin is gone now, inserted into the statue
        coin = self.get_object("coin")
        if coin:
            coin.delete()
        # delete objects that we'll replace with new versions
        self.create_object(RaftersNoCoin, key="rafters")

        statue = self.create_object(
            StatueActive, key='statue', aliases=['monkey'])
        statue.db.desc = STATUE_DESC.strip()

        # introduce the statue talking
        yield(2)
        self.msg(STATUE_AWAKENING_1.rstrip())
        yield(3)
        self.msg(STATUE_AWAKENING_2.rstrip())

    def clean(self):
        super().clean()
        self.room.progress(18)
