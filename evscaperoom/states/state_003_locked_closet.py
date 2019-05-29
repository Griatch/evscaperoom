"""
Listening to the monkey automaton to open the closet

"""

import random
from evennia import DefaultScript
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

    When you get into the cabin, The monkey-statue 'Vale' has just come alive
    and walked over to the door. But he doesn't open it but instead turns around,
    waves his long arms in the air and speaks ...
"""

ROOM_DESC = """
The |rJester's cabin|n is actually just a small single room with a *door.
Ample light enters from two *windows on each side. The underside of the sloping
roof is exposed (as are the *rafters holding them up), making the place taller
and feel more spacious than it is.

On the wall opposite the door is a small stone *fireplace, lined to the left
and right side by a tall *closet and an area acting as a *kitchen
respectively. There is also a carver *chair standing around.

Just to the right of the door is the Jester's messy *bed and to the right is
a long, empty-looking *table.

On the floor by the door is a plate on which sits a nicely smelling hintberry *pie.
*Vale has moved to stand just in front of the door, chattering to itself and
waving its arms above its head, excitedly.

"""


# -----------------------------------------------------------
# Vale (by the door, talking)
# ------------------------------------------------------------

STATUE_DESC = """
In front of the door stands a strange little moving statue depicting a strange
animal with a vaguely human-like face but long arms, ears and a tail. It's
dressed in a red jacket and a conical hat. Since hobbling here on its short
legs it has started waving its hands above its head, chattering excitedly to
itself in its strange, squeaky voice.
"""

STATUE_ARMS = """
The arms are made of wood and each joint is made out of wire. But this doesn't
seem to stop the thing from moving around as if it was alive. The finger joints
seem particularly flexible.
"""

STATUE_FACE = """
Vale's painted monkey face is made of wood. It is too big for the body on which
it sits, like a caricature of the animal. The black glass making out the
things' gleaming eyes seem to have been fitted in the face's empty eye sockets
after the face itself was carved.

"""

STATUE_DOOR = """
Vale chatters excitedly.

  |w"I can see daylight through the keyhole! You just need to find the key.
  Lemme help you out ...

    ... I saw my Mistress put the key in the cauldron. Just get it from there
    and we'll be out into the sunshine in no time!"|n

"""

STATUE_WIND_TURNED = """
Vale, over by the door, seems to sniff the air.

    |w"Huh. I think the wind just turned.|n

"""

STATUE_RHYME = """
Vale waggles his tail and weaves his hands in the arms as he recites:

   |w"The Magus, the Smith and the Baker were once like glue
     - but the Baker had bad pie and then they were only two.

    The Magus and the Smith were once loving someone
     - but the Smith's heart grew cold and then there was only one.

    The Magus had a secret greater than he claimed
     - but he drank too much of his wine, ashamed

    And then only the Monkey remained."|n
"""

# four numbers are needed, count how many people are in each verse -> 3211. From
# the last verse it's suggested the Monkey was actually always there, so
# add one to the first three verses -> 4321


STATUE_RHYME_NOT_NEEDED = """
Vale looks at you. You swear the wooden face looks amused.

    |w"You already figured this out, you know. But if you are so keen to hear my
    Mistress' lovely prose again, who am to refuse?"|n
"""


STATUE_THINK = """
This silly little children's rhyme sounds just like something the Jester would
make up on the spot. This must be a hint to something else though. Maybe some
sort of code?
"""

STATUE_THINK_NOT_NEEDED = """
You already opened the closet by figuring out the rhyme. Surely Vale has served
its purpose now ... or?
"""

STATUE_HINTBERRY_PIE = """
From over by the door, Vale says:

    |wIf you get stuck, you can always try eating a hintberry |cpie|w, you know ..."|n
"""

STATUE_RANDOM_CHATTER0 = """
Over by the door, Vale says aloud:

    |w"The key to this door is over in the cauldron you know. Just get
     it out of there so we can get us some sun!|n
