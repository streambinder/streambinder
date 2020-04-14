# About

Paperboy is a simple CLI application which sends a GTK notification when an email is received, allowing the user to just click on the callback button to open the webmail associated to the account.

In order to do what's been described:

- it registers a `GApplication` through which to make GTK notifications flow
- for each account defined, it connects to the corresponding IMAP server, querying for `UNSEEN` emails
- if any, it fires a notification mapping a callback button to the opening of the webmail URL corresponding to the account

## How to use

Usage is very straightforward, as all the options are passed via a configuration file:

```bash
paperboy -c ~/.config/paperboy
```

The configuration is YAML-formatted and should respect the following sample structure:

```yaml
accounts:
  - alias: "Name"
    address: "email@addre.ss"
    password: "pa$word"
    hostname: "imap.host.name"
    proto: "imaps"
    port: "993"
    url: "https://url.to/webmail"
```

### Scheduling checks

In order to make recurrent IMAP checks, there're multiple cron options. Below the implementation using systemd timers to run a check every 5 minutes:

- Timer unit at `~/.config/systemd/user/paperboy.timer`

```
[Unit]
Description=PaperBoy timer

[Timer]
Unit=paperboy.service
OnCalendar=*-*-* *:00/5
Persistent=true

[Install]
WantedBy=timers.target
```

- Service unit at `~/.config/systemd/user/paperboy.service`

```
[Unit]
Description=PaperBoy service

[Service]
Type=simple
ExecStart=%h/.local/bin/paperboy -c  %h/.config/paperboy
```

- Enablement:

```bash
systemctl --user daemon-reload
systemctl --user enable paperboy.timer
systemctl --user start paperboy.timer
```

# Installation

## Package manager

Installation from repositories is only available for Solus-Project users which have enabled [`ashtray`](/doc/ashtray) repository:

```bash
eopkg it -y paperboy
```

## Run latest source code

```bash
git clone https://github.com/streambinder/paperboy.git
cd paperboy
make
make install
```

### Dependencies

Name       | Type        | Version (tested)
:--------- | :---------- | :---------------
`libgtk-3` | compilation | 3.24.16
`libyaml`  | compilation | 0.2.2
`libcurl`  | compilation | 7.69.1
`xdg-open` | runtime     | 1.1.3
