"""
They left the room - now we ask some questions and a

"""
from random import choice
from django.utils import timezone
from evennia import syscmdkeys, CmdSet
from evennia import ANSIString
from evennia.utils import interactive, time_format, justify
from ..state import BaseState
from ..commands import CmdEvscapeRoom
from ..utils import msg_cinematic, add_msg_borders


GREETING = """
The story is over, all that's left is to answer some questions and
watch the ending cinemematics.

"""

INTRO_TEXT1 = """
The monkey Vale cheers and bounces as you triumphantly leave the cabin:

    |w"Well done! Well done to thee,
     Hope you learned a thing or three

     And also had a lot of fun,
     Off to the fair you better run!"|n

Then the monkey automaton grows still and quiet, its work done. You close the
door to the Jester's cabin and |ghead out into the bright summer sun.|n

    (return to continue)
"""

INTRO_TEXT2 = """
|gThe sun is shining and the summer day is warm. A faint wind brushes your hair
as you hurry from the Jester's cabin through a swaying sea of flowers. On the
wind you can already hear the sound of distant laughter and music from the
village fair.|G

As you rapidly hurry down the flower-lined path from the cabin, you gather your
thoughts. What |g'thing or three'|G did you actually learn from this?|n
"""

# ------------------------------------------------------------
# Scores
# ------------------------------------------------------------

SCOREBOARD = """
|cROOM '{roomname}' END SCORE
{progress_txt} complete after {roomtime}

|cTotal Room Score:|n
{adjusted_percent_txt} ({adjusted_score} / {max_score} points, |Rused |r{hints_used}|R hints|n)

|cRoom achivements:|n
{room_achievements}

|cPersonal achievements for {charname}:|n

{achievements}
"""


def display_score(scoreboard):
    lines = []
    for line in scoreboard.split("\n"):
        if not line.strip():
            lines.append("")
        else:
            lines.append(ANSIString(line).center(80, " "))
    return add_msg_borders(ANSIString("\n").join(lines))


def collect_stats(caller, room):
    """
    Extract score from caller and room

    Args:
        caller (Character): The player.
        room (EvScapeRoom): The current Room.
        stats (dict):

    Returns:
        data (dict): Gathered data.

    """
    stats = room.db.stats

    progress = stats['progress']
    if progress < 50:
        progress_txt = f"|r{progress}%|n"
    elif 50 <= progress < 100:
        progress_txt = f"|y{progress}%|n"
    else:  # 100%
        progress_txt = f"|g{progress}%|n"
    score = sum(val for val in stats['score'].values())
    max_score = stats['max_score']

    room_achievements = []
    # we maxed score - worth an achievement
    if score >= max_score:
        room_achievements.append("|wNo stone unturned|n - |xMaxed the score|n")

    # hints used
    hints_used = stats['hints_used']
    hints_total = stats['hints_total']

    # we adjust score by the number of hints needed
    adjusted_score = min(max_score, max(0, score - hints_used * 5))
    adjusted_score = int(adjusted_score * (progress / 100))
    adjusted_percent = int((adjusted_score / max_score) * 100)

    if adjusted_percent < 50:
        adjusted_percent_txt = f"|r{adjusted_percent}%|n"
    elif 50 <= adjusted_percent < 100:
        adjusted_percent_txt = f"|y{adjusted_percent}%|n"
    else:  # 100%
        adjusted_percent_txt = f"|g{adjusted_percent}%|n"

    # we 'maxed' hints, why not an achievement
    if hints_used >= hints_total:
        room_achievements.append("|wInglorious|n - |xUsed ALL hints|n")

    if not room_achievements:
        room_achievements = ["None"]

    # answers to questions
    question1 = room.check_character_flag(caller, "question1")
    question2 = room.check_character_flag(caller, "question2")
    question3 = room.check_character_flag(caller, "question3")

    # eventual extra room flags
    roomflags = room.db.flags

    # total time played in this room
    roomtime = time_format((timezone.now() -
                            room.db_date_created).seconds)

    # individual achievements
    achievements = caller.attributes.get(
        "achievements", category=room.tagcategory, default={})
    if not achievements:
        achievements = ["(None, zilch, de nada)"]
    else:
        achievements = ["|w{}|n - |x{}|n".format(key, subtxt)
                        for key, subtxt in achievements.items()]

    # this can also be fed directly into the scoreboard
    data = dict(
           char_name=caller.key,
           char_desc=caller.db.desc,
           roomname=room.key,
           roomtime=roomtime,
           hints_used=hints_used,
           hints_total=hints_total,
           score=score,
           max_score=max_score,
           adjusted_score=adjusted_score,
           adjusted_score_percent=adjusted_percent,
           adjusted_percent_txt=adjusted_percent_txt,
           progress=progress,
           progress_txt=progress_txt,
           charname=caller.key,
           room_achievements="\n".join(room_achievements),
           achievement_count=len(achievements),
           achievement_max=12,
           achievements="\n".join(achievements),
           roomflags=roomflags,
           question1=question1,
           question2=question2,
           question3=question3)

    return data


