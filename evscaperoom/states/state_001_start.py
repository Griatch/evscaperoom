"""
Starting state of the room.

The Jester's cabin has the following rough layout:

      <--- SHADOW-SIDE        SUN-SIDE --->
 __________________________________________________
|    closet         fireplace         kitchen      |
|                                                  |
|                                  chair           |
windows                                       windows             scarecrow
|                                                  | roses
|    monkey-statue                                 |
|                                                  |
|                   rug                            |
|                                                  |
|    table                           bed           |
|                                                  |
|             pie                                  |
|______________________ door ______________________|



"""
from evennia.utils import interactive, justify, wrap
from .. import objects
from ..state import BaseState
from ..utils import add_msg_borders

# ------------------------------------------------------------
# initial greeting (called from menu)
# ------------------------------------------------------------

GREETING = """
    This is the situation, {name}:

    The |rJester|n wants to win your village's yearly |wpie-eating contest|n.
    As it turns out, you are one of her most dangerous opponents.

    Today, the day of the contest, she invited you to her small cabin for a
    'strategy chat'. But she tricked you and now you are |wlocked in|n! If you
    don't get out before the contest starts she'll get to eat all those pies on
    her own and surely win!

    This is a matter of pride. She always does stuff like this. You can't just
    break out of here with force, that would mean she has bested you. No, being
    the trickster that she is, you are sure she has left you some way to get
    out that she can lord over you if you fail.

    |wEscape the Jester's cabin|n in some clever way and beat that damned
    Jester at her own game!

    (enter 'help' for help to play)
"""

# ------------------------------------------------------------
# main room desc
# ------------------------------------------------------------

ROOM_DESC = """
The |rJester's cabin|n is actually just a small single room with a *door.
Ample light enters from two *windows on each side. The underside of the sloping
roof is exposed (as are the *rafters holding them up), making the place taller
and feel more spacious than it is.

On the wall opposite the door is a small stone *fireplace, lined to the left
and right side by a tall *closet and an area acting as a *kitchen
respectively. There is also a carver *chair and a strange looking *statue.

Just to the right of the door is the jester's messy *bed and to the left is
a long, empty-looking *table.

On the *floor by the door is a plate with an inviting *pie on it.
"""


# ------------------------------------------------------------
# main door
# ------------------------------------------------------------

CABINDOOR_DESC = """
The main door of the Jester's cabin is gaintly painted in red. Its top is
rounded and the door is not very big. But it's sturdy, made from planks taken
in the woods surrounding the cabin.

It's a sunny day outside and tempting light shines in through the key hole.
"""

CABINDOOR_OPEN_FIRST_TIME = """
You try to open the door by pushing and pulling. It does not budge. Frustrated
you pound on it to no avail.
Finally you peek through the empty key-hole to see if you can see something out
there that can help ...
"""

CABINDOOR_JESTER_TEASE = """
Suddenly a green-grey eye appears on the other side of the keyhole!
Through the hole you hear the |rJester|n giggling:

    |r"Hi there! You didn't think it'd be |mthat|r easy did you, {name}? Besides, I'm
    sure the village fair is really dull. It's like I'm doin' you a favor,
    yessiree! There are so many things to learn.
    Really, you have |mnothing|r to complain about. My cabin is really
    comfortable and I even |mbaked|r for you, you know! Have fun and see you
    after I win the pie-eating contest! Tada!"|n

Before you can reply, the tease is gone. Her giggle hangs in the air only a
moment longer than her words.
"""

CABINDOOR_OPEN = """
You try the door again, but no pushing or pulling or nudging can make it budge.

Light shines in through the keyhole but no Jester appears to tease you this
time.
"""

CABINDOOR_READ = """
There appears to be some sort of marks scratched into the door's red paint with
some sharp implement. After squinting a little, they form letters, but they
don't make any sense:

                 E L A V G N I D E E F Y B T R A T S
"""

CABINDOOR_THINK = """
Damn that little crazy fool! What has she come up with this time?
The key to this door must be around here somewhere.
"""
# START BY FEEDING VALE (Vale is the monkey)

CABINDOOR_CLOSE = """
You try to make the door more closed than it already is.

(... but in case it was not clear - you should really aim to -open- the door!)
"""


class CabinDoor(objects.Readable, objects.Openable):
    "The main cabin door"

    unlock_flag = "unlocked"
    start_open = False

    def at_object_creation(self):
        super().at_object_creation()
        # we allow the mirror object to be used on the door so
        # as to read the text backwards.
        self.set_flag("can_use_mirror")
        self.set_flag("cabin_door")

    @interactive
    def at_locked(self, caller):
        flag = "already_tried_to_open_cabin_door"
        if not self.check_character_flag(caller, flag):
            # first time the Jester appears and teases
            self.msg_char(caller, CABINDOOR_OPEN_FIRST_TIME.strip())
            yield(5)
            self.msg_char(caller, CABINDOOR_JESTER_TEASE.format(name=caller.key).rstrip())
            self.set_character_flag(caller, flag)
            self.room.score(1, "got teased by the jester")
        else:
            # rest of the time she does not show up
            self.msg_char(caller, CABINDOOR_OPEN)

    def at_focus_think(self, caller, **kwargs):
        self.msg_char(caller, CABINDOOR_THINK.strip())

    def at_already_closed(self, caller):
        self.room.score(1, "made front door more closed.")
        self.msg_char(caller, CABINDOOR_CLOSE.strip())

    def at_read(self, caller):
        self.room.score(1, "read door scribbles")
        self.msg_char(caller, CABINDOOR_READ.lstrip())

    def get_cmd_signatures(self):
        txt = ("You can attempt to *open|n/*close|n the door or try to *read|n the markings on it. "
               "You can also *think|n about your next move.")
        return [], txt


# ------------------------------------------------------------
# plate with pies
# ------------------------------------------------------------

HINTBERRY_PLATE_DESC = """
Next to the *door - directly on the *floor, so you almost stumble over it - is
a metal serving plate with a pie on it. The pie is a nice-smelling hintberry
pie cut into slices. There is a note on the plate.
"""

HINTBERRY_PLATE_NOTE = """
The note is written in the Jester's scrawly hand writing. It says:

    "Because I'm the nicest jester within thirty steps, I've baked for you! If
    you get stuck, just take a piece of my delicious hintberry pie! Mine is a
    LOT tastier than the pies at the pie-eating contest anyway. I heard Mrs
    Bullington ran out of apples and had to use iron filings this year ..."

(You can eat a piece of |chintberry pie|n to get a clue when you get stuck ...
but every bite surely must taste of bitter defeat! And if you have too many,
how are you ever going to defeat the Jester in the pie-eating contest, even if
you do get out in time ...?)

"""

HINTBERRY_PLATE_EAT = """
A total of {num} hintberry pie slices have been eaten so far.

|wDo you want to get a clue by eating a slice?|n Yes/[No]?"
"""

HINTBERRY_PLATE_THINK = """
Hintberries are |cblue-green|n and you know they grow right across the river
from here. Everyone knows they are not only very filling but are also said to
help gain magical insight.

The local Magus guards them berries jealously (malicious tongues say he just
wants them for making wine though).

When you think about it, the Jester must have had some really early mornings to
dodge the cranky old magus on his property to get enough berries to make a
whole pie!
"""

HINTBERRY_PLATE_APPLY = """
~You ~grab some hintberry pie and ~add it to the mix.
"""

HINTBERRY_PLATE_CANNOT_APPLY = """
What are you going to do, throw it across the room? Better just eat it.
"""


