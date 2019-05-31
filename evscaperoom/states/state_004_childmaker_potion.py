"""
This state has the closet open with all the goodies inside. It will
end when the players creates the Childmaker potion.

This state creates a lot of objects relevant for the background story.

"""

from evennia.utils import interactive
from .. import objects
from ..state import BaseState


GREETING = """
    This is the situation, {name}:

    The |rJester|n wants to win your village's yearly |wpie-eating contest|n.
    As it turns out, you are one of her most dangerous opponents.

    Today, the day of the contest, she invited you to her small cabin for a
    'strategy chat'. But she tricked you and now you are |wlocked in|n! If you
    don't get out before the contest starts she'll get to eat all those pies on
    her own and surely win!

    When you get into the cabin, the padlock on the *closet was just unlocked
    and the closet doors swung open ...

"""


# ------------------------------------------------------------
# closet (open)
# ------------------------------------------------------------

CLOSET_DESC = """
The 'closet corner' of the cabin is dominated by the namesake closet. It's a
large antique piece of furniture, with open double doors of lacquered hardwood.

Inside, the closet is severely lacking clothes. Instead, half of it is filled
up from the bottom with wide drawers and a middle shelf high enough to act as a
standing table. In the middle of the shelf is a clay *bowl next to a large
*book.

The rest of the closet is empty, but on the back wall of the closet is a big
*poster and a messy *slate board covered in white chalk markings.

"""

CLOSET_THINK = """
This looks less like a closet and more like a workspace. Almost as if the
Jester was doing ... research? Is she just messing with me here?
"""

CLOSET_CLOSE = """
No point in closing the closet again, now that it's open.
"""

CLOSET_DRAWERS = """
The drawers are mostly empty. In one of them you find a forgotten large blue
*blanket however. It looks comfy for a cold winter's day.
"""


class ClosetOpen(objects.Openable):
    # nothing more to do with closet
    start_open = True

    def at_focus_think(self, caller, **kwargs):
        self.msg_char(caller, CLOSET_THINK.strip())

    def at_focus_close(self, caller, **kwargs):
        self.msg_char(caller, CLOSET_CLOSE.strip())

    def at_focus_drawers(self, caller, **kwargs):
        self.room.score(2, "found blanket")
        if not self.room.state.get_object("blanket"):
            blanket = self.room.state.create_object(
                Blanket, key="blanket")
            blanket.db.desc = BLANKET_DESC.strip()
            self.msg_room(caller, "~You found a *blanket in a *closet drawer.", True)

        self.msg_char(caller, CLOSET_DRAWERS.strip())

    def get_cmd_signatures(self):
        txt = ("Obvious actions would be to *open/*close the closet, examine "
               "*drawers or to *think more about this.")
        return [], txt


# ------------------------------------------------------------
# blanket (created when examining closet drawers)
# ------------------------------------------------------------

BLANKET_DESC = """
This is a thick blue blanket. You could wrap this thing around you
on a cold winter's night.
"""

BLANKET_FEEL = """
It's made of thick wool. As you move your hands over it, you notice
the letters "A.B." embroidered to it.
"""

BLANKET_CANNOT_APPLY = """
Let's not waste time redecorating this place.
"""


class Blanket(objects.Feelable, objects.Usable):

    target_flag = "window_coverable"

    def at_focus_feel(self, caller, **kwargs):
        self.room.score(1, "found initials on blanket")
        self.msg_char(caller, BLANKET_FEEL.strip())

    def at_apply(self, caller, action, obj):
        if hasattr(obj, "check_flag") and obj.check_flag("alchemy_mixer"):
            obj.handle_reset(caller)
        else:
            obj.at_cover(caller, self)

    def at_cannot_apply(self, caller, action, obj):
        self.msg_char(caller, BLANKET_CANNOT_APPLY.strip())


# ------------------------------------------------------------
# bowl (in closet)
# ------------------------------------------------------------

BOWL_DESC = """
This is a deep clay bowl inscribed with some sort of arcane pattern around its
edge. It looks old and used but is otherwise whole and clean.
"""

BOWL_READ = """
If the pattern around the edge of the bowl is writing it's in some ancient
language you can never hope to decipher.
"""

