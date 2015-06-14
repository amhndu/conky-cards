#!/usr/bin/env python3
#
#  mediaplayer.py
#
#  Print the metadata of a mediaplayer on conky and control it
#  This can also be used as a stand-alone command line application
#
#  Author : Amish Naidu
#  I release this in the public domain, do with it what you want.

import dbus, argparse, subprocess

#Concat left and right, add alignr if conky_alignr is true and trunc
def fmt_field(left, right, conky_alignr, width):
    res = str(left)
    res += ':${alignr}' if conky_alignr else ': '
    res += str(right)
    if width > 0:
        return res[:width]
    else:
        return res

#Return a string containing time in HH:MM:SS format from microseconds
def fmt_time(microseconds):
    seconds = microseconds/1000000
    return '{:02}:{:02}:{:02}'.format(int(seconds//360), int((seconds%360)//60), int(seconds%60))

if __name__ == '__main__':

    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description='''\
Connect to a media player through dbus to get the metadata or control it.
This can be used to output the current track playing (and it's attributes) on *conky*
%(prog)s can print the metadata of the track currently playing and
make the player perform an action
If the bus was not found, 'Not found' will be printed.
If any property is not found, 'Unknown' will be used/printed.
The 'player' must support MPRIS 2.0''',
epilog='''\
Examples of usage:

To display the Artist, Title and Album with Clementine
  $ python3 %(prog)s clementine -atm
To display the Artist, Title, Album and Genre but this time with ${alignr} between the field and it's value
  $ python3 %(prog)s vlc -atmg -r
Using the long form arguments with Audacious
  $ python3 %(prog)s audacious --album --artist --length
To switch track
  $ python3 %(prog)s amarok --action=next
  $ python3 %(prog)s clementine --action=play

Author: Amish Naidu (amhndu --at-- gmail)
Please report any bugs.
''')


    parser.add_argument('-i', '--running', action='store_true', help="print 'yes' if the 'player' is running, 'no' otherwise")
    parser.add_argument('player', action='store',
        help="name of the player e.g. 'clementine', or 'vlc' or 'audacious' or 'xmms2'")
    parser.add_argument('-r', '--conkyalignr', action='store_true', help='Add ${alignr} before values')
    parser.add_argument('-w', '--width', type=int,
            help="Truncate lines upto 'width' characters. No limit if less than zero (default)", default=-1)
    parser.add_argument('-t', '--title', action='store_true', help='title of the track')
    parser.add_argument('-a', '--artist', action='store_true', help='artist name')
    parser.add_argument('-m', '--album', action='store_true', help='album name')
    parser.add_argument('-g', '--genre', action='store_true', help='genre of the current track')
    parser.add_argument('-y', '--year', action='store_true', help='year of the track')
    parser.add_argument('-l', '--length', action='store_true', help='lenght of the track')
    parser.add_argument('-e', '--elapsed', action='store_true', help='elapsed time for the track')
    parser.add_argument('-p', '--progress', action='store_true',
        help='progress of the track as a percent (not formatted)')
    parser.add_argument('-n', '--track', action='store_true', help='track number')
    parser.add_argument('-c', '--cover',  help='Make a (soft) symlink at the specified location to the album art')
    parser.add_argument('--cover_default', help='If the the album art could not be found from the player, make a link to this')
    parser.add_argument('--action', action='store', help='make the player perform an action : next, prev, play, pause, volume up/down by 0.1',
            choices=['next', 'prev', 'pause', 'play', 'playpause', 'volup', 'voldown'])
    args = parser.parse_args()

    try:
        #MPRIS 2.0 Spec http://specifications.freedesktop.org/mpris-spec/latest/index.html
        player = dbus.SessionBus().get_object('org.mpris.MediaPlayer2.' + args.player, '/org/mpris/MediaPlayer2')
        metadata = player.Get('org.mpris.MediaPlayer2.Player', 'Metadata',
                dbus_interface='org.freedesktop.DBus.Properties')
        running = True
    except dbus.exceptions.DBusException:
        running = False

    if args.running:
        print("yes" if running else "no")
    if not running:
        print("Not found")
    else:
        if args.artist:
            print(fmt_field('Artist',
                metadata['xesam:artist'][0] if 'xesam:artist' in metadata else 'Unknown',
                args.conkyalignr, args.width))
        if args.title:
            print(fmt_field('Title',
                metadata['xesam:title'] if 'xesam:title' in metadata else 'Unknown', args.conkyalignr, args.width))
        if args.album:
            print(fmt_field('Album',
                metadata['xesam:album'] if 'xesam:album' in metadata else 'Unknown', args.conkyalignr, args.width))
        if args.genre:
            print(fmt_field('Genre',
                metadata['xesam:genre'][0] if 'xesam:genre' in metadata else 'Unknown', args.conkyalignr, args.width))
        if args.year:
            print(fmt_field('Year',
                metadata['xesam:contentCreated'][:3] if 'xesam:contentCreated' in metadata else 'Unknown',
                args.conkyalignr, args.width))
        if args.track:
            print(fmt_field('Track',
                metadata['xesam:trackNumber'] if 'xesam:trackNumber' in metadata else 'Unknown',
                args.conkyalignr, args.width))
        if args.elapsed:
            print(fmt_field('Elapsed', fmt_time(player.Get('org.mpris.MediaPlayer2.Player', 'Position',
                dbus_interface='org.freedesktop.DBus.Properties')), args.conkyalignr, args.width))
        if args.length:
            print(fmt_field('Length',
                fmt_time(metadata['mpris:length']) if 'mpris:length' in metadata else 'Unknown',
                args.conkyalignr, args.width))
        if args.progress:
            if 'mpris:length' in metadata and metadata['mpris:length'] != 0:
                print(int(player.Get('org.mpris.MediaPlayer2.Player', 'Position',
                    dbus_interface='org.freedesktop.DBus.Properties')*100/metadata['mpris:length']))
            else:
                print('Unknown')
        if args.cover is not None:
            if 'mpris:artUrl' in metadata:
                location = metadata['mpris:artUrl'][7:]
                subprocess.call(['ln', '-sf', location, args.cover])
            elif args.cover_default is not None:
                subprocess.call(['ln', '-sf', args.cover_default, args.cover])
        if args.action is not None:
            try:
                interface = dbus.Interface(player, dbus_interface='org.mpris.MediaPlayer2.Player')
                if args.action == 'next':
                    interface.Next()
                elif args.action == 'prev':
                    interface.Previous()
                elif args.action == 'pause':
                    interface.Pause()
                elif args.action == 'play':
                    interface.Play()
                elif args.action == 'playpause':
                    interface.PlayPause()
                elif args.action == 'volup' or args.action == 'voldown':
                    volume = player.Get('org.mpris.MediaPlayer2.Player', 'Volume',
                        dbus_interface='org.freedesktop.DBus.Properties')
                    volume += 0.1 if args.action == 'volup' else -0.1
                    player.Set('org.mpris.MediaPlayer2.Player', 'Volume', volume,
                            dbus_interface='org.freedesktop.DBus.Properties')
            except:
                pass
