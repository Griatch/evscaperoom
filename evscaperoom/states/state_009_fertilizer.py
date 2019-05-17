"""
Time to make the super-fertilizer from our ingredients.

"""

from random import random
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

    When you get into the cabin, the *chest was just opened, revealing its
    secrets to the world ...

"""

INTRO1 = """
Over by the door, Vale claps its hands.
"""

# ------------------------------------------------------------
# chest (kept open)
# ------------------------------------------------------------

CHEST_DESC = """
The chest stands open and prop it up so it won't close again accidentally. It's
pretty small, most of its size was clearly taken up by the intricate locking
mechanism.

Inside it you can see a brass *monocular and a partly burnt *letter.

"""


class ChestOpen(objects.EvscaperoomObject):
    pass

# ------------------------------------------------------------
# looking glass
# ------------------------------------------------------------


LOOKINGGLASS_DESC = """
This is a bronze monocular - a 'looking glass' of the type used by sea captains.
It seems to have pretty strong lenses. Better not look at the sun!

"""

LOOKINGGLASS_APPLY = """
You see only a blur. Things in here is way too close.
"""

LOOKINGGLASS_APPLY2 = """
You could maybe direct light through the monocular to put this on fire, but
you doubt it'd burn very well.

"""

LOOKINGGLASS_APPLY_WINDOW = """
The leaves of a distant tree fills your vision. A bird jumps around on a branch, unaware
of your spying. Interesting, but not very useful right now.

However, as you hold up the tube to the window in the right angle you notice
that it causes a very focused spot of intense light around the
location of the fireplace.

"""

LOOKINGGLASS_BOOK = """
You consider burning the Jester's book with the Looking glass. But what if you
need something in there for a later puzzle? There must be something else of
similar dryness that you could burn!
"""

LOOKINGGLASS_BED = """
While the mattress might burn if it was packed with dry straw. But instead it's
packed with fresh grass from the meadow, no way that'll burn any time soon. The
whole thing is even a bit damp ... Guess now you know why! Clearly the Jester
didn't want you to torch her bed.
"""

LOOKINGGLASS_APPLY_TO_ROOM = """
~You ~focus the *monocular at {target}.
"""


LOOKINGGLASS_THINK = """
If you use the looking glass on something that is easily flammable you might be
able to direct enough sunlight onto it to put it on fire!
"""


class LookingGlass(objects.Usable):

    target_flag = "looking_glass_sun"

    def at_apply(self, caller, action, obj):
        self.msg_room(caller, LOOKINGGLASS_APPLY_TO_ROOM.format(target=obj.key))
        if obj.check_flag("burnable"):
            # actually burnable item
            self.room.score(2, "burn with monocular")
            obj.handle_burn(caller, self)
        elif obj.key == "book":
            self.room.score(1, "try to burn book")
            self.msg_char(caller, LOOKINGGLASS_BOOK.strip())
        elif obj.key == "bed":
            self.room.achievement(caller, "Fool planning", "Figured out why the bed is damp")
            self.msg_char(caller, LOOKINGGLASS_BED.strip())
        else:
            self.room.score(1, "used monocular with window")
            self.msg_char(caller, LOOKINGGLASS_APPLY_WINDOW.strip())

    def get_callsigns(self):
        txt = "Actions that make sense: *use on <thing> and *think"
        return [], txt

    def at_focus_think(self, caller, **kwargs):
        self.msg_char(caller, LOOKINGGLASS_THINK.strip())

    def at_cannot_apply(self, caller, action, obj):
        self.msg_room(caller, LOOKINGGLASS_APPLY_TO_ROOM.format(target=obj.key))
        if random() < 0.5:
            self.msg_char(caller, LOOKINGGLASS_APPLY)
        else:
            self.room.score(1, "Getting random insight from monocular")
            self.msg_char(caller, LOOKINGGLASS_APPLY2)


# ------------------------------------------------------------
# letter
# ------------------------------------------------------------

LETTER_DESC = """
This letter sits in a crumpled and partly burned envelope; this looks like
something that was never delivered.

On the front of the envelope it simply says:

        To Agda

"""

LETTER_READ = """
The letter is written in a compact and tight handwriting.

    My beloved Agda,

    I have written so many letters that I've then torn up. Know that I've
    always loved you in secret and that I never aimed to hurt you. But that
    doesn't change the fact that I am the reason you are the way you are today.

    You will know how happy I was when you confided in me. But after that kid
    got hurt, I just couldn't live with the secret. I laced the champion's pies
    with my potion. I am a coward, I could not think of any other way to stop
    him. How was I to know he'd lose his appetite that day of all days?

    He has been so cold to you since, but at least you are apart now. I did not
    know about your other circumstance until much later. But I understand why
    your parents had to do what they did in secret. This guilt too is on my
    shoulders, for I was the one that made you incapable of such a
    responsibility in the first place. You used to hit me out of sport, now you
    can't even raise your hand to defend yourself. It's maddening!

    I experiment with my hintberries daily to find a way to reverse your
    condition. Even if you won't love me, but continue to ridicule and mock me,
    I have no bigger wish than to see the old you return. Because then one day,
    maybe I'll forgive myself.

    Yours forever,
    Vale