BOWL_TURN = """
You look at the bottom of the bowl find a neat label. It's written in tight
and precise hand writing.

    |mLEVEL FIVE ALCHEMIC MIXING BOWL

        PROPERTY OF MR. BLOCH
        NOT A TOY!
        IF FOUND, RETURN IMMEDIATELY.|n

The Jester is known to 'borrow' things from time to time. Things will eventually
come back but this bowl was clearly |wnot|n returned 'immediately' ...
"""

BOWL_MIX = """
~You ~mix {txt_ingredient} in the bowl. The mix
takes on a {color} color and a scent of {smell} spreads
through the room. {extra}
"""

BOWL_RESET = """
The potion in the bowl hisses and boils. In a moment it has evaporated
to nothingness. Looks like you have to start over.
"""

BOWL_SUCCESS = """
As the last ingredient is added, the contents of the bowl swirls and moves as
if by itself. It hisses for a moment and then it comes to a stop. The
concoction shifts in the colors of the rainbow but despite all the horrible
things you put in it, it only smells faintly of apples and roses.

The result is a bowl with the *Childmaker potion!
"""


class Bowl(objects.Rotatable, objects.Readable, objects.Mixable):

    mixer_flag = "alchemy_mixer"

    # ingredients added must have these flags, in sequence
    ingredient_recipe = [
        "childmaker_ingredient_rancid",
        "childmaker_ingredient_roses",
        "childmaker_ingredient_urine",
        "childmaker_ingredient_arrogance",
        "childmaker_ingredient_rancid",
        "childmaker_ingredient_childlike"
    ]

    def at_object_creation(self):
        super().at_object_creation()
        self.set_flag("window_coverable")  # this is just so the bath towel can be used on it

    def at_mix(self, caller, ingredient, **kwargs):
        self.msg_room(caller, BOWL_MIX.format(**kwargs).strip())

    def at_mix_failure(self, caller, ingredient, **kwargs):
        self.room.achievement(caller, "Clutz", "Botched making the childmaker potion")
        self.msg_room(caller, BOWL_RESET.strip())

    def handle_reset(self, caller):
        # called by the bath towel / blanket
        self.db.ingredients = []
        self.msg_room(caller, "~You ~wipe the *bowl clean, starting over.")

    def at_mix_success(self, caller, ingredient, **kwargs):
        self.room.score(2, "created childmaker")
        self.msg_room(caller, BOWL_SUCCESS.strip())
        childmaker = self.room.state.create_object(
            Childmaker, key="childmaker potion",
            aliases=["childmaker", "bowl"])
        childmaker.db.desc = CHILDMAKER_DESC
        # moving on!
        self.next_state()
        # delete ourselves, the childmaker replaces us
        self.delete()

    def at_focus_rotate(self, caller, **kwargs):
        self.msg_char(caller, BOWL_TURN.strip())

    def at_focus_turn(self, caller, **kwargs):
        self.at_focus_rotate(caller, **kwargs)

    def at_focus_read(self, caller, **kwargs):
        self.msg_char(caller, BOWL_READ.strip())

    def get_cmd_signatures(self):
        txt = ("You could try to *read the glyphs on the bowl or *turn it over to "
               "look at its bottom.")
        return [], txt


# ------------------------------------------------------------
# childmaker potion (created in mixing bowl)
# ------------------------------------------------------------

CHILDMAKER_DESC = """
The mixing bowl holds the childmaker potion created from the recipe in the
Jester's *book. It's a clear fluid that smells only faintly despite the
contents you know you added to the mixture.
"""

CHILDMAKER_DRINK1 = """
You swig down the childmaker potion. Tastes not half bad ...

... but was that so smart ...?
"""

CHILDMAKER_DRINK2 = """
    |rGAME OVER|n
"""

CHILDMAKER_DRINK3 = """
... Nah. Just kidding. Of course you're not stupid enough to drink this stuff
knowing what it does!

You put the bowl down, unsipped.
"""

CHILDMAKER_NO_DRINK = """
Not only do you know what stuff you mixed into this, but having read what this
thing does, you should really not drink it. You need all your wits about you if
you are to get out of here!
"""

CHILDMAKER_SMELL = """
It doesn't smell very much. If you mixed it into food you'd never know. If it
is as potent as the text says, this is a really dangerous thing.
"""

