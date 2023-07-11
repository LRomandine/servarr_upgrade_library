#!/usr/bin/env python3
"""
This tool will process your Servarr libraries and trigger searchs for upgrades

This is helpful when first installing Radarr, Sonarr, Lidarr, etc.  with an
existing library, it can systematically go through your entire library and
look for upgrades.

This can cause excessive bandwidth and storage usage for Sonarr as it will
search for series, seasons, and episodes. Then Sonarr will figure out
which to import based on yoru quality settings.

TODO:
- Implement Lidarr
- Implement Readarr
"""
# Changelog
# 0.2.1 - July 10, 2023
#    Fixed a bug that would cause an empty resume file to be written after one *arr completed
# 0.2.0 - July 9, 2023
#   Added resume support
#     kill process to pause progress
#     To reset resume position delete the resume file
#     Resume file format
#       sonarr,series,0,season,0,episode,0
#       radarr,0
# 0.1.0 - July 8, 2023
#   Made compliant with major Python linters
#     flake8 (pep8 & pyflakes)
#       Disabled E501 (line length)
#       Disabled E241 (whitespace after comma)
#     OpenStack Style Guide
#       Disabled H306 (alphabetize imports)
#     pep257
#     pycodestyle
#     pylint
#       Disabled C0301 (line length)
#       Disabled C0326 (whitespace after comma)
from __future__ import print_function
import os
import argparse
import logging
import time
from pyarr import SonarrAPI
from pyarr import RadarrAPI
#from pyarr import ReadarrAPI
#from pyarr import LidarrAPI


# Set up colors for logging
logging.addLevelName(logging.CRITICAL, "\033[1;31m%s\033[1;0m" % logging.getLevelName(logging.CRITICAL))
logging.addLevelName(logging.ERROR,    "\033[1;31m%s\033[1;0m" % logging.getLevelName(logging.ERROR))
logging.addLevelName(logging.WARNING,  "\033[1;34m%s\033[1;0m" % logging.getLevelName(logging.WARNING))
logging.addLevelName(logging.INFO,     "\033[1;35m%s\033[1;0m" % logging.getLevelName(logging.INFO))
logging.addLevelName(logging.DEBUG,    "\033[1;33m%s\033[1;0m" % logging.getLevelName(logging.DEBUG))


