# About

Spotitube is a CLI application to programmatically authenticate to your Spotify account, fetch some music collections and synchronize them locally relying on a set of providers, keeping track of playlists files, inserting metadata informations, album artworks, songs lyrics and maximizing audio quality.

The project was born as per two needs. First one was wanting to learn some _GO-lang_ basics. And, on the other hand, I needed to automate the process of synchronize the songs I wanted to download, which was composed by the following phases:

- Keep track of music I want to download
- Find the best song file I can
- Download it
- Apply correct metadata

## Usage

The most common way to use it is to synchronize your library:

```bash
spotitube -folder ~/Music
```

If you want to synchronize a playlist/album:

```bash
spotitube -folder ~/Music -playlist $playlist_uid -album $album_uid
```

Spotitube supports aggregating multiple collections in a single synchronization flow:

```bash
# library synchronization is done by default
# if no other collection is asked
spotitube -folder ~/Music
# to synchronize both a playlist/album and the library
spotitube -folder ~/Music \
    -playlist $playlist_uid \
    -library
# to synchronize a playlist/album and fix some already
# synchronized tracks
spotitube -folder ~/Music \
    -album $album_uid \
    -fix "~/Music/Artist - Song.mp3"
```

As have been noticed, few flags tend to be always unchanged, as the `-folder` or the `-playlist` , and it's either boring to always write them if they stick to the same value, or difficult to remember them. To simplify the management of such scenario, a configuration file can be used:

```yaml
# the value below is used in case no -folder flag
# is passed exlicitely to spotitube
folder: ~/Music
# the values of these aliases are possibly replaced
# with the ones passed as -playlist|album flags values
aliases:
    - my_playlist: spotify:playlist:whateverUid
    - another_playlist: spotify:playlist:anotherUid
```

### Troubleshooting

Few additional flags have been implemented to simplify the troubleshooting and bugfixing process:

1. `-log` will append every output line of the application to a logfile, located inside the `-folder` the music is getting synchronized in.
2. `-debug` will show additional and detailed messages about the flow that brought the code to choose a song, instead of another, for example. Also, this flag will disable parallelism, in order to have a clearer and more ordered output.
3. `-simulate` will make the process flow till the download step, without proceeding on its way. It's useful to check if searching for results and filtering steps are doing their job.
4. `-disable-gui` will make the application output flow as a simple CLI application, dropping all the noise brought by the GUI-like aesthetics.

# Installation

Spotitube binaries and packages are hosted on GitHub, in project's [_Releases_ section](https://github.com/streambinder/spotitube/releases). It actually supports all the common platforms known, such as generic Linux/Unix systems and Windows.

For Solus-Project, RedHat-based, Debian-based distributions users, there's an installable package, while for the others Linux/Unix systems users a generic binary can be used. For Windows users, an _exe_ binary variant is there, too.

## Dependencies

Dependencies on which the code base is relying to be provenly working follow:

Name         | Type    | Version
:----------- | :------ | :------
`golang`     | compile | 1.14.2
`youtube-dl` | runtime | latest
`ffmpeg`     | runtime | 4.2.2
`xdg-open`   | runtime | 1.1.3

## Updating

Theoretically, Spotitube is taught to be self-updated if not running an updated version. Anyway, nothing forbids you to download and install latest package/binary over the old one.

## Package manager

Installation from repositories is only available for Solus-Project users which have enabled [`ashtray`](/ashtray/) repository:

```bash
eopkg it -y spotitube
```

## Building from source

Behind this tool there's a Spotify application that gets called during the authentication phase, which Spotify gives permissions to, to read many informations, such as the user name, library and playlists. When you use _Spotitube_ for the very first time, Spotify will ask you if you really want to grant this informations to it.

The Spotify application gets linked to this go-lang code using the `SPOTIFY_ID` and the `SPOITIFY_KEY` provided by Spotify to the user who created the application (me). It's not a good deal to publicly hardcode these application credentials into the source code (as I previously was doing), letting anyone to see and use the same ones and letting anyone to pretend to be _Spotitube_, being then able to steal such informations, hiding his real identity. This is the reason behind the choice to hide those credentials from the source code, and applying - expliciting as environment variables - them during the compilation phase.