CHILDMAKER_MIX = """
You should not mix directly into this - if you get it wrong you might ruin the
childmaker potion. Better pour from this into another place instead.
"""

CHILDMAKER_APPLY = """
~You ~drop a few drops of the childmaker potion in the plant's dirt.
"""

CHILDMAKER_COVER = """
You don't want to wipe away the potion, now that you've got it!
"""


class Childmaker(Bowl, objects.Drinkable, objects.Usable):
    """
    This remains a mixable, but we don't actually allow mixing any more
    so as to not mix up the potion. Use this with another mixer instead.
    """
    mixer_flag = "fertilizer_mixer"
    target_flag = "fertilizer_mixer"
    one_consume_only = True

    ingredients_recipe = []

    def at_object_creation(self):
        super().at_object_creation()
        self.set_flag("childmaker")

    def get_cmd_signatures(self):
        txt = "You could *drink, *smell or *use it."
        return [], txt

    def at_cover(self, caller, coverer):
        return self.msg_char(caller, CHILDMAKER_COVER.strip())

    @interactive
    def at_consume(self, caller, action):
        self.msg_char(caller, CHILDMAKER_DRINK1.strip())
        yield(2)
        self.room.state.cinematic(CHILDMAKER_DRINK2, target=caller)
        yield(4)
        self.msg_char(caller, CHILDMAKER_DRINK3.strip())

    def at_already_consumed(self, caller, action):
        self.msg_char(caller, CHILDMAKER_NO_DRINK.strip())

    def at_focus_smell(self, caller, **kwargs):
        self.room.score(1, "smelled childmaker")
        self.msg_char(caller, CHILDMAKER_SMELL)

    def at_mix(self, caller, ingredient, **kwargs):
        self.msg_char(caller, CHILDMAKER_MIX.strip())

    def at_mix_failure(self, caller, ingredient, **kwargs):
        pass

    def at_apply(self, caller, action, obj):
        self.room.score(2, "used childmaker in mix")
        obj.handle_mix(caller, self, txt=CHILDMAKER_APPLY.strip())


# ------------------------------------------------------------
# slate (in closet)
# ------------------------------------------------------------

SLATE_DESC = """
The slate sits at the back of the closet and is scribbled with chalk-marks.
It looks like someone (the Jester?) scribbled words on it, trying to
connect them together with lines:

        BLACKSMITH        CHILDMAKER
          |                   |
          |     >???MUTE MONKEY???<
          |
        BAKER --------?--------- MAGUS

The 'MUTE MONKEY' is circled hard several times.
"""

SLATE_THINK = """
Maybe this is only some nonsense made up by the Jester for the sake of this
game she's playing with you. But this does feel oddly specific.

Whereas you don't know them personally, the blacksmith, the baker and the magus
are all known figures in the village. They are all pretty old by now. You don't
think they have any connection to each other, but maybe they did in the past?

But on the other hand, the Jester is like a child. Some say she's actually
insane. Who knows why she does what she does?

"""


class Slate(objects.EvscaperoomObject):

    def at_focus_think(self, caller, **kwargs):
        self.msg_char(caller, SLATE_THINK.strip())


# ------------------------------------------------------------
# poster (in closet)
# ------------------------------------------------------------

POSTER_DESC = """
An old red-hued wanted poster has been nailed to the back wall of the closet.
It looks official, something issued by the county law. It reads:
                      ~~~~~~~~~~~~~~
                           |mWANTED

                   THE MUTE MONKEY BANDIT|M

    For near-slaying of innocent child, robbery at knife-point
    and for spreading widespread Terror and fear for many a year

    Recognized by always wearing a |mmonkey-shaped mask|M and to not
    speak. Last seen riding a black horse on the road leading
           north-east from the village, past the forest.

                          |mREWARD
                    100 silver coins

    |MFor any information that leads to his capture, dead or alive.
            Know that he is |mNOT|M a ghost or a beast!
         He is a man that must be brought to justice!|n
                      ~~~~~~~~~~~~~~

The poster has an drawn image of the Monkey's mask for identification.
"""

POSTER_THINK = """
You have heard the legend of the Mute Monkey bandit of course - he is a ghost
story you tell around the fire at night. But the elders swear that he was real
and that he was never caught.

Legend has it that if you shout aloud when you cross the river, the Mute Monkey
will come and cut your tongue with his knife when you sleep!

That drawing of the monkey mask looks eerily familiar.
"""


