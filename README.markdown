Enemies of Carlotta 
===================

Enemies of Carlotta is a simple mailing list manager. It tries to
mimic the ezmlm software somewhat, but is written completely from
scratch in Python. The original author decided he didn't want to
live with the QMail and ezmlm licenses, and couldn't find something
small and simple to replace them. 

If you can't stand to use Mailman, this is the list manager for you.

EoC supports English, Finnish, French, Spanish, and Swedish. Other
languages are trivial to add. Support for a language means that all
the mails EoC sends are sent in that language. Language is chosen
for each list separately. More translations are warmly welcome.


**Requirements**: You need Python 2.3 or newer, and lockfile (from procmail). If you are
willing to live without having headers encoded with MIME, Python 2.1 or
2.2 should also work.

To **install**, edit Makefile, set the variables `bindir` and `man1dir`,
and then run s`"make install` as root.  It is also available via
`apt-get` in Debian and Ubuntu.

Enemies of Carlotta is licensed using the GNU General Public License,
version 2.

It was originally written by Lars Wirzenius, and is now maintained
communally here at Github.

About the name
--------------

The name _Enemies of Carlotta_ comes from the movie _Dead Men Don't
Wear Plaid_, with Steve Martin in the lead role. It is a comedy and
a tribute to the old detective movies of the black-and-white era.
As part of the plot, someone makes lists of people that are the
friends or enemies of Carlotta, where Carlotta is an island where
the bad guys are. Enemies of Carlotta are therefore the good guys.

The option `--cleaning-woman` also comes from the movie. The main
character goes berserk at the mention of those words and that is
what the option does: it unsubscribes bouncing addresses from the
list.

The names were chosen because Lars liked the movie and thought the
names were funny. No sexism intended.

