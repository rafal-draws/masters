import argparse
import sys
import logging


def main(parser):
    args = parser.parse_args()
    logger = setup_logging(debug=args.debug)

    if args.generatepath != "":
        pass # todo check if dir exists

    if args.INPUT_FILE_PATH != "":
        pass # todo check if file exists, is mp3 | wav

    if args.OUTPUT_DIRECTORY != "":
        pass # todo check if directory exists, is mp3 | wav

    if args.length != 14:
        pass #todo check if song is long enough

    logger.info("Transformation finished succesfully.")
    logger.info(f"{args.INPUT_FILE_PATH} has been transformed.")
    logger.info(f"{args.OUTPUT_DIRECTORY} has been populated with TRANSFORMATION PRODUCT.")
    logger.info(f"The file contains {args.length} frames, each 22050 frames.")
    
    
    
def setup_logging(debug: bool):
    logger = logging.getLogger("example_logger")
    logger.setLevel(logging.INFO)  # Accept INFO and above

    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    stdout_handler.setLevel(logging.INFO)  # Only log INFO and above

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )
    stdout_handler.setFormatter(formatter)

    logger.addHandler(stdout_handler)

    logger.info("This is INFO and should appear.")
    logger.warning("This is WARNING and should appear.")

    logger.info("Trying to parse the args")
    
    if debug == True:
        logger.setLevel(logging.DEBUG)
        stdout_handler.setLevel(logging.DEBUG)
        logger.debug("DEBUG ON")

    return logger
    


if __name__ == "__main__":
    
    bmo = """insert ascii"""

    parser = argparse.ArgumentParser(
            prog = 'bmo',
            description= f"{bmo}-----------------------------------\n\n\n\nBMO, Binary Music Output.\nMade to load in music, transform it using librosa. If provided with -g [directory] it will generate artifacts in .mp4 form, but will require ffmpeg installed on the system.",
            epilog='Author: Rafał Waldemar Draws, rafal.w.draws@gmail.com'
            )

    parser.add_argument('INPUT_FILE_PATH', help='path to the .mp3/wav file for transformation. Must be valid, and above 15 seconds of length')
    parser.add_argument('OUTPUT_DIRECTORY', help='path store the [filename]-bmo.csv')
    parser.add_argument('-g', '--generatepath', help='path to the folder where the video artifacts are to be stored. The output will be a csv of columns frame_idx,values. Each Frame will have 22050 samples, of float32 precision.')
    parser.add_argument('-l', '--length', type=int, default=14, help='amount of frames. Default - 14.')
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true')
    
    main(parser)