class Poster(objects.EvscaperoomObject):

    def at_focus_think(self, caller, **kwargs):
        self.msg_char(caller, POSTER_THINK.strip())

    def get_cmd_signatures(self):
        txt = "This is worth to *think about."
        return [], txt


# ------------------------------------------------------------
# book (in closet)
# ------------------------------------------------------------


BOOK_DESC = """
On the shelf at the back of the closet lies a large book. It seems to be a sort
of scrapbook, partly filled with notes in the Jester's handwriting and partly
with inserted pieces of paper, clippings and notes from other sources. The
covers are bulging with all the stuff crammed into it.

You won't have time to read this from beginning to end. But it seems to be
sorted, so if you know the term to search for you may be able to look it up.

"""


# book topics

BOOK_JESTER = """
This seems to be part of a handwritten letter written by someone else. Part
of it has been torn off. It also smells distinctly of fish, like if it was
picked out of the garbage.

    "... and made a fool out of herself. From that day it was like everyone
    just decided to accept her as one of us. The kids love her. Despite just
    coming to the village so recently and moved into that cabin on the east
    bank, it feels like she's always been here.  She's like a harmless child.
    Looks it too. But I think she's actually older
    than me ...

In the corner you notice that the Jester has written a comment:

    |rHey, not THAT old! I've still got my teeth!|n
"""

BOOK_THAT = """
The Jester writes:

    So I wrote THAT in big letters and now I must make an entry for the word
    'that'. So there. Now it's done. Hope you are happy, silly fool me.
"""

BOOK_BLACKSMITH = """
The Jester's notes are written in her scribbly style, with lines going in
seemingly random directions at times.

    Angus, the blacksmith, is a hard nut to crack. His face seems scrunched to
    a permanent frown. He's a bit on the older side, but he's still quite a
    handsome fellow if he didn't look so grim all the time. I've decided he's
    this week's project. I -will- make him crack a smile if so it'll kill me!

    I found out that Angus was the pie-eating CHAMPION once upon a time! I
    thought reminding him would make him smile. But it didn't. Curious.

    I think he was married once. He wears a ring, but no one speaks about it.
    Clearly not smile-material.

    When he finishes his work for the day, he makes children's toys. Don't
    think he even sells them, he just makes them for the kids in the village
    free of charge. They are wonderful things - little horses and cats in wood
    and metal!  I have a toy-making request he won't be able to REFUSE.

"""

BOOK_REFUSE = """
The Jester writes:

    I asked for Angus to make me one of his toys. Lately I've concluded that he
    probably does like me, in his stoic way. Maybe I remind him of someone?

    Having read up on the Monkey bandit I know just the toy I want. With some
    of the tricks I learned from the MAGUS, I might even add some extra flair
    to the thing.

    You'd think get a request for one of his toys would cheer him up but nooo.
    I thought he'd outright refuse me after the look he gave me. But he did
    make me my toy, just as I wanted it. Was quick about it too. Now I must
    figure out what to NAME it though ...

    Angus is a little less stiff and grim towards me since then. I even saw the
    hint of a smile the other day. One day I'll make him laugh. I'm sure his
    nose swings back and forth when he laughs, I can't wait to see it.
"""

BOOK_MONKEY_TOY_NAME = """
The Jester writes:

    Still pondering what to name the toy I got from Angus. It is kinda
    goofy-looking and almost pathetic. I'm really tempted to name it after
    someone in the village. But that sounds mean.

    Someone suggested I'd name the toy as revenge against the next person to
    make me cry. Hah - then it'll never get named, I'm sure! But why not - if I
    ever cry, it gets the name of the person that made me do it. Until then,
    I'll just call my new pal CRYBABY.
"""

BOOK_CRYBABY = """
The Jester writes:

    Crybaby is a little too ... non-moving for my taste. I think I'll go have a
    talk with master Bloch to see what can be done about that.

    There's this special form of magic that makes use of little talismans or coins.
    I don't really know how it works, but I think they sort of store magic over
    time and release it when you need it. They only last for a while but when they
    run they can do all sort of nifty stuff. Porta-magic! I'll see if I can make
    one to teach Crybaby some tricks!
"""