class HintberryPlate(objects.Edible, objects.Readable, objects.Usable):
    "The plate with pies"

    read_flag = None
    one_consume_only = False
    # we allow this to mixed into the fertilizer at the end
    target_flag = "fertilizer_mixer"

    def at_object_creation(self):
        super().at_object_creation()
        self.set_flag("hintberries")

    def at_read(self, caller):
        self.msg_char(caller, HINTBERRY_PLATE_NOTE.strip())

    @interactive
    def at_consume(self, caller, action):
        """
        Access the help system for this state
        """
        pies = self.room.db.stats.get("hints_used", 0)
        self.msg_room(caller, "~You ~consider having a slice of |chintberry pie|n.")
        answer = yield(HINTBERRY_PLATE_EAT.format(num=pies).strip())
        if answer.upper() in ("YES", "Y"):
            hint = self.room.state.get_hint()
            if hint is None:
                self.msg_char(caller, wrap(
                     "You feel kinda sick of hintberry pie for the moment. You have "
                     "a feeling you won't learn any more from eating a slice right now."))
            else:
                self.room.achievement(caller, "Glutton", "Ate a hintberry pie")
                maxwidth = max(len(line) for line in hint.split("\n"))
                sep = "|c" + "~" * maxwidth + "|n"
                hint = f"{sep}\n{hint}\n{sep}"

                self.msg_room(caller, "~You ~eat a slice of |chintberry pie|n ...")
                hint = f"The wisdom of the |chinterry pie|n speaks through ~you:\n{hint}"
                self.msg_room(caller, hint)
        else:
            self.msg_char(caller, "You put the slice of hintberry pie down for now.")

    def at_focus_think(self, caller, **kwargs):
        self.room.score(1, "thought about hintberry pie")
        self.msg_char(caller, HINTBERRY_PLATE_THINK.strip())

    def at_apply(self, caller, action, obj):
        self.room.score(1, "used hintberry pie for fertilizer")
        obj.handle_mix(caller, self, txt=HINTBERRY_PLATE_APPLY.strip())

    def at_cannot_apply(self, caller, action, obj):
        self.msg_char(caller, HINTBERRY_PLATE_CANNOT_APPLY.strip())

    def get_cmd_signatures(self):
        txt = "You can *eat the pie. But also *read the note, *use it or *think about it."
        return [], txt

# ------------------------------------------------------------
# windows
# ------------------------------------------------------------


WINDOWS_DESC = """
At first glance, the two windows seem possible avenues of escape. But even
though they let in a lot of light, that light enters through a beautiful but
sturdy *metalwork just outside the glass. Interwoven into the metalwork are
climbing roses that further limit the view. Above each window is a wooden bar
that might have held curtains at one point, but none can be seen anymore.

"""

WINDOWS_NOT_OPEN = """
You can actually open each of the the windows a little, to let in a whiff of
fresh air.  But the *metalworks on the outside effectively block them from
opening more than a finger-width. Maybe the roses have also grown in a bit too
making the windows even harder to operate.

You close the windows again.
"""

WINDOWS_OUTSIDE = """
On the 'shadow-side', the cabin seems to face a green wall of leaves and bushes.
The jester's cabin is after all pretty remote, where it perches just at the
edge of the forest. On the opposite side', sunlight shines over the jester's
little garden. You can see several rose bushes, some rows of sad-looking
vegetables and what looks like a pumpkin patch.

There is no-one around except a *scarecrow with a decidedly weird look.
"""

WINDOWS_LISTEN = """
You listen at the small opening you can make in the window, but all you hear
are the chirps of birds, the rustling of leaves and maybe a faint hiss from
the nearby river.
"""

WINDOWS_SMELL = """
You sniff at the small window opening. It smells vaguely of roses, but mostly
of wind, grass and the forest just behind the cabin. The smell of freedom!
"""

WINDOWS_ROSES = """
The climbing roses outside each of the *windows are pink. Several of them have
opened up in full bloom, but there are also a lot of smaller buds. You can't
really reach them to smell properly but you suspect that they smell like, well,
roses.

You are reminded of the roses growing on the waterbank, just on this side of
the river. You wonder if the Jester originally got them from there.
"""


class Windows(objects.Openable, objects.Listenable, objects.Smellable):

    start_open = False

    def at_object_creation(self):
        super().at_object_creation()
        self.set_flag("looking_glass_sun")

    def at_locked(self, caller):
        self.msg_char(caller, WINDOWS_NOT_OPEN.strip())

    def at_focus_outside(self, caller, **kwargs):
        self.msg_char(caller, WINDOWS_OUTSIDE.strip())

    def at_focus_listen(self, caller, **kwargs):
        self.room.score(1, "listened freedom")
        self.msg_char(caller, WINDOWS_LISTEN.strip())

    def at_focus_smell(self, caller, **kwargs):
        self.room.score(1, "smelled freedom")
        self.msg_char(caller, WINDOWS_SMELL.strip())

    def at_focus_roses(self, caller, **kwargs):
        self.msg_char(caller, WINDOWS_ROSES.strip())

    def get_cmd_signatures(self):
        txt = ("These actions seem to make sense: {callsigns}. "
               "You can also look *outside and smell the *roses.")
        sigs = ["open", "close", "listen", "smell"]
        return sigs, txt


# ------------------------------------------------------------
# metalworks (outside the windows)
# ------------------------------------------------------------

METALWORKS_DESC = """
The metalworks decorating the outside of the Jester's windows are simple but
sturdy. They effectively lock you inside the cabin.

"""

METALWORKS_LOCKED = """
You try to nudge the metalworks but you can't get any leverage through
the small crack in the window. They don't budge and you wonder if they
rusted shut or was maybe never meant to open.
"""


class Metalworks(objects.Openable):

    start_open = False

    def at_locked(self, caller):
        self.room.score(1, "tried to open metalworks")
        self.msg_char(caller, METALWORKS_LOCKED.strip())


# ------------------------------------------------------------
# scarecrow (outside)
# ------------------------------------------------------------

SCARECROW_DESC = """
You can see the scarecrow through the sunny-side window. It sits in the
Jester's little garden and feels way too big for the sorry little plantation
she's got going there.

The scarecrow is made of crossed planks and dressed in a blue rag that acts
like a sail and causes it to turn in the wind. Its head (which is a sack
stuffed with hay) has been crudely painted with big eyelashed eyes and a large
smile. This is clearly meant to look like the Jester herself.

The contraption is holding a large sign.
"""

SCARECROW_SIGN_NOT_VISIBLE = """
The scarecrow holds what looks like a sign on on a stick in one "hand". But
unfortunately the wind keeps the scarecrow rotated in such a way that the
sign is not possible to read.

"""

SCARECROW_SIGN_VISIBLE = """
The scarecrow holds a sign on a stick in one "hand". The wind has turned
to rotate the whole contraption - and now the sign is facing you so you can
clearly read that it says:

    COVER THE WINDOWS

"""


class Scarecrow(objects.Readable):

    read_flag = None  # always able to read, we use state instead

    def at_read(self, caller):
        if self.room.state.name.endswith("state_005_wind_turns"):
            # only show the sign during the state in which the wind has turned
            self.room.score(3, "saw the scarecrow's sign")
            self.msg_char(caller, SCARECROW_SIGN_VISIBLE.strip())
        else:
            self.room.score(1, "saw the back of the scarecrow")
            self.msg_char(caller, SCARECROW_SIGN_NOT_VISIBLE.strip())


# ------------------------------------------------------------
# rafters
# ------------------------------------------------------------

RAFTERS_DESC = """
The cabin's sloping roof is held up by thick criss-crossing wooden rafters,
several of which reaches across the room above your head. They are great
for hanging and storing things just within reach.

Over the rafter closest to the *door, just over the *bed, the Jester has hung
what looks like her *laundry. On the same rafter - but across the room over the
*table - hangs a series of decorative *chimes, gently swinging to and fro.

By the fireplace, you spot what looks like a old *saddle on a higher rafter.

"""

RAFTERS_FEEL = """
The rafters are made of coarsly cut but solid oak. Tapping one randomly gives
off a very solid 'thump' sound.

"""

# This desc shows if the watcher stands on something (bed, chair) and
# can thus see more

RAFTERS_STAND_DESC = """
The cabin's sloping roof is held up by thick criss-crossing wooden rafters,
several of which reaches across the room just above your head. They are great
for hanging and storing things just within reach. You can see that there's
a lot of grime and dust on top of them - the Jester is really a bit of a slob.

Over the rafter closest to the door, just over the bed, the Jester has hung
what looks like her laundry. On the same rafter - but across the room over the
*table * hangs a series of decorative *chimes, gently swinging to and fro. From
your higher vantage point you notice that just above the chimes, a small
glittering *coin has been tucked into a crack in the rafter.

By the fireplace, you spot what looks like a old *saddle on a higher rafter.
It looks like something is written on top of the saddle.

"""


class Rafters(objects.Feelable):

    def at_focus_feel(self, caller, **kwargs):
        self.msg_char(caller, RAFTERS_FEEL.strip())

    def return_appearance(self, caller, **kwargs):
        # we will show different results depending on
        # if the player stands on something or not
        obj, pos = self.get_position(caller)
        if pos == 'climb':
            if not self.check_flag("found_coin"):
                self.room.state.create_object(HiddenCoin, key="coin")
                self.set_flag("found_coin")
            self.room.score(1, "looked at rafters from on high")
            kwargs['desc'] = RAFTERS_STAND_DESC.strip()
            return super().return_appearance(caller, **kwargs)
        else:
            kwargs['desc'] = RAFTERS_DESC.strip()
            return super().return_appearance(caller, **kwargs)


