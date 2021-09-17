# Citrix

## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Setup](#setup)

## General info
The script parses through bind zone files and extracts the necessary informaiton to add to Citrix ADC
	
## Technologies
Project is created with:
* Python 3
	
## Setup
To run this script, have python3 and process the zone files

```
# For forward zones
$ python F5_to_ADC.py <zone_file>

# for reverse entries with single lines per entry
$ python F5_to_ADC_reverse.py <zone_file>

# for single line reverse entries
$ python F5_to_ADC_reverse.py <zone_file> -e
```
