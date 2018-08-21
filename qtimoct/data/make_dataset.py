# -*- coding: utf-8 -*-
import click
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
from glob import glob
from os.path import join, isdir

from qtimoct.data.forum import load_forum_data

@click.command()
@click.argument('input_filepath', type=click.Path(exists=True))
@click.argument('output_dir', type=click.Path())
def main(input_filepath, output_dir, mode='forum'):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info('making final data set from raw data')

    if mode == 'forum':

        try:
            subdirs = [x for x in glob(join(input_filepath, '*')) if isdir(x)]
            assert(len(subdirs) == 2)
            xml_dir, dcm_dir = subdirs if 'xml' in subdirs[0].lower() else subdirs[::-1]
            df = load_forum_data(xml_dir, dcm_dir, output_dir)
            df.to_csv(join(output_dir, 'OCTProcessed.csv'))
        except AssertionError as a:
            print("Input directory must contain XML and DCM folders")
    else:

        raise ValueError("Unsupported data mode f'{mode}'")


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
