"""
Use the lever with the chest (this is a short state)

"""
from random import choice
from evennia.utils import interactive
from ..state import BaseState
from .. import objects
from .state_001_start import Socks
from .state_003_locked_closet import StatueValeChatter

GREETING = """
    This is the situation, {name}:

    The |rJester|n wants to win your village's yearly |wpie-eating contest|n.
    As it turns out, you are one of her most dangerous opponents.

    Today, the day of the contest, she invited you to her small cabin for a
    'strategy chat'. But she tricked you and now you are |wlocked in|n! If you
    don't get out before the contest starts she'll get to eat all those pies on
    her own and surely win!

    When you get into the cabin a stone high up on the chimney was just pushed ...

"""

ROOM_DESC = """
The |rJester's cabin|n is actually just a small single room with a *door.
Ample light enters from two *windows on each side. The underside of the sloping
roof is exposed (as are the *rafters holding them up), making the place taller
and feel more spacious than it is.

On the wall opposite the door is a small stone *fireplace, lined to the left
and right side by a tall *closet and an area acting as a *kitchen
respectively. There is also a carver *chair standing around.

Just to the right of the door is the jester's messy *bed and to the right is
a long, empty-looking *table.

On the floor by the door is a plate on which sits a nicely smelling *hintberry
pie. *Vale idles by the door, chattering to itself from time to time.

"""

# ------------------------------------------------------------
# intro texts for this state
# ------------------------------------------------------------

STONE_PUSH_INTRO1 = """
The stone can now it can be shoved a fair bit inward. It bumps against
something inside the chimney. Something that is giving a little.
"""

STONE_PUSH_INTRO2 = """
Suddenly something on the other side comes loose. It rattles and tumbles down
the chimney, before coming down in the back of the fireplace with a loud
metallic clang.
"""

STONE_PUSH_INTRO3 = """
Over by the door, Vale stops his hand-gesturing and hoots:

    |w"All right! Now get some light back in 'ere so ya can see what ya got!|n

"""

STONE_PUSH_INTRO4 = """
Following Vale's instruction, the makeshift curtains are taken down, letting
light flood the room again.

The bath *towel and the *blanket are put back where they came from.
"""

# ------------------------------------------------------------
# Vale no longer waving its hands
# ------------------------------------------------------------

VALE_DESC = """
Vale stands by the door and watches your actions. It has stopped waving its
hands over its head and seems content just chattering to itself and cheering
your progress.
"""

VALE_FACE = """
Vale's painted monkey face is made of wood. It is too big for the body on which
it sits, like a caricature of the animal. The black glass making out the
things' gleaming eyes seem to have been fitted in the face's empty eye sockets
after the face itself was carved.

That carved face looks strangely familiar.
"""

VALE_SPEAK = """
Vale listens to ~you, its head tilted:

    |w"{reply}"|n,

it comments, amiably.
"""

VALE_RESPONSES = ["I see!", "So how that make you feel?", "I think so too.",
                  "No, really?", "That makes sense", "Not quite",
                  "So it has come to this", "That is good", "U-huh",
                  "Mmm", "I see, I see", "Why is that?", "I don't know, bud",
                  "Indeed", "Don't you have a pie-eating contest to hurry to?"]


class StatueValeQuiet(objects.EvscaperoomObject):

    def at_object_creation(self):
        super().at_object_creation()
        self.scripts.add(StatueValeChatter)

    def at_focus_face(self, caller, **kwargs):
        self.room.score(1, "examine Vale's face")
        self.msg_char(caller, VALE_FACE.strip())

    def at_focus_speak(self, caller, **kwargs):
        args = kwargs['args'].strip().capitalize()
        self.room.log(f"speak to Vale: '{args}'")
        self.msg_room(caller, f"~You says to *Vale: |c'{args}'|n.")
        self.msg_room(caller, VALE_SPEAK.format(reply=choice(VALE_RESPONSES)).strip())

    def get_cmd_signatures(self):
        txt = "You could look at Vale's *face and also *speak <topic> to it."
        return [], txt


# ------------------------------------------------------------
# fireplace (empty of things)
# ------------------------------------------------------------

FIREPLACE_DESC = """
A small stone fireplace sits in the middle of the wall opposite the *door. On
the chimney hangs a small oil *painting of a man. Hanging over the hearth is a
black *cauldron. The piles of *ashes below are disturbed by things recently
landing in them.
"""

