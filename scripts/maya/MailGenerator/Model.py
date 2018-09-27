# -*- coding: utf-8 -*-
"""DOCSTRING."""

from Settings import Settings


class Model(object):
    def __init__(self):
        self.sender = None
        self.user_name = None
        self.project_name = None
        # Lists are used instead of sets as the ordering of contents matters
        self._recipients = []
        self._movies = []
        self._images = []

        self._assets = []
        self._tasks = []

        self._sequence = 0
        self._shot = 0

        self._remark = ''

        self._setupMethods()

    def _setupMethods(self):
        """Create the methods to be called when a value has changed."""
        self.recipientsUpdated = lambda: None
        self.moviesUpdated = lambda: None
        self.imagesUpdated = lambda: None
        self.sequenceShotUpdated = lambda: None

    # ####################################################################### #
    #                            Getters / Setters                            #
    # ####################################################################### #

    @property
    def remark(self):
        return self._remark

    @remark.setter
    def remark(self, value):
        if not isinstance(value, str):
            raise ValueError('Wrong data type {0}'.format(type(value)))
        self._remark = value

    @property
    def recipients(self):
        return self._recipients

    @recipients.setter
    def recipients(self, value):
        if not isinstance(value, list):
            raise ValueError('Wrong data type {0}'.format(type(value)))
        self._recipients = value
        self.recipientsUpdated()

    @property
    def movies(self):
        return self._movies

    @movies.setter
    def movies(self, value):
        if not isinstance(value, list):
            raise ValueError('Wrong data type {0}'.format(type(value)))
        self._movies = value
        self.moviesUpdated()

    @property
    def images(self):
        return self._images

    @images.setter
    def images(self, value):
        if not isinstance(value, list):
            raise ValueError('Wrong data type {0}'.format(type(value)))
        self._images = value
        self.imagesUpdated()

    @property
    def sequence(self):
        return self._sequence

    @sequence.setter
    def sequence(self, value):
        if not isinstance(value, int):
            raise ValueError('Wrong data type {0}'.format(type(value)))
        self._sequence = value
        self.sequenceShotUpdated()

    @property
    def shot(self):
        return self._shot

    @shot.setter
    def shot(self, value):
        if not isinstance(value, int):
            raise ValueError('Wrong data type {0}'.format(type(value)))
        self._shot = value
        self.sequenceShotUpdated()

    @property
    def assets(self):
        return self._assets

    @assets.setter
    def assets(self, value):
        if not isinstance(value, list):
            raise ValueError('Wrong data type {0}'.format(type(value)))
        self._assets = value

    @property
    def tasks(self):
        return self._tasks

    @tasks.setter
    def tasks(self, value):
        if not isinstance(value, list):
            raise ValueError('Wrong data type {0}'.format(type(value)))
        self._tasks = value

    def getHtml(self, images, extra_data=''):
        movies = [
            Settings.MOVIE_TEMPLATE.format(
                href=path.upper()[2:],
                path=path.upper()
            )
            for path in self.movies
        ]

        return Settings.HTML_TEMPLATE.format(
            extra_data=extra_data,
            assets=', '.join(self.assets),
            tasks=', '.join(self.tasks),
            sequence=str(self.sequence).zfill(3),
            shot='{0}_{1}'.format(
                str(self.sequence).zfill(3),
                str(self.shot).zfill(4)
            ),
            movies='\n'.join(movies),
            remarks='<br/>'.join(self.remark.split('\n')),
            images='\n'.join(images),
            user=self.user_name
        )

    @property
    def plain_text(self):
        movies = [
            Settings.MOVIE_PLAIN_TEXT.format(
                href=path[2:],
                path=path
            )
            for path in self.movies
        ]

        return Settings.PLAIN_TEXT.format(
            assets=', '.join(self.assets),
            tasks=', '.join(self.tasks),
            sequence=str(self.sequence).zfill(3),
            shot='{0}_{1}'.format(
                str(self.sequence).zfill(3),
                str(self.shot).zfill(4)
            ),
            movies='\n'.join(movies),
            remarks=self.remark,
            user=self.user_name
        )

    @property
    def subject(self):
        return Settings.SUBJECT.format(
            prod_name=self.project_name,
            assets=', '.join(self.assets),
            shot='{0}_{1}'.format(
                str(self.sequence).zfill(3),
                str(self.shot).zfill(4)
            )
        )
