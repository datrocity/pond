from abc import ABC, abstractmethod
from datetime import datetime, date, timedelta
from typing import Any, Type, Optional, Union
import re

from pond.exceptions import IncompatibleVersionName, InvalidVersionName


# todo: remove, every artifact only has one version name class
def _compare_classnames(this: Any, that: Any) -> int:
    a = this.__class__.__name__
    b = that.__class__.__name__
    return 0 if a == b else (-1 if a < b else 1)


class VersionName(ABC):
    """ Base class for all kind of version naming conventions.

    It defines a way to sort version names and compute the next one.
    """

    # --- VersionName class interface

    @classmethod
    def class_id(cls):
        """ String ID to be able to find this class from its name. """
        return cls.__name__

    @classmethod
    def subclass_from_id(cls, class_id: str) -> Type['Artifact']:
        """ Find a subclass from its class ID. """
        subclasses = cls.__subclasses__()
        for subclass in subclasses:
            if subclass.class_id() == class_id:
                break
        else:
            raise InvalidVersionName(class_id)
        return subclass

    @classmethod
    def from_string(cls, version_name: str) -> 'VersionName':
        """Parses a string into a version name.

        Parameters
        ----------
        version_name: str
            Version name as a string that needs to be parsed

        Returns
        -------
        VersionName
            The parsed version name

        Raises
        ------
        InvalidVersionName
            If the version name cannot be parsed
        """
        # Only first-level subclasses for the moment, it should be sufficient
        # At the same time, we give up defining a version name priority, and will return the
        # first VersionName subclass that can parse the string
        # TODO: remove the magic
        subclasses = cls.__subclasses__()
        for subclass in subclasses:
            try:
                version = subclass.from_string(version_name)
                break
            except InvalidVersionName:
                pass
        else:
            raise InvalidVersionName(version_name)
        return version

    @classmethod
    @abstractmethod
    def next(cls, prev: 'VersionName') -> 'VersionName':
        """ Generate a new version name given a previous one.

        If `prev` is None, this method will generate a first version name.

        Some subclasses of `VersionName` will ignore the argument `prev`, except in case of
        collision (e.g., datetime version names).

        Parameters
        ----------
        prev: Optional['VersionName']
            The previous version name.

        Returns
        -------
        VersionName
            A new version name.
        """
        ...

    @classmethod
    def first(cls) -> 'VersionName':
        """ Generate the first version name.

        Alias for `VersionName.next(None)`.

        Returns
        -------
        VersionName
            The first version name.
        """
        return cls.next(prev=None)

    # --- VersionName protected interface

    @abstractmethod
    def _partial_compare(self, that: 'VersionName') -> Optional[int]:
        ...

    # --- Magic methods

    def __cmp__(self, other: 'VersionName') -> int:
        cmp = self._partial_compare(other)
        return cmp if cmp is not None else _compare_classnames(self, other)

    def __eq__(self, other: Any) -> bool:
        return self._partial_compare(other) == 0

    def __ne__(self, other: Any) -> bool:
        return self._partial_compare(other) != 0

    def __lt__(self, other: Any) -> bool:
        return self.__cmp__(other) < 0

    def __le__(self, other: Any) -> bool:
        return self.__cmp__(other) <= 0

    def __gt__(self, other: Any) -> bool:
        return self.__cmp__(other) > 0

    def __ge__(self, other: Any) -> bool:
        return self.__cmp__(other) >= 0

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}("{str(self)}")'


class SimpleVersionName(VersionName):
    """Simple version name are just an integer number (greater than 0) prefixed with "v" when
    rendered as string."""

    _FORMAT = re.compile('^v?([1-9][0-9]*)$')

    # --- VersionName class interface

    @classmethod
    def from_string(cls, version_name: str) -> 'SimpleVersionName':
        match = SimpleVersionName._FORMAT.match(version_name)
        if not match:
            raise InvalidVersionName(version_name)
        return cls(int(match[1]))

    @classmethod
    def next(cls, prev: Optional['VersionName'] = None) -> VersionName:
        if prev is None:
            next_ = SimpleVersionName(1)
        elif not isinstance(prev, SimpleVersionName):
            raise IncompatibleVersionName(prev, SimpleVersionName)
        else:
            next_ = SimpleVersionName(prev.version_number + 1)
        return next_

    def __init__(self, version_number: int):
        self.version_number = version_number

    # -- VersionName protected interface

    def _partial_compare(self, other: VersionName) -> Optional[int]:
        if isinstance(other, SimpleVersionName):
            return 0 if self.version_number == other.version_number else (
                -1 if self.version_number < other.version_number else 1)
        return None

    # -- Magic methods

    def __hash__(self) -> int:
        return hash(self.version_number)

    def __str__(self) -> str:
        return f'v{self.version_number}'


# todo: does this worlk?

class DateTimeVersionName(VersionName):
    """DateTime version names are versions in the form of an ISO date time with space as a time
    separator (eg. "2020-01-02 03:04:05")"""

    def __init__(self, dt: Union[date, datetime] = None):
        if dt is None:
            dt = datetime.now()
        if not isinstance(dt, datetime):
            dt = datetime(dt.year, dt.month, dt.day, 0, 0, 0)
        self.dt = dt

    # -- VersionName class interface

    @classmethod
    def from_string(cls, version_name: str) -> 'DateTimeVersionName':
        try:
            return cls(datetime.fromisoformat(version_name))
        except ValueError:
            raise InvalidVersionName(version_name)

    @classmethod
    def next(cls, prev: Optional['VersionName'] = None) -> VersionName:
        if prev is None:
            next_ = DateTimeVersionName(datetime.now())
        elif not isinstance(prev, DateTimeVersionName):
            raise IncompatibleVersionName(prev, DateTimeVersionName)
        else:
            now = datetime.now()
            if now == prev.dt:
                next_ = DateTimeVersionName(prev.dt + timedelta(seconds=1))
            else:
                next_ = DateTimeVersionName(now)
        return next_

    # -- VersionName protected interface

    def _partial_compare(self, other: VersionName) -> Optional[int]:
        if isinstance(other, DateTimeVersionName):
            return 0 if self.dt == other.dt else (-1 if self.dt < other.dt else 0)
        return None

    # -- Magic methods

    def __str__(self) -> str:
        return self.dt.isoformat(sep=' ', timespec='seconds')

    def __hash__(self) -> int:
        return hash(self.dt)