BOOK_CHAMPION = """
The Jester writes:

    I talked to some elderly folk who remembered who won the pie-eating contests
    back in those days.

    The Magus
    The Magus
    The Baker
    The Magus
    The Baker
    The Magus
    The Blacksmith
    The Blacksmith
    The Blacksmith
    The Baker

    So they were all three pie-eating champions long ago. But after this suite,
    neither of them ever participated again.

    ... Well -I- find stuff like this interesting, alright?

"""

BOOK_BAKER = """
The Jester writes:

    MRS Bullington has a cottage on the complete opposite side of the village from
    me. As far as I've heard she lives alone since her parents died. She doesn't
    come into town very much.

    Bullington apparently makes the pies to the PIE-eating contest every year.
    Hopefully I can meet her then!

    I met her at the fair, what a lovely woman. She must have been very pretty
    in her youth with that black hair of hers. But now she slobbers a bit and
    has trouble with words sometimes. She's even more aloof than me, imagine
    that!

    But her PIES are great!  Already looking forward to next year's fair!

"""

BOOK_MRS = """
The Jester writes:

    Come to think of it, why does everyone call Mrs Bullington "Mrs"
    Bullington? I saw her place, there's no family there - she seems to have
    trouble enough just managing herself ...
    Maybe she's a widow? I've not gotten a straight answer out of anyone on
    that but I have heard that 'Bullington' is her MAIDEN NAME.

    I found a picture of the blacksmith and Mrs Bullington in her house when I
    visited her one day. When I asked she just blushed and started to stutter.
    She didn't want to say more about it. The two looked happy and both had
    rings on their fingers though. I think I may know where that 'Mrs' is
    coming from now.

"""

BOOK_BORROW = """
The Jester writes:

    Friends borrow stuff from each other, right? People can borrow anything
    from me. So of course I borrow anything from them. Makes sense! I can't
    help that people tend to have more interesting stuff than I do.
"""

BOOK_MAIDEN_NAME = """
The Jester writes:

    I don't really care, but it matters for a lot of the elderly folk around
    here:

    Tradition is for women to take the surnames of their husbands when they
    marry. Their 'birth name' or 'maiden name' is then the surname of their
    father, apparently. Also apparently, the woman takes back her maiden name
    if the couple divorce or live apart for some reason.

    I don't know why people think stuff like this is important. Me, it gives a
    headache! Why can't people just have one name? Like me!
"""

BOOK_PIES = """
The Jester writes:

    MRS Bullington makes her pies from the apple trees growing around her
    house. I asked her why she didn't cross the road to pick HINTBERRIES too -
    there's plenty of berries in the brush over there. But she said that
    the MAGUS lives over there and that he needs the berries for his potions.
    She doesn't want to be a trouble to him.

    What nonsense! Who can tell if you pick a few berries or not! Out of pure
    defiance a picked a basket full and gave her. As thanks she taught me how
    how to make hintberry pies.
"""

BOOK_HINTBERRIES = """
The Jester writes:

    I found that if you follow the west bank of the river and keep following it
    north-westwards up to the main road, you'll find plenty of hintberries. The
    MAGUS is a stickler for the berries, but how many berries can a one man eat
    (or drink) on his own anyway ... ?
"""

BOOK_ROSES = """
The Jester writes:

    The roses around here are beautiful! I love roses, best flower -ever-. On
    the east bank of the river are some really pretty pink ones I've been
    eyeing.

    I got help moving some of those pretty pink rose-bushes to plant by my
    cabin! They were already pretty big but they seem to really prosper even
    more by my windows. Now I can smell the roses every morning!

"""


BOOK_MAGUS = """
The Jester writes:

    Quite a walk through the brush to get to Master Blochs house! Grumpy
    fellow, must cheer him up! He looks so old, I wonder if it's his magic that
    ages him. Or that bluish wine he drinks all the time. I was always
    interested in magic, but wine always tasted icky to me ...

    Master Bloch is not so bad once you get to know him! He's just awkward and
    insecure I think, especially around women - even me. Hah, maybe I should
    grow me a beard ...
    But over time it has gotten better. Just smiling and listening gets you
    far! What a lonely man. Just happy to have anyone listen to his words.

    Master Bloch got drunk the other day and bragged about his most powerful
    potion RECIPE. He says he is doing all sorts of experiments in his
    solitude. Do tell! But he wouldn't tell more. He got all grumpy on me
    again, even shooed me out of his place.

    Ah, what is a poor fool to do, now I just -have- to take a look at that
    RECIPE of his ...

"""