# ------------------------------------------------------------
# chimes (red herring)
# ------------------------------------------------------------

CHIMES_DESC = """
On the *rafters, above the *table, some chimes are swinging gently to and fro.
The hanging pieces are decorated with what looks like little red fishes. They
could be herrings, but you are not entirely sure.
"""


class Chimes(objects.EvscaperoomObject):

    def get_cmd_signatures(self):
        txt = "They are pretty to look at, but you can't think of anything else to do with them."
        return [], txt

# ------------------------------------------------------------
# saddle (in the rafters)
# ------------------------------------------------------------

SADDLE_DESC = """
The saddle hangs on one of the higher rafters above the fireplace. It's an old
thing and looks way too large for the Jester to use.
"""

SADDLE_DESC_STAND = """
The saddle hangs on one of the higher rafters, but as you have gotten up higher
you see more of it. By the saddle's gullet, the letters "AW" are stiched into
the leather with thick thread.

The saddle looks way too large for the Jester. Could 'AW' be the initials of
the real owner of the saddle?
"""
# Agda (not Angus) Warrington

SADDLE_FEEL = """
You cannot reach the saddle to feel it. It hangs over a high rafter above the
fireplace.
"""

SADDLE_FEEL_STAND = """
Having gotten up higher, you are able to feel the surface of the saddle. It is
old but has clearly seen a lot of use in its days. Up close you see a lot of
scratches and brown splotches across the leather, including a long gash that
almost looks like someone struck with a blade across the surface. Was this
saddle used in some sort of battle or fight?
"""


class Saddle(objects.Feelable):

    must_stand_on_flag = "reach_saddle"

    def at_focus_feel(self, caller, **kwargs):
        obj, position = self.get_position(caller)
        if position == 'climb':
            if obj.check_flag(self.must_stand_on_flag):
                self.msg_char(caller, SADDLE_FEEL_STAND.strip())
            else:
                self.msg_char(caller, SADDLE_FEEL.strip())
            return
        self.msg_char(caller, SADDLE_FEEL.strip())

    def return_appearance(self, caller, **kwargs):
        obj, position = self.get_position(caller)
        if position == 'climb':
            if obj.check_flag(self.must_stand_on_flag):
                self.room.score(1, "read text on saddle")
                return super().return_appearance(
                    caller, desc=SADDLE_DESC_STAND.strip(), **kwargs)
            else:
                return super().return_appearance(caller, desc=SADDLE_DESC.strip(), **kwargs)
            return
        return super().return_appearance(caller, desc=SADDLE_DESC.strip(), **kwargs)


# ------------------------------------------------------------
# coin (hidden in the rafters)
# ------------------------------------------------------------

# This does not exist until someone has looked at the
# rafters while standing on something
HIDDEN_COIN_DESC = """
On closer inspection this looks more like a small copper disk than a coin. It
has been polished to a shine.
"""

HIDDEN_COIN_ROTATED = """
As you turn the coin (or disk) over where it sits, you notice the other side
has an engraving on it. It looks like a very hairy man with a tail and a hat.
"""

HIDDEN_COIN_NOT_CHAIR = """
You need to stand on something close enough to the coin to reach it.
"""

HIDDEN_COIN_NOT_STANDING = """
You can't reach the coin up on the *rafter from there. You need to get closer.
"""

HIDDEN_COIN_INSERT_AUTOMATON = """
~You ~take the coin from its resting place in the rafters and
get back down. ~You ~head over to the strange *statue and ~kneel down,
inserting the coin between its lips ...
"""


class HiddenCoin(objects.Insertable, objects.Rotatable):

    target_flag = "monkey_automaton"
    # this flag needs to be set on thhe thing we stand on
    must_stand_on_flag = "reach_coin"

    @interactive
    def at_apply(self, caller, action, target):
        obj, position = self.get_position(caller)
        if position == 'climb':
            if not obj.check_flag(self.must_stand_on_flag):
                self.msg_char(caller, HIDDEN_COIN_NOT_STANDING.strip())
            else:
                # the class has already checked target_flag here
                self.room.score(2, "inserted coin in automaton")
                self.msg_room(caller, HIDDEN_COIN_INSERT_AUTOMATON.strip())
                yield(3)
                # trigger next state!
                self.next_state()

    def get_cmd_signatures(self):
        txt = ("You can *turn the coin over and also insert it "
               "into something with *insert in <object>.")
        return [], txt

    def _can_reach(self, caller):
        obj, position = self.get_position(caller)
        return position == 'climb' and obj.check_flag(self.must_stand_on_flag)

    def at_rotate(self, caller):
        if self._can_reach(caller):
            self.room.score(1, "seeing the back of the coin")
            self.msg_char(caller, HIDDEN_COIN_ROTATED.strip())
        else:
            self.msg_char(caller, HIDDEN_COIN_NOT_STANDING.strip())

    def return_appearance(self, caller, **kwargs):
        if self._can_reach(caller):
            return super().return_appearance(
                caller, desc=HIDDEN_COIN_DESC.strip(), **kwargs)
        else:
            return HIDDEN_COIN_NOT_STANDING.strip()


LAUNDRY_DESC = """
On a wire hung in an arc across the *bed hangs two pairs of *socks and a large
pink bath *towel.
"""

LAUNDRY_FEEL = """
Most of it feels like normal cloth, but the *socks are wet to the feel, as if
the garments just came out of the washing bin and was only wringed out in a
hurry.
"""


class Laundry(objects.Feelable):

    def at_focus_feel(self, caller, **kwargs):
        self.msg_char(caller, LAUNDRY_FEEL.strip())


# ------------------------------------------------------------
# socks
# ------------------------------------------------------------

SOCKS_DESC = """
The socks are red and small enough to fit the Jester's short stature.
"""

SOCKS_FEEL = """
When you pinch them, you notice that the socks are wet and soapy, like if they
went into a wash that was never finished. They drip water onto the bed and
soapy bubbles form where your fingers were.
"""

SOCKS_SMELL = """
Reluctantly you lean in and smell the socks. They smell quite strongly of soap,
which is at least better than any other smell they could have had!
"""


class Socks(objects.Feelable, objects.Smellable, objects.Usable):
    # socks are possible to use for the childmaker potion
    target_flag = "alchemy_mixer"

    def at_object_creation(self):
        # these can also be used as an ingredient for the childmaker potion
        super().at_object_creation()
        self.set_flag("childmaker_ingredient_childlike")

    def at_apply(self, caller, action, target):
        self.room.achievement(caller, "Payback", "Sacrifice the Jester's sock")
        self.room.score(2, "mix childlike ingredient")
        target.handle_mix(
            caller, self,
            txt_ingredient="some fluff off the Jester's socks",
            color="purple",
            smell="soap",
            extra=("You feel that sacrificing some fluff off her sock is but a small part of the \n"
                   "payback the Jester sorely deserves at this point."))

    def at_cannot_apply(self, caller, action, target):
        self.msg_char(caller, "That won't do. Best to not wave those socks around too much.")

    def at_focus_feel(self, caller, **kwargs):
        self.msg_char(caller, SOCKS_FEEL.strip())

    def at_focus_smell(self, caller, **kwargs):
        self.msg_char(caller, SOCKS_SMELL.strip())


# ------------------------------------------------------------
# bathtowel
# ------------------------------------------------------------

BATHTOWEL_DESC = """
This is a large pink bath towel. It looks pretty heavily used but the cloth is
thick and is of good quality. In the corner of it you find the initials "AB".
"""
# (AB - Agda Bullington)

BATHTOWEL_FEEL = """
This bath towel is made of thick, good quality cloth. You wonder who "AB" is.
"""

BATHTOWEL_CANNOT_APPLY = """
No need to dry that off.
"""


class Bathtowel(objects.Feelable, objects.Usable):

    target_flag = "window_coverable"  # this won't be set on windows until later

    def at_focus_feel(self, caller, **kwargs):
        self.msg_char(caller, BATHTOWEL_FEEL.strip())

    def at_apply(self, caller, action, obj):
        if hasattr(obj, "check_flag") and obj.check_flag("alchemy_mixer"):
            obj.handle_reset(caller)
        else:
            obj.at_cover(caller, self)

    def at_cannot_apply(self, caller, action, obj):
        self.msg_char(caller, BATHTOWEL_CANNOT_APPLY.strip())

    def get_cmd_signatures(self):
        txt = "You can *feel and also *use with <target>."
        return [], txt


