import re
import shutil

import click
import pandas
from pandas import DataFrame

import files
from rubrics import Rubric

FORMAT_GRADE = re.compile(r'(?P<actual>\d+,\d+)\s\/\s(?P<maximum>\d+,\d+)')
FORMAT_TU_ID = re.compile(r'^([a-z]{2}\d{2}[a-zA-Z]{4}|[a-zA-Z]+|[a-zA-Z]+_[a-zA-Z]+|[a-zA-Z]{2}\d{4})$')


@click.command(name='filter')
@click.option('--rubrics', type=click.Path(), default='rubrics/csv', help='path to csv directory')
@click.option('--rubrics-moodle', type=click.Path(), default='rubrics/moodle', help='path to moodle files')
@click.option('--rubrics-moodle-filtered', type=click.Path(), default='rubrics/moodle-filtered',
              help='path to filtered moodle files')
@click.option('--report', type=click.Path(), default='report.xlsx', help='path to submission report file')
@click.option('--dictionary', type=click.Path(), default='mapping.csv', help='path to mapping file')
def filter_rubrics(rubrics, rubrics_moodle, rubrics_moodle_filtered, report, dictionary):
    f_dictionary = load_name_id_mapping(dictionary)
    points_rubrics = load_from_rubrics(rubrics)
    points_report = load_points_from_export(report, f_dictionary)
    points = points_rubrics.join(other=points_report, lsuffix='_rubrics', rsuffix='_report')
    points = points[points['points_rubrics'] > points['points_report']]
    for entry in points['file']:
        shutil.copy(f'{rubrics_moodle}/{entry}', f'{rubrics_moodle_filtered}/{entry}')
    click.echo(f'Success! {len(points)} rubrics filtered.')


def load_from_rubrics(rubrics_path: str) -> DataFrame:
    r = [r for r in (Rubric(f) for f in files.find_files(path=rubrics_path, format='csv')) if r.tu_id is not None]
    f = DataFrame(
        data={'tu_id': [r.tu_id for r in r], 'points': [r.points for r in r], 'file': [r.file_name() for r in r]})
    f = f.set_index('tu_id')
    return f


def load_points_from_export(file: str, mappings: DataFrame) -> DataFrame:
    f = pandas.read_excel(file, header=[3])
    f = f.rename(columns={'Anmeldename': 'name', 'Bewertung': 'points'})
    f = f.join(other=mappings.set_index('name'), on='name')
    f = f[['points', 'tu_id']]
    f['points'] = f['points'].apply(_to_points)
    f = f.set_index('tu_id')
    return f


def load_name_id_mapping(file: str) -> DataFrame:
    frame = pandas.read_csv(file)
    frame = frame[frame['tu_id'].apply(lambda x: FORMAT_TU_ID.match(x) is not None)]
    return frame


def _to_points(string: str) -> float:
    if string == '-':
        return 0
    match = FORMAT_GRADE.match(string)
    if not match:
        click.echo(f'<{string}> cannot be converted to points.')
        return 0
    return float(match['actual'].replace(',', '.'))


if __name__ == '__main__':
    filter_rubrics()
