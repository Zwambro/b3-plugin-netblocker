#
# Netblocker Plugin for BigBrotherBot(B3) (www.bigbrotherbot.com)
# Copyright (C) 2014 Mark Weirath (xlr8or@xlr8or.com)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA    02110-1301    USA
#
# netblocker module provided by siebenmann: https://github.com/siebenmann/python-netblock

# Changelog:
# 06-12-2014 : v1.0.0beta : xlr8or
# * First edition of the netblocker
#
# 08-12-2019 : v1.1 : Zwambro
# * Fixing no module error
# * Adding whitelist IP: if trusted IP in banned IP range
# * Adding whitelist Name: if trusted player name has IP in banned IP range
#
# 26-12-2019 : v1.12 : Zwambro
# * Kicking banned IP players silently
#
# 30-05-2020 : v1.13 : Zwambro
# * add sleep time to check player is still on server 
# * fix multiple allowed names and ips
#

__version__ = '1.13'
__author__ = 'xlr8or'

# Edit the path to your path
import sys
sys.path.append(
    'C:/Users/username/Desktop/folder/b3/b3/extplugins/netblocker/netblock')

# b3 events
import b3
import b3.events
import b3.plugin

#import netblock as netblock
import netblock as netblock

#import time for sleep time
import time


class NetblockerPlugin(b3.plugin.Plugin):

    _adminPlugin = None
    _whitelist_ips = []
    _whitelist_names = []
    _blacklist_ips = []
    _maxLevel = 1

    ####################################################################################################################
    #                                                                                                                  #
    #    STARTUP                                                                                                       #
    #                                                                                                                  #
    ####################################################################################################################

    def onStartup(self):
        """
        Initialize plugin.
        """
        # get the admin plugin so we can register commands
        self._adminPlugin = self.console.getPlugin('admin')
        if not self._adminPlugin:
            self.debug('could not find admin plugin')
            return False
        else:
            self.debug("Plugin successfully loaded")

        self.registerEvent(b3.events.EVT_CLIENT_AUTH, self.onConnect)

        self.debug('plugin started')

    def onLoadConfig(self):
        """
        Load plugin configuration
        """
        try:
            # seperate entries on the ,
            _a = self.config.get('settings', 'whitelist_ips').split(',')
            _n = self.config.get('settings', 'whitelist_names').split(',')
            _l = self.config.get('settings', 'blacklist_ips').split(',')
            # strip leading and trailing whitespaces from each list entry
            self._whitelist_ips = [y.strip() for y in _a]
            self._whitelist_names = [z.strip() for z in _n]
            self._blacklist_ips = [x.strip() for x in _l]
        except Exception, err:
            self.error(err)
        self.debug('Allowed netblocks ips: %s' % self._whitelist_ips)
        self.debug('Allowed netblocks name: %s' % self._whitelist_names)
        self.debug('Refused netblocks ips: %s' % self._blacklist_ips)
        try:
            self._maxLevel = self.config.get('settings', 'maxlevel')
        except Exception, err:
            self.error(err)
        self.debug('Maximum level affected: %s' % self._maxLevel)

    ####################################################################################################################
    #                                                                                                                  #
    #    EVENTS                                                                                                        #
    #                                                                                                                  #
    ####################################################################################################################

    def onConnect(self, event):
        """
        Examine players ip address and allow/deny connection.
        """
        client = event.client
        self.debug('checking client: %s, name: %s, ip: %s, level: %s',
                   client.cid, client.name, client.ip, client.maxLevel)

        # check the level of the connecting client before applying the filters
        if client.maxLevel > self._maxLevel:
            self.debug(
                '%s is a higher level user, and allowed to connect', client.name)
            return True
        elif str(client.ip) in self._whitelist_ips:
            self.debug("Tis ip (%s) on whitelist ips, allowed to connect" % (client.ip))
            return True
        elif client.name in self._whitelist_names:
            self.debug('This Name (%s) on whitelist names, allowed to connect' % (client.name))
            return True

        else:
            # transform ip address
            _ip = netblock.convert(client.ip)
            # cycle through our blocks
            for _block in self._blacklist_ips:
                # convert each block
                _b = netblock.convert(_block)
                # check if clients ip is in the disallowed range
                if _b[0] <= _ip[0] <= _b[1]:
                    # client not allowed to connect
                    time.sleep(4)
                    if client in self.console.clients.getList():
                        self.debug('client refused: %s (%s)' % (client.ip, client.name))
                        client.kick("^1Blacklisted Player^7", keyword="Blacklisted", silent=True)
                    return False
