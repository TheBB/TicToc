from datetime import datetime, timedelta
from operator import methodcaller
from time import timezone, altzone

from tzlocal import get_localzone
from pytz import utc

from .util import ConversionGraph


LEAP_SECONDS = sorted([
    datetime(year, 6, 30, 23, 59, 59)
    for year in [1972, 1981, 1982, 1983, 1985, 1992, 1993, 1994, 1997, 2012, 2015]
] + [
    datetime(year, 12, 31, 23, 59, 59)
    for year in [1972, 1973, 1974, 1975, 1976, 1977, 1978, 1979, 1987, 1989, 1990, 1995, 1998, 2005, 2008, 2016]
])


def datetime_to_julian(dt):
    diff = dt - datetime(2000, 1, 1, 12)
    retval = 2_451_545 + diff.days
    retval += diff.seconds / 60 / 60 / 24
    retval += diff.microseconds / 1e6 / 60 / 60 / 24
    return retval

def julian_to_datetime(jd):
    return datetime(2000, 1, 1, 12) + timedelta(days=jd - 2_451_545)

def julian_to_modified(jd):
    return jd - 2_400_000.5

def modified_to_julian(mjd):
    return mjd + 2_400_000.5


convert_timescale = ConversionGraph()

@convert_timescale.register('local', 'utc')
def local_to_utc(dt):
    return dt.astimezone(utc)

@convert_timescale.register('utc', 'local')
def utc_to_local(dt):
    return dt.astimezone(get_localzone())

@convert_timescale.register('utc', 'tai')
def utc_to_tai(dt):
    dt = dt.replace(tzinfo=None)
    delta = 10
    for leap in LEAP_SECONDS:
        if leap < dt:
            delta += 1
        else:
            break
    return dt + timedelta(seconds=delta)

@convert_timescale.register('tai', 'utc')
def tai_to_utc(dt):
    one_second = timedelta(seconds=1)
    for leap in LEAP_SECONDS:
        if dt - one_second > leap:
            dt -= one_second
        else:
            break
    return (dt - timedelta(seconds=10)).replace(tzinfo=utc)

@convert_timescale.register('tai', 'tt')
def tai_to_tt(dt):
    return dt + timedelta(seconds=32, milliseconds=184)

@convert_timescale.register('tt', 'tai')
def tt_to_tai(dt):
    return dt - timedelta(seconds=32, milliseconds=184)

@convert_timescale.register('tt', 'tcg')
def tt_to_tcg(dt):
    # Explanatory Supplement to the Astronomical Almanac, 3rd edition, Eq. 3.27
    jdtai = convert_timescale.convert('tt', 'jdtai', dt)
    diff = 6.969_290_134e-10 * (jdtai - 2_443_144.5) * 86400
    return dt + timedelta(seconds=diff)

for scale in ('tt', 'tai', 'tcg'):
    convert_timescale.register(scale, f'jd{scale}')(datetime_to_julian)
    convert_timescale.register(f'jd{scale}', scale)(julian_to_datetime)
    convert_timescale.register(f'jd{scale}', f'mjd{scale}')(julian_to_modified)
    convert_timescale.register(f'mjd{scale}', f'jd{scale}')(modified_to_julian)


class Time:

    def __init__(self, dt, scale):
        self._dt = dt
        self._scale = scale

    def __str__(self):
        return f'{self._dt} @ {self._scale}'

    @classmethod
    def now(cls):
        dt = datetime.utcnow().replace(tzinfo=utc)
        return cls(dt, 'utc').local

    def toscale(self, scale):
        if scale == self._scale:
            return self
        dt = convert_timescale.convert(self._scale, scale, self._dt)
        return Time(dt, scale)

for scale in ['local', 'utc']:
    setattr(Time, scale, property(methodcaller('toscale', scale)))

for scale in ['tt', 'tai', 'tcg']:
    setattr(Time, scale, property(methodcaller('toscale', scale)))
    setattr(Time, f'jd{scale}', property(methodcaller('toscale', f'jd{scale}')))
    setattr(Time, f'mjd{scale}', property(methodcaller('toscale', f'mjd{scale}')))