If you want, you can easily create an application to the Spotify [developer area](https://beta.developer.spotify.com/dashboard/applications) and use your own API credentials.

For the ones moving this way, `SPOTIFY_KEY` is associated to `SPOTIFY_ID` : if you create your own app, remember to override both values provided to you by Spotify developers dashboard. In order to do so, keep in mind that during the compilation phase, if `SPOTIFY_KEY` and `SPOTIFY_ID` variables are shell-exported as environment keys, the build instructions will take care of hardcoding them into the binary. If no environment key is found, the resulting binary will need ones everytime its getting executed (still, as environment keys).

By default, the application is coded to use the following redirect URIs:

- `http://127.0.0.1:8080/callback`
- `http://localhost:8080/callback`
- `http://spotitube.local:8080/callback`

Assure you configure your Spotify application to allow them.

### Build instructions

```bash
go get github.com/dreadl0ck/zeus
git clone https://github.com/streambinder/spotitube
cd spotitube
zeus build-linux|build-windows
```

If you want to install it widely in the system:

```bash
zeus install
```

Passing Spotify API credentials:

```bash
# the following SPOTIFY_ID and SPOTIFY_KEY are bogus
SPOTIFY_ID=YJ5U6TSB317572L40EMQQPVEI2HICXFL \
    SPOTIFY_KEY=4SW2W3ICZ3DPY6NWC88UFJDBCZJAQA8J \
    zeus build-linux|build-windows
```

### Build using Go tool

As Spotitube is built in Go, you can use the standard method to build it:

```bash
go get github.com/streambinder/spotitube
```

Anyway, take into account that this method won't hardcode Spotify API credentials: as already mentioned, you will need to make them exported at runtime.

### Running on Windows

- For each of the following assets, either install it (making sure their binary path is exported as part of the `%PATH%` variable) or put it in the same folder: `youtube-dl` ([ytdl-org.github.io/youtube-dl](https://ytdl-org.github.io/youtube-dl/download.html)), `ffmpeg` ([ffmpeg.zeranoe.com](https://ffmpeg.zeranoe.com/builds/)), `spotitube` (pick the `exe` variant release).
- Enter the `cmd`
- If you didn't follow the `%PATH%` method, enter the folder in which all the downloaded assets are located
- Run `spotitube` and enjoy

# Engineering

## Execution phases

The solution I wrote to automate the process is covered by three major components:

- **Authentication and data fetching phase:** _**Spotify**_

  This component, once authenticated, is used to keep track of the music to synchronize (both via library or a playlist) and as database for the metadata to apply to every downloaded _mp3_.

- **Searching phase: download providers, such as** _**YouTube**_

  This one is our free music shop, used to be queried to give us the best video it owns about the songs we're looking for.

- **Lyrics fetching phase: lyrics providers, such as** _**Genius**_ **or** _**lyrics.ovh**_

  You will go through this component if you'll enable automatic songs lyrics fetch: _Spotify_ informations about song will be used to find lyrics provided by two entities: _Genius_ and, eventually, if the first one doesn't own it, _lyrics.ovh_.

## Reliability

Several tests got made during the drawing up of the application and now I can say its pretty good at choosing the right song out of a list of keywords (such as the title and the user of any _YouTube_ video).

### Latest statistics

Latest verified statistics describes a sample of 396 songs, cumulative of different musical genres: _rock_, _pop_, _disco_ - _house_, _dubstep_ and _remixes_ -, _chamber music_, _soundtrack_, _folk_, _indie_, _punk_, and many others. Also, they belonged to several decades, with songs from 1975 or up to 2017\. They were produced by many and very different artists, such as _Kodaline_, _Don Diablo_, _OneRepublic_, _The Cinematic Orchestra_, _Sigur Ros_, _Rooney_, _Royal Blood_, _Antonello Venditti_, _Skrillex_, _Savant_, _Knife Party_, _Yann Tiersen_, _Celine Dion_, _The Lumineers_, _alt-J_, _Mumford & Sons_, _Patrick Park_, _Jake Bugg_, _About Wayne_, _Arctic Monkeys_, _The Offspring_, _Maitre Gims_, _Thegiornalisti_, _Glee_ cast, _One Direction_, _Baustelle_, _Kaleo_, _La La Land_ cast, and many, many more.

The result of `spotitube` execution:

Type               | Quantity (of 396)
:----------------- | :----------------
Songs _not found_  | **13**
Found, but _wrong_ | **22**
Found, and _right_ | **361**

In other words, we could say `spotitube` behaved as it was expected to both for _songs not found_ and _found, and right_. In fact, in the first case, the greatest part of the _not found_ songs were actually really not found on _YouTube_.

Type    | Percentage
:------ | :---------
Success | **95%**
Failure | **5%**

### Getting always better

The code can surely be taught to behave always better, but there will always be a small percentage of failures, caused by the specific download provider uploaders, which are very often unable to specify what a video actually is containing and synthesize it in a title that is not ambiguous (I'm thinking about, for example, the case of a really talented teenager who posts his first cover video, without specifying that it actually is a cover). The more you'll get involved on improve `spotitube` , the more you'll notice how lot of things are ambigous and thinking of a way to workaround this ambiguity would bring the project to be too much selective, losing useful results.

# FAQ

## **How to pull out URI from playlist**

// TODO

## **Empty or not recognized playlists on Android**

Android delegates the indexing of every media file stored into internal/external storage to a service called MediaScanner, which gets executed to find any new or deprecated file and to update a database filled with all those entries, MediaStore. This is basically done to let every app be faster to find files on storage, relying on this service rather than on specific implementations.

In few cases, some issues got encountered while testing SpotiTube generated playlists, recognized as empty on Android. After some investigations, it seems that MediaScanner defers the `.m3u` (playlist file) - the same with `.pls` file - effective parsing, in a actually not understood way: it immediately find the physical playlist file, but its informations will never be parsed.

A simple workaround for the ones experiencing this kind of issues, is to run this shell snippet:

```bash
adb shell "am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE \
    -d file:///sdcard/path/to/playlist/file"
sleep 5
adb reboot
```