# ------------------------------------------------------------
# fireplace
# ------------------------------------------------------------

FIREPLACE_DESC = """
A small stone fireplace sits in the middle of the wall opposite the *door. On
the chimney hangs a small oil *painting of a man. Hanging over the hearth is a
black *cauldron. The piles of *ashes below are cold.
"""

FIREPLACE_CLIMB_CLOSED_DAMPER = """
You look up into the chimney. It's pitch black up there but you can tell that
there is no way you could fit to climb up that narrow passage.
"""

FIREPLACE_CLIMB_OPEN_DAMPER = """
You look up into the chimney. With the grille open you can see the bright sky
high up there! The chimney seems to be very uneven though; there is a black
shape, like a pipe or beam, blocking your view somewhere above. But even with
the light it's quite clear you are too big to climb up the chimney.
"""


class Fireplace(objects.Climbable):

    def at_focus_climb(self, caller, **kwargs):
        damper = self.room.state.get_object("damper knob")
        damper_open = damper and damper.check_flag("open")
        if damper_open:
            self.msg_char(caller, FIREPLACE_CLIMB_OPEN_DAMPER.strip())
        else:
            self.msg_char(caller, FIREPLACE_CLIMB_CLOSED_DAMPER.strip())


# ------------------------------------------------------------
# cauldron
# ------------------------------------------------------------

CAULDRON_DESC = """
The cauldron hangs on a hook over the cold hearth. On closer inspection you
find that the iron surface is covered with rim frost and a faint haze is rising
from it. It is very cold to the touch and when you look inside you realize the
inside is a solid block of ice!

Ice in the middle of summer! How did the Jester do |wthat|n?)
"""

CAULDRON_THINK = """
Is that a key frozen below? You think it may be...!

Old Master Bloch may not have a clue about many things, but he knows his
cantrips. Thinking about it, you'd not be surprised if he had some magics to
cool that hintberry liqueur he likes so much. Maybe the Jester got something
from him to make the contents of the cauldron freeze?

She really planned ahead when locking you in here, didn't she?
"""

CAULDRON_FEEL = """
You feel with your hand over the hard ice surface inside the cauldron. It looks
like frozen water. You can vaguely make out an uneven shape embedded in the ice.

Is that a key down there? Yes, you are pretty sure that it is!
"""

CAULDRON_BREAK = """
You tap the surface of the ice with your hand. There is no getting through
that. If it thaws at all, it would take all day and you don't have the time!
And since the cauldron is curved you can also not pour the whole icy mass out
so you can get more leverage.

You are pretty sure you are supposed to find some way to melt that ice. But
how?
"""


class Cauldron(objects.Feelable):

    def at_focus_feel(self, caller, **kwargs):
        self.msg_char(caller, CAULDRON_FEEL.strip())

    def at_focus_think(self, caller, **kwargs):
        self.room.score(1, "thinking on cauldron")
        self.msg_char(caller, CAULDRON_THINK.strip())

    def at_focus_break(self, caller, **kwargs):
        self.msg_char(caller, CAULDRON_BREAK.strip())


# ------------------------------------------------------------
# painting
# ------------------------------------------------------------

PAINTING_DESC = """
Above the *fireplace hangs a round picture frame. The oil painting in the frame
depicts a man with a brown leather apron. His face is scrumpled into a deep
frown and he's holding a hammer raised as if he's about to hit the viewer.

"""

PAINTING_THINK = """
You are pretty sure his nose is not that big, but this is clearly a caricature
of the village blacksmith, Mr Warwick. If he saw this you are sure he'd get
really grumpy, in that stoic way of his. The thought makes you chuckle, despite
yourself.

While clearly made by an amateur, it's not half bad. Did the Jester paint this?
"""

PAINTING_TURN = """
Probingly you lift the painting to see if there is something written on its
back side. There isn't, but you do realize that the painting is hanging from
the knob controlling the fireplace's *damper.

"""


class Painting(objects.Rotatable):

    def at_focus_think(self, caller, **kwargs):
        self.room.score(1, "think about picture")
        self.msg_char(caller, PAINTING_THINK.strip())

    def at_rotate(self, caller):
        self.room.score(2, "rotate picture")
        if not self.check_flag("found_damper"):
            self.room.state.create_object(
                Damper, key="damper knob", aliases=["damper", "fireplace damper", "knob"])
            self.set_flag("found_damper")
        self.msg_char(caller, PAINTING_TURN.strip())

    def get_cmd_signatures(self):
        txt = "You can *turn the painting over to look at its back, or *think about it."
        return [], txt


DAMPER_DESC = """
The *fireplace's damper is controlled by a knob on which a *painting is hanging.
You can however still move the knob without disturbing the picture frame.

"""

DAMPER_OPEN_FIRST = """
~You ~turn the *damper knob of the fireplace. There is a rasping sound as the
damper moves inside the chimney. As ~you ~turn the knob to the open position
there is a soft 'thud' sound from among the *ashes in the fireplace.
"""

DAMPER_OPEN = """
~You ~turn the chimney *damper back to the open position with a rasping sound.
"""

DAMPER_CLOSE = """
~You ~turn the chimney *damper back to the closed position.
"""


# ------------------------------------------------------------
# damper (created when picture is turned)
# ------------------------------------------------------------

class Damper(objects.Openable):

    unlock_flag = None  # starts unlocked
    start_open = False
    open_flag = "open"

    def at_object_creation(self):
        super().at_object_creation()
        self.db.desc = DAMPER_DESC.strip()

    def at_open(self, caller):
        if not self.check_flag("opened_once"):
            self.room.score(2, "opening damper first time")
            self.msg_room(caller, DAMPER_OPEN_FIRST.strip())
            self.set_flag("opened_once")
            locket = self.room.state.create_object(
                Locket, key="locket")
            locket.db.desc = LOCKET_DESC_CLOSED.strip()
            self.room.set_flag("opened_damper_once")
        else:
            self.msg_room(caller, DAMPER_OPEN.strip())

    def at_close(self, caller):
        self.msg_room(caller, DAMPER_CLOSE.strip())


# ------------------------------------------------------------
# ashes
# ------------------------------------------------------------

ASHES_DESC = """
The stone slab making out the base of the *fireplace is covered in ashes. Now
they are all cold though.
"""

ASHES_DESC_LOCKET = """
The stone slab making out the base of the *fireplace is covered in ashes. Now
they are all cold though. Among the ashes lies a small *locket that must have
fallen down when turning the *damper.
"""

ASHES_SMELL = """
The familiar smell of wood ash. The cabin lies just at the edge of the woods
and the firewood most likely came from there.
"""


class Ashes(objects.Smellable):

    def return_appearance(self, caller, **kwargs):
        if self.room.check_flag("opened_damper_once"):
            return super().return_appearance(caller, desc=ASHES_DESC_LOCKET.strip(), **kwargs)
        else:
            return super().return_appearance(caller, desc=ASHES_DESC.strip(), **kwargs)

    def at_focus_smell(self, caller, **kwargs):
        self.msg_char(caller, ASHES_SMELL.strip())


# ------------------------------------------------------------
# locket (falls into ashes when damper is turned)
#  this is technically openable but unless you cheat you
#  should not know the name of the owner yet.
# ------------------------------------------------------------

LOCKET_DESC_CLOSED = """
This is a closed steel locket. It lacks a chain but is otherwise the kind of
thing people have around their necks with a picture of their loved one inside.
Below the engraving is a row of thin letters spelling out:

    "I speak your name to see you, beloved."

"""

# this is the second part of the FERTILIZER recipe found in the book in the closet
LOCKET_DESC_OPEN = """
The locket holds a miniature painting of a young woman in jacket and riding
pants. He long black hair is put up in a knot. She frowns and stares intently at the
viewer with grey-green eyes captured perfectly by the artist.

A torn off piece of paper is folded up in the locket. It starts in the middle
of a sentence and appears to be the end of some sort of recipe:

    "... pinches of cremated plants
     1 handful of hintberries
     1 drop of blood

     Mix directly into soil, exactly in this order.
"""

LOCKET_THINK_CLOSED = """
Beloved?

Could this locket be a gift to someone from their loved one? Or made for a
loved one? If so, who is the owner whose name should be said? Maybe the Jester
got this thing off someone in the village?

Those damn long fingers of hers! You bet half the stuff in here are things
the Jester has 'borrowed' because she found it hilarious at the spur of the
moment.
"""

