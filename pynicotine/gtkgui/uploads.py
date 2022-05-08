# COPYRIGHT (C) 2020-2022 Nicotine+ Contributors
# COPYRIGHT (C) 2016-2018 Mutnick <mutnick@techie.com>
# COPYRIGHT (C) 2016-2017 Michael Labouebe <gfarmerfr@free.fr>
# COPYRIGHT (C) 2009-2011 Quinox <quinox@users.sf.net>
# COPYRIGHT (C) 2009 Hedonist <ak@sensi.org>
# COPYRIGHT (C) 2006-2008 Daelstorm <daelstorm@gmail.com>
# COPYRIGHT (C) 2003-2004 Hyriand <hyriand@thegraveyard.org>
#
# GNU GENERAL PUBLIC LICENSE
#    Version 3, 29 June 2007
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os

from gi.repository import Gtk

from pynicotine.config import config
from pynicotine.gtkgui.transferlist import TransferList
from pynicotine.gtkgui.utils import copy_text
from pynicotine.gtkgui.widgets.dialogs import OptionDialog
from pynicotine.utils import open_file_path


class Uploads(TransferList):

    def __init__(self, frame, core):

        self.path_separator = '\\'
        self.path_label = _("Folder")
        self.retry_label = _("_Retry")
        self.abort_label = _("_Abort")
        self.aborted_status = "Aborted"

        self.transfer_page = frame.uploads_page
        self.user_counter = frame.upload_users_label
        self.file_counter = frame.upload_files_label
        self.expand_button = frame.uploads_expand_button
        self.expand_icon = frame.uploads_expand_icon
        self.grouping_button = frame.uploads_grouping_button

        TransferList.__init__(self, frame, core, transfer_type="upload")

        if Gtk.get_major_version() == 4:
            frame.uploads_content.append(self.container)
        else:
            frame.uploads_content.add(self.container)

        self.popup_menu_clear.add_items(
            ("#" + _("Finished / Aborted / Failed"), self.on_clear_finished_failed),
            ("#" + _("Finished / Aborted"), self.on_clear_finished_aborted),
            ("", None),
            ("#" + _("Finished"), self.on_clear_finished),
            ("#" + _("Aborted"), self.on_clear_aborted),
            ("#" + _("Failed"), self.on_clear_failed),
            ("#" + _("Queued…"), self.on_try_clear_queued),
            ("", None),
            ("#" + _("Everything…"), self.on_try_clear_all),
        )
        self.popup_menu_clear.update_model()

    def retry_transfers(self):
        for transfer in self.selected_transfers:
            self.core.transfers.retry_upload(transfer)

    def on_try_clear_queued(self, *_args):

        OptionDialog(
            parent=self.frame.window,
            title=_('Clear Queued Uploads'),
            message=_('Do you really want to clear all queued uploads?'),
            callback=self.on_clear_response,
            callback_data="queued"
        ).show()

    def on_try_clear_all(self, *_args):

        OptionDialog(
            parent=self.frame.window,
            title=_('Clear All Uploads'),
            message=_('Do you really want to clear all uploads?'),
            callback=self.on_clear_response,
            callback_data="all"
        ).show()

    def on_copy_url(self, *_args):

        transfer = next(iter(self.selected_transfers), None)

        if transfer:
            user = config.sections["server"]["login"]
            url = self.core.userbrowse.get_soulseek_url(user, transfer.filename)
            copy_text(url)

    def on_copy_dir_url(self, *_args):

        transfer = next(iter(self.selected_transfers), None)

        if transfer:
            user = config.sections["server"]["login"]
            url = self.core.userbrowse.get_soulseek_url(user, transfer.filename.rsplit('\\', 1)[0] + '\\')
            copy_text(url)

    def on_open_file_manager(self, *_args):

        transfer = next(iter(self.selected_transfers), None)

        if transfer:
            open_file_path(file_path=transfer.path, command=config.sections["ui"]["filemanager"])

    def on_play_files(self, *_args):

        for transfer in self.selected_transfers:
            base_name = str.split(transfer.filename, '\\')[-1]

            open_file_path(file_path=os.path.join(transfer.path, base_name),
                           command=config.sections["players"]["default"])

    def on_browse_folder(self, *_args):

        transfer = next(iter(self.selected_transfers), None)

        if not transfer:
            return

        user = config.sections["server"]["login"]
        folder = transfer.filename.rsplit('\\', 1)[0] + '\\'

        self.core.userbrowse.browse_user(user, path=folder)

    def on_abort_user(self, *_args):

        self.select_transfers()

        for user in self.selected_users:
            for transfer in self.transfer_list:
                if transfer.user == user and transfer not in self.selected_transfers:
                    self.selected_transfers.append(transfer)

        self.abort_transfers()

    def on_clear_aborted(self, *_args):
        self.clear_transfers(["Aborted", "Cancelled", "Disallowed extension", "User logged off"])

    def on_clear_failed(self, *_args):
        self.clear_transfers(["Connection timeout", "Local file error", "Remote file error"])

    def on_clear_finished_aborted(self, *_args):
        self.clear_transfers(["Aborted", "Cancelled", "Disallowed extension", "User logged off", "Finished"])

    def on_clear_finished_failed(self, *_args):
        self.clear_transfers(["Aborted", "Cancelled", "Disallowed extension", "User logged off", "Finished",
                              "Connection timeout", "Local file error", "Remote file error"])