"""

STATUE_RANDOM_CHATTER1 = """
Over by the door, Vale chatters to itself:

    |w"I wonder whose face this is, really?|n"
"""

STATUE_RANDOM_CHATTER2 = """
Vale chatters to itself over by the door:

    |w"My mistress cannot make herself take anything seriously ...!"|n

Vale quiets, mid-sentence.
"""

STATUE_RANDOM_CHATTER3 = """
Suddenly Vale continues a sentence out of the blue:

    |w" ... not even if she wants to! Funny, but also a little sad, eh?"|n
"""

STATUE_RANDOM_CHATTER4 = """
Vale mutters over by the door:

    |w"Nice day outside - I can see the sunlight through the keyhole!
    Just need to find a key and then we'll be out of here!"|n
"""

STATUE_RANDOM_CHATTER5 = """
Over by the door, the monkey-thing hums contentedly to itself.
"""

STATUE_RANDOM_CHATTER6 = """
Vale talks to itself over by the door:

    |w"My mistress had strict instructions for how I was to look, but the
    blacksmith already had my face ready. Giving it to me made his heart
    lighter, I think ...|n

The thing quiets, as if pondering.
"""

STATUE_RANDOM_CHATTER7 = """
Vale continues after a long pause:

    |w"... Hey! I wonder if that was her plan all along."|n
"""

STATUE_RANDOM_CHATTER8 = """
Vale mumbles over by the door:

    |w"You should not be too miffed with my Mistress for locking you in here
    you know. She just has her .... own way of getting things done."|n
"""

STATUE_RANDOM_CHATTER9 = """
Vale mutters to itself over by the door, its words lost to the world.

"""

STATUE_RANDOM_CHATTERS = [
    STATUE_RANDOM_CHATTER0,
    STATUE_RANDOM_CHATTER1,
    STATUE_RANDOM_CHATTER2,
    STATUE_RANDOM_CHATTER3,
    STATUE_RANDOM_CHATTER4,
    STATUE_RANDOM_CHATTER5,
    STATUE_RANDOM_CHATTER6,
    STATUE_RANDOM_CHATTER7,
    STATUE_RANDOM_CHATTER8,
    STATUE_RANDOM_CHATTER9,
]


class StatueValeChatter(DefaultScript):
    """
    Makes the statue chatter at random intervals.

    """
    def at_script_creation(self):
        self.key = "evscaperoom_vale_chatter"
        self.start_delay = True
        self.interval = 5 * 60
        self.persistent = True

        self.db.chatter_index = 0

    def at_repeat(self):

        if self.obj.room.state.name.endswith("state_005_wind_turns"):
            # if wind changed, we want that every time
            self.obj.room.msg_room(None, STATUE_WIND_TURNED)

        elif self.obj.room.state.name.endswith("state_008_open_chest"):
            # remind the player about the hintberry pie
            self.obj.room.msg_room(None, STATUE_HINTBERRY_PIE.strip())

        elif random.random() < 0.3:
            # most of the time Vale says nothing on repeat
            ind = self.db.chatter_index
            if ind > 9:
                # start randomize after all have been heard once
                chatter = random.choice(STATUE_RANDOM_CHATTERS).strip()
            else:
                # step through each statement in turn
                chatter = STATUE_RANDOM_CHATTERS[ind].strip()
                self.db.chatter_index += 1
            self.obj.room.msg_room(None, chatter)


class StatueVale(objects.EvscaperoomObject):

    def at_object_creation(self):
        super().at_object_creation()
        self.scripts.add(StatueValeChatter)
        self.db.rhyme_needed = True

    def at_focus_arms(self, caller, **kwargs):
        self.room.score(1, "consider Vale's arms")
        self.msg_char(caller, STATUE_ARMS.strip())

    def at_focus_face(self, caller, **kwargs):
        self.room.score(1, "examine Vale's face")
        self.msg_char(caller, STATUE_FACE.strip())

    def at_focus_door(self, caller, **kwargs):
        self.msg_char(caller, STATUE_DOOR.strip())

    def at_focus_think(self, caller, **kwargs):
        if self.db.rhyme_needed:
            self.msg_char(caller, STATUE_THINK.strip())
        else:
            self.msg_char(caller, STATUE_THINK_NOT_NEEDED.strip())

    def at_focus_rhyme(self, caller, **kwargs):
        if self.db.rhyme_needed:
            self.msg_char(caller, STATUE_RHYME.strip())
        else:
            self.msg_char(caller, (STATUE_RHYME_NOT_NEEDED.lstrip() + STATUE_RHYME.rstrip()))

    def get_cmd_signatures(self):
        txt = ("You might look at Vale's {callsigns}. You can also ask "
               "to hear the *rhyme again, ask why he stands by the *door "
               "or *think more on this.")
        return ["arms", "face"], txt


# ------------------------------------------------------------
# closet
# ------------------------------------------------------------

CLOSET_DESC = """
The 'closet corner' of the cabin is dominated by the namesake closet. It's a
large antique piece of furniture, with double doors of lacquered hardwood.