LOCKET_THINK_OPEN = """
So this is Agda then. You wonder who painted this, it looks like they spent many
a late night with it. The artist has depicted her with loving detail, but chose
to give her an expression that looks cruel and harsh.

Now - let's see, what recipe is this and where would you find the rest of it?
"""

LOCKET_LOCKED = """
No matter how much you try, you cannot open the tiny locket.
It's sealed almost as if by magic.
"""

LOCKET_CODE_INCORRECT = """
~You ~tell the locket '{code}' but it doesn't appear to care.
"""

LOCKET_CODE_CORRECT = """
As ~you ~speak the name 'Agda', the locket clicks open.
"""


class Locket(objects.Openable, objects.CodeInput):
    """
    The locket just contains info, it does not trigger anything
    else; so it can be opened at any time.
    """

    code = "Agda"
    case_insensitive = True

    def at_object_creation(self):
        super().at_object_creation()

    def get_cmd_signatures(self):
        txt = ("You could attempt to *open/*close it, as well "
               "as *speak <name> to the locket. You "
               "could also try to *think about it.")
        return [], txt

    def at_focus_think(self, caller, **kwargs):
        if self.check_flag("open"):
            self.msg_char(caller, LOCKET_THINK_OPEN.strip())
        else:
            self.msg_char(caller, LOCKET_THINK_CLOSED.strip())

    def at_focus_speak(self, caller, **kwargs):
        super().at_focus_code(caller, **kwargs)

    def at_locked(self, caller):
        self.msg_char(caller, LOCKET_LOCKED.strip())

    def at_no_code(self, caller):
        self.msg_char(caller, "It looks like it wants you to say a name.")

    def at_code_incorrect(self, caller, code_tried):
        self.room.log(f"{caller.key} tried the name '{code_tried}' to open locket")
        if code_tried.lower() in ("vale", "angus"):
            self.room.achievement(caller, "Awkward", "Named the wrong 'beloved' to the locket")
        self.msg_room(caller, LOCKET_CODE_INCORRECT.format(code=code_tried).strip())

    def at_code_correct(self, caller, code_tried):
        self.room.score(2, "unlocked Locket with code")
        self.msg_room(caller, LOCKET_CODE_CORRECT.strip())
        # we unlock and pop the locket open at the same time
        self.set_flag("unlocked")
        self.set_flag("open")

    def return_appearance(self, looker, **kwargs):
        if self.check_flag("open"):
            return super().return_appearance(looker, desc=LOCKET_DESC_OPEN.strip())
        else:
            return super().return_appearance(looker, desc=LOCKET_DESC_CLOSED.strip())


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

CLOSET_PADLOCK_INCORRECT = """
Trying random numbers won't get you anywhere. While you stand here fiddling,
the pie-eating contest draws nearer! Hopefully you'll be able to make a more
informed guess later.
"""


class Closet(objects.CodeInput, objects.Readable):
    # This version of the padlock cannot be opened yet.
    infinitely_locked = True
    read_flag = None

    code_hint = "four digits, 0 to 9"

    def at_focus_padlock(self, caller, **kwargs):
        self.msg_char(caller, CLOSET_PADLOCK.strip())

    def at_code_incorrect(self, caller, code_tried):
        self.msg_char(caller, CLOSET_PADLOCK_INCORRECT.strip())


# ------------------------------------------------------------
# kitchen
# ------------------------------------------------------------

KITCHEN_DESC = """
To the right of the *fireplace and next to the sun-side *window, is a deep
wooden shelf meant for preparing and eating food.
Right now there are no kitchen utensils here though - the bench is empty except
for five little glass bottles and an animal skull.

"""

ANIMAL_SKULL = """
This looks like the skull of a small dog. Apart from the novelty value, you
don't see why the Jester would have it, you don't think she ever had a dog. In
fact, you suspect that she's a little scared of dogs.
"""

KITCHEN_BOTTLES = """
On the kitchen shelf are five corked bottles in dark glass. A large label is attached
to each bottle-neck, written in the Jester's sprawly handwriting.

    First: |bA STEALTHY LAXATIVE|n
    Second: |rSOMETHING RANCID|n
    Third: |mMY FAVORITE PERFUME|n
    Fourth: |yEAT YELLOW SNOW, IT COULD BE BEER|n
    Fifth: |RDOUCHY BEET ROOT|n

|c[The bottles can be examined as *bottle1|c, *bottle2|c etc]|n
"""


class Kitchen(objects.EvscaperoomObject):

    def at_object_creation(self):
        super()

    def at_focus_bottles(self, caller, **kwargs):
        self.msg_char(caller, KITCHEN_BOTTLES.strip())
        bottle1 = self.room.state.create_object(
            Bottle, key="bottle one", aliases=["bottle1", "bottle 1"],
            attributes=[
                ("desc", BOTTLE_DESC1.strip()),
                ("txt_smell", "roses"),
                ("txt_ingredient", "a few drops from the first bottle"),
                ("txt_color", "pink")])
        bottle1.set_flag("childmaker_ingredient_roses")
        bottle2 = self.room.state.create_object(
            Bottle, key="bottle two", aliases=["bottle2", "bottle 2"],
            attributes=[
                ("desc", BOTTLE_DESC2.strip()),
                ("txt_smell", "earthy delight"),
                ("txt_ingredient", "a few drops from the second bottle"),
                ("txt_color", "purple")])
        bottle2.set_flag("childmaker_ingredient_arrogance")
        bottle3 = self.room.state.create_object(
            Bottle, key="bottle three", aliases=["bottle3", "bottle 3"],
            attributes=[
                ("desc", BOTTLE_DESC3.strip()),
                ("txt_smell", "Father Death having gasses"),
                ("txt_ingredient", "a very small drop from the third bottle"),
                ("txt_color", "brown-red")])
        bottle3.set_flag("childmaker_ingredient_rancid")
        bottle4 = self.room.state.create_object(
            Bottle, key="bottle four", aliases=["bottle4", "bottle 4"],
            attributes=[
                ("desc", BOTTLE_DESC4.strip()),
                ("txt_smell", "clean air"),
                ("txt_ingredient", "a few drops from the fourth bottle"),
                ("txt_color", "transparent")])
        bottle4.set_flag("childmaker_ingredient_stealth")
        bottle5 = self.room.state.create_object(
            Bottle, key="bottle five", aliases=["bottle5", "bottle 5"],
            attributes=[
                ("desc", BOTTLE_DESC5.strip()),
                ("txt_smell", "loo"),
                ("txt_ingredient", "a drop from the fifth bottle"),
                ("txt_color", "yellow")])
        bottle5.set_flag("childmaker_ingredient_urine")

    def at_focus_skull(self, caller, **kwargs):
        self.msg_char(caller, ANIMAL_SKULL.strip())

    def get_cmd_signatures(self):
        txt = ("You can inspect the *bottles and look at the *skull.\n"
               "|c[that is, just enter 'bottles' or 'skull' here]|n")
        return [], txt


# ------------------------------------------------------------
# bottle (five different types, created in kitchen)
# ------------------------------------------------------------

BOTTLE_DESC1 = """
The label of the first bottle reads

    |bA STEALTHY LAXATIVE|n

"""

BOTTLE_DESC2 = """
The second bottle is labeled

    |rSOMETHING RANCID|n

"""

BOTTLE_DESC3 = """
These bottles all look the same, but this third one is labeled

    |mMY FAVORITE PERFUME|n

A little red heart is drawn the corner of the label.
"""

BOTTLE_DESC4 = """
The forth bottle is labeled

    |yEAT YELLOW SNOW, IT COULD BE BEER|n

"""

BOTTLE_DESC5 = """
The final, fifth bottle is labeled

    |RDOUCHY BEET ROOT|n

Huh ...?
"""

# the smells does not match the labels. Mapping:
# 1->4, 2->3, 3->1, 4->5, 5->2

BOTTLE_SMELL_ONE = """
You carefully uncork the first bottle and takes a whiff. You are pleasantly
suprised that the first bottle smells nicely of roses.
"""

BOTTLE_SMELL_TWO = """
You uncork the second bottle. The contents has a rather pleasant, thick and earthy smell.
"""

BOTTLE_SMELL_THREE = """
Ew! The third bottle nearly makes you puke! Let's not smell that anymore!
"""

BOTTLE_SMELL_FOUR = """
You sniff and sniff at the fourth bottle, but you smell nothing at all. Maybe
this one is only water?
"""

BOTTLE_SMELL_FIVE = """
You open the fifth bottle but immediately close it again, nose wrinkled. It's a
very familiar smell, but this liquid belongs in the outhouse, not in a bottle!
"""