def process_sonarr(args):
    """Process Sonarr"""
    logging.info("Starting to process Sonarr")
    sonarr = SonarrAPI(args.sonarr_host, args.sonarr_apikey)
    series_list = sonarr.get_series()
    series_count = len(series_list)
    resume_file_lines_list = read_resume_file(args)
    resume_file_sonarr_content = None
    for index, resume_line in enumerate(resume_file_lines_list):
        if "sonarr" in resume_line:
            resume_file_sonarr_index = index
            resume_file_sonarr_content = resume_line
    if resume_file_sonarr_content is None:
        resume_file_sonarr_content = "sonarr,series,0,season,0,episode,0"
        resume_file_sonarr_index = len(resume_file_lines_list) + 1
    resume_file_sonarr_content_list = resume_file_sonarr_content.split(',')
    resume_file_obj = open(args.resume_file, 'w')
    logging.debug("Sonarr resume line index is " + str(resume_file_sonarr_index) + " and content is "+ str(resume_file_sonarr_content).strip())
    for series_counter, series in enumerate(series_list):
        if series_counter >= int(resume_file_sonarr_content_list[2]):
            logging.info("Working on " + series['title'] + " :: series " + str(series_counter) + " of " + str(series_count))
            resume_file_sonarr_content_list[2] = str(series_counter)
            resume_file_lines_list[resume_file_sonarr_index] = ','.join(resume_file_sonarr_content_list)
            for line in resume_file_lines_list:
                resume_file_obj.write(line)
            episode_list = sonarr.get_episode(series['id'], series=True)
            episode_count = len(episode_list)
            # Trigger a search for the whole series (it looks like under the covers this actually searches for each season based on the logs?)
            if series['monitored'] is True:
                sonarr.post_command('SeriesSearch', seriesId=series['id']) 
            else:
                logging.info("Not searching this series due to not monitored in sonarr")
            logging.debug("Sleeping for " + str(args.search_wait) + " seconds")
            time.sleep(int(args.search_wait))
            # Trigger a search for every season
            for season_counter, season in enumerate(series['seasons']):
                if season_counter >= int(resume_file_sonarr_content_list[4]):
                    resume_file_sonarr_content_list[4] = str(season_counter)
                    resume_file_lines_list[resume_file_sonarr_index] = ','.join(resume_file_sonarr_content_list)
                    for line in resume_file_lines_list:
                        resume_file_obj.write(line)
                    if season['monitored'] is True:
                        logging.info("Searching for season " + str(season_counter))
                        sonarr.post_command('SeasonSearch', seriesId=series['id'], seasonNumber=season['seasonNumber']) 
                        logging.debug("Sleeping for " + str(args.search_wait) + " seconds")
                        time.sleep(int(args.search_wait))
                    else:
                        logging.info("Not searching this season due to not monitored in sonarr")
                else:
                    logging.debug("Skipping season " + str(season_counter) + " due to resume position being " + str(resume_file_sonarr_content_list[4]))
            # Trigger a search for every episode
            for episode_counter, episode in enumerate(episode_list):
                if episode_counter >= int(resume_file_sonarr_content_list[6]):
                    resume_file_sonarr_content_list[6] = str(episode_counter)
                    resume_file_lines_list[resume_file_sonarr_index] = ','.join(resume_file_sonarr_content_list)
                    for line in resume_file_lines_list:
                        resume_file_obj.write(line)
                    if episode['monitored'] is True:
                        logging.info("Searching for episode " + str(episode_counter) + " of " + str(episode_count))
                        sonarr.post_command('EpisodeSearch', episodeIds=[episode['id']]) 
                        logging.debug("Sleeping for " + str(args.search_wait) + " seconds")
                        time.sleep(int(args.search_wait))
                    else:
                        logging.info("Not searching this episode due to not monitored in sonarr")
                else:
                    logging.debug("Skipping episode " + str(episode_counter) + " due to resume position being " + str(resume_file_sonarr_content_list[6]))
        else:
            logging.debug("Skipping series " + str(series_counter) + " due to resume position being " + str(resume_file_sonarr_content_list[2]).strip())
    for line in resume_file_lines_list:
        resume_file_obj.write(line)
    resume_file_obj.close()
    logging.info("Finished processing Sonarr")
    return


def read_resume_file(args):
    """Read in the resume file"""
    logging.debug("Processing resume file")
    try:
        resume_file_obj = open(args.resume_file, 'r')
        resume_file_lines = resume_file_obj.readlines()
        resume_file_obj.close()
        logging.debug("Resume file contents are")
        logging.debug(resume_file_lines)
        return resume_file_lines
    except IOError:
        logging.info("Resume file not found, starting from scratch")
        return []


def process_radarr(args):
    """Process Radarr"""
    logging.info("Starting to process Radarr")
    radarr = RadarrAPI(args.radarr_host, args.radarr_apikey)
    movies_list = radarr.get_movie()
    movies_count = len(movies_list)
    resume_file_lines_list = read_resume_file(args)
    resume_file_radarr_content = None
    for index, resume_line in enumerate(resume_file_lines_list):
        if "radarr" in resume_line:
            resume_file_radarr_index = index
            resume_file_radarr_content = resume_line
    if resume_file_radarr_content is None:
        resume_file_radarr_content = "radarr,0"
        resume_file_radarr_index = len(resume_file_lines_list) + 1
    resume_file_radarr_content_list = resume_file_radarr_content.split(',')
    resume_file_obj = open(args.resume_file, 'w')
    logging.debug("Radarr resume line index is " + str(resume_file_radarr_index) + " and content is "+ str(resume_file_radarr_content).strip())
    logging.debug("Movie count is "+ str(movies_count))
    for movies_counter, movie in enumerate(movies_list):
        if movies_counter >= int(resume_file_radarr_content_list[1]):
            resume_file_radarr_content_list[1] = str(movies_counter)
            resume_file_lines_list[resume_file_radarr_index] = ','.join(resume_file_radarr_content_list)
            for line in resume_file_lines_list:
                resume_file_obj.write(line)
            logging.info("Working on " + movie['cleanTitle'] + " :: movie " + str(movies_counter) + " of " + str(movies_count))
            if movie['monitored'] is True:
                radarr.post_command('MoviesSearch', movieIds=[movie['id']]) 
                logging.debug("Sleeping for " + str(args.search_wait) + " seconds")
                time.sleep(int(args.search_wait))
            else:
                logging.info("Not searching this movie due to not monitored in radarr")
        else:
            logging.debug("Skipping movie " + str(movies_counter) + " due to resume position being " + str(resume_file_radarr_content_list[1]).strip())
    for line in resume_file_lines_list:
        resume_file_obj.write(line)
    resume_file_obj.close()
    logging.info("Finished processing Radarr")
    return