FIREPLACE_CLIMB_CLOSED_DAMPER = """
You look up into the chimney. It's pitch black up there but you can tell that
there is no way you could fit to climb up that narrow passage.
"""

FIREPLACE_CLIMB_OPEN_DAMPER = """
You look up into the chimney. With the grille open you can see the bright sky
high up there! You have a clear view all the way, but even so, it's
quite clear you are too big to climb up the chimney pipe.
"""


class FireplaceEmpty(objects.Climbable):

    def at_focus_climb(self, caller, **kwargs):
        damper = self.room.state.get_object("damper knob")
        damper_open = damper and damper.check_flag("open")
        if damper_open:
            self.room.achievement(
                caller, "Optimist Santa", "Trying to climb the chimney to the last")
            self.msg_char(caller, FIREPLACE_CLIMB_OPEN_DAMPER.strip())
        else:
            self.msg_char(caller, FIREPLACE_CLIMB_CLOSED_DAMPER.strip())


# ------------------------------------------------------------
# ashes - both locket and lever must be here at this point
# ------------------------------------------------------------

ASHES_DESC = """
The stone slab making out the base of the fireplace is covered in
ashes. Now they are all cold though.

Among the ashes lies a small *locket that must have fallen down when turning
the damper, and a larger metal *lever that came crashing down when you
pressed the stone in the fireplace.
"""

ASHES_SMELL = """
These smell like normal ashes, probably comes from burning wood from the forest
the cabin lies just at the edge of.
"""

ASHES_APPLY = """
~You ~spread a pinch of ash over the dirt.
"""


class AshesUsable(objects.Smellable, objects.Usable):

    target_flag = "fertilizer_mixer"

    def at_object_creation(self):
        super().at_object_creation()
        self.set_flag("ashes")

    def at_focus_smell(self, caller, **kwargs):
        self.msg_char(caller, ASHES_SMELL.strip())

    def at_apply(self, caller, action, obj):
        self.room.score(6, "apply ashes to fertilizer")
        obj.handle_mix(caller, self, txt=ASHES_APPLY.strip())


# ------------------------------------------------------------
# sooty lever
# ------------------------------------------------------------

LEVER_DESC = """
This is some sort of metal lever or shaft. It's sooty from having fallen down from
its resting place up the chimney. One end of the lever is shaped like a cross and the
other end is clearly marked with a compass star:

            |rN|n
        |yW|n       |gE|n
            |cS|n

"""

LEVER_READ_SOOT = """
It seems like something is written on the side of the lever as well, but it's
so covered by soot that you can't make out what it is. Trying to brush the soot
aside with your hand only makes it black in turn.
"""

LEVER_SOOT_TO_ROOM = """
~You ~clean the *lever using the soap-drenched *socks.
"""

LEVER_READ_CLEAN = """
Having cleaned off the worst of the soot, you can clearly read the following:

    'THE LONG WALK HOME' - look me up!

"""

LEVER_ROTATE = """
You turn the thing around in your hands. The cross-shaped end of the
lever/shaft looks intricate, like it's meant to operate some sort of locking
mechanism.
"""

LEVER_APPLY = """
~You ~test to insert the lever/shaft into the chest and find that it fits
perfectly! The shape of the 'key hole' is such that the lever only fits in one
direction.

Unfortunately it does not appear to actually open the chest. Instead the lever
can move up, down, left or right inside its mount. Every movement there is a
small 'click' as if some mechanism is moving inside.

"""


class Lever(objects.Readable, objects.Insertable, objects.Rotatable):

    target_flag = "chest_lever_insert"

    def at_object_creation(self):
        super().at_object_creation()
        self.set_flag("cleanable")
        self.set_flag("sooty")

    def get_cmd_signatures(self):
        txt = "You can *rotate, try to *read and *insert in <object>."
        return [], txt

    def at_focus_rotate(self, caller, **kwargs):
        self.msg_char(caller, LEVER_ROTATE.strip())

    def at_apply(self, caller, action, target):
        self.room.score(2, "inserted lever in chest")
        self.msg_room(caller, LEVER_APPLY.strip())
        # move on!
        self.next_state()

    def at_read(self, caller):
        if self.check_flag("sooty"):
            self.msg_char(caller, LEVER_READ_SOOT.strip())
        else:
            self.room.score(2, "read cleaned lever")
            self.msg_char(caller, LEVER_READ_CLEAN.strip())

    def at_clean(self, caller, cleaner, txt=""):
        # called by cleaning agent
        if self.check_flag("sooty"):
            self.msg_char(caller, txt)
            self.msg_room(caller, LEVER_SOOT_TO_ROOM.strip(), True)
            self.unset_flag("sooty")
        else:
            self.msg_char(caller, "The lever is already clean enough.")