BOTTLE_CANNOT_APPLY = """
You don't want to just spread this stuff around randomly, who knows what this
stuff does!
"""


class Bottle(objects.Smellable, objects.Usable):

    target_flag = "alchemy_mixer"
    # must set flag on creation

    def at_focus_smell(self, caller, **kwargs):
        # set the .db.smell attr on creation
        self.msg_char(caller, self.db.txt_smell.strip())

    def at_apply(self, caller, action, target):
        self.room.score(2, f"apply_bottle_{self.key}")
        target.handle_mix(
            caller, self,
            txt_ingredient=self.db.txt_ingredient,
            color=self.db.txt_color,
            smell=self.db.txt_smell,
            extra=self.db.txt_extra or "")

    def at_cannot_apply(self, caller, action, target):
        self.msg_char(caller, BOTTLE_CANNOT_APPLY)

    def get_cmd_signatures(self):
        txt = "Suitable actions would be *smell and *use with <target>."
        return [], txt


# ------------------------------------------------------------
# chair
# ------------------------------------------------------------

CHAIR_DESC = """
This is a curved and comfortable carver chair. It's painted a bright and merry
red. It looks pretty sturdy.
"""

CHAIR_MOVE_DOOR = """
You move the chair next to the *door. The red of the chair makes it nigh
invisible against the surface of the door - the two are the exact same hue of
red.
"""

CHAIR_MOVE_CLOSET = """
You move the chair over to the *closet. The chair looks small next to the large
piece of furniture.
"""

CHAIR_MOVE_FIREPLACE = """
You move the chair over to the *fireplace. Must be nice to sit in front of a
roaring fire on cold winter nights.
"""

CHAIR_MOVE_KITCHEN = """
You move the chair back to the *kitchen area, where it started out.
"""


class Chair(objects.Movable, objects.Sittable, objects.Kneelable, objects.Climbable):

    move_positions = {"door": "at_move_door",
                      "closet": "at_move_closet",
                      "fireplace": "at_move_fireplace",
                      "kitchen": "at_move_kitchen"}
    start_position = "kitchen"

    def get_cmd_signatures(self):
        """
        We embed the chair's position here too
        """
        txt = ("The following actions makes sense with the chair: {callsigns}. "
               f"The chair currently stands near the {self.db.position}.")
        return ["sit", "kneel", "climb", "move to door",
                "move to closet", "move to fireplace",
                "move to kitchen"], txt

    def at_cannot_move(self, caller):
        self.msg_char(caller, "A little crammed to move the chair there.")

    def _step_off(self, caller):
        "step of chair before moving it"
        obj, pos = self.get_position(caller)
        if pos:
            self.set_position(caller, None)
            self.msg_room(caller, "~You ~step off the *chair.")

    def at_move_door(self, caller):
        self._step_off(caller)
        self.room.score(2, "move chair to door")
        self.msg_char(caller, CHAIR_MOVE_DOOR.strip())
        self.set_flag("reach_coin")
        self.unset_flag("reach_saddle")
        self.unset_flag("reach_stone")

    def at_move_closet(self, caller):
        self._step_off(caller)
        self.room.score(1, "move chair to closet")
        self.msg_char(caller, CHAIR_MOVE_CLOSET.strip())
        self.unset_flag("reach_coin")
        self.unset_flag("reach_stone")
        self.unset_flag("reach_saddle")

    def at_move_fireplace(self, caller):
        self._step_off(caller)
        self.room.score(2, "move chair to fireplace")
        self.msg_char(caller, CHAIR_MOVE_FIREPLACE.strip())
        self.unset_flag("reach_coin")
        self.set_flag("reach_saddle")
        self.set_flag("reach_stone")

    def at_move_kitchen(self, caller):
        self._step_off(caller)
        self.room.score(1, "move chair to kitchen")
        self.msg_char(caller, CHAIR_MOVE_KITCHEN.strip())
        self.unset_flag("reach_coin")
        self.unset_flag("reach_saddle")
        self.unset_flag("reach_stone")


# ------------------------------------------------------------
# monkey statue
# ------------------------------------------------------------

STATUE_DESC = """
By the shadow-side *window, not far from the *closet, stands a curious monkey
statue, reaching you to your waist. It is carved mostly from wood but the
joints, tail and head are linked with wire so they can be moved. It's like a
huge version of one of the children's toys Mr Warwick makes.

The wooden toy monkey is dressed in a red jacket and a conical hat.
"""

STATUE_TAIL = """
The tail is made of thick strands of rope, mixed with metal wire to make it
hold its position.
"""

STATUE_FACE = """
The face of the monkey is carved in wood and looks too big for its shoulders,
The ears are large and round, painted brown to suggest fur. The face is almost
human-like except for the heavy brows and protruding lips and chin. The ears
are large and round, clearly painted brown as if to suggest them being covered
in fur.

You notice that the thick wooden-carved lips are slightly separated.  It looks
like you could fit something like a coin in there. The face has two holes where
black glass orbs have been inserted as eyes. They stare unseeingly across the
room.
"""

STATUE_ARMS = """
The arms of the statue-monkey are long and reaches to the floor. The hands have
fine wiring so the fingers can be put in different positions. But the fingers
are much too long to be human.
"""

STATUE_CLOTHES = """
The statue is dressed in what looks like small but real clothes; it has a red
vest strapped over its barrel-like chest and a cute little red cone is attached
to the top of its strange head.
"""

STATUE_FEEL = """
The statue is warm to the touch. The sun must have heated it.
"""


class Statue(objects.Feelable):

    def at_object_creation(self):
        super().at_object_creation()
        # this is the lock-flag checked by the coin,
        # for the coin to be 'insertable'
        # between the statue's lips.
        self.set_flag("monkey_automaton")

    def at_focus_feel(self, caller, **kwargs):
        self.msg_char(caller, STATUE_FEEL.strip())

    def at_focus_tail(self, caller, **kwargs):
        self.msg_char(caller, STATUE_TAIL.strip())

    def at_focus_face(self, caller, **kwargs):
        self.msg_char(caller, STATUE_FACE.strip())

    def at_focus_arms(self, caller, **kwargs):
        self.msg_char(caller, STATUE_ARMS.strip())

    def at_focus_clothes(self, caller, **kwargs):
        self.msg_char(caller, STATUE_CLOTHES.strip())

    def get_cmd_signatures(self):

        txt = ("You can *feel the statue's surface, but also look at its "
               "*tail, *arms, *face and *clothes.")
        return [], txt


# ------------------------------------------------------------
# bed
# ------------------------------------------------------------

BED_DESC = """
The Jester's bed is unmade inside its rickety wooden frame. The sheets are
linen, crumpled into a pile along the wall as if the Jester just jumped up and
left it behind. A pillow is mashed into the corner in the same fashion.
"""

BED_LIE = """
You probingly lie down on the Jester's bed. It's too short for you, your feet
stick out over the end of the bed. The mattress is packed with meadow-grass
which makes it smell nicely but is also a bit damp now that you think about it.

The bed creaks but is otherwise reasonably comfortable, especially the
pillow. You notice some *hairs left behind on the pillow from its previous
occupant.
"""

# smell when lying down on bed
BED_SMELL_LIE = """
As you lie flat on top of the bed, you smell freshly cut grass but also a hint
of roses from the pillow. Do Jesters smell of roses? You're not surprised by
anything at this point.
"""

# smell when not lying down on bed
BED_SMELL_NO_LIE = """
You sniff the air but don't smell anything in particular.
"""

BED_SIT = """
You sit at the edge of the bed. It creaks under your weight. You notice some
dark strands of *hair on the Jester's pillow. The mattress feels freshly
stuffed with meadow-grass.
"""

BED_KNEEL = """
You kneel down on top of the bed and gets the Jester's *socks in your face.
They hang above the bed along with a bath *towel. They are wet and you shy
away, rubbing your face. A pair of wet socks are NOT what you want to have on
your nose!
"""

BED_UNDER = """
The bed is too low to look under from this position. You need to get down on
the *floor before you can look under the bed.

    |C(hey, that's a free hint right there, you'll need to eat a slice of
       hintberry *pie |Cfor those henceforth!)|n
"""

# visible once you lie down on the floor
BED_UNDER_LYING = """
Where you lie on the floor you peek in under the bed. Under it, shoved far back,
you spot what looks like a small *chest.
"""

BED_UNDER_NOT_LYING = """
Where you {position} on the floor you can almost look in under the bed. But you
are not low enough.
"""