The thing has a padlock with four spinning wheels on it.
"""

CLOSET_PADLOCK = """
The padlock is a metal construct with four wheels of numbers 0-9 on it. It
looks like you need to rotate these to set a given number.
"""

CLOSET_CODE_CORRECT = """
4,3,2,1 - the number of people mentioned in each of Vale's verses, including
the 'Monkey' that turned out to always be around as well.

The padlock clicks and the metal bar unlocks. But still - the code was just
4321? Seriously? What a stupid code. Typical of the Jester!

The doors to the closet swing open.
"""


class ClosetClosed(objects.CodeInput):
    # The closet can now be opened
    infinitely_locked = False
    code = "4321"
    code_hint = "four digits, 0 to 9"
    read_flag = None

    def at_focus_padlock(self, caller, **kwargs):
        self.msg_char(caller, CLOSET_PADLOCK.strip())

    @interactive
    def at_code_correct(self, caller, code_tried, **kwargs):
        self.msg_room(caller, "~You ~enter a code in the *padlock.")
        self.room.score(2, "unlock the closet")
        self.msg_room(caller, CLOSET_CODE_CORRECT)
        yield(2)
        self.next_state()


# -----------------------------------------------------------
# State
# ------------------------------------------------------------

STATE_HINT_LVL1 = """
Vale's rhyme tells a story involving a number of people. Maybe you need a code for something?
"""

STATE_HINT_LVL2 = """
The *closet is locked with a lock that requires four digits. The rhyme seems to have four stanzas.
"""

STATE_HINT_LVL3 = """
If you read between the lines, how many people are *actually* in each stanza of the rhyme?
"""

STATE_HINT_LVL4 = """
Enter the code '4321' into the closet lock. The number of people mentioned in each stanza is
3211, but the last line implies that the Monkey was always there without being mentioned
explicitly, so add +1 to the first three values.
"""


class State(BaseState):

    next_state = "state_004_childmaker_potion"

    hints = [STATE_HINT_LVL1,
             STATE_HINT_LVL2,
             STATE_HINT_LVL3,
             STATE_HINT_LVL4]

    def character_enters(self, character):
        self.cinematic(GREETING.format(name=character.key),
                       target=character)

    def init(self):
        # room desc changed since Vale moved
        self.room.db.desc = ROOM_DESC.strip()

        # replace statue with one that speaks
        statue = self.get_object("statue")
        if statue:
            statue.delete()
        statue = self.create_object(
            StatueVale, key="Vale", aliases=['statue', 'monkey'])
        statue.db.desc = STATUE_DESC.strip()
        closet = self.create_object(
            ClosetClosed, key="closet")
        closet.db.desc = CLOSET_DESC.strip()

        self.room.msg_room(None, STATUE_RHYME.strip())

    def clear(self):
        super().clear()
        self.room.progress(25)
