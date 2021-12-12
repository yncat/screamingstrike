# Screaming Strike

## Intro

I decided to opensource this.

## Dependencies

Windows: pip install -r requirements-win.txt

Mac: pip3 install -r requirements-mac.txt

## Running from source

Windows: python ss.py

Mac: python3 ss.py

## Other useful commands

Note: If You're using mac, you need to use / instead of \ (on windows you can use both \ and /).

Windows: python tools/build.py

Mac: python3 tools/build.py

Builds the app on win and mac. Please read the following building section for details.

Windows: python tools/updateTranslation.py

Mac: python3 tools/updateTranslation.py

Updates the translation catalog. Currently, cannot be executed on mac. Please read the following translating section for details.

Windows: python tools/buildTranslation.py

Compiles your edited translation catalogs. Currently, it cannot be executed on mac.

Windows: python tools/initdoc.py

Mac: python3 tools/initdoc.py

Initializes auto document creation. Please read the auto documentation section for details.

Windows: python build/gendoc.py

Mac: python3 build/gendoc.py

to generate the API document.

## Building

The game uses pyinstaller for building.

For automated packaging for Windows, WinRAR must be installed and WinRAR.exe must be accessible from the environment variable path.

## Codesigning and notarization on Mac

Build.py runs codesign command to sign all executables in the app bundle. You must have Apple Developer payd membership for issuing your own developer certificate and correctly set it up in your keychain. You will need to change the certificate identifier in the build script to your matching. I haven't made it so that the values can be loaded for the env var.

After running build.py, the script creates build/screamingStrike2.zip for notarization.

Run

`xcrun altool --notarize-app -t osx -f build/screamingStrike2.zip --primary-bundle-id "com.your.identifier" --asc-provider "provider_short_name" -u "your@apple.id" -p "your_app_password"`

To notarize.

com.your.identifier should be changed to your own app identifier. You can choose whatever you like, using alphabets and numbers. com.orgname.appname is the common pattern.

provider_short_name is not necessary if you have only one provider (I don't know how the number of providers increase, I had two). If you have multiple providers, you need to substitute the the provider short name that you want to use. Your providers can be listed by running `xcrun altool --list-providers -u "your@apple.id" -p "app_specific_password"` .

`your@apple.id` must be replaced with your apple ID (email).

app_specific_password can be generated from apple ID account dashboard page. You cannot authenticate altool access with your apple ID password; you need to generate one.

You will receive an email informing that your app has successfully been notarized after several minutes. Once it's done, run the following.

`python3 tools/after_notarization_zip.py`

This will staple the notarization ticket to the app, compress it to a dmg and codesign the dmg. After that, run the following.

`xcrun altool --notarize-app -t osx -f build/screamingStrike2.dmg --primary-bundle-id "com.your.identifier" --asc-provider "provider_short_name" -u "your@apple.id" -p "your_app_password"`

Now, the app and its container dmg is both notarized. Finally, run

`python3 tools/after_notarization_dmg.py`

to staple the notarization ticket to the dmg.

You can distribute the dmg!

## Translating

Sorry, it works only on Windows right now.

First, create folder for your language in the locale folder (E.G. ja-JP).

Run 'python tools/updateTranslation.py'

Edit the catalog file in the lc_messages folder under your created folder.

Run 'python tools/buildTranslation.py'

Your added language should be selectable from the options menu.

## API reference

You need sphinx.

pip install sphinx

run the following commands to generate the API reference, which may help you how the game is coded. There's missing docstrings here and there, so a small part of the API reference may have less detailed info.

python tools/initdoc.py

python tools/gendoc.py

On mac, change python to python3.

## Contributing

Please post issues / suggestions / ideas to the issue tracking in this repository. If you did something interesting, feel free to send pull requests.