# ------------------------------------------------------------
# Questions to answer
# ------------------------------------------------------------


QUESTION1 = """
|gQuestion one:

    What's the real Vale's last name?|n
"""

QUESTION2 = """
|gQuestion two:

    What is the first name of the Mute Monkey Bandit?|n
"""
QUESTION3 = """
|gAnd then the final question:

    What is |rthe Jester's|g maiden name?|n
"""

# ------------------------------------------------------------
# Endings
# ------------------------------------------------------------

ENDING_CONTEST_INTRO_1 = """
Now, about that pie-eating contest ...
"""

ENDING_CONTEST_INTRO_2 = """
Over at the village square, the pie-eating contest is starting. Hungry
contestants from across the village are lining up to take on this years
strongest challenger - the |rJester|n. Small as she is, the fool has a
reputation for a dangerous appetite.

    |w"But wait!"|n, calls the {spectator}. |w"Was not {name} supposed to be
    here too?"

    |y"Yeah! That's someone who could give the Jester a run for her pies!"|n

    |r"I don't see {name} around though..."|n the Jester coos innocently.
    |r"- But I'm sure they're having fun though, whever they are!"|n

    The {spectator} looks suspicious. |w"Girl, what have you done this time?"|n

    |r"Nooothing."|n

    |y"Well, we must start"|n, says the judge. |w"If {name}|y does not show up,
    that's their loss."|n

    |r"You know what? I think so too."|n

The judge shrugs and prepares to start the contest.
"""

# we missed the contest


ENDING_CONTEST_MISSED_1 = """
... However, when this all took place, you were just struggling to make sense
of the rug-map puzzle. You were nowhere near the village and completely missed
the whole thing.

As you finally make your way back to town, the pie contest is long over, the
tables filled with empty plates. The |rJester|n sits on the middle of the table
waiting for you.

    |r"You know"|n, she says, |r"That was a pretty pathetic."|n

Fuming, you tower over her, but she continues unabated:

    |r"I really thought you'd make it at the last minute! I found out that it
    was not as fun to beat the snot out of you in pie-eating when you where not
    even there!"
"""

ENDING_CONTEST_MISSED_2 = """
You are about to tell the Jester a truthful curse or two when she reaches behind
her.

    |r"I did save this for you though, slow-pokes."|n

From behind her she pulls out one of Mrs Bullington's pies. That distracts you,
and you stare as he holds it up to your face.

    |r"After that debacle, this is just what you deserve."|n

Then she smacks the pie flat in your face.

So at least this ends in pie.
"""

# we arrive but we lose the contest


