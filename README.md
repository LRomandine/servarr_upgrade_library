# Update for 2025
There is now an application that performs this type of functionality on a consistent basis
[Huntarr.io](https://github.com/plexguide/Huntarr.io)

---
---
---

# servarr_upgrade_library
Automatically search your Servarr libraries for upgrades to your content.

This automates going to every TV episode and movie to search for higher quality versions. This is helpful if you have an existing library but want to search for higher quality releases. Normally Radarr and Sonarr only check newly posted items to indexers via RSS, but this tool will automate searching all your indexers for all your content. Be careful, it is easy to hit API limits on indexers, fill up your storage, etc. especially with larger libraries.


## Dependencies
[Pyarr](https://github.com/totaldebug/pyarr)

## Usage
```
# ./servarr_upgrade_library.py --help
usage: servarr_upgrade_library.py [-h] [--sonarr-host SONARR_HOST] [--sonarr-apikey SONARR_APIKEY] [--sonarr-skip-seasons] [--sonarr-skip-episodes]
                                  [--radarr-host RADARR_HOST] [--radarr-apikey RADARR_APIKEY] [--lidarr-host LIDARR_HOST] [--lidarr-apikey LIDARR_APIKEY]
                                  [--readarr-host READARR_HOST] [--readarr-apikey READARR_APIKEY] [--resume-file RESUME_FILE] [--max-num-searches MAX_NUM_SEARCHES]
                                  [--search-wait SEARCH_WAIT] [--skip-warning] [--debug]

Process Servarr libraries and check for upgrades.

options:
  -h, --help            show this help message and exit
  --sonarr-host SONARR_HOST
                        Set the Sonarr host, default is http://127.0.0.1:8989/
  --sonarr-apikey SONARR_APIKEY
                        Set the Sonarr API key, required for Sonarr processing
  --sonarr-skip-seasons
                        Set Sonarr to not search for seasons
  --sonarr-skip-episodes
                        Set Sonarr to not search for individual episodes
  --radarr-host RADARR_HOST
                        Set the Radarr host default is http://127.0.0.1:7878/
  --radarr-apikey RADARR_APIKEY
                        Set the Radarr API key, required for Radarr processing
  --lidarr-host LIDARR_HOST
                        Set the Lidarr host default is http://127.0.0.1:8686/
  --lidarr-apikey LIDARR_APIKEY
                        Set the Lidarr API key, required for Lidarr processing
  --readarr-host READARR_HOST
                        Set the Readarr host default is http://127.0.0.1:8787/
  --readarr-apikey READARR_APIKEY
                        Set the Readarr API key, required for Readarr processing
  --resume-file RESUME_FILE
                        Set resume filethat will be used, default is servarr_upgrade_library.resume
  --max-num-searches MAX_NUM_SEARCHES
                        Maximum number of searches per run, default is 50
  --search-wait SEARCH_WAIT
                        How many seconds to wait between searches, default is 60
  --skip-warning        Skip the warning about this script running a long time
  --debug               Enable debug output
```

## Example Usage
```
./servarr_check_for_upgrades.py --radarr-apikey abcd1234efgh5678ijkl9012mnop3456 --sonarr-apikey abcdefghijklmnop1234567890123456
```

## Testing
Tested on
- Ubuntu 22.04
- Python 3.10
- Sonarr 3.0.10
- Radarr 4.5.2
- Pyarr 5.1.0
  - Pyarr 5.1.0 requires [this PR](https://github.com/totaldebug/pyarr/pull/156) to work for Radarr
 
## Contributing
Posting this on Github to share with the community as I have seen forum posts asking for this functionality. I do not intend to add Lidarr or Readarr functionality but will gladly accept PRs.