def process_lidarr(args):
    logging.critical("Lidarr functionality not implemented yet.")
    return


def process_readarr(args):
    logging.critical("Readarr functionality not implemented yet.")
    return


def main():
    """The true main function."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='\033[1;33mProcess Servarr libraries and check for upgrades.\033[1;0m'
        )
    parser.add_argument('--sonarr-host',    dest='sonarr_host',                         default='http://127.0.0.1:8989/',         help='Set the Sonarr host, default is http://127.0.0.1:8989/')
    parser.add_argument('--sonarr-apikey',  dest='sonarr_apikey',                       default=None,                             help='Set the Sonarr API key, required for Sonarr processing')
    parser.add_argument('--radarr-host',    dest='radarr_host',                         default='http://127.0.0.1:7878/',         help='Set the Radarr host default is http://127.0.0.1:7878/')
    parser.add_argument('--radarr-apikey',  dest='radarr_apikey',                       default=None,                             help='Set the Radarr API key, required for Radarr processing')
    parser.add_argument('--lidarr-host',    dest='lidarr_host',                         default='http://127.0.0.1:8686/',         help='Set the Lidarr host default is http://127.0.0.1:8686/')
    parser.add_argument('--lidarr-apikey',  dest='lidarr_apikey',                       default=None,                             help='Set the Lidarr API key, required for Lidarr processing')
    parser.add_argument('--readarr-host',   dest='readarr_host',                        default='http://127.0.0.1:8787/',         help='Set the Readarr host default is http://127.0.0.1:8787/')
    parser.add_argument('--readarr-apikey', dest='readarr_apikey',                      default=None,                             help='Set the Readarr API key, required for Readarr processing')
    parser.add_argument('--resume-file',    dest='resume_file',                         default='servarr_upgrade_library.resume', help='Set resume filethat will be used, default is servarr_upgrade_library.resume')
    parser.add_argument('--search-wait',    dest='search_wait',                         default='60',                             help='How many seconds to wait between searches, default is 60')
    parser.add_argument('--skip-warning',   dest='skip_warning',   action='store_true', default=False,                            help='Skip the warning about this script running a long time')
    parser.add_argument('--debug',          dest='debug',          action='store_true', default=False,                            help='Enable debug output')
    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG, format="[%(levelname)8s] %(message)s")
    else:
        logging.basicConfig(level=logging.INFO,  format="[%(levelname)8s] %(message)s")

    if args.skip_warning is False:
        logging.critical("This script can run for hours or days depending on your search wait setting, you should only run this in the background or in a headless terminal")
        logging.critical("It can also cause you to reach API/search limits with your indexers, large storage usage, large bandwidth usage, etc.")
        input("Press any key to continue...")

    if args.sonarr_apikey is None:
        logging.info("Sonarr API key not provided, skipping Sonarr.")
    else:
        sonarr_results = process_sonarr(args)

    if args.radarr_apikey is None:
        logging.info("Radarr API key not provided, skipping Radarr.")
    else:
        sonarr_results = process_radarr(args)

    if args.lidarr_apikey is None:
        logging.info("Lidarr API key not provided, skipping Lidarr.")
    else:
        sonarr_results = process_lidarr(args)

    if args.readarr_apikey is None:
        logging.info("Readarr API key not provided, skipping Readarr.")
    else:
        sonarr_results = process_readarr(args)

    return



if __name__ == '__main__':
    main()