ENDING_CONTEST_DEFEAT_1 = """
... But there you are! A bit out of breath, but you made it! Your friends cheer
as you take a seat. You glare at the Jester across the table. She grins and
puts out her tongue to you.

    |r"Better late than never! I didn't think my front door was -that- hard for
    you to open!"|n

Before you can reply, the contest is under way! In a storm of pie eating frenzy
you all dive into the plates. You eat a pie and then reaches for the next.  The
Jester does the same. As the contest goes on, more and more villagers are
forced to step back from their plates. Yet the two of you keep eating ...

"""

ENDING_CONTEST_DEFEAT_2 = """
... But then your stomach just can't take it anymore. Maybe your time in her
cabin mixing all those nasty ingredients is taking their toll. The pie is about
to come back up again. Pale-faced you lean back from the plate.

    |r"Does that mean I win?"|n the Jester asks over the edge of her
    plate. The crowd goes wild.

With a bit of cheating too, you think bitterly as the Jester gets celebrated
for her win.

Some time later, the Jester comes and sits down across from you.

    |r"Oooh, looks like you are FUMING"|n she says, "Well, I can't help you were
    so crappy at solving my easy little game! Besides, now you have an
    excuse for losing to someone half your size, eh?"|n

You've had enough.

    |c"I know someone who's taking a dip in the river very soon"|n, you say.

The Jester's eyes go wide.
"""

# we arrive and win the contest

ENDING_CONTEST_WIN_1 = """
... But there you are, and in good time too! Your friends cheer as you take your
seat. The Jester looks amused as she take you in.

    |r"Hah, I -knew- you'd make it! It would not have been nearly as much
    fun to out-eat you if you wheren't here. So let's go at it then!"

The contest starts and all the contestants dig into their pies. You finish a
pie and then another one. Things are going well! But the Jester keeps pace.
One by one the other contestants are forced to abandon the fight. Yet
the two of you keep eating ...

"""

ENDING_CONTEST_WIN_2 = """
Finally the Jester burps loudly, sways and collapses over her plate.

    |r"I ... haven't given up ... just resting a little ..."

There is of course no such thing as resting in a pie eating contest! You |gwin|n!
Sweet triumph! You are celebrated in town as the new pie-eating champion!

Some time later you go and sit across from the Jester, who has now recovered.
You feel you have the right to gloat:

    |c"You tried your hardest to lock me in! But your plan failed! I won
    against the odds!"|n

The Jester winks and taps your shoulder.

    |r"The odds? Buddy, you just out-ate a girl half your size. Congrats."|n

You glare at her and stand up.

    |c"Well, at least I know a girl half my size who's taking a very
    well-deserved half-sized dip in the river very soon."|n

The Jester's eyes go wide.
"""

# we arrive and dominates!

ENDING_CONTEST_DOMINATE_1 = """

    |c"I'm right here"|n you say and step forth.

Calmly you take your seet across the Jester. She watches you with narrow
eyes.

    |r"My, maybe I've understimated you. How fun! Let's eat!"|n

The contest starts. Everyone dives down on their pies in a frenzy. You finish a
pie and reach for another. You feel strong and edged on by righteous
indignation over the trick your opponent tried to pull on you.

One by one the other contestants have to forfeit. Yet the two of you keep
eating ...
"""

ENDING_CONTEST_DOMINATE_2 = """
Finally the Jester bites down on the pie, but then lets it fall down on the plate
again. You meet her gaze across the table, just as you reach for another pie.

    |r"You keep eating that"|n she says, weakly. |r"I'll just go barf over here
    in the meantime ..."|n

You have |gwon|n! And in a grand fashion! You feel you could down at least one
more pie, maybe two.

Some time later, the Jester has recovered enough to come by your table.

    |r"Congrats"|n she smirks, |r"Not sure I want to see my cabin when I come back,
    I imagine you went over it with a fine tooth comb. And with that kind of
    eating, you can't have had many of my pies either."|n

You feel you have earned to right to gloat.

    |c"You gave it your best shot. But I beat you easily anyway!"|n

The Jester smiles sweetly:

    |r"Buddy, you out-ate a girl half your size. It's not -that- impressive you
    know."|n

You nod and stand up.

    |c"Well, maybe so. But at least I know one half-sized girl who has more
    than earned herself a full-sized dip in the river."|n

The Jester's eyes go wide.
"""