class Bed(objects.Sittable, objects.Liable, objects.Kneelable, objects.Smellable):

    def at_object_creation(self):
        super().at_object_creation()
        self.set_flag("looking_glass_sun")  # needed much later

    def at_unfocus(self, caller):
        # when unfocusing the bed, get out of it.
        self.set_position(caller, None)
        self.msg_char(caller, "You can't see well enough from the bed, so you get "
                 "back on your feet.")

    def at_position(self, caller, position):
        if position == "lie":
            self.room.score(2, "lay down on bed")
            self.msg_char(caller, BED_LIE.strip())
            self.msg_room(caller, "~You ~lie down on the *bed.", True)
            if not self.room.state.get_object("hairs"):
                self.room.state.create_object(
                    Hairs, key="hairs", aliases=["hair"])
        elif position == "sit":
            self.room.score(1, "sit down on bed")
            self.msg_char(caller, BED_SIT.strip())
            self.msg_room(caller, "~You ~sit down on the edge of the *bed.", True)
            if not self.room.state.get_object("hairs"):
                self.room.state.create_object(
                    Hairs, key="hairs", aliases=["hair"])
        elif position == "kneel":
            self.room.achievement(caller, "Foot fetish", "Made close contact with some wet socks")
            self.msg_room(caller, "~You ~kneel on top of the *bed.", True)
            self.msg_char(caller, BED_KNEEL.strip())

    def at_focus_smell(self, caller, **kwargs):
        obj, position = self.get_position(caller)
        if obj == self and position == "lie":
            self.msg_char(caller, BED_SMELL_LIE.strip())
        else:
            self.msg_char(caller, BED_SMELL_NO_LIE.strip())

    def at_focus_under(self, caller, **kwargs):
        obj, position = self.get_position(caller)
        if obj and position:
            if obj.check_flag("floor"):
                if position == 'lie':
                    # if we lie on the 'floor'-tagged object we  can see the chest.
                    if not self.check_flag("saw_chest_once"):
                        # first time we see the chest. Create it.
                        self.room.score(2, "found chest under bed")
                        self.room.state.create_object(
                            Chest, key="chest under the bed", aliases=["chest"])
                    self.msg_char(caller, BED_UNDER_LYING.strip())
                else:
                    self.msg_char(caller, BED_UNDER_NOT_LYING.format(position=position).strip())
        else:
            self.msg_char(caller, BED_UNDER.strip())

    def get_cmd_signatures(self):
        txt = ("It looks like you can {callsigns} on the bed. You can "
               "also *smell or check *under it.")
        sigs = ["sit", "lie", "kneel"]
        return sigs, txt


# ------------------------------------------------------------
# hairs (on pillow, created when lying/sitting in bed)
# ------------------------------------------------------------

HAIR_DESC = """
There are some black strands of hair left behind on the Jester's pillow.
"""

HAIR_CANNOT_APPLY = """
Seriously, why are you so obsessed with a few strands of hair?
"""


class Hairs(objects.Edible, objects.Usable):

    target_flag = "alchemy_mixer"

    def at_object_creation(self):
        super().at_object_creation()
        self.db.desc = HAIR_DESC.strip()
        self.set_flag("childmaker_ingredient_childlike")

    @interactive
    def at_consume(self, caller, action):
        self.room.achievement(caller, "Ewww", "Got too familiar with the Jester's hair")
        self.msg_room(caller, "~You tried to EAT some *hair off "
                      "the jester's pillow! Eeewww!", True)
        self.msg_char(caller, "|rNo! What are you, a cat?|n")
        yield(2)
        self.msg_char(caller, "|rEAT the hair, really?")
        yield(2)
        self.msg_char(caller, "|rDidn't think you'd actually TRY that. Ewww.|n")
        yield(2)
        self.msg_char(caller, "|rWeirdo.|n")

    def at_already_consumed(self, caller, action):
        self.msg_char(caller, "No. Just no.")

    def at_apply(self, caller, action, target):
        self.room.score(2, "mix childlike ingredient")
        target.handle_mix(
            caller, self,
            txt_ingredient="a strand of the Jester's black hair",
            color="red",
            smell="laughing roses",
            extra="FINALLY found some use for those tempting hairs, eh?")

    def at_cannot_apply(self, caller, action, target):
        self.msg_char(caller, HAIR_CANNOT_APPLY.strip())


# ------------------------------------------------------------
# floor
# ------------------------------------------------------------

FLOOR_DESC = """
The floor of the Jester's cabin is made of thick hardwood planks. At one point
they were probably oiled, but these days they are dried and creaking. The
spaces between them are filled with dust, dirt and grime. Now that you really
look you notice a leather *rug almost in the middle of the floor; it's thin and
worn and is almost the same color as the floorboards.
"""

FLOOR_CLIMB = """
~You ~make a brave attempt to climb the *floor but ~fail since it is,
you know, a floor.
"""


class Floor(objects.Positionable):

    def at_object_creation(self):
        super().at_object_creation()
        # this flag is checked by the bed to see if we are lying on
        # this object to see the chest.
        self.set_flag("floor")

    def at_focus_climb(self, caller, **kwargs):
        self.room.achievement(caller, "Optimist climber", "Tried to climb the floor")
        self.msg_room(caller, FLOOR_CLIMB.strip())


# ------------------------------------------------------------
# chest (under bed)
# ------------------------------------------------------------

CHEST_DESC_FIRST = """
Under the *bed is what looks like a small chest. It is pushed far in under
the low bed so it was impossible to see without lying down.
"""

CHEST_PULL_OUT = """
Lying on the *floor, ~you ~pull out a *chest from under the *bed. It's
now easily accessible without having to lie down.
"""

CHEST_DESC = """
The chest that was under the bed has all the markings of a miniature sailor's
chest, with an ornate lid. But instead of a regular key-hole, there is a
cross-shaped hole in the center of it. It looks like some type of weird lock
for an ever weirder key.
"""


class Chest(objects.Openable):

    # this is not openable at this point
    start_open = False

    def at_object_creation(self):
        super().at_object_creation()
        # marks this as a valid target for the lever later
        self.set_flag("chest_lever_insert")

    def return_appearance(self, caller, **kwargs):
        if not self.check_flag("pulled_out_chest"):
            self.msg_char(caller, CHEST_DESC_FIRST)
            self.msg_room(caller, CHEST_PULL_OUT.strip())
            self.set_flag("pulled_out_chest")
            return ""
        else:
            return CHEST_DESC.strip()


# ------------------------------------------------------------
# rug
# ------------------------------------------------------------

RUG_DESC = """
The rug in the middle of the *floor is not very big. It's also colored almost
the same as the floor boards, making it easy to overlook. It's unclear from
which animal it is made but it looks dirty, worn and thin from the repeated
passage of feet.
"""

RUG_FEEL = """
The leather of the rug is stomped thin and is miscolored and worn at the edges.
It feels dry and rough to the touch.

"""

RUG_TURN = """
When you turn over the rug you find that the back of it is paler of color and
is covered in thin painted lines in the form of a crude map. It's not hard
to pick out what the symbols mean.

......................................
:                                    :
:                \                   :
:                |                   :
:         |wH|n      \  |wH|n                :
:    ____________O_______________    :
:      "        /           ^ ^      :
:    "          |      ^ ^ ^ ^ ^     :
:            "   \     |wH|n ^ ^ ^ ^     :
:        "       /        ^ ^ ^      :
:         |wH|n      \       ^ ^ ^       :
:    "            \      ^ ^         :
:                                    :
:    O  village          |wH|n  house    :
:    __  road            |  river    :
:    ^  forest           "  shrubs   :
......................................

What is the purpose of the map? You don't know.

"""

RUG_TO_ROOM = """
~You ~turn *rug around, discovering some sort of map on its other side.
"""


class Rug(objects.Feelable):

    def at_focus_feel(self, caller, **kwargs):
        self.msg_char(caller, RUG_FEEL.strip())

    def at_focus_turn(self, caller, **kwargs):
        self.room.score(2, "found the map")
        self.msg_room(caller, RUG_TO_ROOM, True)
        self.msg_char(caller, RUG_TURN.lstrip())


# ------------------------------------------------------------
# table
# ------------------------------------------------------------

TABLE_DESC = """
To the left of the door, opposite the bed, is a long table. It's suspiciously
empty, but there are dark markings on it as if whatever used to stand here was
recently cleaned and wiped off.

The only things on the table are a potted *plant and a small hand *mirror.

"""

TABLE_SURFACE = """
While wiped clean, the table's wooden surface is covered in old splotches and
stains.  There are also lighter spots where something large and uneven used to
stand until recently.
"""


