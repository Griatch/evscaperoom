r"""
Evennia settings file.

The available options are found in the default settings file found
here:

/home/griatch/Devel/Home/evennia/evennia/evennia/settings_default.py

Remember:

Don't copy more from the default file than you actually intend to
change; this will make sure that you don't overload upstream updates
unnecessarily.

When changing a setting requiring a file system path (like
path/to/actual/file.py), use GAME_DIR and EVENNIA_DIR to reference
your game folder and the Evennia library folders respectively. Python
paths (path.to.module) should be given relative to the game's root
folder (typeclasses.foo) whereas paths within the Evennia library
needs to be given explicitly (evennia.foo).

If you want to share your game dir, including its settings, you can
put secret game- or server-specific settings in secret_settings.py.

"""

# Use the defaults from Evennia unless explicitly overridden
from evennia.settings_default import *

######################################################################
# Evennia base server config
######################################################################

# This is the name of your game. Make it catchy!
SERVERNAME = "EvscapeRoom"

TYPECLASS_PATHS += ["evscaperoom"]

IDLE_TIMEOUT = 7 * 24 * 3600

GUEST_ENABLED = True

GUEST_LIST = ["Avofee", "Bergine", "Caerin", "Duvoe", "Ergaloe", "Farala",
              "Gilse", "Hikatec", "Iirvaline", "Jegrasz", "Karahtine",
              "Liratac", "Medue", "Nycewa", "Oloat", "Pyrreni", "Qurran",
              "Riftdin", "Saela", "Turvadi", "Uiviite", "Vegdarin", "Xinai",
              "Ylveur", "Zatharyn"]

GAME_INDEX_LISTING = {
    'game_status': 'launched',
    # Optional, comment out or remove if N/A
    'game_website': 'http://experimental.evennia.com',
    'short_description': "Multiplayer 'escape-room' with full story",
    # Optional but highly recommended. Markdown is supported"
    'long_description': (
        """This is a multiplayer 'escape room' created in Evennia. It has a
        (maybe surprisingly deep) story with creepy monkeys, silly antics and
        pie. Lots of pie.\n\nThe Evscaperoom was created in a month for the Game Creator's Guild's
        second Game Jam, which had the theme *One Room*.\n\nTry it out! The engine will 
        likely become an Evennia contrib. The source code is available online (see website)."""
    ),
    'listing_contact': 'griatch@gmail.com',
    # At minimum, specify this or the web_client_url options. Both is fine, too.
    'telnet_hostname': '128.199.48.138',
    'telnet_port': 4000,
    # At minimum, specify this or the telnet_* options. Both is fine, too.
    'web_client_url': 'http://experimental.evennia.com/webclient',
}

######################################################################
# Settings given in secret_settings.py override those in this file.
######################################################################
try:
    from server.conf.secret_settings import *
except ImportError:
    print("secret_settings.py file not found or failed to import.")
