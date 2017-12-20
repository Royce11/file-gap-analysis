from pyhocon import ConfigFactory,config_tree
import re

filename = "vendor-comscore/raw/original/AU/search_fact/DGCS_AUSearch_20140526_02.dat.gz"

# pattern = r".*/DGCS_(?P<country>(?!CA)[A-Z]{2})Search_(?P<year>\\d{4})(\\d{2})(\\d{2})_02.dat.gz"
match = re.match(".*/DGCS_(?P<country>(?!CA)[A-Z]{2})Search_(?P<year>\\d{4})(\\d{2})(\\d{2})_02.dat.gz",filename)

if match.group('country'):
    country = match.group('country')

if match.group('year'):
    print(type(match.group('year')))
    year = match.group('year')
