#!/usr/bin/env python3
#
#  Copyright (c) 2004-present, Facebook, Inc.
#  All rights reserved.
#
#  This source code is licensed under the BSD-style license found in the
#  LICENSE file in the root directory of this source tree. An additional grant
#  of patent rights can be found in the PATENTS file in the same directory.


from fboss.cli.commands import commands as cmds
from fboss.cli.data.oui_to_vendor_ieee import NIC_VENDOR_OUI_MAP


class NicCmd(cmds.PrintNeighborTableCmd):
    '''Class for host NIC related commands in fboss.'''

    _LENGTH_OF_OUI = 8
    _NO_MAC_FOUND_MESSAGE = "No MAC address found in ARP/NDP tables found."
    _UNKNOWN_VENDOR_MESSAGE = "Unknown NIC Vendor."

    def run(self, detail, verbose):
        self._client = self._create_agent_client()

        # Get the MAC addresses for IPV4.
        arp_table_detailed = self._client.getArpTable()
        arp_mac_addresses = [arp_mac.mac for arp_mac in arp_table_detailed]

        # Get the MAC addresses for IPV6.
        ndp_table_detailed = self._client.getNdpTable()
        ndp_mac_addresses = [ndp_mac.mac for ndp_mac in ndp_table_detailed]

        mac_address_set = set(arp_mac_addresses + ndp_mac_addresses)
        # Ignore the broadcast mac.
        mac_address_set -= set(['ff:ff:ff:ff:ff:ff', 'FF:FF:FF:FF:FF:FF'])

        if not len(mac_address_set):
            print(self._NO_MAC_FOUND_MESSAGE)
            return

        mac_nic_dictionary = {}
        for mac in mac_address_set:
            oui = mac[:self._LENGTH_OF_OUI].upper()
            if oui in NIC_VENDOR_OUI_MAP.keys():
                mac_nic_dictionary[mac] = NIC_VENDOR_OUI_MAP[oui]
            else:
                mac_nic_dictionary[mac] = self._UNKNOWN_VENDOR_MESSAGE

        if detail or verbose:
            for mac_address, vendor_name in mac_nic_dictionary.items():
                print("MAC Address: " + mac_address + " Vendor: " + vendor_name)
            return

        # Non verbose output needs only NIC vendor names.
        nic_vendor_set = set(mac_nic_dictionary.values())

        response = ""
        if len(nic_vendor_set) == 0:
            response = self._NO_MAC_FOUND_MESSAGE
        elif len(nic_vendor_set) > 1:
            response += ", ".join(str(nic_vendor_iterator)
                                  for nic_vendor_iterator in nic_vendor_set)
        else:
            response += nic_vendor_set.pop()

        print(response)