BOOK_RECIPE = """
This is not written in the Jester's hand, but with flowing, tight lettering.
The paper is old. This is not a new discovery.

    CHILDMAKER POTION

        Add in this exact order the following ingredients into an alchemic
        mixing bowl of a least level three:

            - 1 small drop of the liquefied carcass of a dog dead on a Tuesday
            - A sprinkle of a girl's favorite perfume
            - A squirt of Naturally produced Ammoniac
            - Some drops of bottled Arrogance (Beet juice works too).
            - Another drop of carcass
            - Something from a grown child

        Notes:
            I inherited this recipe from my grandfather. He called it 'the
            potion of youth' but it's nothing as benevolent as that. In secret
            I tested it on one of the adult farmer cats to terrifying effect -
            the cat didn't rejuvenate but instead it reverted to -acting- as a
            young kitten. Worse, soon after, it had a litter of kittens of its
            own. Her kittens were not only smaller than normal, they grew only
            very slowly and also never reached full maturity or adult behavior.
            Not only does it appear the effect is permanent - it spreads
            across generations!

            This thing is -very- dangerous!  But it's my most potent mixture,
            so maybe I could use it as a base for something else. With some
            modifications, I think can turn it into some sort of FERTILIZER
            instead ...

"""

BOOK_FERTILIZER = """
Again, this is not written by the Jester's hand, but with the same tight lettering
as the Childmaker potion RECIPE.

    I think the Childmaker could be turned into something less dangerous by
    modifying it to work for plants only. I hope to 'invert' its effects to
    instead have the plant grow fast. My biggest concern is that if the plant
    does not have enough water it will grow so fast so as to instead quickly
    become a withered and dry husk ...

        - 1 Childmaker potion
        - 3 ...

The bottom of the recipe has been torn off, there no telling what follows.

"""

BOOK_MONKEY = """
The Jester writes:

    The legend of the Mute Monkey bandit is soo neat! Best thing is that he was
    real! Around here the road goes almost perfectly straight from south-west to
    north-east. No bends and still he managed to just appear out of nowhere to
    surprise travellers. He must have known the land well!

    That monkey mask fascinates me. I like monkeys, but would not a scarf be
    enough to hide your identity? It did work though - people are still scared
    of the Mute Monkey! People say he got ever more violent until the day he
    slashed a merchant's kid on the way to the village fair. I found the wanted
    poster from that time in a drawer over at Master Blochs house! I'm sure he
    won't miss it, hihi.

    Best thing with the legend was that the Monkey just ... disappeared after
    that. They never caught him. Maybe those wanted posters spooked him? Or
    maybe he returned to his lair underground, only to return in a hundred
    years, muahaha!

"""

# hint for the chest-opening puzzle
# E, W, N, E, W, S, S, E, N, W
BOOK_THE_LONG_WALK_HOME = """
Written in the Jester's sprawly handwriting, this entry reads:

    I started at my cottage, expecting a great day
    For breakfast I went to the Baker, but she had lost her way.

    So I went to Angus for a quick morning bite
    And then back to my cottage to fly my kite.

    To Mrs Bullington I then went and now there was pie to eat
    I brought some to the Magus to get him on his feet.

    At Master Bloch's, a letter from the oven I freed
    I took it with me home to quietly read.

    I ended my day by looking into the Blacksmith's eyes
    And going to the Baker to help her with her pies.

"""


