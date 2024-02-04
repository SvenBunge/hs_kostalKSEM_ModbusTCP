# Kostal KSEM G1 / G2 ModbusTCP (14181)

Gira Homeserver 4 Logic module to poll power values from Kostal Smart Energy Meter (KSEM) G1 / G2 via Modbus TCP.

## Developer Notes

Developed for the GIRA HomeServer 4.12. Could work with prior versions.
Licensed under the LGPL to keep all copies & forks free!

:exclamation: **If you fork this project and distribute the module by your own CHANGE the Logikbaustein-ID because 14181 is only for this one and registered to @SvenBunge !!** :exclamation:

If something doesn't work like expected: Just open an issue. Even better: Fix the issue and fill a pull request.

## Installation

Download a [release](https://github.com/SvenBunge/hs_kostalKSEM_ModbusTCP/releases) and install the module / Logikbaustein like others in Experte.
You find the module in the category "Energiemanagement". Just enter the IP address of the KSEM and wire the output to your communication objects. 

The latest version of the module is also available in the [KNX-User Forum Download Section](https://service.knx-user-forum.de/?comm=download&id=14181)

## Documentation

This module fetches power / grid information of the Kostal Smart Energy Meter (KSEM).

More [detailed documentation](doc/log14181.md)

For further questions use the [Promotion Thread](https://knx-user-forum.de/forum/%C3%B6ffentlicher-bereich/knx-eib-forum/1630161-logikbaustein-kostal-ksem-via-modbus-tcp-abfragen) of the KNX User Forum (German)

### Keep notice

* No output is SBC (send-by-change) - all are fired every interval

## Build from scratch

1. Download [Schnittstelleninformation](http://www.hs-help.net/hshelp/gira/other_documentation/Schnittstelleninformationen.zip) from GIRA Homepage
2. Decompress zip, use `HSL SDK/2-0/framework` Folder for development.
3. Checkout this repo to the `projects/hs_kostalKSEM_ModbusTCP` folder
4. Run the generator.pyc (`python2 ./generator.pyc hs_kostalKSEM_ModbusTCP`)
5. Import the module `release/14181_kostalKSEM_ModbusTCP.hsl` into the Experte Software
6. Use the module in your logic editor

You can replace step 4 with the `./buildRelease.sh` script. With the help of the markdown2 python module (`pip install markdown2`) it creates the documentation and packages the `.hslz` file. This file is also installable in step 5 and adds the module documentation into the Experte-Tool.  
 
## Libraries

* pymodbus 2.5.3 - https://github.com/riptideio/pymodbus

The shipped libraries may distributed under a different license conditions. Respect those licenses as well!