# whois vale

ENDING_VALE_MAGUS = """
"|gAs you walk towards the village, you conclude that the Magus, master
Bloch's first name must be |wVale|n. |wVale Bloch|G.

Everyone thought he just made wine with those hintberries but in in the letter
he wrote (but never sent) to Agda, he claims to use them for some sort of
experiments to make her 'better', whatever that means. He seems convinced some
other person were dangerous but accidentally poisoned Agda instead of his
intended target. Apparently Agda's docile and aloof persona was not always like
that - she seemed to bully him in the past. Vale didn't seem to care though -
he just blindly wanted her back the way she was, no matter what.|g

In one of the pages of the book, the Jester says that she'll name the toy
monkey after the next person to make her cry. In the rhyme, the Jester took the
letter from the Magus and read it. Maybe the contents of that letter is what
made her cry and that's why she named the monkey Vale.|n
"""

ENDING_VALE_BLACKSMITH = """
|gAs you walk towards the village you conclude that the Blacksmith's first name
must be |wVale|n - |wVale Warwick|G.

The Jester refers to him as 'Angus', but maybe that's his second name? He
created the Monkey bearing the same name - the toy even said the Blacksmith
cried when doing it. So the Jester named the toy as an homage to him.|g

In the letter from 'Vale', he talks like he hurt Agda in the past. Maybe he
conspired or stole some concoction from the Magus to do what he di. It could be
why the Blacksmith is so grumpy. He was even married in the past, according to
the Jester. Maybe it was to Agda.|n

"""

ENDING_VALE_BAKER = """
|gAs you walk towards the village you conclude that the Baker's first name
must be |wVale|g - |wVale Bullington|g, short for |wValerie|n, maybe?|G

Vale's secret is her hidden love for Agda, whom she adresses in her letter.
She has good access to hintberries (just cross the road!) and could have gotten
hold of the recipe from the Magus, same as the Jester did. She aimed her poison
at someone else, but got Agda by accident. Her aloof persona is simply her
being constantly consumed by plans to make things better!|g

The Jester clearly named the monkey 'Vale' as a mockery of the Baker. Love is a
joke to that one, you are sure.|n
"""

ENDING_VALE_JESTER = """
|gAs you walk towards the village you conclude that Vale is infact |wthe Jester
herself|n. Maybe it's short for |wValerie|g or something.|G

No one knows the Jester's name. She cannot take anything seriously. Whom better
to speak for her than a mechanical monkey? The thing even said so itself - she
cannot bear being serious. So the monkey does it for her.|g

You wonder if 'Agda' even exists or if she's some figment of the Jester's
imagination. All the details of the book, all those notes and comments clearly
suggests someone with a great deal of imagination and unhealthy fascination
with tiny and useless details. Maybe this whole thing was just so that Jester
could find a good rhyme for 'Baker' ...|n

"""

ENDING_VALE_OTHER = """
|gAs you walk towards the village you conclude that 'Vale' probably didn't exist
at all. The Jester probably just made it up for her game. She mixed in some
real names from the village to make it more interesting.|G

Maybe she pictured her new toy 'Vale' to be writing the letter. It would
sound like her to think it being truly alive. She then gave it a whole
back story and a little mystery.|g

She's always trying to fool you, but this time you figured her out!|n
"""

ENDING_VALE_MAP = {
    "MAGUS": ENDING_VALE_MAGUS,
    "BLACKSMITH": ENDING_VALE_BLACKSMITH,
    "BAKER": ENDING_VALE_BAKER,
    "JESTER": ENDING_VALE_JESTER,
    "OTHER": ENDING_VALE_OTHER}


# knowing the monkey bandit

