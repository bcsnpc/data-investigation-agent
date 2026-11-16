"""Owner's laptop headroom rule; check before admission, never delete data."""
import os
import shutil


LAPTOP_FREE_BYTES = {'C:/': 40_000_000_000, 'D:/': 80_000_000_000}


def require_laptop_headroom(*, platform=None, disk_usage=None):
    """Cloud/Linux volumes retain their own checks; both Windows drives must pass."""
    if (os.name if platform is None else platform) != 'nt':
        return {'status': 'NOT_APPLICABLE', 'reason': 'NOT_WINDOWS_LAPTOP'}
    usage = disk_usage or shutil.disk_usage
    observed = {}
    for drive, minimum in LAPTOP_FREE_BYTES.items():
        try:
            free = usage(drive).free
        except OSError as error:
            raise ValueError('LAPTOP_DISK_HEADROOM_UNESTABLISHED:' + drive) from error
        observed[drive] = {'free_bytes': free, 'minimum_free_bytes': minimum}
        if free < minimum:
            raise ValueError('LAPTOP_DISK_HEADROOM_LOW:' + drive + ':' + str(free)
                             + '<' + str(minimum))
    return {'status': 'PASS', 'drives': observed}