class Book(objects.IndexReadable):

    index = {
        'jester': BOOK_JESTER,
        "blacksmith": BOOK_BLACKSMITH,
        "smith": "blacksmith",
        "baker": BOOK_BAKER,
        "pies": BOOK_PIES,
        "pie": "pies",
        "mrs": BOOK_MRS,
        "that": BOOK_THAT,
        "magus": BOOK_MAGUS,
        "refuse": BOOK_REFUSE,
        "champion": BOOK_CHAMPION,
        "champions": "champion",
        "recipe": BOOK_RECIPE,
        "fertilizer": BOOK_FERTILIZER,
        "mute monkey bandit": BOOK_MONKEY,
        "mute": "mute monkey bandit",
        "monkey": "mute monkey bandit",
        "bandit": "mute monkey bandit",
        "the long walk home": BOOK_THE_LONG_WALK_HOME,
        "long walk home": "the long walk home",
        "the long walk": "the long walk home",
        "long walk": "the long walk home",
        "maiden name": BOOK_MAIDEN_NAME,
        "maiden": "maiden_name",
        "monkey toy name": BOOK_MONKEY_TOY_NAME,
        "name": "monkey toy name",
        "crybaby": BOOK_CRYBABY,
        "borrow": BOOK_BORROW,
        "borrowing": "borrow",
        "hintberries": BOOK_HINTBERRIES,
        "hintberry": "hintberries",
        "roses": BOOK_ROSES,
        "rose": "roses"
    }

    def at_read(self, caller, topic, entry):
        super().at_read(caller, topic, entry)
        self.room.score(2, "read an entry in the book")
        # scores
        if topic == "that":
            self.room.achievement(
                caller, "Stickler for detail", "Following the tiniest lead in the book")
        elif topic == "recipe":
            self.room.score(2, "found childmaker recipe")
        elif topic == "fertilizer":
            self.room.score(2, "found fertilizer recipe")

    def at_object_creation(self):
        super().at_object_creation()
        self.set_flag("looking_glass_sun")

    def get_cmd_signatures(self):
        txt = (f"Use *read <topic> to look something up - you can't start reading this thing from "
               "beginning to end if you hope to get out of here before the pie-eating "
               "contest!")
        return [], txt


# ------------------------------------------------------------
# main state
# ------------------------------------------------------------

STATE_HINT_LVL1 = """
You should read the *book in the *closet. It has some nice recipes that may
interest you.
"""

STATE_HINT_LVL2 = """
Read the book for |wrecipe|n. The 'childmaker' potion requires some weird
ingredients.  We already have a *bowl. Look at the bottles in the *kitchen.
Be aware of those labels though, better not trust them ...
"""

STATE_HINT_LVL3 = """
The Jester has swapped those labels around. Smell them to find out what's what:

- The liquefied carcass smells horrible.
- The fool's favorite perfume is rose-water. So it smells like roses (duh)
- Natural ammoniac is in urine and thus smells of the loo.
- Arrogance/Beet juice has an earthy smell.

Now all that's needed is 'something from a grown child'. Do we know one of those?
"""

STATE_HINT_LVL4 = """
Lie on the *bed to find the Jester's *hairs left on the pillow. She is childlike
enough!  Use that as the last ingredient.
"""

STATE_HINT_LVL5 = """
Mix in this order to create the 'childmaker' potion':

1. *bottle3 (label says perfume, smells horrible)
2. *bottle1 (label says stealth, smells roses)
3. *bottle5 (label says beet root, smells urine)
4. *bottle2 (label says rancid, smells earthy)
5. *bottle3 (label says perfume, smells horrible)
6. *hairs  (from bed pillow)
"""


class State(BaseState):

    next_state = "state_005_wind_turns"

    hints = [STATE_HINT_LVL1,
             STATE_HINT_LVL2,
             STATE_HINT_LVL3,
             STATE_HINT_LVL4,
             STATE_HINT_LVL5]

    def character_enters(self, character):
        self.cinematic(GREETING.format(name=character.key),
                       target=character)

    def init(self):
        closet = self.create_object(
            ClosetOpen, key="closet")
        closet.db.desc = CLOSET_DESC.strip()

        vale = self.get_object("vale")
        if vale:
            vale.db.rhyme_needed = False

        bowl = self.create_object(
            Bowl, key="alchemy bowl", aliases=["bowl"])
        bowl.db.desc = BOWL_DESC.strip()

        slate = self.create_object(
            Slate, key="slate")
        slate.db.desc = SLATE_DESC.strip()
        poster = self.create_object(
            Poster, key="poster", aliases=["wanted poster"])
        poster.db.desc = POSTER_DESC.strip()
        book = self.create_object(
            Book, key="book", aliases='lexicon')
        book.db.desc = BOOK_DESC.strip()

    def clear(self):
        super().clear()
        self.room.progress(34)
