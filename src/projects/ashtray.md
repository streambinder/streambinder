# About

## What is it

**Ashtray** is a custom and private `eopkg` repository. `eopkg` is the packaging format conceived and adopted by [Solus-Project](https://getsol.us), a Linux desktop distribution built from scratch.

This private repository was born by the need of having a place where to put custom packages which were not included by default on official repository.

The most important component hosted on this repository is Pantheon Desktop, which is the Desktop Environment developed by the [Elementary OS](https://elementary.io) team and which hasn't been included on Solus-Project repository due to [legitimate reasons](https://discuss.getsol.us/d/1500-how-to-generate-custom-iso/12). This is the answer I got from one of the development team members as a reply to my _why won't Pantheon Desktop be officially supported?_:

> Because Pantheon, first-and-foremost, is designed **for** elementary OS. To such a degree that I had to patch Granite, their toolkit that everything of theirs uses, to not segfault when using DateTime APIs when it **assumed** you had their Pantheon schemas for time set. And working with them as a downstream would be miserable, they can't even merge a single one of my PRs in. Fixing an entire desktop and all their applications to work **as we expect** them to? That's a hard nope.
>
> Pantheon, like Cinnamon, XFCE, etc. will never be supported or provided by us.

# Installation

As any other Solus-Project handled repository, you can use `eopkg *-repo` subcommands to handle this one. Hence, the installation instruction is pretty straightforward:

```bash
eopkg add-repo streambinder https://solus.davidepucci.it/eopkg-index.xml.xz
```

If you want it to point to a specific GitHub release - represented by the `$TAG` variable:

```bash
tag="https://github.com/streambinder/ashtray/releases/download/v1"
eopkg add-repo streambinder "${tag}/eopkg-index.xml.xz
```

You may notice in the first case `solus.davidepucci.it` host name gets used, while in the latter you would be pointing directly to the GitHub repository: I get more in depth about this on the [Infrastructure page](infrastructure.md#packages-free-hosting).

# Infrastructure

The whole thing started while trying to package a tool that wasn't part of the official Solus-Project repository: it's back then I found out the work done by [Devil505](https://gitlab.com/devil505).

He basically had done what I wanted in a slightly messier way, but the idea behind the project was the same I had: collecting packages that the Solus-Project would have not included in the official repository, while being able to handle the whole thing in a single Git repository.

## Git repository structure standardization

The first thing I reorganized has been the physical repository file organization, hence the choice to move all the packages templates in a dedicated `src` folder and drop all the `eopkg` (the effective package files).

The main reason to drop out all the `eopkg` files was about the fact it could have lead to a very heavy repository, while Git has not been built to host binary files. On the other hand, GitHub is offering the _Releases_ functionality which is actually more about file hosting (and projects releases, indeed), so I preferred to differentiate the roles: the repository would have kept all the packages `yml` templates, the instructions needed to build them, while the _Releases_ would have wrapped the effective `eopkg` supported repository, keeping all the history of repository's packages updates.

## Incremental and automated building

The repository offers a `Makefile` to batch _do things_, such as running a common repository full build or a check for packages pending updates.

The order used by the `Makefile` to build files is imposed by the `src/series` file: this is needed as several packages have build dependencies _inside_ the repository itself. Hence, the `series` file splits all the packages in several subsequent iteration groups, which assure that a specific `package-x` gets built and indexed on the local (in-build) repository before the depending `package-y` package.

Also, in order to make the whole process work, `solbuild` (the tool used to build the package starting from a `package.yml` template) needs to be configured to treat the local build directory as a local repository. This can be done by editing the `/usr/share/solbuild/main-x86_64.profile` settings and adding the following lines:

```go
remove_repos = ["Solus"]
add_repos = ["Local", "Ashtray", "Solus"]

[repo.Local]
uri = "/path/to/ashtray/bin"
local = true
autoindex = true

[repo.Ashtray]
uri = "https://solus.davidepucci.it/eopkg-index.xml.xz"

[repo.Solus]
uri = "https://mirrors.rit.edu/solus/packages/shannon/eopkg-index.xml.xz"
```

## Packages (free) hosting

This section resumes what was outlined in the [About page](about.md#installation).

Basically, the whole repository is hosted on GitHub: the packages templates and build instructions in the Git repository itself, while the built `eopkg` files and the indexes are kept in dedicated repository releases.

The issues I faced were the following:

1. the repository URL was way too long and complicated to be easily remembered;
2. `eopkg` repository management does not support repository URL redirections: this means `github.com/streambinder/ashtray/releases/latest` could not be used as repository URL and that the only way to offer the repository without additional headaches was to create a single fixed release, which would have been filled with any package updates everytime it was needed.

These two issues lead to the additional headache of configuring a custom web server which translates the requests made to `https://solus.davidepucci.it` to the latest GitHub repository release, by rewriting the request `Location` header. This gets done with this little PHP snippet:

```php
<?php

if (strlen($_SERVER['REQUEST_URI']) == 0
        || strcmp($_SERVER['REQUEST_URI'], '/') == 0) {
    header("location: https://doc.davidepucci.it/p/ashtray");
    return;
}

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, 'https://github.com/streambinder/ashtray/releases/latest');
curl_setopt($ch, CURLOPT_HEADER, true);
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_exec($ch);
$ch_url = curl_getinfo($ch, CURLINFO_EFFECTIVE_URL);
$ch_download_url = str_replace('/tag/', '/download/', $ch_url);
header("location: ".$ch_download_url.$_SERVER['REQUEST_URI']);

?>
```

This way, the `solus.davidepucci.it` host behaves as a poor proxy, redirecting dynamically the requests without taking charge of the traffic generated by repository indexes and packages downloads.

Also, this `.htaccess` is used to forward all the files `GET` requests to the PHP snippet above:

```
RewriteEngine on
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^.*$ /index.php [L,QSA]
```

# Solbump

Solbump is a tool to automatically upgrade `eopkg` YAML-formatted source files to latest releases. Hence, the naming similarity with `solbuild`, the tool made from Solus project core team to build `eopkg` packages.

Based on the amount of defined (and pluggable) providers, it tries to recognize the format of the tarballs or archives defined as source files from the YAML file and find a matching provider. Then it's able to query for a more updated release and, if so, it fetches the asset, calculates the hashsum and update the original `package.yml` coherently.

## Usage

Before starting using the tool, further actions need to be taken, in order to access all its capabilities. In fact, few providers could be in the need of API tokens or specific configurations. So create the configuration file at `~/.config/solbump` and, depending on your needs, fill it with data you own:

```yaml
# To obtain the token, go to:
# 
# Solbump does not require any scope to be enabled.
github:
    api: habmfnlzrwmxuopmjganlqfpmccouxieijlouxcl

# To obtain the token, go to:
# https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html
# Solbump requires only the API access scope enablement.
gitlab:
    api: hmlhnbzndrogcifs-akb
```

Using the tool is pretty straightforward:

```bash
solbump package1.yml package2/package.yml
```

## Installation

### Package manager

Installation from repositories is only available for Solus-Project users which have enabled [`ashtray`](./) repository:

```bash
eopkg it -y solbump
```

### GO toolset

```bash
go get github.com/streambinder/solbump
```
