#!/usr/bin/env python
"""

Download CDC life tables in Excel format, and
save locally as CSV files.

Provide access stored in the CSV files.

Data is available for 50 states plus DC.
All states have groups Total, Male, Female,
White, Male White, and Female White.
Many states have Black, Male Black, and Female Black.

"""

import os
import ssl
import pandas as pd

from glob import glob

try:
    import urllib2  # python2
except:
    import urllib.request as urllib2  # python3


states_table = """ALABAMA AL
ALASKA  AK
ARIZONA AZ
ARKANSAS    AR
CALIFORNIA  CA
COLORADO    CO
CONNECTICUT CT
DELAWARE    DE
DISTRICT OF COLUMBIA    DC
FLORIDA FL
GEORGIA GA
HAWAII  HI
IDAHO   ID
ILLINOIS    IL
INDIANA IN
IOWA    IA
KANSAS  KS
KENTUCKY    KY
LOUISIANA   LA
MAINE   ME
MARYLAND    MD
MASSACHUSETTS   MA
MICHIGAN    MI
MINNESOTA   MN
MISSISSIPPI MS
MISSOURI    MO
MONTANA MT
NEBRASKA    NE
NEVADA  NV
NEW HAMPSHIRE   NH
NEW JERSEY  NJ
NEW MEXICO  NM
NEW YORK    NY
NORTH CAROLINA  NC
NORTH DAKOTA    ND
OHIO    OH
OKLAHOMA    OK
OREGON  OR
PENNSYLVANIA    PA
RHODE ISLAND    RI
SOUTH CAROLINA  SC
SOUTH DAKOTA    SD
TENNESSEE   TN
TEXAS   TX
UTAH    UT
VERMONT VT
VIRGINIA    VA
WASHINGTON  WA
WEST VIRGINIA   WV
WISCONSIN   WI
WYOMING WY"""

two_letter_abbrev = {}
abbrev2name = {}
for line in states_table.split('\n'):
    state = line[:-2].strip()
    abbrev = line[-2:]

    abbrev2name[abbrev] = state.title()

    state = state.lower()
    state = state.replace(' ', '_')

    two_letter_abbrev[state] = abbrev

group_labels = {
    'total': 'total', 'male': 'male', 'female': 'female',
    'white': 'white', 'wm': 'white male', 'wf': 'white female',
    'black': 'black', 'bm': 'black male', 'bf': 'black female',
}
groups_long2short = dict([(group_labels[k], k) for k in group_labels])

groups = ['total', 'male', 'female',
          'white', 'wm', 'wf',
          'black', 'bm', 'bf', ]

cdc_url = 'http://ftp.cdc.gov/pub/Health_Statistics/NCHS/Publications/NVSR/60_09/'
lt_dir = '/data/cdc/'

try:
    lt_dir = os.getcwd() + lt_dir
except NameError:
    pass


def remove_digits(s):
    return ''.join([x for x in s if x not in '0123456789'])


# Download life tables from CDC FTP site
n_life_table_csv_files = len(glob(lt_dir + '*.csv'))
if n_life_table_csv_files != 426:
    if not os.path.isdir(lt_dir):
        os.mkdir(lt_dir)

    for state in two_letter_abbrev:
        s = state.lower().replace(' ', '_')
        state_url = cdc_url + 'lewk4_{}.xlsx'.format(s)
        url = urllib2.urlopen(state_url, context=ssl._create_unverified_context())

        xls = pd.ExcelFile(url)
        sheets = xls.sheet_names
        for sheet in xls.sheet_names:
            group = remove_digits(sheet)
            if group.startswith('sderr'): continue

            df = xls.parse(sheet, skiprows=range(3),
                           index_col=0)

            df.to_csv('{}{}_{}.csv'.format(lt_dir, s, group))


def life_table(state_abbrev, demographic_group):
    """
    Inputs:
      * state_abbrev - 2 letter string, postal code of US state or DC
      * demographic_group - One of ['total', 'male', 'female',
                                    'white', 'wm', 'wf',
                                    'black', 'bm', 'bf',
                                    'white male', 'white female',
                                    'black male', 'black female', ]

    Returns:
      * pandas.Series with q values for years 0 thru 109
          q is the probability of subject dying in a given age of life
    """
    # Get inputs in correct case
    state_abbrev = state_abbrev.upper()

    try:
        state = abbrev2name[state_abbrev]
    except KeyError:
        raise ValueError('"{}" not a state abbreviation.'.format(state_abbrev))

    state = state.lower().replace(' ', '_')

    try:
        demographic_group = demographic_group.lower()
        if len(demographic_group) > 2:
            demographic_group = groups_long2short[demographic_group]
    except KeyError:
        raise ValueError('"{}" not a valid group.'.format(demographic_group))

    s = '{}{}_{}.csv'.format(lt_dir, state, demographic_group)

    if os.path.exists(s):
        df = pd.read_csv(s)
    else:
        raise ValueError('{} not a demographic group for {}.'.format(
            demographic_group, state_abbrev))

    return df['qx']


if __name__ == '__main__':
    q = life_table('PA', 'wf')