ENDING_MONKEY_MAGUS = """
|gAfter having thought about it, you draw the amazing conclusion that the |wMagus|g,
|wVale|g, once was the Mute Monkey bandit!|G

Clearly the Jester things so too. She even named the monkey 'Vale'. And the
mask it wears is eerily similar to the bandit's.|g

Master Bloch was once young too. He could well have been good with knife and
horse back in the day. And no wonder he seemed able to just appear out of
nowhere - he used his magic to do so! The monkey mask might even have been some
sort of magical talisman to cast fear in his victims.|G

If he wrote the letter from 'Vale', it was either a forgery or him trying to
justify his actions to himself - that's why he burned it; it was never meant to
be read by anyone by himself. Most likely someone discovered his identity and
he tried to use his potion to get rid of that person. He stopped being the Monkey
after poisoning Agda. Maybe he realized what he had become.|g

Then again, he claims poisoning Agda was a mistake, but who knows, right?|n

"""

ENDING_MONKEY_BLACKSMITH = """
|gAfter having thought long and hard about it, you think that the |wBlacksmith|g,
|wAngus|g, was the Mute Monkey Bandit as a young man!|G

The blacksmith is a crafty man, strong and good with his hands. Surely he was a
formidable man in his youth. The saddle hanging in the rafters also shows signs
of battle and maybe blood. It's marked AW - Angus Warwick.|g

The Jester found that the Blacksmith was married once - what if it was to Agda?
In Vale's letter, the author says that he wanted to save Agda from "him". Agda
had confided in Vale but Vale could not live with the secret. The secret was of
course that her husband, the Blacksmith, was the Monkey bandit!|G

The Jester found that back in the day, the Blacksmith had won the pie-eating
contest three years in a row.  Vale tried to use his potion on the champion
but Agda ended up eating the poisoned pie instead.|g

The poster and the Jester's research found that the bandit nearly killed a kid.
Maybe that caused the Blacksmith to rethink his life. These days he's making
kid's toys - maybe that's his way to recant.|G

Finally, when he made the Monkey automaton for the Jester, he glared at her but
was very fast about it. That's because he already had the face - its face is
the same mask that the bandit wore!|n

"""

ENDING_MONKEY_BAKER = """
|gAfter having thought it through, you reach the conclusion that the |wBaker|n,
|gAgda|g, was in fact the the Mute Monkey Bandit!|G

Why did the bandit wear a mask? Why was he mute? That's because if she spoke
people would immediately hear it was a woman. This was how the bandit could
appear out of nowhere too - she would just change her clothes and hide the mask
and no one would suspect her being nearby.|g

Agda and the Blacksmith could have been - or maybe still are - married, despite
livibg apart. Maybe he even created the mask, but as she grew more violent, his
heart grew cold. Agda was a bully and probably perfectly aware that Vale was
hopelessly in love with her. She 'confided' in him that her husband was the
bandit as a backup in case her husband should turn on her. Vale believed her
without question.|G

But she didn't count on Vale taking matters into his own hands. After the
incident where the Bandit nearly killed a young kid, Vale used the childmaker
potion to try to poison the Blacksmith. But the Blacksmith was so distraught
over his wife's actions that he lost his appetite and Agda ate his pie instead.|g

The reason the Mute Monkey Bandit disappeared is because Agda's mind was ruined
by Vale's potion. He got the right villain by accident.|n
"""

ENDING_MONKEY_JESTER = """
|gAfter having thought back and forth on it, you wonder if |wthe Jester
herself|g is the Mute Monkey Bandit!|G

The Jester knows some magic and has done some impressive research. Everyone
says that The Jester's older than she looks. She came to the village pretty
recently - but still everyone says that it's like she's always been here ...|g

The Magus's grandfather called the childmaker potion the 'potion of youth'.
Maybe someone else also ate that pie together with Agda? Agda turned into a
wreck, maybe the other person instead stayed young?|G

Also, why was the Monkey bandit wearing a mask? Why was he mute? Because he was
a woman! After the pie, the bandit left (maybe it had side effects?) and only
recently came back in the guise of the Jester.

"""