class Table(objects.Positionable):

    def at_object_creation(self):
        super().at_object_creation()
        # this flag is checked by the coin to see if we can see/reach it.
        self.set_flag("reach_coin")

    def at_focus_surface(self, caller, **kwargs):
        self.msg_char(caller, TABLE_SURFACE.strip())

    def get_cmd_signatures(self):
        sigs, txt = objects.Positionable.get_cmd_signatures(self)
        txt += " You can also examine its *surface."
        return sigs, txt


# ------------------------------------------------------------
# mirror (on table)
# ------------------------------------------------------------

MIRROR_DESC = """
On the table lies a simple round hand mirror. It is made from carved wood and
the mirror itself is attached to the backplate with a few metal nubs.
"""

MIRROR_ROTATE = """
On the back of the hand mirror, the letters "V.B." have been burned into the
wood with a heated poker.
"""

MIRROR_USE_DOOR = """
When you hold up the mirror to the *door, the sequence of letters you see in the
mirror is reversed. Each letter is also reversed, of course, but they are easily
turned around in your mind to form:

    S T A R T B Y F E E D I N G V A L E
"""
# -> start by feeding vale
# (Vale is the name of the monkey statue)

MIRROR_USE_OTHER = """
You hold up the mirror to {obj} and ... see its reflection in the mirror.
Nothing groundbreaking there.
"""

MIRROR_TO_ROOM = """
~You ~hold up *mirror and ~look at {obj} through it.
"""


class Mirror(objects.Usable, objects.Rotatable):

    target_flag = "can_use_mirror"

    def at_rotate(self, caller):
        self.msg_char(caller, MIRROR_ROTATE.strip())

    def at_apply(self, caller, action, obj):
        # this object is usable with the mirror, but which obj is it?
        if obj.check_flag("cabin_door"):
            self.room.score(2, "look at door in mirror")
            self.msg_char(caller, MIRROR_USE_DOOR.lstrip())
        else:
            self.msg_char(caller, MIRROR_USE_OTHER.format(obj=obj.key).strip())
        self.msg_room(caller, MIRROR_TO_ROOM.format(obj=obj).strip(), True)

    def at_cannot_apply(self, caller, action, obj):
        self.msg_char(caller, MIRROR_USE_OTHER.format(obj=obj.key).strip())
        self.msg_room(caller, MIRROR_TO_ROOM.format(obj=obj).strip(), True)

    def get_cmd_signatures(self):
        txt = "You can *use |wwith <target>|n or *turn it around."
        return [], txt


# ------------------------------------------------------------
# potted plant (on table)
# ------------------------------------------------------------

PLANT_DESC = """
On the table, side nearest to the window, stands a potted plant. It's a rose
cutling, no more than a little green stem and a few leaves.

On the pot sits a little note:

    |wI'll make fine firewood when I grow up|n

"""

PLANT_DIG = """
Carefully you probe around in the small pot with your fingers, but even after
circling the cutling and fully probed the bottom of the pot you don't find anything
hidden in the dirt.

You shuffle the displaced dirt back into place around the fledging little plant.
"""

PLANT_THINK = """
This seems to be the same type of rose that grows outside the windows. The
Jester sure likes her roses.

It will take forever for this thing to grow into anything big enough to use for
firewood!
"""

PLANT_FEEL = """
Ouch! It may be small, but this thing already has thorns! You almost prick your
finger.
"""


class Plant(objects.Feelable):

    def at_focus_dig(self, caller, **kwargs):
        self.msg_char(caller, PLANT_DIG.strip())

    def at_focus_feel(self, caller, **kwargs):
        self.msg_char(caller, PLANT_FEEL.strip())

    def at_focus_think(self, caller, **kwargs):
        self.msg_char(caller, PLANT_THINK.strip())

    def get_cmd_signatures(self):
        txt = "You could try to *dig in the dirt, *feel the leaves or *think about it."
        return [], txt


# ------------------------------------------------------------
# main state class
# ------------------------------------------------------------

STATE_HINT_LVL1 = """
Sometimes seeing things from a higher vantage point will help.
"""

STATE_HINT_LVL2 = """
The statue looks hungry, maybe feed it something from above?
"""

STATE_HINT_LVL3 = """
Stand on the table and look at the rafters to find the coin.
Insert coin in the statue.
"""


class State(BaseState):

    next_state = "state_002_automaton"

    hints = [STATE_HINT_LVL1,
             STATE_HINT_LVL2,
             STATE_HINT_LVL3]

    def character_enters(self, character):
        self.cinematic(GREETING.format(name=character.key),
                       target=character)

    def init(self):
        """
        This'll be a big one since it creates the room as a whole.
        """
        self.room.db.desc = ROOM_DESC

        cabindoor = self.create_object(
            CabinDoor, key="door to the cabin", aliases=["door"])
        cabindoor.db.desc = CABINDOOR_DESC.strip()
        hintberry_plate = self.create_object(
            HintberryPlate, key="pie on a plate",
            aliases=["stool", "hintberry", "hintberry pie"])
        hintberry_plate.db.desc = HINTBERRY_PLATE_DESC.strip()
        windows = self.create_object(
            Windows, key="windows", aliases=['window'])
        windows.db.desc = WINDOWS_DESC.strip()
        metalworks = self.create_object(
            Metalworks, key="metalworks (outside)", aliases='metalworks')
        metalworks.db.desc = METALWORKS_DESC
        scarecrow = self.create_object(
            Scarecrow, key="scarecrow (outside)", aliases=['scarecrow'])
        scarecrow.db.desc = SCARECROW_DESC.strip()
        rafters = self.create_object(
            Rafters, key='rafters')
        rafters.db.desc = RAFTERS_DESC.strip()
        chimes = self.create_object(
            Chimes, key='chimes with red herrings', aliases="chimes")
        chimes.db.desc = CHIMES_DESC.strip()
        laundry = self.create_object(
            Laundry, key="laundry")
        laundry.db.desc = LAUNDRY_DESC.strip()
        saddle = self.create_object(
            Saddle, key="saddle")
        saddle.db.desc = SADDLE_DESC.strip()
        socks = self.create_object(
            Socks, key="socks")
        socks.db.desc = SOCKS_DESC.strip()
        bathtowel = self.create_object(
            Bathtowel, key="bathtowel", aliases=["towel"])
        bathtowel.db.desc = BATHTOWEL_DESC.strip()
        fireplace = self.create_object(
            Fireplace, key="fireplace", aliases=["chimney"])
        fireplace.db.desc = FIREPLACE_DESC.strip()
        cauldron = self.create_object(
            Cauldron, key="cauldron")
        cauldron.db.desc = CAULDRON_DESC.strip()
        painting = self.create_object(
            Painting, key="painting over the fireplace", aliases=["painting"])
        painting.db.desc = PAINTING_DESC.strip()
        ashes = self.create_object(
            Ashes, key="ashes in the fireplace", aliases=["ashes"])
        ashes.db.desc = ASHES_DESC.strip()
        closet = self.create_object(
            Closet, key="closet")
        closet.db.desc = CLOSET_DESC.strip()
        kitchen = self.create_object(
            Kitchen, key="kitchen")
        kitchen.db.desc = KITCHEN_DESC.strip()
        chair = self.create_object(
            Chair, key="chair")
        chair.db.desc = CHAIR_DESC.strip()
        statue = self.create_object(
            Statue, key='statue', aliases=["monkey"])
        statue.db.desc = STATUE_DESC.strip()
        hair = self.create_object(
            Hairs, key="hair", aliases=['hairs', 'strands of hair'])
        hair.db.desc = HAIR_DESC.strip()
        bed = self.create_object(
            Bed, key="bed")
        bed.db.desc = BED_DESC.strip()
        floor = self.create_object(
            Floor, key="floor", aliases=["floor boards"])
        floor.db.desc = FLOOR_DESC.strip()
        rug = self.create_object(
            Rug, key="rug", aliases=['carpet'])
        rug.db.desc = RUG_DESC.strip()
        table = self.create_object(
            Table, key="table")
        table.db.desc = TABLE_DESC.strip()
        mirror = self.create_object(
            Mirror, key="mirror")
        mirror.db.desc = MIRROR_DESC.strip()
        plant = self.create_object(
            Plant, key="plant")
        plant.db.desc = PLANT_DESC.strip()

    def clean(self):
        # reset all positions (get off chair/table etc)
        super().clean()
        self.room.progress(9)
        for char in self.room.get_all_characters():
            self.room.set_position(char, None)
