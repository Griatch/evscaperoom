"""
This state is about opening the chest by combining all we've learned
so far.

"""

from evennia.utils import interactive
from ..state import BaseState
from .. import objects
from .state_007_chest_lever import Lever


GREETING = """
    This is the situation, {name}:

    The |rJester|n wants to win your village's yearly |wpie-eating contest|n.
    As it turns out, you are one of her most dangerous opponents.

    Today, the day of the contest, she invited you to her small cabin for a
    'strategy chat'. But she tricked you and now you are |wlocked in|n! If you
    don't get out before the contest starts she'll get to eat all those pies on
    her own and surely win!

    When you get into the cabin, a *lever was just inserted into the mystical
    *chest under the bed. Now, how to open it ...?

"""


# ------------------------------------------------------------
# ashes (looks different without lever)
# ------------------------------------------------------------

ASHES_DESC = """
The stone slab making out the base of the fireplace is covered in
ashes. Now they are all cold though.

Among the ashes lies a small *locket that must have fallen down when turning
the damper. There is a large empty space where the *lever used to be.
"""

# ------------------------------------------------------------
# lever (mounted in chest)
# ------------------------------------------------------------

LEVER_DESC = """
The metal lever is mounted in the locking mechanism of the *chest. Turning
it is not possible, but you can wiggle it up, down, left and right. Every time
you do there is a tiny 'click' from inside.

At the end of the lever facing you are clear compass markings for the
directions you can move the lever:

             (up)
            |rN|n
 (left) |yW|n       |gE|n (right)
            |cS|n
            (down)

"""

LEVER_ROTATE = """
Where it sits in the chest mechanism, the lever can not be rotated but only
moved from side to side. Maybe it can be turned later, once something in
the lock has changed.
"""

LEVER_ROTATE_SUCCESS = """
~You ~turn the lever and ~find that it rotates easily now. A satisfying 'thunk'
comes from the lock.
"""

LEVER_MOVE = """
~You ~move the lever {direction} ({compass_direction}). There is a soft 'click'
from inside the mechanism when doing so.
"""

LEVER_RESET = """
There is a rattle of gears and clicks from inside the chest. Nothing more
happens but you think the mechanism just reset itself. Maybe ~you did something
wrong.
"""

LEVER_SUCCEED = """
As ~you move the lever {direction}, there is a slightly louder click-sound from
inside the lid. That sounds promising!
"""


class LeverMovable(Lever):
    """
    This can still be cleaned.
    The 'Movable' parent does not fit so we make our own here
    """

    # unlocking sequence
    correct_sequence = [
        'right', 'left', 'up', 'right',
        'left', 'down', 'down', 'right',
        'up', 'left']

    direction_map = {"up": "N",
                     "down": "S",
                     "left": "W",
                     "right": "E"}

    def at_object_creation(self):
        super().at_object_creation()
        self.db.sequence = []

    def get_cmd_signatures(self):
        txt = "Actions: *move <direction>, *rotate, *read"
        return [], txt

    def check_sequence(self):
        "check so sequence is correct, returning True/False"
        return (len(self.db.sequence) == len(self.correct_sequence) and
                all(direction == self.correct_sequence[idir]
                    for idir, direction in enumerate(self.db.sequence)))

    def at_focus_move(self, caller, **kwargs):
        args = kwargs.get("args").strip().lower()
        if not args or args not in ("up", "down", "left", "right"):
            self.msg_char(caller, "You can only move the lever 'left', 'right', 'up' or 'down'.")
            return

        self.room.score(1, f"moved lever {args}")

        self.db.sequence.append(args)
        self.msg_room(caller, LEVER_MOVE.format(
            direction=args, compass_direction=self.direction_map[args]).strip())

        if len(self.db.sequence) >= len(self.correct_sequence):
            if self.check_sequence():
                self.msg_room(caller, LEVER_SUCCEED.format(direction=args).strip())
            else:
                self.room.log(f"chest open failed: "
                              f"Tried {' + '.join([dr for dr in self.db.sequence])}")
                self.db.sequence = []
                self.msg_room(caller, LEVER_RESET.strip())

    def at_focus_rotate(self, caller, **kwargs):
        "Rotate to lock/unlock the chest, assuming code is right."
        chest = self.room.state.get_object("chest")
        if chest and self.check_sequence():
            if chest.check_flag("unlocked"):
                chest.unset_flag("unlocked")
            else:
                self.room.score(4, "unlocked chest")
                chest.set_flag("unlocked")
                self.msg_room(caller, LEVER_ROTATE_SUCCESS.strip())
        else:
            self.msg_char(caller, LEVER_ROTATE.strip())