ENDING_MONKEY_OTHER = """
|gAfter thinking about it, you are not sure the Mute monkey bandit was ever more
than a legend. A local bandit with a mask probably existed but over the years
his legend grew.|G

The Jester loves stories and legends. She took this one and expanded on it with
a whole fanciful mystery for the sake of her little 'game'. She even ordered a
toy monkey with a look based on the old poster!|g

If the original bandit ever existed he is probably either dead or very old by
now awyway.|n

"""

ENDING_MONKEY_MAP = {
    "MAGUS": ENDING_MONKEY_MAGUS,
    "BLACKSMITH": ENDING_MONKEY_BLACKSMITH,
    "BAKER": ENDING_MONKEY_BAKER,
    "JESTER": ENDING_MONKEY_JESTER,
    "OTHER": ENDING_MONKEY_OTHER}

# knowing the jester's maiden name

ENDING_MAIDEN_NAME_MAGUS = """
|gYou turn up on bridge across the river. You think you know what the Jester's
maiden name must be. It is |wBloch|g, as in the Magus' last name.|G

The Jester spends a lot of time over at the Magus' house. She sits and listen
to him talk for hours on end. The old man clearly likes to keep him around,
he even tells her about his experiments.|g

The monkey made it clear that the Jester can't take things seriously even if
she wanted. She could maybe not tell you this herself, but had to device this
strange game for you to figure it out on your own.|G

The Magus and his damned 'childmaker' potion. By accident he poisoned Agda with
it, but how did he know it worked on humans? He only mentions a cat in the
recipe. The Jester sure acts like a child, yet everyone thinks she's probably
older than she acts and looks.  What if the Jester is one of his early
experiments? He could have adopted her as her daughter in that case.|g

He could have sent her away and only now arranged to get her back, to see the
effects of his potion over a long time. He'd want to know that if he wants
to help Agda ... |n

"""

ENDING_MAIDEN_NAME_BLACKSMITH = """
|gAs you turn the corner and step up on the bridge across the river, you realize
that you know what the Jester's maiden name is. It is |wWarwick|g, as in the
Blacksmith. The Jester's notes suggest that Maiden names are always taken from
the -father- in these parts after all.|G

The Jester seems to think the Blacksmith and the Baker are married but are now
living apart. Agda was poisoned by the Vale's potion and that messed her up. In
his letter he also mentions 'her other condition'. This could meant that Agda
was pregnant when she got the childmaker potion. The letter also suggests that
Agda's child was sent away since she was unable to care for another life.|g

The notes for the childmaker potion tells about the experiment with a cat and
its kittens. If the childmaker affects a kitten, maybe it also affects a child
...  A child that grew up outside the village and only came to search her roots
just recently. A child that had grown up and yet never truly did.|G

The Jester is none other than the daughter of Agda and Angus Warwick!|g

They probably doesn't know who she is either. The monkey said that the Jester
cannot handle being serious even if she wants to. Maybe this 'game' of hers was
her way of telling her story in the most convoluted way possible ...|n
"""

ENDING_MAIDEN_NAME_BAKER = """
|gAs you turn the the corner and step up onto the bridge across the river,
you ponder the possibility that |wBullington|g is the Jester's maiden name.|G

Mrs Bullington has lived alone for a long time and she's pretty weird. But the
Jester is also pretty weird! And in her notes she did show a large amount of
interest in the baker.|g

The Jester suggests in her texs that Mrs Bullington was married at some point,
but that 'Bullington' he Baker's own maiden name. This is why the Jester
researched maiden names in her book! For the Jester to have her name, she must
either have gotten the child before the marriage or after being separated or
divorced for a long time. She was completely messed up by Vale's potion, so it
must have happened before the marriage then.|G

That would make the Jester the baker's illegitimate daughter!|n
"""


ENDING_MAIDEN_NAME_OTHER = """
|gAs you turn the corner and step up onto the bridge across the river, you are
not sure if Jesters even -have- maiden names.|G

The Jester is the kind of person that could just have spawned fully formed and
then never change after that day. The thought of Jesters popping up out of the
ground is both amusing and disturbing as you quicken your steps ...|n

"""

