# About

Chopper is a CLI application which has been built to provide a simple way to exchange all-sizes files over the internet.

It relies on generic free storage providers which offer lot of little space: Chopper basically distributes all the parts of the files over those storages building a manifest that keep tracks of all the pieces.

The resulting manifest file can then be exchanged and used to let Chopper reconstruct the original file.

## How to use

The way it can be used is very simple. If you want to _chop_ a file \(upload it and generate an exchangeable file\):

``` bash
chopper filename.mp4
```

If you want to increase _chop_ redundancy:

``` bash
chopper -r 3 filename.mp4
```

If you want to rebuild a file starting from its manifest:

``` bash
chopper build filename.chop
```

# Installation

Chopper is written using Python and has been thought to be free from every external plugin. So you won't need anything else but its source code to run it or the prebuilt binary file.

## Prebuilt binary

Head to [Chopper releases](https://github.com/streambinder/chopper) page to fetch latest binary file.

## Run latest source code

``` bash
git clone https://github.com/streambinder/chopper.git
python3 chopper/src/main.py -h
```

# Engineering

Chopper operates in two different modes: _chopping_ and _glueing_ mode. Since the latter is very easy and most of the engineering relies on the first one, that will be ignored.

## Knifing

The first part of the process relies on chopping the file in several chunks, whose size depends on which storage provider is going to be used.

Basically, Chopper will use `Knife` component to always request another chunk: this chunk is a byte sequence. In case of binary files, this chunk is translated to simple text using _base85_ algorithm. The single drawback of this, is that it results in a bigger overall file size. For instance, for every 1024 bytes of binary data requested, `Knife` will provide 1280 bytes of _base85_ encoded text.

The consequence, in case of binary files, is that for every X file data requested for a chunk, the effective payload will be slightly bigger: _(X / 4) * 5_.

That's because _base85_ algorithm needs an additional byte for every 4 bytes it's going to encode.

This means that _chopping_ a 10MB file will, at least, upload 12.5MB of data.

## Uploading and downloading chunks

The chunk upload phase is actually depending on the provider the chunk is being pushed onto.

In fact, every storage provider is extending a generic \(and abstract\) `Provider` class which imposes to define many methods, such as the most important `upload()` and `download()` ones, but also many others to make them be properly handled by the whole process, such as the following:

* `enabled()` : used to indicate whether the provider is usable or not
* `nice_name()` : used to represent in a human-readable way the provider
* `is_supporting()` : used to ask a provider if it's actually able to handle a URI to download content \(chunks\) from it
* `max_chunk_size()` : used to indicate the maximum byte size sequence allowed by the provider
* `trottle()` : used to trottle requests to the provider when a `TrottlingException` gets caught

### Upload

The entry gets a payload as argument - which is assumed to be at max as the maximum size allowed by that provider - and pack it up in a request that will be done the way the provider class is taught to.

Every upload call must return a URI - if no exception is thrown - that can be passed to the `download()` method to get the content back.

### Download

The download method accepts a URI string as argument and must always return a byte sequence.

#### Supporting new providers

The whole thing has been thought to be as extendible as possible: this means any provider can use its very own logic inside every method it must implement and override.

## Manifest

A manifest is a _base64_ encoded content which represents a JSON structured this way:

``` javascript
{
    "chunks": [{
            "md5": "3b33399a12f208075a2413114220f46c",
            "origins": [
                "https://provider1/chunk1",
                "https://provider3/chunk1"
            ]
        },
        {
            "md5": "3b33123a12f208075a2413114220f46c",
            "origins": [
                "https://provider2/chunk2",
                "https://provider1/chunk2"
            ]
        }
    ],
    "filename": "file.md",
    "binary": True
}
```

## Redundancy

In order to assure more redundancy over the data, Chopper has been taught to provide the possibility to upload every chunk on several storage providers: this obviously increase the amount of data that is being pushed, along with an increase of the probability the file will be kept safe.