"""


class Letter(objects.Readable):

    def at_read(self, caller):
        self.room.score(2, "read letter")
        self.msg_char(caller, LETTER_READ.strip())
        if not self.check_flag("read_already"):
            # reading the letter makes the plant mixable so
            # we can create the fertilizer
            plant = self.room.state.create_object(
                PlantMixable, key="plant")
            plant.db.desc = PLANT_DESC.strip()


# ------------------------------------------------------------
# potted plant (on table)
# ------------------------------------------------------------

PLANT_DESC = """
On the table, on the side nearest to the window, stands a potted plant - it's a
rose cutling, no more than a little green stem and a few leaves.
"""

PLANT_DIG_ROOM = """
~You digs around in the dirt of the *plant, to no avail.
"""

PLANT_DIG = """
Carefully you probe around in the small pot with your fingers, but even after
circling the cutling and fully probed the bottom of the pot you don't find
anything hidden in the dirt.

You shuffle the displaced dirt back into place around the fledging little plant.
"""

PLANT_FEEL_ROOM = """
~You ~prick a finger on *plant, letting a drop of blood fall into the dirt.
"""

PLANT_FEEL = """
Ouch! It may be small, but this thing already has thorns! You draw a drop of
blood and let it fall into the dirt.
"""

PLANT_MIX_RESET = """
The mix does not seem to work. ~you ~wipe off the top layer of soil from the
*plant and ~start again.
"""

PLANT_MIX_SUCCESS = """
As ~you ~drop {ingredient} into the soil of the *plant, the rose stickling
suddently starts to shift and writhe. ~You quickly ~back away.

"""


class PlantMixable(objects.Feelable, objects.Mixable):

    mixer_flag = "fertilizer_mixer"

    ingredient_recipe = [
        "childmaker",
        "ashes",
        "ashes",
        "ashes",
        "hintberries",
        "blood",
    ]

    def at_object_creation(self):
        super().at_object_creation()
        self.set_flag("blood")
        self.set_flag("fertilizer_mixer")

    def at_focus_dig(self, caller, **kwargs):
        self.msg_room(caller, PLANT_DIG_ROOM.strip(), True)
        self.msg_char(caller, PLANT_DIG.strip())
        # reset any mixture now
        self.db.ingredients = []

    def at_focus_feel(self, caller, **kwargs):
        # add ourselves!
        self.msg_room(caller, PLANT_FEEL_ROOM.strip(), True)
        self.handle_mix(caller, self, txt=PLANT_FEEL.strip())

    def at_mix(self, caller, ingredient, txt=None):
        self.msg_char(caller, txt)

    def at_mix_failure(self, caller, ingredient, **kwargs):
        self.msg_room(caller, PLANT_MIX_RESET.strip())

    @interactive
    def at_mix_success(self, caller, ingredient, **kwargs):
        self.room.score(2, "Made fertilizer")
        self.msg_room(caller, PLANT_MIX_SUCCESS.format(ingredient=ingredient.key).lstrip())
        yield(2)
        self.next_state()


# ------------------------------------------------------------
# state
# ------------------------------------------------------------

STATE_HINT_LVL1 = """
It's time to grow to the occation. The *locket that fell down into the *ashes
looks important.
"""

STATE_HINT_LVL2 = """
The *letter may be useful for figuring out how to open the *locket. Inside
you'll find the end of a recipe. See if you can find the beginning of it
somewhere.
"""

STATE_HINT_LVL3 = """
Say 'Agda' to the locket to open it. Read about the FERTILIZER in *book to get
the first part of the fertilizer recipe.  To make the fertilizer, put the
ingredients in the potted *plant. You need a drop of blood as the last
ingredient. Maybe if you pricked your finger?
"""

STATE_HINT_LVL4 = """
Use the following ingredients with *plant:
- *childmaker potion
- *ashes
- *ashes
- *ashes
- *pie (the hintberry pie)
Finally, examine and feel the potted *plant to prick yourself on its thorns and
get a drop of blood.

"""


class State(BaseState):

    next_state = "state_010_burn_firewood"

    hints = [STATE_HINT_LVL1,
             STATE_HINT_LVL2,
             STATE_HINT_LVL3,
             STATE_HINT_LVL4]

    def character_enters(self, character):
        self.cinematic(GREETING.format(name=character.key),
                       target=character)

    @interactive
    def init(self):

        # we don't need the lever anymore
        lever = self.get_object("lever")
        if lever:
            lever.delete()

        # chest needs no further interaction
        chest = self.create_object(
            ChestOpen, key="chest")
        chest.db.desc = CHEST_DESC.strip()
        lookingglass = self.create_object(
            LookingGlass, key="looking glass", aliases=["monocular", "lookingglass", "glass"])
        lookingglass.db.desc = LOOKINGGLASS_DESC.strip()
        letter = self.create_object(
            Letter, key="letter")
        letter.db.desc = LETTER_DESC.strip()

        yield(3)

        self.msg(INTRO1.rstrip())

    def clean(self):
        super().clean()
        self.room.progress(84)