ENDING_MAIDEN_NAME_MAP = {
    "MAGUS": ENDING_MAIDEN_NAME_MAGUS,
    "BLACKSMITH": ENDING_MAIDEN_NAME_BLACKSMITH,
    "BAKER": ENDING_MAIDEN_NAME_BAKER,
    "OTHER": ENDING_MAIDEN_NAME_OTHER}


ENDING_END = """

|g~ THE END ~|n

|x- a game by Griatch, May 2019|n

"""


def get_endings(stats):
    """
    Figure out which ending sequence to use

    Args:
        stats (dict): Calculated from the score.

    Returns:
        endings (list): Sequence of ending texts to cycle through.

    """
    endings = []

    # the 'thinking' scenes depend on how the questions were answered.

    question1, question2, question3 = stats['question1'], stats['question2'], stats['question3']

    endings.append(ENDING_VALE_MAP.get(question1))
    endings.append(ENDING_MONKEY_MAP.get(question2))
    endings.append(ENDING_MAIDEN_NAME_MAP.get(question3))

    # the outcome of the contest is based on score and number of hintberry pies

    score_percent = stats['adjusted_score_percent']
    name = stats['char_name']
    desc = stats['char_desc']

    if score_percent < 40:
        # a failure - we were too late
        endings.extend([
            ENDING_CONTEST_INTRO_1,
            ENDING_CONTEST_INTRO_2.format(spectator="Magus", name=name),
            ENDING_CONTEST_MISSED_1,
            ENDING_CONTEST_MISSED_2])
    elif 40 <= score_percent < 70:
        # we get there, but are defeated
        endings.extend([
            ENDING_CONTEST_INTRO_1,
            ENDING_CONTEST_INTRO_2.format(spectator="Magus", name=name),
            ENDING_CONTEST_DEFEAT_1,
            ENDING_CONTEST_DEFEAT_2])
    elif 70 <= score_percent < 95:
        # we get there and win
        endings.extend([
            ENDING_CONTEST_INTRO_1,
            ENDING_CONTEST_INTRO_2.format(spectator="Blacksmith", name=name),
            ENDING_CONTEST_WIN_1,
            ENDING_CONTEST_WIN_2])
    else:
        # we get there and OWN
        endings.extend([
            ENDING_CONTEST_INTRO_1,
            ENDING_CONTEST_INTRO_2.format(spectator="Blacksmith", name=name),
            ENDING_CONTEST_DOMINATE_1,
            ENDING_CONTEST_DOMINATE_2])

    return endings + [ENDING_END]


# ------------------------------------------------------------
# Custom command for stepping forward
# ------------------------------------------------------------

# identify answers

ANSWER_MAP_QUESTION_1 = {
    "bloch": "MAGUS",
    "vale bloch": "MAGUS",
    "master vale bloch": "MAGUS",
    "mr vale bloch": "MAGUS",
    "warwick": "BLACKSMITH",
    "warvick": "BLACKSMITH",  # accept misspelling too
    "varvick": "BLACKSMITH",  # accept misspelling too
    "vale warwick": "BLACKSMITH",
    "master vale warwick": "BLACKSMITH",
    "jester": "JESTER",
    "bullington": "BAKER",
    "bulington": "BAKER",  # accept misspelling
    "bullinton": "BAKER",  # accept misspelling
    "vale bullington": "BAKER"}

ANSWER_MAP_QUESTION_2 = {
    "jester": "JESTER",
    "vale": "MAGUS",
    "angus": "BLACKSMITH",
    "agda": "BAKER"}

ANSWER_MAP_QUESTION_3 = {
    "warwick": "BLACKSMITH",
    "bullington": "BAKER",
    "bloch": "MAGUS"}