# ------------------------------------------------------------
# socks (cleaning)
# ------------------------------------------------------------

SOCKS_DESC = """
The socks are red and small enough to fit someone of the
Jester's short stature.
"""

SOCKS_DESC_SOOTY = """
The socks are sooty black now from using them to wipe off the lever.
"""

SOCKS_APPLY = """
The socks are drenched in soap, so using them to wipe off the soot from the
lever is easy. The Jester ends up with some really black socks but you don't
pity her one bit.
"""


class SocksCleanable(Socks):

    target_flag = "cleanable"

    def at_apply(self, caller, action, target):
        self.room.score(2, "clean lever with sock")
        target.at_clean(caller, self, txt=SOCKS_APPLY.strip())
        self.db.desc = SOCKS_DESC_SOOTY.strip()


# ------------------------------------------------------------
# windows (cleared)
# ------------------------------------------------------------

WINDOWS_DESC = """
The two windows let in a lot of light. They can't be opened more than a
finger's width due to the sturdy metalwork just outside the glass. Intervoven
into the *metalwork are climbing roses that further limit the view. Above each
window is a wooden bar that you briefly used for hanging your temporary
'curtains' earlier.

"""


# ------------------------------------------------------------
# state
# ------------------------------------------------------------

STATE_HINT_LVL1 = """
Something big fell into the *ashes. It looks like it could be inserted into something.

"""

STATE_HINT_LVL2 = """
Lie down on *floor and examine *bed to find the *chest and pull it out. Insert
*lever into *chest.
"""


STATE_HINT_LVL3 = """
~You ~eat a piece of pie to celebrate your progress so far. Useless? Sure. But
sometimes you just have to treat yourself.
"""

STATE_HINT_LVL4 = """
~You ~have another piece of pie. Nothing more is learned, but ~you ~feel a littler better.
"""


class State(BaseState):

    next_state = "state_008_open_chest"

    hints = [STATE_HINT_LVL1,
             STATE_HINT_LVL2,
             STATE_HINT_LVL3,
             STATE_HINT_LVL4]

    def character_enters(self, character):
        self.cinematic(GREETING.format(name=character.key),
                 target=character)

    @interactive
    def init(self):

        self.msg(STONE_PUSH_INTRO1.rstrip())
        yield(3)
        self.msg(STONE_PUSH_INTRO2.rstrip())

        lever = self.create_object(
            Lever, key="lever", aliases=["shaft"])
        lever.db.desc = LEVER_DESC.strip()
        socks = self.create_object(
            SocksCleanable, key="socks")
        socks.db.desc = SOCKS_DESC.strip()

        # replace fireplace since it looks different now
        fireplace = self.create_object(
            FireplaceEmpty, key="fireplace")
        fireplace.db.desc = FIREPLACE_DESC.strip()
        ashes = self.get_object("ashes")
        if ashes:
            ashes.delete()
        ashes = self.create_object(
            AshesUsable, key="ashes")
        ashes.db.desc = ASHES_DESC.strip()

        yield(3)

        self.room.msg_room(None, STONE_PUSH_INTRO3.rstrip())
        yield(4)

        vale = self.get_object("Vale")
        if vale:
            vale.delete()
        vale = self.create_object(
            StatueValeQuiet, key="Vale", aliases=["statue", "monkey"])
        vale.db.desc = VALE_DESC.strip()

        windows = self.get_object("windows")
        if windows:
            windows.db.desc = WINDOWS_DESC.strip()

        self.room.msg_room(None, STONE_PUSH_INTRO4.rstrip())

        self.room.db.desc = ROOM_DESC.strip()

    def clean(self):
        super().clean()
        self.room.progress(59)
