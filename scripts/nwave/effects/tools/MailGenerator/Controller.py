# -*- coding: utf-8 -*-
"""DOCSTRING."""

import zefir
zefir.configuration.configure()

from Settings import Settings

from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import re
import smtplib
import zefir


class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        self._context = zefir.get_context()
        if not self._context:
            raise RuntimeError('Zefir did not load properly.')

        self._user = self._context.authenticated_user
        if not self._user:
            raise RuntimeError('User not logged in zefiro.')

        self._connectModel()
        self._connectView()

        self.model.sender = self._user.email
        self.model.user_name = self._user.common_name
        self.model.project_name = self._context.find_project().name.upper()
        self.model.recipients = Settings.RECIPIENTS

        self.view.setHtml(Settings.DEFAULT_HTML)

    def _connectModel(self):
        self.model.recipientsUpdated = self._updateRecipients
        self.model.moviesUpdated = self._updateMovies
        self.model.imagesUpdated = self._updateImages
        self.model.sequenceShotUpdated = self._updateSequenceShot

    def _connectView(self):
        self.view.setRemark = self._setRemark
        self.view.addVolumeData = self._addVolumeData
        self.view.preview = self._previewHtml
        self.view.send = self._send

        self.view.recipientAdded = self._recipientAdded
        self.view.recipientChanged = self._recipientChanged
        self.view.recipientDeleted = self._recipientChanged
        self.view.recipientRenamed = self._recipientRenamed

        self.view.movieAdded = self._movieChanged
        self.view.movieChanged = self._movieChanged
        self.view.movieDeleted = self._movieChanged

        self.view.imageAdded = self._imageChanged
        self.view.imageChanged = self._imageChanged
        self.view.imageDeleted = self._imageChanged

        self.view.sequenceChanged = self._sequenceChanged
        self.view.shotChanged = self._shotChanged

        self.view.assetChecked = self._assetChecked
        self.view.taskChecked = self._taskChecked

        self.view.closeTool = self._closeTool

    def _getShot(self, sequence_number, shot_number):
        shot = self._context.find_shot(code='{seq}_{shot}'.format(
            seq=str(sequence_number).zfill(3),
            shot=str(shot_number).zfill(4),
        ))

        return shot

    def _setRemark(self):
        self.model.remark = self.view.remark

    def _addVolumeData(self):
        self.view.remark = '{0}\n{1}'.format(
            self.model.remark,
            '\n'.join(Settings.VOLUME_SETTINGS)
        )

    # ####################################################################### #
    #                               Recipients                                #
    # ####################################################################### #

    def _recipientAdded(self):
        new_recipient = str(self.view.new_recipient)
        if not re.match(Settings.MAIL_TEMPLATE, new_recipient):
            self.view.displayWarning(
                'Wrong address',
                'The address provided is incorrect.'
            )
            return
        recipients = self.model.recipients
        if new_recipient in recipients:
            self.view.displayWarning(
                'Duplicate address',
                'The address provided is already in the list.'
            )
            return
        recipients.append(new_recipient)
        self.model.recipients = recipients

    def _recipientChanged(self):
        self.model.recipients = self.view.recipients

    def _recipientRenamed(self, old_name, new_name):
        if not re.match(Settings.MAIL_TEMPLATE, new_name):
            self.view.displayWarning(
                'Wrong address',
                'The address provided is incorrect.'
            )
            return self.view.renameRecipient(old_name)
        recipients = self.model.recipients
        if new_name in recipients:
            self.view.displayWarning(
                'Duplicate address',
                'The address provided is already in the list.'
            )
            return self.view.renameRecipient(old_name)
        index = recipients.index(old_name)
        recipients[index] = new_name
        self.model.recipients = recipients

    def _updateRecipients(self):
        self.view.recipients = self.model.recipients

    # ####################################################################### #
    #                                 Movies                                  #
    # ####################################################################### #

    def _movieChanged(self):
        self.model.movies = self.view.movies

    def _updateMovies(self):
        self.view.movies = self.model.movies

    # ####################################################################### #
    #                                 Images                                  #
    # ####################################################################### #

    def _imageChanged(self):
        self.model.images = self.view.images

    def _updateImages(self):
        self.view.images = self.model.images

    def _previewHtml(self):
        extra_data = (
            '<p><b>From :</b> {user_mail}</p><p><b>To :</b> {recipients}</p>'
        ).format(
            user_mail=self.model.sender,
            recipients=', '.join(self.model.recipients)
        )

        images = [
            Settings.IMAGE_TEMPLATE.format(
                path=path
            )
            for path in self.model.images
        ]

        self.view.setHtml(self.model.getHtml(images, extra_data))

    # ####################################################################### #
    #                             Sequence / Shot                             #
    # ####################################################################### #

    def _sequenceChanged(self):
        self.model.sequence = self.view.sequence

    def _shotChanged(self):
        self.model.shot = self.view.shot

    def _updateSequenceShot(self):
        if self.model.sequence == 0 or self.model.shot == 0:
            return

        zefir_shot = self._getShot(self.model.sequence, self.model.shot)
        if zefir_shot is None:
            self.view.displayWarning(
                'Shot not found',
                'Could not find the shot {0}_{1} in the database.'.format(
                    str(self.model.sequence).zfill(3),
                    str(self.model.shot).zfill(4)
                )
            )
            return

        fx_simulations = []
        for shot_instance in zefir_shot.shot_instances:
            components = [
                component
                for component in shot_instance.components
                if component.stage == zefir.STAGES.FX_SIMULATION
            ]
            if components:
                fx_simulations.append(shot_instance.string_repr(shot=False))
        self.view.assets = fx_simulations
        self.model.assets = []

        fx_tasks = [
            task.name
            for task in zefir_shot.tasks
            if task.stage == zefir.TASK_STAGES.SPECIAL_EFFECTS
        ]
        self.view.tasks = fx_tasks
        self.model.tasks = []

        # shot_path = self._context.get_workspace_directory(
        #     'MAYA', zefir_shot,
        #     custom_team=zefir.TEAMS.SPECIAL_EFFECTS
        # )
        # TODO: Use proper zefir way to get path
        path = "//nwave/projects/{0}/PROD/SEQ/{1}/{2}/SPECIAL_EFFECTS".format(
            self.model.project_name,
            str(self.model.sequence).zfill(3),
            str(self.model.shot).zfill(4)
        )
        self.view.last_movie_folder = path
        path = (
            "//nwave/projects/{0}/PROD/SEQ/{1}/{2}/SPECIAL_EFFECTS/{3}/MAYA"
        ).format(
            self.model.project_name,
            str(self.model.sequence).zfill(3),
            str(self.model.shot).zfill(4),
            self._user.code
        )
        self.view.last_image_folder = path

    def _assetChecked(self):
        self.model.assets = self.view.getCheckedAsset()

    def _taskChecked(self):
        self.model.tasks = self.view.tasks

    def _closeTool(self):
        self.view.close()

    def _send(self):
        """Send a mail for each shot in the shot list."""
        if not self.model.recipients:
            self.view.displayWarning(
                'No recipients',
                'No recipients have been set for the email.'
            )
            return

        if not (self.model.assets or self.model.tasks):
            self.view.displayWarning(
                'No asset or tasks',
                'No asset or task have been set for the email.'
            )
            return

        recipients = self.model.recipients
        recipients.append(self.model.sender)

        s = smtplib.SMTP(Settings.MAIL_SERVER)

        # Create the root message
        msg_root = MIMEMultipart('related')
        msg_root['Subject'] = self.model.subject
        msg_root['From'] = self.model.sender
        msg_root['To'] = ', '.join(recipients)
        msg_root.preable = 'This is a multi-part message in MIME format.'

        msg_alternative = MIMEMultipart('alternative')
        msg_root.attach(msg_alternative)

        images = [
            Settings.IMAGE_MAIL_TEMPLATE.format(
                image_name='image_{0}'.format(i)
            )
            for i in range(len(self.model.images))
        ]

        msg_alternative.attach(MIMEText(self.model.plain_text, 'plain'))
        msg_alternative.attach(MIMEText(self.model.getHtml(images), 'html'))

        for i, path in enumerate(self.model.images):
            with open(path, 'rb') as image:
                msg_image = MIMEImage(image.read())
                msg_image.add_header('Content-ID', '<image_{0}>'.format(i))
                msg_root.attach(msg_image)

        s.sendmail(
            self.model.sender,
            recipients,
            msg_root.as_string()
        )
        s.quit()

        return True