class CmdHandleEnding(CmdEvscapeRoom):
    """
    Ask questions - capture all input
    """
    key = "_startending"

    def func(self):

        caller = self.caller

        room = self.room

        caller.msg(INTRO_TEXT2.strip())
        yield("(press return to continue)")

        # question one
        caller.msg(QUESTION1.lstrip())
        confirm = 'N'
        while True:
            reply1 = yield(" (write your answer)")
            if not reply1:
                cnf = "You don't think Vale has a last name. "
            else:
                cnf = f"You think Vale's full name is '{reply1.capitalize()}'. "

            confirm = yield(cnf + f"Is this what you think? |g[Y]|n/|rN|n")
            if not confirm or confirm.upper() in ('Y', 'YES'):
                break
        answer = ANSWER_MAP_QUESTION_1.get(reply1.strip().lower(), "OTHER")
        room.log(f"Question 1: {caller} answered '{reply1.strip()}' ({answer})")
        room.set_character_flag(caller, "question1", value=answer)

        # question two
        caller.msg(QUESTION2.lstrip())
        confirm = 'N'
        while True:
            reply2 = yield(" (write your answer)")
            if not reply2:
                cnf = "You don't think the monkey bandit is real. "
            else:
                cnf = f"You think the bandit's name is '{reply2.capitalize()}'. "

            confirm = yield(cnf + "Is this what you think? |g[Y]|n/|rN|n")
            if not confirm or confirm.upper() in ('Y', 'YES'):
                break
        answer = ANSWER_MAP_QUESTION_2.get(reply2.strip().lower(), "OTHER")
        room.log(f"Question 2: {caller} answered '{reply2.strip()}' ({answer})")
        room.set_character_flag(caller, "question2", value=answer)

        # question three
        caller.msg(QUESTION3.lstrip())
        confirm = 'N'
        while True:
            reply3 = yield(" (write your answer)")
            if not reply3:
                cnf = "You don't think she has a maiden name. "
            else:
                cnf = f"You think her maiden name is '{reply3.capitalize()}'. "

            confirm = yield(cnf + "Is this what you think? |g[Y]|n/|rN|n")
            if not confirm or confirm.upper() in ('Y', 'YES'):
                break
        answer = ANSWER_MAP_QUESTION_3.get(reply3.strip().lower(), "OTHER")
        room.log(f"Question 3: {caller} answered '{reply3.strip()}' ({answer})")
        room.set_character_flag(caller, "question3", value=answer)

        # get individualized stats
        stats = collect_stats(caller, room)

        scoreboard = SCOREBOARD.format(**stats)

        room.log(scoreboard)

        # figure out endings and run them
        endings = get_endings(stats)
        for ending in endings:
            caller.msg(msg_cinematic(ending.strip()))
            yield(" (press return to continue)")

        # show scoreboard
        caller.msg(display_score(scoreboard))
        room.log(f"{caller} watched cinematic and scoreboard")

        yield(" (press return to exit the game and go back to Evscaperoom menu)")

        # note - when the last char leaves the room will delete itself.
        self.room.character_exit(caller)


class EndingCmdSet(CmdSet):

    key = "endings"
    priority = 2
    merge_type = "Replace"

    def at_cmdset_creation(self):
        self.add(CmdHandleEnding())


# ------------------------------------------------------------
# Base state
# ------------------------------------------------------------


class State(BaseState):

    def character_enters(self, character):
        self.cinematic(GREETING.format(name=character.key),
                       target=character)

    def init(self):

        for char in self.room.get_all_characters():
            # we can't have this cmdset on the room, the
            # interactivity of it gets cross-used.
            char.cmdset.add(EndingCmdSet)
            char.execute_cmd("_startending")

        # we need to stop Vale's chatter
        vale = self.get_object("Vale")
        if vale:
            vale.delete()

        # we want interactivity here, so we ask the user to press return, which
        # will trigger the CmdAskQuestions command.
        self.msg(INTRO_TEXT1.strip(), borders=False)

    def clear(self):
        self.room.cmdset.remove("endings")
