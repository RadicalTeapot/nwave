# -*- coding: utf-8 -*-
"""View of the Zefir reader."""

import re

from nwave.effects.houdini.DigitalAssets.ZefirReader.Settings import Settings


class View(object):
    """Class for the view of the Zefir reader.

    Attributes
    ----------
    COUNT_PARM_TEMPLATE: str
        Template for the asset count parm names.
    LOAD_ALL_PARM_TEMPLATE: str
        Template for the load all asset parm names.
    LOAD_PARM_TEMPLATE: str
        Template for the load asset parm names.
    ASSET_NAME_PARM_TEMPLATE: str
        Template for the asset name parm names.
    ASSET_STAGE_PARM_TEMPLATE: str
        Template for the asset stage parm names.
    INSTANCE_ID_PARM_TEMPLATE: str
        Template for the asset instance id parm names.
    PARAMETER_ID_PATTERN: SRE_pattern
        The regex pattern used to find a paramter's id number.

    """

    COUNT_PARM_TEMPLATE = '{category}_assets'
    LOAD_ALL_PARM_TEMPLATE = 'load_all_{category}'
    LOAD_PARM_TEMPLATE = 'load_{category}_asset{parm_id}'
    ASSET_NAME_PARM_TEMPLATE = '{category}_name{parm_id}'
    ASSET_STAGE_PARM_TEMPLATE = '{category}_stage{parm_id}'
    INSTANCE_ID_PARM_TEMPLATE = '{category}_instanceId{parm_id}'

    PARAMETER_ID_PATTERN = re.compile(
        r'''
        ^          # The beginning of the line
        .+?        # Any character (non greedy)
        (\d+)      # The id number at the end of the line (greedy)
        $          # The end of the line
        ''',
        re.VERBOSE
    )

    def __init__(self, node):
        """Initialize the view, setup the ui and the methods."""
        self._node = node
        self._context = None

        self._setupMethods()

    def _setupMethods(self):
        """Create the methods to be called when an ui event is called."""
        self.loadData = lambda: None
        self.getUpdate = lambda: None
        self.setChecked = lambda parm: None
        self.seqShotChanged = lambda: None
        self.loadAssetChecked = lambda category, id: None
        self.assetnameChanged = lambda category, id: None
        self.assetStageChanged = lambda category, id: None

    # ####################################################################### #
    #                                Callbacks                                #
    # ####################################################################### #

    def _loadData(self):
        """Load data from zefir database.

        This method is called by the Houdini node when the 'Refresh' button is
        clicked.
        """
        self.loadData()

    def _getUpdate(self):
        """Extract the path to alembic files for selected assets.

        This method is called by the Houdini node when the 'Get / Update'
        button is clicked.
        """
        self.getUpdate()

    def _setChecked(self, parm):
        """Check / Uncheck all checkers for a given category.

        This method is called by the Houdini node when a 'Load all' checkbox
        is checked / unchecked.

        Parameter
        ---------
        parm: hou.Parm
            The parm which has been checked / unchecked.

        """
        self.setChecked(parm)

    def _seqShotChanged(self):
        """Sequence or shot number has been modified by user.

        This method is called by the Houdini node when the 'sequenceshot' parm
        is modified by the user.
        """
        self.seqShotChanged()

    def _loadAssetChecked(self, parm):
        """Load parm has been checked / unchecked.

        This method is called by the Houdini node when an asset load checkbox
        state has changed.

        Parameter
        ---------
        parm: hou.Parm
            The parm which has been checked / unchecked.

        """
        self.loadAssetChecked(*self.getParmCategoryAndId(parm))

    def _assetNameChanged(self, parm):
        """Asset name has been modified by user.

        This method is called by the Houdini node when an asset name has been
        changed by the user

        Parameter
        ---------
        parm: hou.Parm
            The asset name parm.

        """
        self.assetNameChanged(*self.getParmCategoryAndId(parm))

    def _assetStageChanged(self, parm):
        """Asset stage has been changed by the user.

        This method is called by the Houdini node when an asset stage to load
        has been changed by the user.

        Parameter
        ---------
        parm: hou.Parm
            The stage menu parm.

        """
        self.assetStageChanged(*self.getParmCategoryAndId(parm))

    # ####################################################################### #
    #                            Internal Methods                             #
    # ####################################################################### #
    def _getParm(self, template, category, parm_id=None):
        """Find and return a parm with given category and id.

        Parameters
        ----------
        template: str
            The parm name template.
        category: str
            The category of the parm to find.
        parm_id: str or int
            The id of the parm to find.

        Raises
        ------
        RuntimeError
            If a parm with the given category and id cannot be found.

        Returns
        -------
        hou.Parm
            The parm with the given category and id.

        """
        name = ''
        if parm_id is not None:
            name = template.format(
                category=category,
                parm_id=parm_id
            )
        else:
            name = template.format(
                category=category
            )

        parm = self._node.parm(name)
        if not parm:
            raise RuntimeError('Could not find parm with name {0}'.format(
                name
            ))
        return parm

    # ####################################################################### #
    #                            Getters / Setters                            #
    # ####################################################################### #

    @property
    def sequence(self):
        """int: the number of the sequence to load."""
        return self._node.parm('sequenceshotx').evalAsInt()

    @property
    def shot(self):
        """int: the number of the shot to load."""
        return self._node.parm('sequenceshoty').evalAsInt()

    def getAssetCount(self, category):
        """Return the asset count for the given category.

        Parameter
        ----------
        category: str
            The name of the asset category.

        Returns
        -------
        int
            The number of assets for the given category.

        """
        return self._getParm(
            View.COUNT_PARM_TEMPLATE,
            category
        ).evalAsInt()

    def setAssetCount(self, category, count):
        """Set the asset count for a given category.

        Parameters
        ----------
        category: str
            The name of the category for which to set the asset count.
        count: int
            The value to use for the asset count.

        """
        self._getParm(
            View.COUNT_PARM_TEMPLATE,
            category
        ).set(count)

    def getLoadAsset(self, category, parm_id):
        """Return the state of a load asset with given category and parm id.

        Parameters
        ----------
        category: str
            The name of the category the asset belongs to.
        parm_id: int
            The id of parm to get.

        Returns
        -------
        bool
            The state of the load asset checkbox.

        """
        state = self._getParm(
            View.LOAD_PARM_TEMPLATE,
            category,
            parm_id
        ).evalAsInt()
        return bool(state)

    def setLoadAsset(self, category, parm_id, value):
        """Set the checkbox state to load an asset.

        Parameters
        ----------
        category: str
            The name of the category the asset belongs to.
        parm_id: int
            The id of parm to change.
        value: bool
            The state to set the checkbox.

        """
        if not isinstance(value, bool):
            raise TypeError('Expected bool, got {0} instead'.format(
                type(value).__name__
            ))
        self._getParm(
            View.LOAD_PARM_TEMPLATE,
            category,
            parm_id
        ).set(value)

    def getLoadAll(self, category):
        """Return the state of the load all checkbox for given category.

        Parameters
        ----------
        category: str
            The name of the category.

        Returns
        -------
        bool
            The state of the load all checkbox.

        """
        state = self._getParm(
            View.LOAD_ALL_PARM_TEMPLATE,
            category
        ).evalAsInt()
        return bool(state)

    def setLoadAll(self, category, value):
        """Set the checkbox state to load all assets of given category.

        Parameters
        ----------
        category: str
            The name of the category the asset belongs to.
        value: bool
            The state to set the checkbox.

        """
        if not isinstance(value, bool):
            raise TypeError('Expected bool, got {0} instead'.format(
                type(value).__name__
            ))
        self._getParm(
            View.LOAD_ALL_PARM_TEMPLATE,
            category
        ).set(value)

    def getAssetName(self, category, parm_id):
        """Return the name for the asset with given category and parm id.

        Parameters
        ----------
        category: str
            The name of the category the asset belongs to.
        parm_id: int
            The id of parm to get.

        Returns
        -------
        str
            The name for the asset.

        """
        return self._getParm(
            View.ASSET_NAME_PARM_TEMPLATE,
            category,
            parm_id
        ).evalAsString()

    def setAssetName(self, category, parm_id, value):
        """Set the name for the asset with given category and parm id.

        Parameters
        ----------
        category: str
            The name of the category the asset belongs to.
        parm_id: int
            The id of parm to change.
        value: bool
            The state to set the checkbox.

        """
        if not isinstance(value, str):
            raise TypeError('Expected str, got {0} instead'.format(
                type(value).__name__
            ))
        self._getParm(
            View.ASSET_NAME_PARM_TEMPLATE,
            category,
            parm_id
        ).set(value)

    def getAssetStage(self, category, parm_id):
        """Return the stage if of the stage to load for an asset.

        Parameters
        ----------
        category: str
            The name of the category the asset belongs to.
        parm_id: int
            The id of parm to get.

        Returns
        -------
        int
            The stage id to load.

        """
        return self._getParm(
            View.ASSET_STAGE_PARM_TEMPLATE,
            category,
            parm_id
        ).evalAsInt()

    @property
    def severity(self):
        """int: the warning/error flag state."""
        return self._node.parm('severity').evalAsInt()

    @severity.setter
    def severity(self, value):
        if not isinstance(value, int):
            raise TypeError('Expected int, got {0} instead'.format(
                type(value).__name__
            ))
        self._node.parm('severity').set(value)

    @property
    def message(self):
        """str: the warning/error message."""
        return self._node.parm('message').evalAsString()

    @message.setter
    def message(self, value):
        if not isinstance(value, str):
            raise TypeError('Expected str, got {0} instead'.format(
                type(value).__name__
            ))
        self._node.parm('message').set(value)

    # ####################################################################### #
    #                             Regular Methods                             #
    # ####################################################################### #
    def getParmCategoryAndId(self, parm):
        """Extract the category and id from a parm.

        Parameters
        ----------
        parm: hou.Parm
            The parameter from which to extract the category and id.

        Raises
        ------
        RuntimeError
            If the parm category or id cannot be extracted from it's name.

        Returns
        -------
        str, int
            The category and id of the given parm.

        """
        name = parm.name()
        category = None
        for value in Settings.CATEGORIES.values():
            if value in name:
                category = value
                break
        if not category:
            raise RuntimeError('Could not find parameter {0} category'.format(
                name
            ))
        parm_id = View.PARAMETER_ID_PATTERN.match(name)
        if not parm_id.groups():
            raise RuntimeError('Could not find parameter {0} id'.format(name))
        return category, int(parm_id.group(1))