# ------------------------------------------------------------
# chest (under bed, now openable)
# ------------------------------------------------------------

CHEST_DESC = """
The chest that was under the bed has all the markings of a miniature sailor's
chest, with an ornate lid. The *lever fit perfectly in the cross-shaped hole
in the chest's center.

"""

CHEST_LOCKED = """
You tug at the lid but the thing stays stubbornly locked.
"""

CHEST_OPEN = """
You tug at the lid and the chest swings open! You did it!
"""


class ChestOpenable(objects.Openable):

    # this is unlocked by lever
    unlock_flag = "unlocked"
    start_open = False

    def at_locked(self, caller):
        self.msg_char(caller, CHEST_LOCKED.strip())

    def at_open(self, caller):
        self.msg_char(caller, CHEST_OPEN.strip())
        self.next_state()


# ------------------------------------------------------------
# state
# ------------------------------------------------------------

STATE_HINT_LVL1 = """
That lever is pretty sooty. If you clean it off you might learn something, but
you need something to wipe it with.
"""

STATE_HINT_LVL2 = """
Use *socks to clean the lever. Then look up THE LONG WALK in the *book.
"""

STATE_HINT_LVL3 = """
Turn over the *rug to find a map of the village. THE LONG WALK describes a path
between the houses of the different people. You need to know more about all
those people mentioned, particularly where they live.
"""

STATE_HINT_LVL4 = """
You don't actually know which direction on the map is North. Maybe you can find
some more info about the village landmarks somewhere to clue you in.
"""

STATE_HINT_LVL5 = """
There are many hints as to the true orientation of the map. Here are some:

The *poster says that the (straight) road goes 'north-east from the village,
past the forest'.

The *book (reading about HINTBERRIES) mentions that the shrubs with the hintberries is
on the west bank of a river that runs north-west.

Looking out the windows shows the Jester's cabin being by the forest.
Looking at the *roses, mentions that these roses are found on 'this side of the river'.
The *book (reading about ROSES) says that these roses are on the east bank of the river.

The houses are in fact forming a cross, with the house at the top-right of the
map being the northernmost one.
"""

STATE_HINT_LVL6 = """
By reading the *book, looking out the *windows and at the map on the *rug
you can infer that:

- The Jester's cabin is to the East (by the forest)
- The Magus (Master Bloch) lives to the South (across the river from the
  Jester, among the shrubs).
- The Baker (Mrs Bullington) lives to the West (across the road from the Magus,
  opposite side of the village from the Jester).
- The Blacksmith (Angus) lives in the remaining house, to the North.

"""

STATE_HINT_LVL7 = """
Each line of the rhyme corresponds to the compass direction of the house of the
person the Jester is located at for that line.

"""

STATE_HINT_LVL8 = """
Move lever up for North, right for East etc. To open the chest, move the lever
as follows:

 |wright|n, |wleft|n, |wup|n, |wright|n,
 |wleft|n, |wdown|n, |wdown|n, |wright|n,
 |wup|n and then finally |wleft|n.

When you hear a louder, promising click, |wrotate|n the lever to unlock the chest.

"""


class State(BaseState):

    next_state = "state_009_fertilizer"

    hints = [STATE_HINT_LVL1,
             STATE_HINT_LVL2,
             STATE_HINT_LVL3,
             STATE_HINT_LVL4,
             STATE_HINT_LVL5,
             STATE_HINT_LVL6,
             STATE_HINT_LVL7,
             STATE_HINT_LVL8]

    def character_enters(self, character):
        self.cinematic(GREETING.format(name=character.key),
                 target=character)

    def init(self):
        # ashes changed look now that lever is gone
        ashes = self.get_object("ashes")
        if ashes:
            ashes.db.desc = ASHES_DESC.strip()

        # replace lever with movable version
        lever = self.create_object(
            LeverMovable, key="lever", aliases=['shaft'])
        lever.db.desc = LEVER_DESC.strip()

        # replace chest with openable version
        chest = self.create_object(
            ChestOpenable, key="chest")
        chest.db.desc = CHEST_DESC.strip()

    def clean(self):
        super().clean()
        self.room.progress(76)
