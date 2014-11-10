#
# Copyright (C) 2013-2014 eNovance SAS <licensing@enovance.com>
#
# Author: Frederic Lepied <frederic.lepied@enovance.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import fcntl
import mock
import socket
import unittest

import detect
import detect_utils


class Keeper:
    def __init__(self, fname, rets):
        self.rets = rets
        self.fname = fname

    def fake(self, arg):
        if len(self.rets) == 0:
            raise Exception('Invalid call to %s(%s)' % (self.fname, arg))
#         else:
#             print('Call to %s(%s)' % (self.fname, arg))
        ret = self.rets[0]
        self.rets = self.rets[1:]
        return ret


class TestDetect(unittest.TestCase):

    def test_size_in_gb(self):
        self.assertEqual(detect.size_in_gb('100 GB'), '100')

    def test_size_in_tb(self):
        self.assertEqual(detect.size_in_gb('100TB'), '100000')

    def test_size_in_dottb(self):
        self.assertEqual(detect.size_in_gb('3.4601 TB'), '3460')

    def test_size_in_nothing(self):
        self.assertEqual(detect.size_in_gb('100'), '100')

    def test_get_cidr(self):
        self.assertEqual(detect.get_cidr('255.255.0.0'), '16')

    def _save_functions(self, nbproc, nbphys):
        # replace the call to nproc by a fake result
        self.save = detect.cmd
        self.output_lines = detect.output_lines
        self.saved_ntoa = socket.inet_ntoa
        self.saved_ioctl = fcntl.ioctl
        self.saved_get_uuid = detect.get_uuid
        self.saved_lld_status = detect_utils.get_lld_status

        def fake(x):
            return (0, nbproc)

        def fake_ntoa(arg):
            return '255.255.255.0'

        def fake_ioctl(arg, arg2, arg3):
            return []

        def fake_get_uuid():
            return '83462C81-52BA-11CB-870F'

        def fake_lld_status(arg, arg1):
            return []

        detect.cmd = fake
        keeper = Keeper('detect.output_lines',
                        [('vmx', ) for idx in range(nbphys)] +
                        [('Ubuntu', ),
                         ('Ubuntu 14.04 LTS', ),
                         ('3.13.0-24-generic', ),
                         ('x86_64', ),
                         ('BOOT_IMAGE=/boot/vmlinuz', )])
        detect.output_lines = mock.MagicMock(side_effect=keeper.fake)
        socket.inet_ntoa = fake_ntoa
        fcntl.ioctl = fake_ioctl
        detect.get_uuid = fake_get_uuid
        detect_utils.get_lld_status = fake_lld_status

    def test_parse_dmesg(self):
        hw = []
        detect.parse_dmesg(hw, "src/sample_dmesg")
        self.assertEqual(hw, [('ahci', '0000:00:1f.2:', 'flags', '64bit apst clo ems led ncq part pio slum sntf')])

    def _restore_functions(self):
        detect.cmd = self.save
        detect.output_lines = self.output_lines
        socket.inet_ntoa = self.saved_ntoa
        fcntl.ioctl = self.saved_ioctl
        detect.get_uuid = self.saved_get_uuid
        detect_utils.get_lld_status = self.saved_lld_status

    def test_detect_system_3(self):
        l = []
        self._save_functions("4", 2)
        detect.detect_system(l, XML3)
        self._restore_functions()
        self.assertEqual(
            l,
            [('system', 'product', 'serial', 'Empty'),
             ('system', 'product', 'name', 'S2915'),
             ('system', 'product', 'vendor', 'Tyan Computer Corporation'),
             ('system', 'product', 'version', 'REFERENCE'),
             ('system', 'product', 'uuid', '83462C81-52BA-11CB-870F'),
             ('system', 'motherboard', 'name', 'S2915'),
             ('system', 'motherboard', 'vendor', 'Tyan Computer Corporation'),
             ('system', 'motherboard', 'version', 'REFERENCE'),
             ('system', 'motherboard', 'serial', 'Empty'),
             ('firmware', 'bios', 'version', 'v3.00.2915 (10/10/2008)'),
             ('firmware', 'bios', 'vendor', 'Phoenix Technologies Ltd.'),
             ('memory', 'total', 'size', '4294967296'),
             ('memory', 'bank:0:0', 'description', 'DIMM Synchronous [empty]'),
             ('memory', 'bank:0:0', 'slot', 'C0_DIMM0'),
             ('memory', 'bank:0:1', 'description', 'DIMM Synchronous [empty]'),
             ('memory', 'bank:0:1', 'slot', 'C0_DIMM1'),
             ('memory', 'bank:0:2', 'size', '1073741824'),
             ('memory', 'bank:0:2', 'description', 'DIMM Synchronous'),
             ('memory', 'bank:0:2', 'slot', 'C0_DIMM2'),
             ('memory', 'bank:0:3', 'size', '1073741824'),
             ('memory', 'bank:0:3', 'description', 'DIMM Synchronous'),
             ('memory', 'bank:0:3', 'slot', 'C0_DIMM3'),
             ('memory', 'bank:0:4', 'description', 'DIMM Synchronous [empty]'),
             ('memory', 'bank:0:4', 'slot', 'C0_DIMM0'),
             ('memory', 'bank:0:5', 'description', 'DIMM Synchronous [empty]'),
             ('memory', 'bank:0:5', 'slot', 'C1_DIMM1'),
             ('memory', 'bank:0:6', 'size', '1073741824'),
             ('memory', 'bank:0:6', 'description', 'DIMM Synchronous'),
             ('memory', 'bank:0:6', 'slot', 'C1_DIMM2'),
             ('memory', 'bank:0:7', 'size', '1073741824'),
             ('memory', 'bank:0:7', 'description', 'DIMM Synchronous'),
             ('memory', 'bank:0:7', 'slot', 'C1_DIMM3'),
             ('memory', 'banks', 'count', '8'),
             ('cpu', 'physical_0', 'physid', '3'),
             ('cpu', 'physical_0', 'product',
              'Dual-Core AMD Opteron(tm) Processor 8218'),
             ('cpu', 'physical_0', 'vendor', 'Advanced Micro Devices [AMD]'),
             ('cpu', 'physical_0', 'version', 'AMD'),
             ('cpu', 'physical_0', 'frequency', '1000000000'),
             ('cpu', 'physical_0', 'clock', '200000000'),
             ('cpu', 'physical_0', 'flags', 'vmx'),
             ('cpu', 'physical_1', 'physid', '4'),
             ('cpu', 'physical_1', 'product',
              'Dual-Core AMD Opteron(tm) Processor 8218'),
             ('cpu', 'physical_1', 'vendor', 'Advanced Micro Devices [AMD]'),
             ('cpu', 'physical_1', 'version', 'AMD'),
             ('cpu', 'physical_1', 'frequency', '1000000000'),
             ('cpu', 'physical_1', 'clock', '200000000'),
             ('cpu', 'physical_1', 'flags', 'vmx'),
             ('cpu', 'physical', 'number', '2'),
             ('cpu', 'logical', 'number', '4'),
             ('system', 'os', 'vendor', 'Ubuntu'),
             ('system', 'os', 'version', 'Ubuntu 14.04 LTS'),
             ('system', 'kernel', 'version', '3.13.0-24-generic'),
             ('system', 'kernel', 'arch', 'x86_64'),
             ('system', 'kernel', 'cmdline', 'BOOT_IMAGE=/boot/vmlinuz'),
             ]
            )

    def test_detect_system_2(self):
        l = []
        self._save_functions("4", 1)
        detect.detect_system(l, XML2)
        self._restore_functions()
        self.assertEqual(
            l,
            [('system', 'product', 'serial', 'PB4F20N'),
             ('system', 'product', 'name', '2347GF8 (LENOVO_MT_2347)'),
             ('system', 'product', 'vendor', 'LENOVO'),
             ('system', 'product', 'version', 'ThinkPad T430'),
             ('system', 'product', 'uuid', '83462C81-52BA-11CB-870F'),
             ('system', 'motherboard', 'name', '2347GF8'),
             ('system', 'motherboard', 'vendor', 'LENOVO'),
             ('system', 'motherboard', 'version', 'Not Defined'),
             ('system', 'motherboard', 'serial', '1ZLMB31B1G6'),
             ('firmware', 'bios', 'version', 'G1ET73WW (2.09 )'),
             ('firmware', 'bios', 'date', '10/19/2012'),
             ('firmware', 'bios', 'vendor', 'LENOVO'),
             ('memory', 'total', 'size', '8589934592'),
             ('memory', 'bank:0', 'size', '4294967296'),
             ('memory', 'bank:0', 'clock', '1600000000'),
             ('memory', 'bank:0',  'description',
              'SODIMM DDR3 Synchrone 1600 MHz (0,6 ns)'),
             ('memory', 'bank:0', 'vendor', 'Samsung'),
             ('memory', 'bank:0', 'product', 'M471B5273CH0-CK0'),
             ('memory', 'bank:0', 'serial', '1222BCCE'),
             ('memory', 'bank:0', 'slot', 'ChannelA-DIMM0'),
             ('memory', 'bank:1', 'size', '4294967296'),
             ('memory', 'bank:1', 'clock', '1600000000'),
             ('memory', 'bank:1', 'description',
              'SODIMM DDR3 Synchrone 1600 MHz (0,6 ns)'),
             ('memory', 'bank:1', 'vendor', 'Samsung'),
             ('memory', 'bank:1', 'product', 'M471B5273CH0-CK0'),
             ('memory', 'bank:1', 'serial', '1222BCA2'),
             ('memory', 'bank:1', 'slot', 'ChannelB-DIMM0'),
             ('memory', 'banks', 'count', '2'),
             ('network', 'eth0', 'businfo', 'pci@0000:00:19.0'),
             ('network', 'eth0', 'vendor', 'Intel Corporation'),
             ('network', 'eth0', 'product',
              '82579LM Gigabit Network Connection'),
             ('network', 'eth0', 'firmware', '0.13-3'),
             ('network', 'eth0', 'link', 'no'),
             ('network', 'eth0', 'driver', 'e1000e'),
             ('network', 'eth0', 'latency', '0'),
             ('network', 'eth0', 'autonegotiation', 'on'),
             ('network', 'eth0', 'serial', '00:21:cc:d9:bf:26'),
             ('network', 'wlan0', 'businfo', 'pci@0000:03:00.0'),
             ('network', 'wlan0', 'vendor', 'Intel Corporation'),
             ('network', 'wlan0', 'product',
              'Centrino Advanced-N 6205 [Taylor Peak]'),
             ('network', 'wlan0', 'firmware', '18.168.6.1'),
             ('network', 'wlan0', 'ipv4', '192.168.1.185'),
             ('network', 'wlan0', 'ipv4-netmask', '255.255.255.0'),
             ('network', 'wlan0', 'ipv4-cidr', '24'),
             ('network', 'wlan0', 'ipv4-network', '192.168.1.0'),
             ('network', 'wlan0', 'link', 'yes'),
             ('network', 'wlan0', 'driver', 'iwlwifi'),
             ('network', 'wlan0', 'latency', '0'),
             ('network', 'wlan0', 'serial', '84:3a:4b:33:62:82'),
             ('network', 'wwan0', 'firmware', 'Mobile Broadband Network Device'),
             ('network', 'wwan0', 'link', 'no'),
             ('network', 'wwan0', 'driver', 'cdc_ncm'),
             ('network', 'wwan0', 'serial', '02:15:e0:ec:01:00'),
             ('cpu', 'physical_0', 'physid', '1'),
             ('cpu', 'physical_0', 'product',
              'Intel(R) Core(TM) i5-3320M CPU @ 2.60GHz'),
             ('cpu', 'physical_0', 'vendor', 'Intel Corp.'),
             ('cpu', 'physical_0', 'version', 'Intel(R) Core(TM) i5-3320M CPU @ 2.60GHz'),
             ('cpu', 'physical_0', 'frequency', '2601000000'),
             ('cpu', 'physical_0', 'clock', '100000000'),
             ('cpu', 'physical_0', 'cores', '2'),
             ('cpu', 'physical_0', 'enabled_cores', '2'),
             ('cpu', 'physical_0', 'threads', '4'),
             ('cpu', 'physical_0', 'flags', 'vmx'),
             ('cpu', 'physical', 'number', '1'),
             ('cpu', 'logical', 'number', '4'),
             ('system', 'os', 'vendor', 'Ubuntu'),
             ('system', 'os', 'version', 'Ubuntu 14.04 LTS'),
             ('system', 'kernel', 'version', '3.13.0-24-generic'),
             ('system', 'kernel', 'arch', 'x86_64'),
             ('system', 'kernel', 'cmdline', 'BOOT_IMAGE=/boot/vmlinuz'),
             ]
            )

    def test_detect_system(self):
        self.maxDiff = None
        l = []
        self._save_functions("7", 4)
        detect.detect_system(l, XML)
        self._restore_functions()
        self.assertEqual(
            l,
            [('system', 'product', 'serial', 'C02JR02WF57J'),
             ('system', 'product', 'name', 'MacBookAir5,2 (System SKU#)'),
             ('system', 'product', 'vendor', 'Apple Inc.'),
             ('system', 'product', 'version', '1.0'),
             ('system', 'product', 'uuid', '83462C81-52BA-11CB-870F'),
             ('system', 'motherboard', 'name', 'Mac-2E6FAB96566FE58C'),
             ('system', 'motherboard', 'vendor', 'Apple Inc.'),
             ('system', 'motherboard', 'version', 'MacBookAir5,2'),
             ('system', 'motherboard', 'serial', 'C02245301ZFF25WAT'),
             ('firmware', 'bios', 'version', 'MBA51.88Z.00EF.B01.1207271122'),
             ('firmware', 'bios', 'date', '07/27/2012'),
             ('firmware', 'bios', 'vendor', 'Apple Inc.'),
             ('memory', 'total', 'size', '8589934592'),
             ('memory', 'bank:0', 'size', '4294967296'),
             ('memory', 'bank:0', 'clock', '1600000000'),
             ('memory', 'bank:0', 'description',
              'SODIMM DDR3 Synchronous 1600 MHz (0,6 ns)'),
             ('memory', 'bank:0', 'vendor',
              'Hynix Semiconductor (Hyundai Electronics)'),
             ('memory', 'bank:0', 'product', 'HMT451S6MFR8A-PB'),
             ('memory', 'bank:0', 'serial', '0x00000000'),
             ('memory', 'bank:0', 'slot', 'DIMM0'),
             ('memory', 'bank:1', 'size', '4294967296'),
             ('memory', 'bank:1', 'clock', '1600000000'),
             ('memory', 'bank:1', 'description',
              'SODIMM DDR3 Synchronous 1600 MHz (0,6 ns)'),
             ('memory', 'bank:1', 'vendor',
              'Hynix Semiconductor (Hyundai Electronics)'),
             ('memory', 'bank:1', 'product', 'HMT451S6MFR8A-PB'),
             ('memory', 'bank:1', 'serial', '0x00000000'),
             ('memory', 'bank:1', 'slot', 'DIMM0'),
             ('memory', 'banks', 'count', '2'),
             ('network', 'vnet0', 'size', '10000000'),
             ('network', 'vnet0', 'link', 'yes'),
             ('network', 'vnet0', 'driver', 'tun'),
             ('network', 'vnet0', 'duplex', 'full'),
             ('network', 'vnet0', 'speed', '10Mbit/s'),
             ('network', 'vnet0', 'autonegotiation', 'off'),
             ('network', 'vnet0', 'serial', 'fe:54:00:c1:1a:f7'),
             ('network', 'tap0', 'size', '10000000'),
             ('network', 'tap0', 'ipv4', '10.152.18.103'),
             ('network', 'tap0', 'ipv4-netmask', '255.255.255.0'),
             ('network', 'tap0', 'ipv4-cidr', '24'),
             ('network', 'tap0', 'ipv4-network', '10.152.18.0'),
             ('network', 'tap0', 'link', 'yes'),
             ('network', 'tap0', 'driver', 'tun'),
             ('network', 'tap0', 'duplex', 'full'),
             ('network', 'tap0', 'speed', '10Mbit/s'),
             ('network', 'tap0', 'autonegotiation', 'off'),
             ('network', 'tap0', 'serial', 'e2:66:69:22:be:fb'),
             ('network', 'wlan0', 'firmware', 'N/A'),
             ('network', 'wlan0', 'ipv4', '192.168.12.13'),
             ('network', 'wlan0', 'ipv4-netmask', '255.255.255.0'),
             ('network', 'wlan0', 'ipv4-cidr', '24'),
             ('network', 'wlan0', 'ipv4-network', '192.168.12.0'),
             ('network', 'wlan0', 'link', 'yes'),
             ('network', 'wlan0', 'driver', 'brcmsmac'),
             ('network', 'wlan0', 'serial', '00:88:65:35:2b:50'),
             ('cpu', 'physical_0', 'physid', '0'),
             ('cpu', 'physical_0', 'product',
              'Intel(R) Core(TM) i7-3667U CPU @ 2.00GHz'),
             ('cpu', 'physical_0', 'vendor', 'Intel Corp.'),
             ('cpu', 'physical_0', 'version', 'Intel(R) Core(TM) i7-3667U CPU @ 2.00GHz'),
             ('cpu', 'physical_0', 'frequency', '800000000'),
             ('cpu', 'physical_0', 'clock', '25000000'),
             ('cpu', 'physical_0', 'flags', 'vmx'),
             ('cpu', 'physical_1', 'physid', '5'),
             ('cpu', 'physical_1', 'vendor', 'Intel(R) Corporation'),
             ('cpu', 'physical_1', 'version', 'Intel(R) Core(TM) i7-3667U CPU @ 2.00GHz'),
             ('cpu', 'physical_1', 'frequency', '800000000'),
             ('cpu', 'physical_1', 'clock', '25000000'),
             ('cpu', 'physical_1', 'flags', 'vmx'),
             ('cpu', 'physical_2', 'physid', 'a'),
             ('cpu', 'physical_2', 'vendor', 'Intel(R) Corporation'),
             ('cpu', 'physical_2', 'version', 'Intel(R) Core(TM) i7-3667U CPU @ 2.00GHz'),
             ('cpu', 'physical_2', 'frequency', '800000000'),
             ('cpu', 'physical_2', 'clock', '25000000'),
             ('cpu', 'physical_2', 'flags', 'vmx'),
             ('cpu', 'physical_3', 'physid', 'f'),
             ('cpu', 'physical_3', 'vendor', 'Intel(R) Corporation'),
             ('cpu', 'physical_3', 'version', 'Intel(R) Core(TM) i7-3667U CPU @ 2.00GHz'),
             ('cpu', 'physical_3', 'frequency', '800000000'),
             ('cpu', 'physical_3', 'clock', '25000000'),
             ('cpu', 'physical_3', 'flags', 'vmx'),
             ('cpu', 'physical', 'number', '4'),
             ('cpu', 'logical', 'number', '7'),
             ('system', 'os', 'vendor', 'Ubuntu'),
             ('system', 'os', 'version', 'Ubuntu 14.04 LTS'),
             ('system', 'kernel', 'version', '3.13.0-24-generic'),
             ('system', 'kernel', 'arch', 'x86_64'),
             ('system', 'kernel', 'cmdline', 'BOOT_IMAGE=/boot/vmlinuz'),
             ]
            )

XML = '''<?xml version="1.0" standalone="yes" ?>
<!-- generated by lshw-B.02.16 -->
<!-- GCC 4.7.1 -->
<!-- Linux 3.8.0-26-generic #38-Ubuntu SMP Mon Jun 17 21:43:33 UTC 2013 x86_64 -->
<!-- GNU libc 2 (glibc 2.17) -->
<list>
<node id="fred-macbookair" claimed="true" class="system" handle="DMI:001B">
 <description>Notebook</description>
 <product>MacBookAir5,2 (System SKU#)</product>
 <vendor>Apple Inc.</vendor>
 <version>1.0</version>
 <serial>C02JR02WF57J</serial>
 <width units="bits">64</width>
 <configuration>
  <setting id="boot" value="normal" />
  <setting id="chassis" value="notebook" />
  <setting id="family" value="MacBook Air" />
  <setting id="sku" value="System SKU#" />
  <setting id="uuid" value="32520E5E-DB6F-0A58-97C3-598FBCAACA5A" />
 </configuration>
 <capabilities>
  <capability id="smbios-2.4" >SMBIOS version 2.4</capability>
  <capability id="dmi-2.4" >DMI version 2.4</capability>
  <capability id="vsyscall32" >32-bit processes</capability>
 </capabilities>
  <node id="core" claimed="true" class="bus" handle="DMI:001C">
   <description>Motherboard</description>
   <product>Mac-2E6FAB96566FE58C</product>
   <vendor>Apple Inc.</vendor>
   <physid>0</physid>
   <version>MacBookAir5,2</version>
   <serial>C02245301ZFF25WAT</serial>
   <slot>Part Component</slot>
    <node id="cpu:0" claimed="true" class="processor" handle="DMI:0000">
     <description>CPU</description>
     <product>Intel(R) Core(TM) i7-3667U CPU @ 2.00GHz</product>
     <vendor>Intel Corp.</vendor>
     <physid>0</physid>
     <businfo>cpu@0</businfo>
     <version>Intel(R) Core(TM) i7-3667U CPU @ 2.00GHz</version>
     <slot>U2E1</slot>
     <size units="Hz">800000000</size>
     <capacity units="Hz">800000000</capacity>
     <width units="bits">64</width>
     <clock units="Hz">25000000</clock>
     <capabilities>
      <capability id="fpu" >mathematical co-processor</capability>
      <capability id="fpu_exception" >FPU exceptions reporting</capability>
      <capability id="wp" />
      <capability id="vme" >virtual mode extensions</capability>
      <capability id="de" >debugging extensions</capability>
      <capability id="pse" >page size extensions</capability>
      <capability id="tsc" >time stamp counter</capability>
      <capability id="msr" >model-specific registers</capability>
      <capability id="pae" >4GB+ memory addressing (Physical Address Extension)</capability>
      <capability id="mce" >machine check exceptions</capability>
      <capability id="cx8" >compare and exchange 8-byte</capability>
      <capability id="apic" >on-chip advanced programmable interrupt controller (APIC)</capability>
      <capability id="sep" >fast system calls</capability>
      <capability id="mtrr" >memory type range registers</capability>
      <capability id="pge" >page global enable</capability>
      <capability id="mca" >machine check architecture</capability>
      <capability id="cmov" >conditional move instruction</capability>
      <capability id="pat" >page attribute table</capability>
      <capability id="pse36" >36-bit page size extensions</capability>
      <capability id="clflush" />
      <capability id="dts" >debug trace and EMON store MSRs</capability>
      <capability id="acpi" >thermal control (ACPI)</capability>
      <capability id="mmx" >multimedia extensions (MMX)</capability>
      <capability id="fxsr" >fast floating point save/restore</capability>
      <capability id="sse" >streaming SIMD extensions (SSE)</capability>
      <capability id="sse2" >streaming SIMD extensions (SSE2)</capability>
      <capability id="ss" >self-snoop</capability>
      <capability id="ht" >HyperThreading</capability>
      <capability id="tm" >thermal interrupt and status</capability>
      <capability id="pbe" >pending break event</capability>
      <capability id="syscall" >fast system calls</capability>
      <capability id="nx" >no-execute bit (NX)</capability>
      <capability id="rdtscp" />
      <capability id="x86-64" >64bits extensions (x86-64)</capability>
      <capability id="constant_tsc" />
      <capability id="arch_perfmon" />
      <capability id="pebs" />
      <capability id="bts" />
      <capability id="rep_good" />
      <capability id="nopl" />
      <capability id="xtopology" />
      <capability id="nonstop_tsc" />
      <capability id="aperfmperf" />
      <capability id="eagerfpu" />
      <capability id="pni" />
      <capability id="pclmulqdq" />
      <capability id="dtes64" />
      <capability id="monitor" />
      <capability id="ds_cpl" />
      <capability id="vmx" />
      <capability id="smx" />
      <capability id="est" />
      <capability id="tm2" />
      <capability id="ssse3" />
      <capability id="cx16" />
      <capability id="xtpr" />
      <capability id="pdcm" />
      <capability id="pcid" />
      <capability id="sse4_1" />
      <capability id="sse4_2" />
      <capability id="x2apic" />
      <capability id="popcnt" />
      <capability id="tsc_deadline_timer" />
      <capability id="aes" />
      <capability id="xsave" />
      <capability id="avx" />
      <capability id="f16c" />
      <capability id="rdrand" />
      <capability id="lahf_lm" />
      <capability id="ida" />
      <capability id="arat" />
      <capability id="xsaveopt" />
      <capability id="pln" />
      <capability id="pts" />
      <capability id="dtherm" />
      <capability id="tpr_shadow" />
      <capability id="vnmi" />
      <capability id="flexpriority" />
      <capability id="ept" />
      <capability id="vpid" />
      <capability id="fsgsbase" />
      <capability id="smep" />
      <capability id="erms" />
      <capability id="cpufreq" >CPU Frequency scaling</capability>
     </capabilities>
      <node id="cache:0" claimed="true" class="memory" handle="DMI:0002">
       <description>L1 cache</description>
       <physid>2</physid>
       <slot>Unknown</slot>
       <size units="bytes">32768</size>
       <capacity units="bytes">32768</capacity>
       <capabilities>
        <capability id="asynchronous" >Asynchronous</capability>
        <capability id="internal" >Internal</capability>
        <capability id="write-back" >Write-back</capability>
       </capabilities>
      </node>
      <node id="cache:1" claimed="true" class="memory" handle="DMI:0003">
       <description>L2 cache</description>
       <physid>3</physid>
       <slot>Unknown</slot>
       <size units="bytes">262144</size>
       <capacity units="bytes">262144</capacity>
       <capabilities>
        <capability id="asynchronous" >Asynchronous</capability>
        <capability id="internal" >Internal</capability>
        <capability id="write-back" >Write-back</capability>
        <capability id="instruction" >Instruction cache</capability>
       </capabilities>
      </node>
      <node id="cache:2" claimed="true" class="memory" handle="DMI:0004">
       <description>L3 cache</description>
       <physid>4</physid>
       <slot>Unknown</slot>
       <size units="bytes">4096</size>
       <capacity units="bytes">4096</capacity>
       <capabilities>
        <capability id="asynchronous" >Asynchronous</capability>
        <capability id="internal" >Internal</capability>
        <capability id="write-back" >Write-back</capability>
        <capability id="instruction" >Instruction cache</capability>
       </capabilities>
      </node>
    </node>
    <node id="cache:0" claimed="true" class="memory" handle="DMI:0001">
     <description>L1 cache</description>
     <physid>1</physid>
     <slot>Unknown</slot>
     <size units="bytes">32768</size>
     <capacity units="bytes">32768</capacity>
     <capabilities>
      <capability id="asynchronous" >Asynchronous</capability>
      <capability id="internal" >Internal</capability>
      <capability id="write-back" >Write-back</capability>
     </capabilities>
    </node>
    <node id="cpu:1" claimed="true" class="processor" handle="DMI:0005">
     <description>CPU</description>
     <vendor>Intel(R) Corporation</vendor>
     <physid>5</physid>
     <businfo>cpu@1</businfo>
     <version>Intel(R) Core(TM) i7-3667U CPU @ 2.00GHz</version>
     <slot>U2E1</slot>
     <size units="Hz">800000000</size>
     <capacity units="Hz">800000000</capacity>
     <clock units="Hz">25000000</clock>
     <capabilities>
      <capability id="cpufreq" >CPU Frequency scaling</capability>
     </capabilities>
      <node id="cache:0" claimed="true" class="memory" handle="DMI:0007">
       <description>L1 cache</description>
       <physid>7</physid>
       <slot>Unknown</slot>
       <size units="bytes">32768</size>
       <capacity units="bytes">32768</capacity>
       <capabilities>
        <capability id="asynchronous" >Asynchronous</capability>
        <capability id="internal" >Internal</capability>
        <capability id="write-back" >Write-back</capability>
       </capabilities>
      </node>
      <node id="cache:1" claimed="true" class="memory" handle="DMI:0008">
       <description>L2 cache</description>
       <physid>8</physid>
       <slot>Unknown</slot>
       <size units="bytes">262144</size>
       <capacity units="bytes">262144</capacity>
       <capabilities>
        <capability id="asynchronous" >Asynchronous</capability>
        <capability id="internal" >Internal</capability>
        <capability id="write-back" >Write-back</capability>
        <capability id="instruction" >Instruction cache</capability>
       </capabilities>
      </node>
      <node id="cache:2" claimed="true" class="memory" handle="DMI:0009">
       <description>L3 cache</description>
       <physid>9</physid>
       <slot>Unknown</slot>
       <size units="bytes">4096</size>
       <capacity units="bytes">4096</capacity>
       <capabilities>
        <capability id="asynchronous" >Asynchronous</capability>
        <capability id="internal" >Internal</capability>
        <capability id="write-back" >Write-back</capability>
        <capability id="instruction" >Instruction cache</capability>
       </capabilities>
      </node>
    </node>
    <node id="cache:1" claimed="true" class="memory" handle="DMI:0006">
     <description>L1 cache</description>
     <physid>6</physid>
     <slot>Unknown</slot>
     <size units="bytes">32768</size>
     <capacity units="bytes">32768</capacity>
     <capabilities>
      <capability id="asynchronous" >Asynchronous</capability>
      <capability id="internal" >Internal</capability>
      <capability id="write-back" >Write-back</capability>
     </capabilities>
    </node>
    <node id="cpu:2" claimed="true" class="processor" handle="DMI:000A">
     <description>CPU</description>
     <vendor>Intel(R) Corporation</vendor>
     <physid>a</physid>
     <businfo>cpu@2</businfo>
     <version>Intel(R) Core(TM) i7-3667U CPU @ 2.00GHz</version>
     <slot>U2E1</slot>
     <size units="Hz">800000000</size>
     <capacity units="Hz">800000000</capacity>
     <clock units="Hz">25000000</clock>
     <capabilities>
      <capability id="cpufreq" >CPU Frequency scaling</capability>
     </capabilities>
      <node id="cache:0" claimed="true" class="memory" handle="DMI:000C">
       <description>L1 cache</description>
       <physid>c</physid>
       <slot>Unknown</slot>
       <size units="bytes">32768</size>
       <capacity units="bytes">32768</capacity>
       <capabilities>
        <capability id="asynchronous" >Asynchronous</capability>
        <capability id="internal" >Internal</capability>
        <capability id="write-back" >Write-back</capability>
       </capabilities>
      </node>
      <node id="cache:1" claimed="true" class="memory" handle="DMI:000D">
       <description>L2 cache</description>
       <physid>d</physid>
       <slot>Unknown</slot>
       <size units="bytes">262144</size>
       <capacity units="bytes">262144</capacity>
       <capabilities>
        <capability id="asynchronous" >Asynchronous</capability>
        <capability id="internal" >Internal</capability>
        <capability id="write-back" >Write-back</capability>
        <capability id="instruction" >Instruction cache</capability>
       </capabilities>
      </node>
      <node id="cache:2" claimed="true" class="memory" handle="DMI:000E">
       <description>L3 cache</description>
       <physid>e</physid>
       <slot>Unknown</slot>
       <size units="bytes">4096</size>
       <capacity units="bytes">4096</capacity>
       <capabilities>
        <capability id="asynchronous" >Asynchronous</capability>
        <capability id="internal" >Internal</capability>
        <capability id="write-back" >Write-back</capability>
        <capability id="instruction" >Instruction cache</capability>
       </capabilities>
      </node>
    </node>
    <node id="cache:2" claimed="true" class="memory" handle="DMI:000B">
     <description>L1 cache</description>
     <physid>b</physid>
     <slot>Unknown</slot>
     <size units="bytes">32768</size>
     <capacity units="bytes">32768</capacity>
     <capabilities>
      <capability id="asynchronous" >Asynchronous</capability>
      <capability id="internal" >Internal</capability>
      <capability id="write-back" >Write-back</capability>
     </capabilities>
    </node>
    <node id="cpu:3" claimed="true" class="processor" handle="DMI:000F">
     <description>CPU</description>
     <vendor>Intel(R) Corporation</vendor>
     <physid>f</physid>
     <businfo>cpu@3</businfo>
     <version>Intel(R) Core(TM) i7-3667U CPU @ 2.00GHz</version>
     <slot>U2E1</slot>
     <size units="Hz">800000000</size>
     <capacity units="Hz">800000000</capacity>
     <clock units="Hz">25000000</clock>
     <capabilities>
      <capability id="cpufreq" >CPU Frequency scaling</capability>
     </capabilities>
      <node id="cache:0" claimed="true" class="memory" handle="DMI:0011">
       <description>L1 cache</description>
       <physid>11</physid>
       <slot>Unknown</slot>
       <size units="bytes">32768</size>
       <capacity units="bytes">32768</capacity>
       <capabilities>
        <capability id="asynchronous" >Asynchronous</capability>
        <capability id="internal" >Internal</capability>
        <capability id="write-back" >Write-back</capability>
       </capabilities>
      </node>
      <node id="cache:1" claimed="true" class="memory" handle="DMI:0012">
       <description>L2 cache</description>
       <physid>12</physid>
       <slot>Unknown</slot>
       <size units="bytes">262144</size>
       <capacity units="bytes">262144</capacity>
       <capabilities>
        <capability id="asynchronous" >Asynchronous</capability>
        <capability id="internal" >Internal</capability>
        <capability id="write-back" >Write-back</capability>
        <capability id="instruction" >Instruction cache</capability>
       </capabilities>
      </node>
      <node id="cache:2" claimed="true" class="memory" handle="DMI:0013">
       <description>L3 cache</description>
       <physid>13</physid>
       <slot>Unknown</slot>
       <size units="bytes">4096</size>
       <capacity units="bytes">4096</capacity>
       <capabilities>
        <capability id="asynchronous" >Asynchronous</capability>
        <capability id="internal" >Internal</capability>
        <capability id="write-back" >Write-back</capability>
        <capability id="instruction" >Instruction cache</capability>
       </capabilities>
      </node>
    </node>
    <node id="cache:3" claimed="true" class="memory" handle="DMI:0010">
     <description>L1 cache</description>
     <physid>10</physid>
     <slot>Unknown</slot>
     <size units="bytes">32768</size>
     <capacity units="bytes">32768</capacity>
     <capabilities>
      <capability id="asynchronous" >Asynchronous</capability>
      <capability id="internal" >Internal</capability>
      <capability id="write-back" >Write-back</capability>
     </capabilities>
    </node>
    <node id="memory" claimed="true" class="memory" handle="DMI:0014">
     <description>System Memory</description>
     <physid>14</physid>
     <slot>System board or motherboard</slot>
     <size units="bytes">8589934592</size>
      <node id="bank:0" claimed="true" class="memory" handle="DMI:0016">
       <description>SODIMM DDR3 Synchronous 1600 MHz (0,6 ns)</description>
       <product>HMT451S6MFR8A-PB</product>
       <vendor>Hynix Semiconductor (Hyundai Electronics)</vendor>
       <physid>0</physid>
       <serial>0x00000000</serial>
       <slot>DIMM0</slot>
       <size units="bytes">4294967296</size>
       <clock units="Hz">1600000000</clock>
      </node>
      <node id="bank:1" claimed="true" class="memory" handle="DMI:0018">
       <description>SODIMM DDR3 Synchronous 1600 MHz (0,6 ns)</description>
       <product>HMT451S6MFR8A-PB</product>
       <vendor>Hynix Semiconductor (Hyundai Electronics)</vendor>
       <physid>1</physid>
       <serial>0x00000000</serial>
       <slot>DIMM0</slot>
       <size units="bytes">4294967296</size>
       <clock units="Hz">1600000000</clock>
      </node>
    </node>
    <node id="firmware" claimed="true" class="memory" handle="">
     <description>BIOS</description>
     <vendor>Apple Inc.</vendor>
     <physid>1a</physid>
     <version>MBA51.88Z.00EF.B01.1207271122</version>
     <date>07/27/2012</date>
     <size units="bytes">1048576</size>
     <capacity units="bytes">8323072</capacity>
     <capabilities>
      <capability id="pci" >PCI bus</capability>
      <capability id="upgrade" >BIOS EEPROM can be upgraded</capability>
      <capability id="shadowing" >BIOS shadowing</capability>
      <capability id="cdboot" >Booting from CD-ROM/DVD</capability>
      <capability id="bootselect" >Selectable boot path</capability>
      <capability id="acpi" >ACPI</capability>
      <capability id="ieee1394boot" >Booting from IEEE1394 (Firewire)</capability>
      <capability id="smartbattery" >Smart battery</capability>
      <capability id="netboot" >Function-key initiated network service boot</capability>
     </capabilities>
    </node>
    <node id="pci" claimed="true" class="bridge" handle="PCIBUS:0000:00">
     <description>Host bridge</description>
     <product>3rd Gen Core processor DRAM Controller</product>
     <vendor>Intel Corporation</vendor>
     <physid>100</physid>
     <businfo>pci@0000:00:00.0</businfo>
     <version>09</version>
     <width units="bits">32</width>
     <clock units="Hz">33000000</clock>
      <node id="display" claimed="true" class="display" handle="PCI:0000:00:02.0">
       <description>VGA compatible controller</description>
       <product>3rd Gen Core processor Graphics Controller</product>
       <vendor>Intel Corporation</vendor>
       <physid>2</physid>
       <businfo>pci@0000:00:02.0</businfo>
       <version>09</version>
       <width units="bits">64</width>
       <clock units="Hz">33000000</clock>
       <configuration>
        <setting id="driver" value="i915" />
        <setting id="latency" value="0" />
       </configuration>
       <capabilities>
        <capability id="msi" >Message Signalled Interrupts</capability>
        <capability id="pm" >Power Management</capability>
        <capability id="vga_controller" />
        <capability id="bus_master" >bus mastering</capability>
        <capability id="cap_list" >PCI capabilities listing</capability>
        <capability id="rom" >extension ROM</capability>
       </capabilities>
       <resources>
        <resource type="irq" value="45" />
        <resource type="memory" value="a0000000-a03fffff" />
        <resource type="memory" value="90000000-9fffffff" />
        <resource type="ioport" value="2000(size=64)" />
       </resources>
      </node>
      <node id="usb:0" claimed="true" class="bus" handle="PCI:0000:00:14.0">
       <description>USB controller</description>
       <product>7 Series/C210 Series Chipset Family USB xHCI Host Controller</product>
       <vendor>Intel Corporation</vendor>
       <physid>14</physid>
       <businfo>pci@0000:00:14.0</businfo>
       <version>04</version>
       <width units="bits">64</width>
       <clock units="Hz">33000000</clock>
       <configuration>
        <setting id="driver" value="xhci_hcd" />
        <setting id="latency" value="0" />
       </configuration>
       <capabilities>
        <capability id="pm" >Power Management</capability>
        <capability id="msi" >Message Signalled Interrupts</capability>
        <capability id="xhci" />
        <capability id="bus_master" >bus mastering</capability>
        <capability id="cap_list" >PCI capabilities listing</capability>
       </capabilities>
       <resources>
        <resource type="irq" value="43" />
        <resource type="memory" value="a0600000-a060ffff" />
       </resources>
      </node>
      <node id="communication" claimed="true" class="communication" handle="PCI:0000:00:16.0">
       <description>Communication controller</description>
       <product>7 Series/C210 Series Chipset Family MEI Controller #1</product>
       <vendor>Intel Corporation</vendor>
       <physid>16</physid>
       <businfo>pci@0000:00:16.0</businfo>
       <version>04</version>
       <width units="bits">64</width>
       <clock units="Hz">33000000</clock>
       <configuration>
        <setting id="driver" value="mei" />
        <setting id="latency" value="0" />
       </configuration>
       <capabilities>
        <capability id="pm" >Power Management</capability>
        <capability id="msi" >Message Signalled Interrupts</capability>
        <capability id="bus_master" >bus mastering</capability>
        <capability id="cap_list" >PCI capabilities listing</capability>
       </capabilities>
       <resources>
        <resource type="irq" value="46" />
        <resource type="memory" value="a0617100-a061710f" />
       </resources>
      </node>
      <node id="usb:1" claimed="true" class="bus" handle="PCI:0000:00:1a.0">
       <description>USB controller</description>
       <product>7 Series/C210 Series Chipset Family USB Enhanced Host Controller #2</product>
       <vendor>Intel Corporation</vendor>
       <physid>1a</physid>
       <businfo>pci@0000:00:1a.0</businfo>
       <version>04</version>
       <width units="bits">32</width>
       <clock units="Hz">33000000</clock>
       <configuration>
        <setting id="driver" value="ehci-pci" />
        <setting id="latency" value="0" />
       </configuration>
       <capabilities>
        <capability id="pm" >Power Management</capability>
        <capability id="debug" >Debug port</capability>
        <capability id="ehci" >Enhanced Host Controller Interface (USB2)</capability>
        <capability id="bus_master" >bus mastering</capability>
        <capability id="cap_list" >PCI capabilities listing</capability>
       </capabilities>
       <resources>
        <resource type="irq" value="23" />
        <resource type="memory" value="a0616c00-a0616fff" />
       </resources>
      </node>
      <node id="multimedia" claimed="true" class="multimedia" handle="PCI:0000:00:1b.0">
       <description>Audio device</description>
       <product>7 Series/C210 Series Chipset Family High Definition Audio Controller</product>
       <vendor>Intel Corporation</vendor>
       <physid>1b</physid>
       <businfo>pci@0000:00:1b.0</businfo>
       <version>04</version>
       <width units="bits">64</width>
       <clock units="Hz">33000000</clock>
       <configuration>
        <setting id="driver" value="snd_hda_intel" />
        <setting id="latency" value="0" />
       </configuration>
       <capabilities>
        <capability id="pm" >Power Management</capability>
        <capability id="msi" >Message Signalled Interrupts</capability>
        <capability id="pciexpress" >PCI Express</capability>
        <capability id="bus_master" >bus mastering</capability>
        <capability id="cap_list" >PCI capabilities listing</capability>
       </capabilities>
       <resources>
        <resource type="irq" value="47" />
        <resource type="memory" value="a0610000-a0613fff" />
       </resources>
      </node>
      <node id="pci:0" claimed="true" class="bridge" handle="PCIBUS:0000:01">
       <description>PCI bridge</description>
       <product>7 Series/C210 Series Chipset Family PCI Express Root Port 1</product>
       <vendor>Intel Corporation</vendor>
       <physid>1c</physid>
       <businfo>pci@0000:00:1c.0</businfo>
       <version>c4</version>
       <width units="bits">32</width>
       <clock units="Hz">33000000</clock>
       <configuration>
        <setting id="driver" value="pcieport" />
       </configuration>
       <capabilities>
        <capability id="pci" />
        <capability id="pciexpress" >PCI Express</capability>
        <capability id="msi" >Message Signalled Interrupts</capability>
        <capability id="pm" >Power Management</capability>
        <capability id="normal_decode" />
        <capability id="bus_master" >bus mastering</capability>
        <capability id="cap_list" >PCI capabilities listing</capability>
       </capabilities>
       <resources>
        <resource type="irq" value="40" />
        <resource type="memory" value="a0500000-a05fffff" />
       </resources>
      </node>
      <node id="pci:1" claimed="true" class="bridge" handle="PCIBUS:0000:02">
       <description>PCI bridge</description>
       <product>7 Series/C210 Series Chipset Family PCI Express Root Port 2</product>
       <vendor>Intel Corporation</vendor>
       <physid>1c.1</physid>
       <businfo>pci@0000:00:1c.1</businfo>
       <version>c4</version>
       <width units="bits">32</width>
       <clock units="Hz">33000000</clock>
       <configuration>
        <setting id="driver" value="pcieport" />
       </configuration>
       <capabilities>
        <capability id="pci" />
        <capability id="pciexpress" >PCI Express</capability>
        <capability id="msi" >Message Signalled Interrupts</capability>
        <capability id="pm" >Power Management</capability>
        <capability id="normal_decode" />
        <capability id="bus_master" >bus mastering</capability>
        <capability id="cap_list" >PCI capabilities listing</capability>
       </capabilities>
       <resources>
        <resource type="irq" value="41" />
        <resource type="memory" value="a0400000-a04fffff" />
       </resources>
        <node id="network" claimed="true" class="network" handle="PCI:0000:02:00.0">
         <description>Network controller</description>
         <product>BCM43224 802.11a/b/g/n</product>
         <vendor>Broadcom Corporation</vendor>
         <physid>0</physid>
         <businfo>pci@0000:02:00.0</businfo>
         <version>01</version>
         <width units="bits">64</width>
         <clock units="Hz">33000000</clock>
         <configuration>
          <setting id="driver" value="bcma-pci-bridge" />
          <setting id="latency" value="0" />
         </configuration>
         <capabilities>
          <capability id="pm" >Power Management</capability>
          <capability id="msi" >Message Signalled Interrupts</capability>
          <capability id="pciexpress" >PCI Express</capability>
          <capability id="bus_master" >bus mastering</capability>
          <capability id="cap_list" >PCI capabilities listing</capability>
         </capabilities>
         <resources>
          <resource type="irq" value="17" />
          <resource type="memory" value="a0400000-a0403fff" />
         </resources>
        </node>
      </node>
      <node id="pci:2" claimed="true" class="bridge" handle="PCIBUS:0000:03">
       <description>PCI bridge</description>
       <product>7 Series/C210 Series Chipset Family PCI Express Root Port 5</product>
       <vendor>Intel Corporation</vendor>
       <physid>1c.4</physid>
       <businfo>pci@0000:00:1c.4</businfo>
       <version>c4</version>
       <width units="bits">32</width>
       <clock units="Hz">33000000</clock>
       <configuration>
        <setting id="driver" value="pcieport" />
       </configuration>
       <capabilities>
        <capability id="pci" />
        <capability id="pciexpress" >PCI Express</capability>
        <capability id="msi" >Message Signalled Interrupts</capability>
        <capability id="pm" >Power Management</capability>
        <capability id="normal_decode" />
        <capability id="bus_master" >bus mastering</capability>
        <capability id="cap_list" >PCI capabilities listing</capability>
       </capabilities>
       <resources>
        <resource type="irq" value="42" />
        <resource type="ioport" value="3000(size=12288)" />
        <resource type="memory" value="a0700000-ac9fffff" />
        <resource type="ioport" value="aca00000(size=201326592)" />
       </resources>
      </node>
      <node id="usb:2" claimed="true" class="bus" handle="PCI:0000:00:1d.0">
       <description>USB controller</description>
       <product>7 Series/C210 Series Chipset Family USB Enhanced Host Controller #1</product>
       <vendor>Intel Corporation</vendor>
       <physid>1d</physid>
       <businfo>pci@0000:00:1d.0</businfo>
       <version>04</version>
       <width units="bits">32</width>
       <clock units="Hz">33000000</clock>
       <configuration>
        <setting id="driver" value="ehci-pci" />
        <setting id="latency" value="0" />
       </configuration>
       <capabilities>
        <capability id="pm" >Power Management</capability>
        <capability id="debug" >Debug port</capability>
        <capability id="ehci" >Enhanced Host Controller Interface (USB2)</capability>
        <capability id="bus_master" >bus mastering</capability>
        <capability id="cap_list" >PCI capabilities listing</capability>
       </capabilities>
       <resources>
        <resource type="irq" value="22" />
        <resource type="memory" value="a0616800-a0616bff" />
       </resources>
      </node>
      <node id="isa" claimed="true" class="bridge" handle="PCI:0000:00:1f.0">
       <description>ISA bridge</description>
       <product>QS77 Express Chipset LPC Controller</product>
       <vendor>Intel Corporation</vendor>
       <physid>1f</physid>
       <businfo>pci@0000:00:1f.0</businfo>
       <version>04</version>
       <width units="bits">32</width>
       <clock units="Hz">33000000</clock>
       <configuration>
        <setting id="driver" value="lpc_ich" />
        <setting id="latency" value="0" />
       </configuration>
       <capabilities>
        <capability id="isa" />
        <capability id="bus_master" >bus mastering</capability>
        <capability id="cap_list" >PCI capabilities listing</capability>
       </capabilities>
       <resources>
        <resource type="irq" value="0" />
       </resources>
      </node>
      <node id="storage" claimed="true" class="storage" handle="PCI:0000:00:1f.2">
       <description>SATA controller</description>
       <product>7 Series Chipset Family 6-port SATA Controller [AHCI mode]</product>
       <vendor>Intel Corporation</vendor>
       <physid>1f.2</physid>
       <businfo>pci@0000:00:1f.2</businfo>
       <version>04</version>
       <width units="bits">32</width>
       <clock units="Hz">66000000</clock>
       <configuration>
        <setting id="driver" value="ahci" />
        <setting id="latency" value="0" />
       </configuration>
       <capabilities>
        <capability id="storage" />
        <capability id="msi" >Message Signalled Interrupts</capability>
        <capability id="pm" >Power Management</capability>
        <capability id="ahci_1.0" />
        <capability id="bus_master" >bus mastering</capability>
        <capability id="cap_list" >PCI capabilities listing</capability>
       </capabilities>
       <resources>
        <resource type="irq" value="44" />
        <resource type="ioport" value="2098(size=8)" />
        <resource type="ioport" value="20bc(size=4)" />
        <resource type="ioport" value="2090(size=8)" />
        <resource type="ioport" value="20b8(size=4)" />
        <resource type="ioport" value="2060(size=32)" />
        <resource type="memory" value="a0616000-a06167ff" />
       </resources>
      </node>
      <node id="serial" class="bus" handle="PCI:0000:00:1f.3">
       <description>SMBus</description>
       <product>7 Series/C210 Series Chipset Family SMBus Controller</product>
       <vendor>Intel Corporation</vendor>
       <physid>1f.3</physid>
       <businfo>pci@0000:00:1f.3</businfo>
       <version>04</version>
       <width units="bits">64</width>
       <clock units="Hz">33000000</clock>
       <configuration>
        <setting id="latency" value="0" />
       </configuration>
       <resources>
        <resource type="memory" value="a0617000-a06170ff" />
        <resource type="ioport" value="efa0(size=32)" />
       </resources>
      </node>
    </node>
    <node id="scsi:0" claimed="true" class="storage" handle="">
     <physid>2</physid>
     <logicalname>scsi0</logicalname>
     <capabilities>
      <capability id="emulated" >Emulated device</capability>
     </capabilities>
      <node id="disk" claimed="true" class="disk" handle="SCSI:00:00:00:00">
       <description>ATA Disk</description>
       <product>APPLE SSD SM512E</product>
       <physid>0.0.0</physid>
       <businfo>scsi@0:0.0.0</businfo>
       <logicalname>/dev/sda</logicalname>
       <dev>8:0</dev>
       <version>CXM0</version>
       <serial>S0YENYAC762532</serial>
       <size units="bytes">500277790720</size>
       <configuration>
        <setting id="ansiversion" value="5" />
        <setting id="sectorsize" value="4096" />
       </configuration>
       <capabilities>
        <capability id="partitioned" >Partitioned disk</capability>
        <capability id="partitioned:dos" >MS-DOS partition table</capability>
       </capabilities>
        <node id="volume:0" class="volume" handle="">
         <description>EFI GPT partition</description>
         <physid>1</physid>
         <businfo>scsi@0:0.0.0,1</businfo>
         <capacity>209735168</capacity>
         <capabilities>
          <capability id="primary" >Primary partition</capability>
          <capability id="nofs" >No filesystem</capability>
         </capabilities>
        </node>
        <node id="volume:1" claimed="true" class="volume" handle="">
         <description>Darwin/OS X HFS+ partition</description>
         <vendor>Mac OS X (journaled)</vendor>
         <physid>2</physid>
         <businfo>scsi@0:0.0.0,2</businfo>
         <logicalname>/dev/sda2</logicalname>
         <dev>8:2</dev>
         <version>4</version>
         <serial>47234807-a2e0-ba3c-0000-000000e89000</serial>
         <size units="bytes">33683525632</size>
         <capacity>33683525632</capacity>
         <configuration>
          <setting id="boot" value="osx" />
          <setting id="checked" value="2012-10-19 04:57:54" />
          <setting id="created" value="2012-10-19 01:57:54" />
          <setting id="filesystem" value="hfsplus" />
          <setting id="lastmountedby" value="HFSJ" />
          <setting id="modified" value="2013-06-11 12:14:38" />
          <setting id="state" value="clean" />
         </configuration>
         <capabilities>
          <capability id="primary" >Primary partition</capability>
          <capability id="bootable" >Bootable partition (active)</capability>
          <capability id="journaled" />
          <capability id="osx" >Contains a bootable Mac OS X installation</capability>
          <capability id="hfsplus" >MacOS HFS+</capability>
          <capability id="initialized" >initialized volume</capability>
         </capabilities>
        </node>
        <node id="volume:2" claimed="true" class="volume" handle="">
         <description>Darwin/OS X HFS+ partition</description>
         <vendor>Mac OS X (journaled)</vendor>
         <physid>3</physid>
         <businfo>scsi@0:0.0.0,3</businfo>
         <logicalname>/dev/sda3</logicalname>
         <dev>8:3</dev>
         <version>4</version>
         <serial>55724187-98b3-725b-0000-000000005000</serial>
         <size units="bytes">650002432</size>
         <capacity>650002432</capacity>
         <configuration>
          <setting id="boot" value="osx" />
          <setting id="checked" value="2012-10-19 04:59:42" />
          <setting id="created" value="2012-10-19 01:59:42" />
          <setting id="filesystem" value="hfsplus" />
          <setting id="lastmountedby" value="HFSJ" />
          <setting id="modified" value="2012-10-19 05:37:56" />
          <setting id="state" value="clean" />
         </configuration>
         <capabilities>
          <capability id="primary" >Primary partition</capability>
          <capability id="journaled" />
          <capability id="bootable" />
          <capability id="macos" >Contains a bootable Mac OS installation</capability>
          <capability id="osx" >Contains a bootable Mac OS X installation</capability>
          <capability id="hfsplus" >MacOS HFS+</capability>
          <capability id="initialized" >initialized volume</capability>
         </capabilities>
        </node>
        <node id="volume:3" claimed="true" class="volume" handle="">
         <description>Linux filesystem partition</description>
         <physid>4</physid>
         <businfo>scsi@0:0.0.0,4</businfo>
         <logicalname>/dev/sda4</logicalname>
         <dev>8:4</dev>
         <capacity>1048576</capacity>
         <capabilities>
          <capability id="primary" >Primary partition</capability>
         </capabilities>
        </node>
      </node>
    </node>
    <node id="scsi:1" claimed="true" class="storage" handle="SCSI:06">
     <physid>3</physid>
     <businfo>usb@2:1.8.3</businfo>
     <logicalname>scsi6</logicalname>
     <configuration>
      <setting id="driver" value="usb-storage" />
     </configuration>
     <capabilities>
      <capability id="emulated" >Emulated device</capability>
      <capability id="scsi-host" >SCSI host adapter</capability>
     </capabilities>
      <node id="disk" claimed="true" class="disk" handle="SCSI:06:00:00:00">
       <description>SCSI Disk</description>
       <product>SD Card Reader</product>
       <vendor>APPLE</vendor>
       <physid>0.0.0</physid>
       <businfo>scsi@6:0.0.0</businfo>
       <logicalname>/dev/sdb</logicalname>
       <dev>8:16</dev>
       <version>2.00</version>
       <configuration>
        <setting id="sectorsize" value="512" />
       </configuration>
       <capabilities>
        <capability id="removable" >support is removable</capability>
       </capabilities>
        <node id="medium" claimed="true" class="disk" handle="">
         <physid>0</physid>
         <logicalname>/dev/sdb</logicalname>
         <dev>8:16</dev>
        </node>
      </node>
    </node>
    <node id="scsi:2" claimed="true" class="storage" handle="SCSI:22">
     <physid>4</physid>
     <businfo>usb@3:1</businfo>
     <logicalname>scsi22</logicalname>
     <configuration>
      <setting id="driver" value="usb-storage" />
     </configuration>
     <capabilities>
      <capability id="emulated" >Emulated device</capability>
      <capability id="scsi-host" >SCSI host adapter</capability>
     </capabilities>
      <node id="disk:0" claimed="true" class="disk" handle="SCSI:22:00:00:00">
       <description>SCSI Disk</description>
       <physid>0.0.0</physid>
       <businfo>scsi@22:0.0.0</businfo>
       <logicalname>/dev/sdc</logicalname>
       <dev>8:32</dev>
       <configuration>
        <setting id="sectorsize" value="512" />
       </configuration>
      </node>
      <node id="disk:1" claimed="true" class="disk" handle="SCSI:22:00:00:01">
       <description>SCSI Disk</description>
       <physid>0.0.1</physid>
       <businfo>scsi@22:0.0.1</businfo>
       <logicalname>/dev/sdd</logicalname>
       <dev>8:48</dev>
       <configuration>
        <setting id="sectorsize" value="512" />
       </configuration>
      </node>
    </node>
  </node>
  <node id="battery" claimed="true" class="power" handle="DMI:0031">
   <product>Unknown</product>
   <vendor>Unknown</vendor>
   <physid>1</physid>
   <version>Unknown</version>
   <serial>Unknown</serial>
   <slot>Unknown</slot>
  </node>
  <node id="network:0" claimed="true" class="network" handle="">
   <description>Ethernet interface</description>
   <physid>2</physid>
   <logicalname>vnet0</logicalname>
   <serial>fe:54:00:c1:1a:f7</serial>
   <size units="bit/s">10000000</size>
   <configuration>
    <setting id="autonegotiation" value="off" />
    <setting id="broadcast" value="yes" />
    <setting id="driver" value="tun" />
    <setting id="driverversion" value="1.6" />
    <setting id="duplex" value="full" />
    <setting id="link" value="yes" />
    <setting id="multicast" value="yes" />
    <setting id="port" value="twisted pair" />
    <setting id="speed" value="10Mbit/s" />
   </configuration>
   <capabilities>
    <capability id="ethernet" />
    <capability id="physical" >Physical interface</capability>
   </capabilities>
  </node>
  <node id="network:1" claimed="true" class="network" handle="">
   <description>Ethernet interface</description>
   <physid>3</physid>
   <logicalname>tap0</logicalname>
   <serial>e2:66:69:22:be:fb</serial>
   <size units="bit/s">10000000</size>
   <configuration>
    <setting id="autonegotiation" value="off" />
    <setting id="broadcast" value="yes" />
    <setting id="driver" value="tun" />
    <setting id="driverversion" value="1.6" />
    <setting id="duplex" value="full" />
    <setting id="ip" value="10.152.18.103" />
    <setting id="link" value="yes" />
    <setting id="multicast" value="yes" />
    <setting id="port" value="twisted pair" />
    <setting id="speed" value="10Mbit/s" />
   </configuration>
   <capabilities>
    <capability id="ethernet" />
    <capability id="physical" >Physical interface</capability>
   </capabilities>
  </node>
  <node id="network:2" claimed="true" class="network" handle="">
   <description>Wireless interface</description>
   <physid>4</physid>
   <logicalname>wlan0</logicalname>
   <serial>00:88:65:35:2b:50</serial>
   <configuration>
    <setting id="broadcast" value="yes" />
    <setting id="driver" value="brcmsmac" />
    <setting id="driverversion" value="3.8.0-26-generic" />
    <setting id="firmware" value="N/A" />
    <setting id="ip" value="192.168.12.13" />
    <setting id="link" value="yes" />
    <setting id="multicast" value="yes" />
    <setting id="wireless" value="IEEE 802.11abgn" />
   </configuration>
   <capabilities>
    <capability id="ethernet" />
    <capability id="physical" >Physical interface</capability>
    <capability id="wireless" >Wireless-LAN</capability>
   </capabilities>
  </node>
</node>
</list>
'''

XML2 = '''<?xml version="1.0" standalone="yes" ?>
<list>
<node id="localhost.localdomain" claimed="true" class="system" handle="DMI:000F">
 <description>Ordinateur Bloc-notes</description>
 <product>2347GF8 (LENOVO_MT_2347)</product>
 <vendor>LENOVO</vendor>
 <version>ThinkPad T430</version>
 <serial>PB4F20N</serial>
 <width units="bits">64</width>
 <configuration>
  <setting id="administrator_password" value="disabled" />
  <setting id="chassis" value="notebook" />
  <setting id="family" value="ThinkPad T430" />
  <setting id="power-on_password" value="disabled" />
  <setting id="sku" value="LENOVO_MT_2347" />
  <setting id="uuid" value="81ACF869-C952-CB11-AF7F-DF81D2500F24" />
 </configuration>
 <capabilities>
  <capability id="smbios-2.7" >SMBIOS version 2.7</capability>
  <capability id="dmi-2.7" >DMI version 2.7</capability>
  <capability id="vsyscall32" >excution d'applications 32 bits</capability>
 </capabilities>
  <node id="core" claimed="true" class="bus" handle="DMI:0010">
   <description>Carte mre</description>
   <product>2347GF8</product>
   <vendor>LENOVO</vendor>
   <physid>0</physid>
   <version>Not Defined</version>
   <serial>1ZLMB31B1G6</serial>
   <slot>Not Available</slot>
    <node id="cpu" claimed="true" class="processor" handle="DMI:0001">
     <description>CPU</description>
     <product>Intel(R) Core(TM) i5-3320M CPU @ 2.60GHz</product>
     <vendor>Intel Corp.</vendor>
     <physid>1</physid>
     <businfo>cpu@0</businfo>
     <version>Intel(R) Core(TM) i5-3320M CPU @ 2.60GHz</version>
     <serial>None</serial>
     <slot>CPU Socket - U3E1</slot>
     <size units="Hz">2601000000</size>
     <capacity units="Hz">2601000000</capacity>
     <width units="bits">64</width>
     <clock units="Hz">100000000</clock>
     <configuration>
      <setting id="cores" value="2" />
      <setting id="enabledcores" value="2" />
      <setting id="threads" value="4" />
     </configuration>
     <capabilities>
      <capability id="x86-64" >64bits extensions (x86-64)</capability>
      <capability id="fpu" >mathematical co-processor</capability>
      <capability id="fpu_exception" >FPU exceptions reporting</capability>
      <capability id="wp" />
      <capability id="vme" >virtual mode extensions</capability>
      <capability id="de" >debugging extensions</capability>
      <capability id="pse" >page size extensions</capability>
      <capability id="tsc" >time stamp counter</capability>
      <capability id="msr" >model-specific registers</capability>
      <capability id="pae" >4GB+ memory addressing (Physical Address Extension)</capability>
      <capability id="mce" >machine check exceptions</capability>
      <capability id="cx8" >compare and exchange 8-byte</capability>
      <capability id="apic" >on-chip advanced programmable interrupt controller (APIC)</capability>
      <capability id="sep" >fast system calls</capability>
      <capability id="mtrr" >memory type range registers</capability>
      <capability id="pge" >page global enable</capability>
      <capability id="mca" >machine check architecture</capability>
      <capability id="cmov" >conditional move instruction</capability>
      <capability id="pat" >page attribute table</capability>
      <capability id="pse36" >36-bit page size extensions</capability>
      <capability id="clflush" />
      <capability id="dts" >debug trace and EMON store MSRs</capability>
      <capability id="acpi" >thermal control (ACPI)</capability>
      <capability id="mmx" >multimedia extensions (MMX)</capability>
      <capability id="fxsr" >fast floating point save/restore</capability>
      <capability id="sse" >streaming SIMD extensions (SSE)</capability>
      <capability id="sse2" >streaming SIMD extensions (SSE2)</capability>
      <capability id="ss" >self-snoop</capability>
      <capability id="ht" >HyperThreading</capability>
      <capability id="tm" >thermal interrupt and status</capability>
      <capability id="pbe" >pending break event</capability>
      <capability id="syscall" >fast system calls</capability>
      <capability id="nx" >no-execute bit (NX)</capability>
      <capability id="rdtscp" />
      <capability id="constant_tsc" />
      <capability id="arch_perfmon" />
      <capability id="pebs" />
      <capability id="bts" />
      <capability id="rep_good" />
      <capability id="nopl" />
      <capability id="xtopology" />
      <capability id="nonstop_tsc" />
      <capability id="aperfmperf" />
      <capability id="eagerfpu" />
      <capability id="pni" />
      <capability id="pclmulqdq" />
      <capability id="dtes64" />
      <capability id="monitor" />
      <capability id="ds_cpl" />
      <capability id="vmx" />
      <capability id="smx" />
      <capability id="est" />
      <capability id="tm2" />
      <capability id="ssse3" />
      <capability id="cx16" />
      <capability id="xtpr" />
      <capability id="pdcm" />
      <capability id="pcid" />
      <capability id="sse4_1" />
      <capability id="sse4_2" />
      <capability id="x2apic" />
      <capability id="popcnt" />
      <capability id="tsc_deadline_timer" />
      <capability id="aes" />
      <capability id="xsave" />
      <capability id="avx" />
      <capability id="f16c" />
      <capability id="rdrand" />
      <capability id="lahf_lm" />
      <capability id="ida" />
      <capability id="arat" />
      <capability id="epb" />
      <capability id="xsaveopt" />
      <capability id="pln" />
      <capability id="pts" />
      <capability id="dtherm" />
      <capability id="tpr_shadow" />
      <capability id="vnmi" />
      <capability id="flexpriority" />
      <capability id="ept" />
      <capability id="vpid" />
      <capability id="fsgsbase" />
      <capability id="smep" />
      <capability id="erms" />
      <capability id="cpufreq" >CPU Frequency scaling</capability>
     </capabilities>
      <node id="cache:0" claimed="true" class="memory" handle="DMI:0003">
       <description>L1 cache</description>
       <physid>3</physid>
       <slot>L1-Cache</slot>
       <size units="bytes">32768</size>
       <capacity units="bytes">32768</capacity>
       <capabilities>
        <capability id="internal" >Interne</capability>
        <capability id="write-through" >Write-trough</capability>
        <capability id="instruction" >Cache d'instructions</capability>
       </capabilities>
      </node>
      <node id="cache:1" claimed="true" class="memory" handle="DMI:0004">
       <description>L2 cache</description>
       <physid>4</physid>
       <slot>L2-Cache</slot>
       <size units="bytes">262144</size>
       <capacity units="bytes">262144</capacity>
       <capabilities>
        <capability id="internal" >Interne</capability>
        <capability id="write-through" >Write-trough</capability>
        <capability id="unified" >Cache unifi</capability>
       </capabilities>
      </node>
      <node id="cache:2" claimed="true" class="memory" handle="DMI:0005">
       <description>L3 cache</description>
       <physid>5</physid>
       <slot>L3-Cache</slot>
       <size units="bytes">3145728</size>
       <capacity units="bytes">3145728</capacity>
       <capabilities>
        <capability id="internal" >Interne</capability>
        <capability id="write-back" >Write-back</capability>
        <capability id="unified" >Cache unifi</capability>
       </capabilities>
      </node>
    </node>
    <node id="cache" claimed="true" class="memory" handle="DMI:0002">
     <description>L1 cache</description>
     <physid>2</physid>
     <slot>L1-Cache</slot>
     <size units="bytes">32768</size>
     <capacity units="bytes">32768</capacity>
     <capabilities>
      <capability id="internal" >Interne</capability>
      <capability id="write-through" >Write-trough</capability>
      <capability id="data" >Cache de donnes</capability>
     </capabilities>
    </node>
    <node id="memory" claimed="true" class="memory" handle="DMI:0007">
     <description>Mmoire Systme</description>
     <physid>7</physid>
     <slot>Carte mre</slot>
     <size units="bytes">8589934592</size>
      <node id="bank:0" claimed="true" class="memory" handle="DMI:0008">
       <description>SODIMM DDR3 Synchrone 1600 MHz (0,6 ns)</description>
       <product>M471B5273CH0-CK0</product>
       <vendor>Samsung</vendor>
       <physid>0</physid>
       <serial>1222BCCE</serial>
       <slot>ChannelA-DIMM0</slot>
       <size units="bytes">4294967296</size>
       <width units="bits">64</width>
       <clock units="Hz">1600000000</clock>
      </node>
      <node id="bank:1" claimed="true" class="memory" handle="DMI:0009">
       <description>SODIMM DDR3 Synchrone 1600 MHz (0,6 ns)</description>
       <product>M471B5273CH0-CK0</product>
       <vendor>Samsung</vendor>
       <physid>1</physid>
       <serial>1222BCA2</serial>
       <slot>ChannelB-DIMM0</slot>
       <size units="bytes">4294967296</size>
       <width units="bits">64</width>
       <clock units="Hz">1600000000</clock>
      </node>
    </node>
    <node id="firmware" claimed="true" class="memory" handle="">
     <description>BIOS</description>
     <vendor>LENOVO</vendor>
     <physid>e</physid>
     <version>G1ET73WW (2.09 )</version>
     <date>10/19/2012</date>
     <size units="bytes">131072</size>
     <capacity units="bytes">12517376</capacity>
     <capabilities>
      <capability id="pci" >bus PCI</capability>
      <capability id="pnp" >Plug-and-Play</capability>
      <capability id="upgrade" >BIOS EEPROM can be upgraded</capability>
      <capability id="shadowing" >BIOS shadowing</capability>
      <capability id="cdboot" >Dmarrage depuis un CD-ROM/DVD</capability>
      <capability id="bootselect" >Selectable boot path</capability>
      <capability id="edd" >Enhanced Disk Drive extensions</capability>
      <capability id="int13floppy720" >3.5&quot; 720KB floppy</capability>
      <capability id="int5printscreen" >Print Screen key</capability>
      <capability id="int9keyboard" >controleur de clavier i8042</capability>
      <capability id="int14serial" >INT14 serial line control</capability>
      <capability id="int17printer" >INT17 printer control</capability>
      <capability id="int10video" >INT10 CGA/Mono video</capability>
      <capability id="acpi" >ACPI</capability>
      <capability id="usb" >USB legacy emulation</capability>
      <capability id="biosbootspecification" >BIOS boot specification</capability>
      <capability id="uefi" >UEFI specification is supported</capability>
     </capabilities>
    </node>
    <node id="pci" claimed="true" class="bridge" handle="PCIBUS:0000:00">
     <description>Host bridge</description>
     <product>3rd Gen Core processor DRAM Controller</product>
     <vendor>Intel Corporation</vendor>
     <physid>100</physid>
     <businfo>pci@0000:00:00.0</businfo>
     <version>09</version>
     <width units="bits">32</width>
     <clock units="Hz">33000000</clock>
      <node id="display" claimed="true" class="display" handle="PCI:0000:00:02.0">
       <description>VGA compatible controller</description>
       <product>3rd Gen Core processor Graphics Controller</product>
       <vendor>Intel Corporation</vendor>
       <physid>2</physid>
       <businfo>pci@0000:00:02.0</businfo>
       <version>09</version>
       <width units="bits">64</width>
       <clock units="Hz">33000000</clock>
       <configuration>
        <setting id="driver" value="i915" />
        <setting id="latency" value="0" />
       </configuration>
       <capabilities>
        <capability id="msi" >Message Signalled Interrupts</capability>
        <capability id="pm" >Power Management</capability>
        <capability id="vga_controller" />
        <capability id="bus_master" >bus mastering</capability>
        <capability id="cap_list" >PCI capabilities listing</capability>
        <capability id="rom" >extension ROM</capability>
       </capabilities>
       <resources>
        <resource type="irq" value="43" />
        <resource type="memoire" value="f0000000-f03fffff" />
        <resource type="memoire" value="e0000000-efffffff" />
        <resource type="portE/S" value="5000(taille=64)" />
       </resources>
      </node>
      <node id="usb:0" claimed="true" class="bus" handle="PCI:0000:00:14.0">
       <description>USB controller</description>
       <product>7 Series/C210 Series Chipset Family USB xHCI Host Controller</product>
       <vendor>Intel Corporation</vendor>
       <physid>14</physid>
       <businfo>pci@0000:00:14.0</businfo>
       <version>04</version>
       <width units="bits">64</width>
       <clock units="Hz">33000000</clock>
       <configuration>
        <setting id="driver" value="xhci_hcd" />
        <setting id="latency" value="0" />
       </configuration>
       <capabilities>
        <capability id="pm" >Power Management</capability>
        <capability id="msi" >Message Signalled Interrupts</capability>
        <capability id="xhci" />
        <capability id="bus_master" >bus mastering</capability>
        <capability id="cap_list" >PCI capabilities listing</capability>
       </capabilities>
       <resources>
        <resource type="irq" value="44" />
        <resource type="memoire" value="f2520000-f252ffff" />
       </resources>
      </node>
      <node id="communication" claimed="true" class="communication" handle="PCI:0000:00:16.0">
       <description>Communication controller</description>
       <product>7 Series/C210 Series Chipset Family MEI Controller #1</product>
       <vendor>Intel Corporation</vendor>
       <physid>16</physid>
       <businfo>pci@0000:00:16.0</businfo>
       <version>04</version>
       <width units="bits">64</width>
       <clock units="Hz">33000000</clock>
       <configuration>
        <setting id="driver" value="mei" />
        <setting id="latency" value="0" />
       </configuration>
       <capabilities>
        <capability id="pm" >Power Management</capability>
        <capability id="msi" >Message Signalled Interrupts</capability>
        <capability id="bus_master" >bus mastering</capability>
        <capability id="cap_list" >PCI capabilities listing</capability>
       </capabilities>
       <resources>
        <resource type="irq" value="45" />
        <resource type="memoire" value="f2535000-f253500f" />
       </resources>
      </node>
      <node id="network" claimed="true" class="network" handle="PCI:0000:00:19.0">
       <description>Ethernet interface</description>
       <product>82579LM Gigabit Network Connection</product>
       <vendor>Intel Corporation</vendor>
       <physid>19</physid>
       <businfo>pci@0000:00:19.0</businfo>
       <logicalname>eth0</logicalname>
       <version>04</version>
       <serial>00:21:CC:D9:BF:26</serial>
       <capacity>1000000000</capacity>
       <width units="bits">32</width>
       <clock units="Hz">33000000</clock>
       <configuration>
        <setting id="autonegotiation" value="on" />
        <setting id="broadcast" value="yes" />
        <setting id="driver" value="e1000e" />
        <setting id="driverversion" value="2.1.4-k" />
        <setting id="firmware" value="0.13-3" />
        <setting id="latency" value="0" />
        <setting id="link" value="no" />
        <setting id="multicast" value="yes" />
        <setting id="port" value="twisted pair" />
       </configuration>
       <capabilities>
        <capability id="pm" >Power Management</capability>
        <capability id="msi" >Message Signalled Interrupts</capability>
        <capability id="bus_master" >bus mastering</capability>
        <capability id="cap_list" >PCI capabilities listing</capability>
        <capability id="ethernet" />
        <capability id="physical" >Interface physique</capability>
        <capability id="tp" >paire torsade</capability>
        <capability id="10bt" >10Mbit/s</capability>
        <capability id="10bt-fd" >10Mbit/s (full duplex)</capability>
        <capability id="100bt" >100Mbit/s</capability>
        <capability id="100bt-fd" >100Mbit/s (full duplex)</capability>
        <capability id="1000bt-fd" >1Gbit/s (full duplex)</capability>
        <capability id="autonegotiation" >Auto-ngotiation</capability>
       </capabilities>
       <resources>
        <resource type="irq" value="48" />
        <resource type="memoire" value="f2500000-f251ffff" />
        <resource type="memoire" value="f253b000-f253bfff" />
        <resource type="portE/S" value="5080(taille=32)" />
       </resources>
      </node>
      <node id="usb:1" claimed="true" class="bus" handle="PCI:0000:00:1a.0">
       <description>USB controller</description>
       <product>7 Series/C210 Series Chipset Family USB Enhanced Host Controller #2</product>
       <vendor>Intel Corporation</vendor>
       <physid>1a</physid>
       <businfo>pci@0000:00:1a.0</businfo>
       <version>04</version>
       <width units="bits">32</width>
       <clock units="Hz">33000000</clock>
       <configuration>
        <setting id="driver" value="ehci-pci" />
        <setting id="latency" value="0" />
       </configuration>
       <capabilities>
        <capability id="pm" >Power Management</capability>
        <capability id="debug" >Debug port</capability>
        <capability id="ehci" >Enhanced Host Controller Interface (USB2)</capability>
        <capability id="bus_master" >bus mastering</capability>
        <capability id="cap_list" >PCI capabilities listing</capability>
       </capabilities>
       <resources>
        <resource type="irq" value="16" />
        <resource type="memoire" value="f253a000-f253a3ff" />
       </resources>
      </node>
      <node id="multimedia" claimed="true" class="multimedia" handle="PCI:0000:00:1b.0">
       <description>Audio device</description>
       <product>7 Series/C210 Series Chipset Family High Definition Audio Controller</product>
       <vendor>Intel Corporation</vendor>
       <physid>1b</physid>
       <businfo>pci@0000:00:1b.0</businfo>
       <version>04</version>
       <width units="bits">64</width>
       <clock units="Hz">33000000</clock>
       <configuration>
        <setting id="driver" value="snd_hda_intel" />
        <setting id="latency" value="0" />
       </configuration>
       <capabilities>
        <capability id="pm" >Power Management</capability>
        <capability id="msi" >Message Signalled Interrupts</capability>
        <capability id="pciexpress" >PCI Express</capability>
        <capability id="bus_master" >bus mastering</capability>
        <capability id="cap_list" >PCI capabilities listing</capability>
       </capabilities>
       <resources>
        <resource type="irq" value="46" />
        <resource type="memoire" value="f2530000-f2533fff" />
       </resources>
      </node>
      <node id="pci:0" claimed="true" class="bridge" handle="PCIBUS:0000:02">
       <description>PCI bridge</description>
       <product>7 Series/C210 Series Chipset Family PCI Express Root Port 1</product>
       <vendor>Intel Corporation</vendor>
       <physid>1c</physid>
       <businfo>pci@0000:00:1c.0</businfo>
       <version>c4</version>
       <width units="bits">32</width>
       <clock units="Hz">33000000</clock>
       <configuration>
        <setting id="driver" value="pcieport" />
       </configuration>
       <capabilities>
        <capability id="pci" />
        <capability id="pciexpress" >PCI Express</capability>
        <capability id="msi" >Message Signalled Interrupts</capability>
        <capability id="pm" >Power Management</capability>
        <capability id="normal_decode" />
        <capability id="bus_master" >bus mastering</capability>
        <capability id="cap_list" >PCI capabilities listing</capability>
       </capabilities>
       <resources>
        <resource type="irq" value="16" />
        <resource type="portE/S" value="4000(taille=4096)" />
        <resource type="memoire" value="f1d00000-f24fffff" />
        <resource type="portE/S" value="f0400000(taille=8388608)" />
       </resources>
        <node id="generic" claimed="true" class="generic" handle="PCI:0000:02:00.0">
         <description>System peripheral</description>
         <product>MMC/SD Host Controller</product>
         <vendor>Ricoh Co Ltd</vendor>
         <physid>0</physid>
         <businfo>pci@0000:02:00.0</businfo>
         <version>07</version>
         <width units="bits">32</width>
         <clock units="Hz">33000000</clock>
         <configuration>
          <setting id="driver" value="sdhci-pci" />
          <setting id="latency" value="0" />
         </configuration>
         <capabilities>
          <capability id="msi" >Message Signalled Interrupts</capability>
          <capability id="pm" >Power Management</capability>
          <capability id="pciexpress" >PCI Express</capability>
          <capability id="bus_master" >bus mastering</capability>
          <capability id="cap_list" >PCI capabilities listing</capability>
         </capabilities>
         <resources>
          <resource type="irq" value="16" />
          <resource type="memoire" value="f1d00000-f1d000ff" />
         </resources>
        </node>
      </node>
      <node id="pci:1" claimed="true" class="bridge" handle="PCIBUS:0000:03">
       <description>PCI bridge</description>
       <product>7 Series/C210 Series Chipset Family PCI Express Root Port 2</product>
       <vendor>Intel Corporation</vendor>
       <physid>1c.1</physid>
       <businfo>pci@0000:00:1c.1</businfo>
       <version>c4</version>
       <width units="bits">32</width>
       <clock units="Hz">33000000</clock>
       <configuration>
        <setting id="driver" value="pcieport" />
       </configuration>
       <capabilities>
        <capability id="pci" />
        <capability id="pciexpress" >PCI Express</capability>
        <capability id="msi" >Message Signalled Interrupts</capability>
        <capability id="pm" >Power Management</capability>
        <capability id="normal_decode" />
        <capability id="bus_master" >bus mastering</capability>
        <capability id="cap_list" >PCI capabilities listing</capability>
       </capabilities>
       <resources>
        <resource type="irq" value="17" />
        <resource type="memoire" value="f1c00000-f1cfffff" />
       </resources>
        <node id="network" claimed="true" class="network" handle="PCI:0000:03:00.0">
         <description>Interface rseau sans fil</description>
         <product>Centrino Advanced-N 6205 [Taylor Peak]</product>
         <vendor>Intel Corporation</vendor>
         <physid>0</physid>
         <businfo>pci@0000:03:00.0</businfo>
         <logicalname>wlan0</logicalname>
         <version>34</version>
         <serial>84:3a:4b:33:62:82</serial>
         <width units="bits">64</width>
         <clock units="Hz">33000000</clock>
         <configuration>
          <setting id="broadcast" value="yes" />
          <setting id="driver" value="iwlwifi" />
          <setting id="driverversion" value="3.8.13.4-desktop-1.mga3" />
          <setting id="firmware" value="18.168.6.1" />
          <setting id="ip" value="192.168.1.185" />
          <setting id="latency" value="0" />
          <setting id="link" value="yes" />
          <setting id="multicast" value="yes" />
          <setting id="wireless" value="IEEE 802.11abgn" />
         </configuration>
         <capabilities>
          <capability id="pm" >Power Management</capability>
          <capability id="msi" >Message Signalled Interrupts</capability>
          <capability id="pciexpress" >PCI Express</capability>
          <capability id="bus_master" >bus mastering</capability>
          <capability id="cap_list" >PCI capabilities listing</capability>
          <capability id="ethernet" />
          <capability id="physical" >Interface physique</capability>
          <capability id="wireless" >Rseau sans fil</capability>
         </capabilities>
         <resources>
          <resource type="irq" value="47" />
          <resource type="memoire" value="f1c00000-f1c01fff" />
         </resources>
        </node>
      </node>
      <node id="pci:2" claimed="true" class="bridge" handle="PCIBUS:0000:04">
       <description>PCI bridge</description>
       <product>7 Series/C210 Series Chipset Family PCI Express Root Port 3</product>
       <vendor>Intel Corporation</vendor>
       <physid>1c.2</physid>
       <businfo>pci@0000:00:1c.2</businfo>
       <version>c4</version>
       <width units="bits">32</width>
       <clock units="Hz">33000000</clock>
       <configuration>
        <setting id="driver" value="pcieport" />
       </configuration>
       <capabilities>
        <capability id="pci" />
        <capability id="pciexpress" >PCI Express</capability>
        <capability id="msi" >Message Signalled Interrupts</capability>
        <capability id="pm" >Power Management</capability>
        <capability id="normal_decode" />
        <capability id="bus_master" >bus mastering</capability>
        <capability id="cap_list" >PCI capabilities listing</capability>
       </capabilities>
       <resources>
        <resource type="irq" value="18" />
        <resource type="portE/S" value="3000(taille=4096)" />
        <resource type="memoire" value="f1400000-f1bfffff" />
        <resource type="portE/S" value="f0c00000(taille=8388608)" />
       </resources>
      </node>
      <node id="usb:2" claimed="true" class="bus" handle="PCI:0000:00:1d.0">
       <description>USB controller</description>
       <product>7 Series/C210 Series Chipset Family USB Enhanced Host Controller #1</product>
       <vendor>Intel Corporation</vendor>
       <physid>1d</physid>
       <businfo>pci@0000:00:1d.0</businfo>
       <version>04</version>
       <width units="bits">32</width>
       <clock units="Hz">33000000</clock>
       <configuration>
        <setting id="driver" value="ehci-pci" />
        <setting id="latency" value="0" />
       </configuration>
       <capabilities>
        <capability id="pm" >Power Management</capability>
        <capability id="debug" >Debug port</capability>
        <capability id="ehci" >Enhanced Host Controller Interface (USB2)</capability>
        <capability id="bus_master" >bus mastering</capability>
        <capability id="cap_list" >PCI capabilities listing</capability>
       </capabilities>
       <resources>
        <resource type="irq" value="23" />
        <resource type="memoire" value="f2539000-f25393ff" />
       </resources>
      </node>
      <node id="isa" claimed="true" class="bridge" handle="PCI:0000:00:1f.0">
       <description>ISA bridge</description>
       <product>QM77 Express Chipset LPC Controller</product>
       <vendor>Intel Corporation</vendor>
       <physid>1f</physid>
       <businfo>pci@0000:00:1f.0</businfo>
       <version>04</version>
       <width units="bits">32</width>
       <clock units="Hz">33000000</clock>
       <configuration>
        <setting id="driver" value="lpc_ich" />
        <setting id="latency" value="0" />
       </configuration>
       <capabilities>
        <capability id="isa" />
        <capability id="bus_master" >bus mastering</capability>
        <capability id="cap_list" >PCI capabilities listing</capability>
       </capabilities>
       <resources>
        <resource type="irq" value="0" />
       </resources>
      </node>
      <node id="storage" claimed="true" class="storage" handle="PCI:0000:00:1f.2">
       <description>SATA controller</description>
       <product>7 Series Chipset Family 6-port SATA Controller [AHCI mode]</product>
       <vendor>Intel Corporation</vendor>
       <physid>1f.2</physid>
       <businfo>pci@0000:00:1f.2</businfo>
       <version>04</version>
       <width units="bits">32</width>
       <clock units="Hz">66000000</clock>
       <configuration>
        <setting id="driver" value="ahci" />
        <setting id="latency" value="0" />
       </configuration>
       <capabilities>
        <capability id="storage" />
        <capability id="msi" >Message Signalled Interrupts</capability>
        <capability id="pm" >Power Management</capability>
        <capability id="ahci_1.0" />
        <capability id="bus_master" >bus mastering</capability>
        <capability id="cap_list" >PCI capabilities listing</capability>
       </capabilities>
       <resources>
        <resource type="irq" value="42" />
        <resource type="portE/S" value="50a8(taille=8)" />
        <resource type="portE/S" value="50b4(taille=4)" />
        <resource type="portE/S" value="50a0(taille=8)" />
        <resource type="portE/S" value="50b0(taille=4)" />
        <resource type="portE/S" value="5060(taille=32)" />
        <resource type="memoire" value="f2538000-f25387ff" />
       </resources>
      </node>
      <node id="serial" claimed="true" class="bus" handle="PCI:0000:00:1f.3">
       <description>SMBus</description>
       <product>7 Series/C210 Series Chipset Family SMBus Controller</product>
       <vendor>Intel Corporation</vendor>
       <physid>1f.3</physid>
       <businfo>pci@0000:00:1f.3</businfo>
       <version>04</version>
       <width units="bits">64</width>
       <clock units="Hz">33000000</clock>
       <configuration>
        <setting id="driver" value="i801_smbus" />
        <setting id="latency" value="0" />
       </configuration>
       <resources>
        <resource type="irq" value="18" />
        <resource type="memoire" value="f2534000-f25340ff" />
        <resource type="portE/S" value="efa0(taille=32)" />
       </resources>
      </node>
    </node>
    <node id="scsi:0" claimed="true" class="storage" handle="">
     <physid>0</physid>
     <logicalname>scsi0</logicalname>
     <capabilities>
      <capability id="emulated" >Emulated device</capability>
     </capabilities>
      <node id="disk" claimed="true" class="disk" handle="SCSI:00:00:00:00">
       <description>ATA Disk</description>
       <product>TOSHIBA THNSNC12</product>
       <vendor>Toshiba</vendor>
       <physid>0.0.0</physid>
       <businfo>scsi@0:0.0.0</businfo>
       <logicalname>/dev/sda</logicalname>
       <dev>8:0</dev>
       <version>CJLA</version>
       <serial>81PS10ECTMAZ</serial>
       <size units="bytes">128035676160</size>
       <configuration>
        <setting id="ansiversion" value="5" />
        <setting id="sectorsize" value="512" />
        <setting id="signature" value="0001bcc1" />
       </configuration>
       <capabilities>
        <capability id="partitioned" >Partitioned disk</capability>
        <capability id="partitioned:dos" >MS-DOS partition table</capability>
       </capabilities>
        <node id="volume:0" claimed="true" class="volume" handle="">
         <description>Linux swap volume</description>
         <physid>1</physid>
         <businfo>scsi@0:0.0.0,1</businfo>
         <logicalname>/dev/sda1</logicalname>
         <dev>8:1</dev>
         <version>1</version>
         <serial>d8b3f967-8950-4b3b-8c6a-764d232429b3</serial>
         <size units="bytes">8380510208</size>
         <capacity>8380511744</capacity>
         <configuration>
          <setting id="filesystem" value="swap" />
          <setting id="pagesize" value="4096" />
         </configuration>
         <capabilities>
          <capability id="primary" >Primary partition</capability>
          <capability id="bootable" >Bootable partition (active)</capability>
          <capability id="nofs" >No filesystem</capability>
          <capability id="swap" >Linux swap</capability>
          <capability id="initialized" >initialized volume</capability>
         </capabilities>
        </node>
        <node id="volume:1" claimed="true" class="volume" handle="">
         <description>Extended partition</description>
         <physid>2</physid>
         <businfo>scsi@0:0.0.0,2</businfo>
         <logicalname>/dev/sda2</logicalname>
         <dev>8:2</dev>
         <size units="bytes">119651374080</size>
         <capacity>119651374080</capacity>
         <capabilities>
          <capability id="primary" >Primary partition</capability>
          <capability id="extended" >Extended partition</capability>
          <capability id="partitioned" >Partitioned disk</capability>
          <capability id="partitioned:extended" >Extended partition</capability>
         </capabilities>
          <node id="logicalvolume:0" claimed="true" class="volume" handle="">
           <description>Linux filesystem partition</description>
           <physid>5</physid>
           <logicalname>/dev/sda5</logicalname>
           <logicalname>/</logicalname>
           <dev>8:5</dev>
           <capacity>31336512000</capacity>
           <configuration>
            <setting id="mount.fstype" value="ext4" />
            <setting id="mount.options" value="rw,noatime,data=ordered" />
            <setting id="state" value="mounted" />
           </configuration>
          </node>
          <node id="logicalvolume:1" claimed="true" class="volume" handle="">
           <description>Linux filesystem partition</description>
           <physid>6</physid>
           <logicalname>/dev/sda6</logicalname>
           <logicalname>/home</logicalname>
           <dev>8:6</dev>
           <capacity>88313601024</capacity>
           <configuration>
            <setting id="mount.fstype" value="ext4" />
            <setting id="mount.options" value="rw,noatime,data=ordered" />
            <setting id="state" value="mounted" />
           </configuration>
          </node>
        </node>
      </node>
    </node>
    <node id="scsi:1" claimed="true" class="storage" handle="">
     <physid>3</physid>
     <logicalname>scsi1</logicalname>
     <capabilities>
      <capability id="emulated" >Emulated device</capability>
     </capabilities>
      <node id="cdrom" claimed="true" class="disk" handle="SCSI:01:00:00:00">
       <description>DVD-RAM writer</description>
       <product>DVDRAM GT50N</product>
       <vendor>HL-DT-ST</vendor>
       <physid>0.0.0</physid>
       <businfo>scsi@1:0.0.0</businfo>
       <logicalname>/dev/sr0</logicalname>
       <dev>11:0</dev>
       <version>LT20</version>
       <configuration>
        <setting id="ansiversion" value="5" />
        <setting id="status" value="nodisc" />
       </configuration>
       <capabilities>
        <capability id="removable" >support is removable</capability>
        <capability id="audio" >Audio CD playback</capability>
        <capability id="cd-r" >CD-R burning</capability>
        <capability id="cd-rw" >CD-RW burning</capability>
        <capability id="dvd" >DVD playback</capability>
        <capability id="dvd-r" >DVD-R burning</capability>
        <capability id="dvd-ram" >DVD-RAM burning</capability>
       </capabilities>
      </node>
    </node>
  </node>
  <node id="battery" claimed="true" class="power" handle="DMI:002E">
   <product>45N1011</product>
   <vendor>LGC</vendor>
   <physid>1</physid>
   <slot>Rear</slot>
   <capacity units="mWh">93600</capacity>
   <configuration>
    <setting id="voltage" value="11,1V" />
   </configuration>
  </node>
  <node id="network" disabled="true" claimed="true" class="network" handle="">
   <description>Ethernet interface</description>
   <physid>2</physid>
   <logicalname>wwan0</logicalname>
   <serial>02:15:e0:ec:01:00</serial>
   <configuration>
    <setting id="broadcast" value="yes" />
    <setting id="driver" value="cdc_ncm" />
    <setting id="driverversion" value="14-Mar-2012" />
    <setting id="firmware" value="Mobile Broadband Network Device" />
    <setting id="link" value="no" />
    <setting id="multicast" value="yes" />
   </configuration>
   <capabilities>
    <capability id="ethernet" />
    <capability id="physical" >Interface physique</capability>
   </capabilities>
  </node>
</node>
</list>
'''

XML3 = '''<?xml version="1.0" standalone="yes" ?>
<!-- generated by lshw-B.02.10 -->
<!-- GCC 4.1.1 20070105 (Red Hat 4.1.1-52) -->
<node id="alkan" claimed="true" class="system" handle="DMI:0001">
 <description>System</description>
 <product>MCP55</product>
 <vendor>Tyan Computer Corporation</vendor>
 <version>REFERENCE</version>
 <serial>0123456789</serial>
 <width units="bits">32</width>
 <configuration>
  <setting id="boot" value="oem-specific" />
  <setting id="chassis" value="server" />
 </configuration>
  <node id="core" claimed="true" class="bus" handle="DMI:0002">
   <description>Motherboard</description>
   <product>S2915</product>
   <vendor>Tyan Computer Corporation</vendor>
   <physid>0</physid>
   <version>REFERENCE</version>
   <serial>Empty</serial>
    <node id="firmware" claimed="true" class="memory" handle="">
     <description>BIOS</description>
     <vendor>Phoenix Technologies Ltd.</vendor>
     <physid>1</physid>
     <version>v3.00.2915 (10/10/2008)</version>
     <size units="bytes">106992</size>
     <capacity units="bytes">983040</capacity>
     <capabilities>
      <capability id="pci" >PCI bus</capability>
      <capability id="pnp" >Plug-and-Play</capability>
      <capability id="upgrade" >BIOS EEPROM can be upgraded</capability>
      <capability id="shadowing" >BIOS shadowing</capability>
      <capability id="escd" >ESCD</capability>
      <capability id="cdboot" >Booting from CD-ROM/DVD</capability>
      <capability id="bootselect" >Selectable boot path</capability>
      <capability id="edd" >Enhanced Disk Drive extensions</capability>
      <capability id="int13floppy360" >5.25" 360KB floppy</capability>
      <capability id="int13floppy1200" >5.25" 1.2MB floppy</capability>
      <capability id="int13floppy720" >3.5" 720KB floppy</capability>
      <capability id="int13floppy2880" >3.5" 2.88MB floppy</capability>
      <capability id="int5printscreen" >Print Screen key</capability>
      <capability id="int9keyboard" >i8042 keyboard controller</capability>
      <capability id="int14serial" >INT14 serial line control</capability>
      <capability id="int17printer" >INT17 printer control</capability>
      <capability id="int10video" >INT10 CGA/Mono video</capability>
      <capability id="acpi" >ACPI</capability>
      <capability id="usb" >USB legacy emulation</capability>
     </capabilities>
    </node>
    <node id="cpu:0" claimed="true" class="processor" handle="DMI:0004">
     <description>CPU</description>
     <product>Dual-Core AMD Opteron(tm) Processor 8218</product>
     <vendor>Advanced Micro Devices [AMD]</vendor>
     <physid>3</physid>
     <businfo>cpu@0</businfo>
     <version>AMD</version>
     <slot>CPU0-Socket F</slot>
     <size units="Hz">1000000000</size>
     <capacity units="Hz">3000000000</capacity>
     <width units="bits">64</width>
     <clock units="Hz">200000000</clock>
     <capabilities>
      <capability id="fpu" >mathematical co-processor</capability>
      <capability id="fpu_exception" >FPU exceptions reporting</capability>
      <capability id="wp" />
      <capability id="vme" >virtual mode extensions</capability>
      <capability id="de" >debugging extensions</capability>
      <capability id="pse" >page size extensions</capability>
      <capability id="tsc" >time stamp counter</capability>
      <capability id="msr" >model-specific registers</capability>
      <capability id="pae" >4GB+ memory addressing (Physical Address Extension)</capability>
      <capability id="mce" >machine check exceptions</capability>
      <capability id="cx8" >compare and exchange 8-byte</capability>
      <capability id="apic" >on-chip advanced programmable interrupt controller (APIC)</capability>
      <capability id="sep" >fast system calls</capability>
      <capability id="mtrr" >memory type range registers</capability>
      <capability id="pge" >page global enable</capability>
      <capability id="mca" >machine check architecture</capability>
      <capability id="cmov" >conditional move instruction</capability>
      <capability id="pat" >page attribute table</capability>
      <capability id="pse36" >36-bit page size extensions</capability>
      <capability id="clflush" />
      <capability id="mmx" >multimedia extensions (MMX)</capability>
      <capability id="fxsr" >fast floating point save/restore</capability>
      <capability id="sse" >streaming SIMD extensions (SSE)</capability>
      <capability id="sse2" >streaming SIMD extensions (SSE2)</capability>
      <capability id="ht" >HyperThreading</capability>
      <capability id="syscall" >fast system calls</capability>
      <capability id="nx" >no-execute bit (NX)</capability>
      <capability id="mmxext" >multimedia extensions (MMXExt)</capability>
      <capability id="fxsr_opt" />
      <capability id="rdtscp" />
      <capability id="x86-64" >64bits extensions (x86-64)</capability>
      <capability id="3dnowext" >multimedia extensions (3DNow!Ext)</capability>
      <capability id="3dnow" >multimedia extensions (3DNow!)</capability>
      <capability id="rep_good" />
      <capability id="nopl" />
      <capability id="extd_apicid" />
      <capability id="pni" />
      <capability id="cx16" />
      <capability id="lahf_lm" />
      <capability id="cmp_legacy" />
      <capability id="svm" />
      <capability id="extapic" />
      <capability id="cr8_legacy" />
      <capability id="cpufreq" >CPU Frequency scaling</capability>
     </capabilities>
      <node id="cache:0" claimed="true" class="memory" handle="DMI:0006">
       <description>L1 cache</description>
       <physid>6</physid>
       <slot>H0 L1 Cache</slot>
       <size units="bytes">65536</size>
       <capacity units="bytes">65536</capacity>
       <capabilities>
        <capability id="asynchronous" >Asynchronous</capability>
        <capability id="internal" >Internal</capability>
        <capability id="write-back" >Write-back</capability>
       </capabilities>
      </node>
      <node id="cache:1" claimed="true" class="memory" handle="DMI:0007">
       <description>L2 cache</description>
       <physid>7</physid>
       <slot>H0 L2 Cache</slot>
       <size units="bytes">1048576</size>
       <capacity units="bytes">1048576</capacity>
       <capabilities>
        <capability id="synchronous" >Synchronous</capability>
        <capability id="internal" >Internal</capability>
        <capability id="write-through" >Write-trough</capability>
        <capability id="unified" >Unified cache</capability>
       </capabilities>
      </node>
    </node>
    <node id="cpu:1" claimed="true" class="processor" handle="DMI:0005">
     <description>CPU</description>
     <product>Dual-Core AMD Opteron(tm) Processor 8218</product>
     <vendor>Advanced Micro Devices [AMD]</vendor>
     <physid>4</physid>
     <businfo>cpu@1</businfo>
     <version>AMD</version>
     <slot>CPU1-Socket F</slot>
     <size units="Hz">1000000000</size>
     <capacity units="Hz">3000000000</capacity>
     <width units="bits">64</width>
     <clock units="Hz">200000000</clock>
     <capabilities>
      <capability id="fpu" >mathematical co-processor</capability>
      <capability id="fpu_exception" >FPU exceptions reporting</capability>
      <capability id="wp" />
      <capability id="vme" >virtual mode extensions</capability>
      <capability id="de" >debugging extensions</capability>
      <capability id="pse" >page size extensions</capability>
      <capability id="tsc" >time stamp counter</capability>
      <capability id="msr" >model-specific registers</capability>
      <capability id="pae" >4GB+ memory addressing (Physical Address Extension)</capability>
      <capability id="mce" >machine check exceptions</capability>
      <capability id="cx8" >compare and exchange 8-byte</capability>
      <capability id="apic" >on-chip advanced programmable interrupt controller (APIC)</capability>
      <capability id="sep" >fast system calls</capability>
      <capability id="mtrr" >memory type range registers</capability>
      <capability id="pge" >page global enable</capability>
      <capability id="mca" >machine check architecture</capability>
      <capability id="cmov" >conditional move instruction</capability>
      <capability id="pat" >page attribute table</capability>
      <capability id="pse36" >36-bit page size extensions</capability>
      <capability id="clflush" />
      <capability id="mmx" >multimedia extensions (MMX)</capability>
      <capability id="fxsr" >fast floating point save/restore</capability>
      <capability id="sse" >streaming SIMD extensions (SSE)</capability>
      <capability id="sse2" >streaming SIMD extensions (SSE2)</capability>
      <capability id="ht" >HyperThreading</capability>
      <capability id="syscall" >fast system calls</capability>
      <capability id="nx" >no-execute bit (NX)</capability>
      <capability id="mmxext" >multimedia extensions (MMXExt)</capability>
      <capability id="fxsr_opt" />
      <capability id="rdtscp" />
      <capability id="x86-64" >64bits extensions (x86-64)</capability>
      <capability id="3dnowext" >multimedia extensions (3DNow!Ext)</capability>
      <capability id="3dnow" >multimedia extensions (3DNow!)</capability>
      <capability id="rep_good" />
      <capability id="nopl" />
      <capability id="extd_apicid" />
      <capability id="pni" />
      <capability id="cx16" />
      <capability id="lahf_lm" />
      <capability id="cmp_legacy" />
      <capability id="svm" />
      <capability id="extapic" />
      <capability id="cr8_legacy" />
      <capability id="cpufreq" >CPU Frequency scaling</capability>
     </capabilities>
      <node id="cache:0" claimed="true" class="memory" handle="DMI:0008">
       <description>L1 cache</description>
       <physid>8</physid>
       <slot>H1 L1 Cache</slot>
       <size units="bytes">65536</size>
       <capacity units="bytes">65536</capacity>
       <capabilities>
        <capability id="asynchronous" >Asynchronous</capability>
        <capability id="internal" >Internal</capability>
        <capability id="write-back" >Write-back</capability>
       </capabilities>
      </node>
      <node id="cache:1" claimed="true" class="memory" handle="DMI:0009">
       <description>L2 cache</description>
       <physid>9</physid>
       <slot>H1 L2 Cache</slot>
       <size units="bytes">1048576</size>
       <capacity units="bytes">1048576</capacity>
       <capabilities>
        <capability id="synchronous" >Synchronous</capability>
        <capability id="internal" >Internal</capability>
        <capability id="write-through" >Write-trough</capability>
        <capability id="unified" >Unified cache</capability>
       </capabilities>
      </node>
    </node>
    <node id="memory:0" claimed="true" class="memory" handle="DMI:000F">
     <description>System Memory</description>
     <physid>5</physid>
     <slot>System board or motherboard</slot>
     <size units="bytes">4294967296</size>
      <node id="bank:0" claimed="true" class="memory" handle="DMI:0010">
       <description>DIMM Synchronous [empty]</description>
       <physid>0</physid>
       <slot>C0_DIMM0</slot>
      </node>
      <node id="bank:1" claimed="true" class="memory" handle="DMI:0011">
       <description>DIMM Synchronous [empty]</description>
       <physid>1</physid>
       <slot>C0_DIMM1</slot>
      </node>
      <node id="bank:2" claimed="true" class="memory" handle="DMI:0012">
       <description>DIMM Synchronous</description>
       <physid>2</physid>
       <slot>C0_DIMM2</slot>
       <size units="bytes">1073741824</size>
       <width units="bits">64</width>
      </node>
      <node id="bank:3" claimed="true" class="memory" handle="DMI:0013">
       <description>DIMM Synchronous</description>
       <physid>3</physid>
       <slot>C0_DIMM3</slot>
       <size units="bytes">1073741824</size>
       <width units="bits">64</width>
      </node>
      <node id="bank:4" claimed="true" class="memory" handle="DMI:0014">
       <description>DIMM Synchronous [empty]</description>
       <physid>4</physid>
       <slot>C0_DIMM0</slot>
      </node>
      <node id="bank:5" claimed="true" class="memory" handle="DMI:0015">
       <description>DIMM Synchronous [empty]</description>
       <physid>5</physid>
       <slot>C1_DIMM1</slot>
      </node>
      <node id="bank:6" claimed="true" class="memory" handle="DMI:0016">
       <description>DIMM Synchronous</description>
       <physid>6</physid>
       <slot>C1_DIMM2</slot>
       <size units="bytes">1073741824</size>
       <width units="bits">64</width>
      </node>
      <node id="bank:7" claimed="true" class="memory" handle="DMI:0017">
       <description>DIMM Synchronous</description>
       <physid>7</physid>
       <slot>C1_DIMM3</slot>
       <size units="bytes">1073741824</size>
       <width units="bits">64</width>
      </node>
    </node>
    <node id="memory:1" class="memory" handle="PCI:0000:00:00.0">
     <description>RAM memory</description>
     <product>MCP55 Memory Controller</product>
     <vendor>NVIDIA Corporation</vendor>
     <physid>7</physid>
     <businfo>pci@0000:00:00.0</businfo>
     <version>a2</version>
     <width units="bits">32</width>
     <clock units="Hz">66000000</clock>
     <configuration>
      <setting id="latency" value="0" />
     </configuration>
     <capabilities>
      <capability id="ht" >HyperTransport</capability>
      <capability id="bus_master" >bus mastering</capability>
      <capability id="cap_list" >PCI capabilities listing</capability>
     </capabilities>
    </node>
    <node id="isa" claimed="true" class="bridge" handle="PCI:0000:00:01.0">
     <description>ISA bridge</description>
     <product>MCP55 LPC Bridge</product>
     <vendor>NVIDIA Corporation</vendor>
     <physid>100</physid>
     <businfo>pci@0000:00:01.0</businfo>
     <version>a3</version>
     <width units="bits">32</width>
     <clock units="Hz">66000000</clock>
     <configuration>
      <setting id="latency" value="0" />
     </configuration>
     <capabilities>
      <capability id="isa" />
      <capability id="bus_master" >bus mastering</capability>
     </capabilities>
    </node>
    <node id="serial:0" claimed="true" class="bus" handle="PCI:0000:00:01.1">
     <description>SMBus</description>
     <product>MCP55 SMBus</product>
     <vendor>NVIDIA Corporation</vendor>
     <physid>a</physid>
     <businfo>pci@0000:00:01.1</businfo>
     <version>a3</version>
     <width units="bits">32</width>
     <clock units="Hz">66000000</clock>
     <configuration>
      <setting id="driver" value="nForce2_smbus" />
      <setting id="latency" value="0" />
      <setting id="module" value="i2c_nforce2" />
     </configuration>
     <capabilities>
      <capability id="pm" >Power Management</capability>
      <capability id="cap_list" >PCI capabilities listing</capability>
     </capabilities>
    </node>
    <node id="usb:0" claimed="true" class="bus" handle="PCI:0000:00:02.0">
     <description>USB controller</description>
     <product>MCP55 USB Controller</product>
     <vendor>NVIDIA Corporation</vendor>
     <physid>2</physid>
     <businfo>pci@0000:00:02.0</businfo>
     <version>a1</version>
     <width units="bits">32</width>
     <clock units="Hz">66000000</clock>
     <configuration>
      <setting id="driver" value="ohci_hcd" />
      <setting id="latency" value="0" />
      <setting id="maxlatency" value="1" />
      <setting id="mingnt" value="3" />
     </configuration>
     <capabilities>
      <capability id="pm" >Power Management</capability>
      <capability id="ohci" >Open Host Controller Interface</capability>
      <capability id="bus_master" >bus mastering</capability>
      <capability id="cap_list" >PCI capabilities listing</capability>
     </capabilities>
    </node>
    <node id="usb:1" claimed="true" class="bus" handle="PCI:0000:00:02.1">
     <description>USB controller</description>
     <product>MCP55 USB Controller</product>
     <vendor>NVIDIA Corporation</vendor>
     <physid>2.1</physid>
     <businfo>pci@0000:00:02.1</businfo>
     <version>a2</version>
     <width units="bits">32</width>
     <clock units="Hz">66000000</clock>
     <configuration>
      <setting id="driver" value="ehci_hcd" />
      <setting id="latency" value="0" />
      <setting id="maxlatency" value="1" />
      <setting id="mingnt" value="3" />
      <setting id="module" value="ehci_hcd" />
     </configuration>
     <capabilities>
      <capability id="debug" >Debug port</capability>
      <capability id="pm" >Power Management</capability>
      <capability id="ehci" >Enhanced Host Controller Interface (USB2)</capability>
      <capability id="bus_master" >bus mastering</capability>
      <capability id="cap_list" >PCI capabilities listing</capability>
     </capabilities>
    </node>
    <node id="ide:0" claimed="true" class="storage" handle="PCI:0000:00:04.0">
     <description>IDE interface</description>
     <product>MCP55 IDE</product>
     <vendor>NVIDIA Corporation</vendor>
     <physid>b</physid>
     <businfo>pci@0000:00:04.0</businfo>
     <version>a1</version>
     <width units="bits">32</width>
     <clock units="Hz">66000000</clock>
     <configuration>
      <setting id="driver" value="pata_amd" />
      <setting id="latency" value="0" />
      <setting id="maxlatency" value="1" />
      <setting id="mingnt" value="3" />
      <setting id="module" value="pata_amd" />
     </configuration>
     <capabilities>
      <capability id="ide" />
      <capability id="pm" >Power Management</capability>
      <capability id="bus_master" >bus mastering</capability>
      <capability id="cap_list" >PCI capabilities listing</capability>
     </capabilities>
    </node>
    <node id="ide:1" claimed="true" class="storage" handle="PCI:0000:00:05.0">
     <description>IDE interface</description>
     <product>MCP55 SATA Controller</product>
     <vendor>NVIDIA Corporation</vendor>
     <physid>c</physid>
     <businfo>pci@0000:00:05.0</businfo>
     <version>a3</version>
     <width units="bits">32</width>
     <clock units="Hz">66000000</clock>
     <configuration>
      <setting id="driver" value="sata_nv" />
      <setting id="latency" value="0" />
      <setting id="maxlatency" value="1" />
      <setting id="mingnt" value="3" />
      <setting id="module" value="sata_nv" />
     </configuration>
     <capabilities>
      <capability id="ide" />
      <capability id="pm" >Power Management</capability>
      <capability id="msi" >Message Signalled Interrupts</capability>
      <capability id="ht" >HyperTransport</capability>
      <capability id="bus_master" >bus mastering</capability>
      <capability id="cap_list" >PCI capabilities listing</capability>
     </capabilities>
    </node>
    <node id="ide:2" claimed="true" class="storage" handle="PCI:0000:00:05.1">
     <description>IDE interface</description>
     <product>MCP55 SATA Controller</product>
     <vendor>NVIDIA Corporation</vendor>
     <physid>5.1</physid>
     <businfo>pci@0000:00:05.1</businfo>
     <version>a3</version>
     <width units="bits">32</width>
     <clock units="Hz">66000000</clock>
     <configuration>
      <setting id="driver" value="sata_nv" />
      <setting id="latency" value="0" />
      <setting id="maxlatency" value="1" />
      <setting id="mingnt" value="3" />
      <setting id="module" value="sata_nv" />
     </configuration>
     <capabilities>
      <capability id="ide" />
      <capability id="pm" >Power Management</capability>
      <capability id="msi" >Message Signalled Interrupts</capability>
      <capability id="ht" >HyperTransport</capability>
      <capability id="bus_master" >bus mastering</capability>
      <capability id="cap_list" >PCI capabilities listing</capability>
     </capabilities>
    </node>
    <node id="ide:3" claimed="true" class="storage" handle="PCI:0000:00:05.2">
     <description>IDE interface</description>
     <product>MCP55 SATA Controller</product>
     <vendor>NVIDIA Corporation</vendor>
     <physid>5.2</physid>
     <businfo>pci@0000:00:05.2</businfo>
     <version>a3</version>
     <width units="bits">32</width>
     <clock units="Hz">66000000</clock>
     <configuration>
      <setting id="driver" value="sata_nv" />
      <setting id="latency" value="0" />
      <setting id="maxlatency" value="1" />
      <setting id="mingnt" value="3" />
      <setting id="module" value="sata_nv" />
     </configuration>
     <capabilities>
      <capability id="ide" />
      <capability id="pm" >Power Management</capability>
      <capability id="msi" >Message Signalled Interrupts</capability>
      <capability id="ht" >HyperTransport</capability>
      <capability id="bus_master" >bus mastering</capability>
      <capability id="cap_list" >PCI capabilities listing</capability>
     </capabilities>
    </node>
    <node id="pci:0" claimed="true" class="bridge" handle="PCIBUS:0000:01">
     <description>PCI bridge</description>
     <product>MCP55 PCI bridge</product>
     <vendor>NVIDIA Corporation</vendor>
     <physid>6</physid>
     <businfo>pci@0000:00:06.0</businfo>
     <version>a2</version>
     <width units="bits">32</width>
     <clock units="Hz">66000000</clock>
     <capabilities>
      <capability id="pci" />
      <capability id="ht" >HyperTransport</capability>
      <capability id="subtractive_decode" />
      <capability id="bus_master" >bus mastering</capability>
      <capability id="cap_list" >PCI capabilities listing</capability>
     </capabilities>
      <node id="firewire" claimed="true" class="bus" handle="PCI:0000:01:05.0">
       <description>FireWire (IEEE 1394)</description>
       <product>TSB43AB22A IEEE-1394a-2000 Controller (PHY/Link) [iOHCI-Lynx]</product>
       <vendor>Texas Instruments</vendor>
       <physid>5</physid>
       <businfo>pci@0000:01:05.0</businfo>
       <version>00</version>
       <width units="bits">32</width>
       <clock units="Hz">33000000</clock>
       <configuration>
        <setting id="driver" value="firewire_ohci" />
        <setting id="latency" value="64" />
        <setting id="maxlatency" value="4" />
        <setting id="mingnt" value="2" />
        <setting id="module" value="firewire_ohci" />
       </configuration>
       <capabilities>
        <capability id="pm" >Power Management</capability>
        <capability id="ohci" >Open Host Controller Interface</capability>
        <capability id="bus_master" >bus mastering</capability>
        <capability id="cap_list" >PCI capabilities listing</capability>
       </capabilities>
      </node>
    </node>
    <node id="multimedia" claimed="true" class="multimedia" handle="PCI:0000:00:06.1">
     <description>Audio device</description>
     <product>MCP55 High Definition Audio</product>
     <vendor>NVIDIA Corporation</vendor>
     <physid>6.1</physid>
     <businfo>pci@0000:00:06.1</businfo>
     <version>a2</version>
     <width units="bits">32</width>
     <clock units="Hz">66000000</clock>
     <configuration>
      <setting id="driver" value="snd_hda_intel" />
      <setting id="latency" value="0" />
      <setting id="maxlatency" value="5" />
      <setting id="mingnt" value="2" />
      <setting id="module" value="snd_hda_intel" />
     </configuration>
     <capabilities>
      <capability id="pm" >Power Management</capability>
      <capability id="msi" >Message Signalled Interrupts</capability>
      <capability id="ht" >HyperTransport</capability>
      <capability id="bus_master" >bus mastering</capability>
      <capability id="cap_list" >PCI capabilities listing</capability>
     </capabilities>
    </node>
    <node id="bridge:0" claimed="true" class="bridge" handle="PCI:0000:00:08.0">
     <description>Ethernet interface</description>
     <product>MCP55 Ethernet</product>
     <vendor>NVIDIA Corporation</vendor>
     <physid>8</physid>
     <businfo>pci@0000:00:08.0</businfo>
     <logicalname>eth0</logicalname>
     <version>a3</version>
     <serial>00:e0:81:71:f1:3a</serial>
     <size>1000000000</size>
     <capacity>1000000000</capacity>
     <width units="bits">32</width>
     <clock units="Hz">66000000</clock>
     <configuration>
      <setting id="autonegotiation" value="on" />
      <setting id="broadcast" value="yes" />
      <setting id="driver" value="forcedeth" />
      <setting id="driverversion" value="0.64" />
      <setting id="duplex" value="full" />
      <setting id="ip" value="10.121.8.22" />
      <setting id="latency" value="0" />
      <setting id="link" value="yes" />
      <setting id="maxlatency" value="20" />
      <setting id="mingnt" value="1" />
      <setting id="module" value="forcedeth" />
      <setting id="multicast" value="yes" />
      <setting id="port" value="MII" />
      <setting id="speed" value="1GB/s" />
     </configuration>
     <capabilities>
      <capability id="bridge" />
      <capability id="pm" >Power Management</capability>
      <capability id="msix" >MSI-X</capability>
      <capability id="msi" >Message Signalled Interrupts</capability>
      <capability id="ht" >HyperTransport</capability>
      <capability id="bus_master" >bus mastering</capability>
      <capability id="cap_list" >PCI capabilities listing</capability>
      <capability id="ethernet" />
      <capability id="physical" >Physical interface</capability>
      <capability id="mii" >Media Independant Interface</capability>
      <capability id="10bt" >10MB/s</capability>
      <capability id="10bt-fd" >10MB/s (full duplex)</capability>
      <capability id="100bt" >100MB/s</capability>
      <capability id="100bt-fd" >100MB/s (full duplex)</capability>
      <capability id="1000bt-fd" >1GB/s (full duplex)</capability>
      <capability id="autonegotiation" >Auto-negotiation</capability>
     </capabilities>
    </node>
    <node id="bridge:1" disabled="true" claimed="true" class="bridge" handle="PCI:0000:00:09.0">
     <description>Ethernet interface</description>
     <product>MCP55 Ethernet</product>
     <vendor>NVIDIA Corporation</vendor>
     <physid>9</physid>
     <businfo>pci@0000:00:09.0</businfo>
     <logicalname>eth1</logicalname>
     <version>a3</version>
     <serial>00:e0:81:71:f1:3b</serial>
     <capacity>1000000000</capacity>
     <width units="bits">32</width>
     <clock units="Hz">66000000</clock>
     <configuration>
      <setting id="autonegotiation" value="on" />
      <setting id="broadcast" value="yes" />
      <setting id="driver" value="forcedeth" />
      <setting id="driverversion" value="0.64" />
      <setting id="latency" value="0" />
      <setting id="link" value="no" />
      <setting id="maxlatency" value="20" />
      <setting id="mingnt" value="1" />
      <setting id="module" value="forcedeth" />
      <setting id="multicast" value="yes" />
      <setting id="port" value="MII" />
     </configuration>
     <capabilities>
      <capability id="bridge" />
      <capability id="pm" >Power Management</capability>
      <capability id="msix" >MSI-X</capability>
      <capability id="msi" >Message Signalled Interrupts</capability>
      <capability id="ht" >HyperTransport</capability>
      <capability id="bus_master" >bus mastering</capability>
      <capability id="cap_list" >PCI capabilities listing</capability>
      <capability id="ethernet" />
      <capability id="physical" >Physical interface</capability>
      <capability id="mii" >Media Independant Interface</capability>
      <capability id="10bt" >10MB/s</capability>
      <capability id="10bt-fd" >10MB/s (full duplex)</capability>
      <capability id="100bt" >100MB/s</capability>
      <capability id="100bt-fd" >100MB/s (full duplex)</capability>
      <capability id="1000bt-fd" >1GB/s (full duplex)</capability>
      <capability id="autonegotiation" >Auto-negotiation</capability>
     </capabilities>
    </node>
    <node id="pci:1" claimed="true" class="bridge" handle="PCIBUS:0000:02">
     <description>PCI bridge</description>
     <product>MCP55 PCI Express bridge</product>
     <vendor>NVIDIA Corporation</vendor>
     <physid>101</physid>
     <businfo>pci@0000:00:0a.0</businfo>
     <version>a3</version>
     <width units="bits">32</width>
     <clock units="Hz">33000000</clock>
     <configuration>
      <setting id="driver" value="pcieport" />
     </configuration>
     <capabilities>
      <capability id="pci" />
      <capability id="pm" >Power Management</capability>
      <capability id="msi" >Message Signalled Interrupts</capability>
      <capability id="ht" >HyperTransport</capability>
      <capability id="pciexpress" >PCI Express</capability>
      <capability id="normal_decode" />
      <capability id="bus_master" >bus mastering</capability>
      <capability id="cap_list" >PCI capabilities listing</capability>
     </capabilities>
    </node>
    <node id="pci:2" claimed="true" class="bridge" handle="PCIBUS:0000:03">
     <description>PCI bridge</description>
     <product>MCP55 PCI Express bridge</product>
     <vendor>NVIDIA Corporation</vendor>
     <physid>102</physid>
     <businfo>pci@0000:00:0d.0</businfo>
     <version>a3</version>
     <width units="bits">32</width>
     <clock units="Hz">33000000</clock>
     <configuration>
      <setting id="driver" value="pcieport" />
     </configuration>
     <capabilities>
      <capability id="pci" />
      <capability id="pm" >Power Management</capability>
      <capability id="msi" >Message Signalled Interrupts</capability>
      <capability id="ht" >HyperTransport</capability>
      <capability id="pciexpress" >PCI Express</capability>
      <capability id="normal_decode" />
      <capability id="bus_master" >bus mastering</capability>
      <capability id="cap_list" >PCI capabilities listing</capability>
     </capabilities>
      <node id="pci:0" claimed="true" class="bridge" handle="PCIBUS:0000:04">
       <description>PCI bridge</description>
       <product>uPD720400 PCI Express - PCI/PCI-X Bridge</product>
       <vendor>NEC Corporation</vendor>
       <physid>0</physid>
       <businfo>pci@0000:03:00.0</businfo>
       <version>06</version>
       <width units="bits">32</width>
       <clock units="Hz">33000000</clock>
       <capabilities>
        <capability id="pci" />
        <capability id="pciexpress" >PCI Express</capability>
        <capability id="pcix" >PCI-X</capability>
        <capability id="pm" >Power Management</capability>
        <capability id="normal_decode" />
        <capability id="bus_master" >bus mastering</capability>
        <capability id="cap_list" >PCI capabilities listing</capability>
       </capabilities>
      </node>
      <node id="pci:1" claimed="true" class="bridge" handle="PCIBUS:0000:05">
       <description>PCI bridge</description>
       <product>uPD720400 PCI Express - PCI/PCI-X Bridge</product>
       <vendor>NEC Corporation</vendor>
       <physid>0.1</physid>
       <businfo>pci@0000:03:00.1</businfo>
       <version>06</version>
       <width units="bits">64</width>
       <clock units="Hz">33000000</clock>
       <capabilities>
        <capability id="pci" />
        <capability id="pciexpress" >PCI Express</capability>
        <capability id="pcix" >PCI-X</capability>
        <capability id="pm" >Power Management</capability>
        <capability id="msi" >Message Signalled Interrupts</capability>
        <capability id="normal_decode" />
        <capability id="bus_master" >bus mastering</capability>
        <capability id="cap_list" >PCI capabilities listing</capability>
       </capabilities>
      </node>
    </node>
    <node id="pci:3" claimed="true" class="bridge" handle="PCIBUS:0000:06">
     <description>PCI bridge</description>
     <product>MCP55 PCI Express bridge</product>
     <vendor>NVIDIA Corporation</vendor>
     <physid>103</physid>
     <businfo>pci@0000:00:0f.0</businfo>
     <version>a3</version>
     <width units="bits">32</width>
     <clock units="Hz">33000000</clock>
     <configuration>
      <setting id="driver" value="pcieport" />
     </configuration>
     <capabilities>
      <capability id="pci" />
      <capability id="pm" >Power Management</capability>
      <capability id="msi" >Message Signalled Interrupts</capability>
      <capability id="ht" >HyperTransport</capability>
      <capability id="pciexpress" >PCI Express</capability>
      <capability id="normal_decode" />
      <capability id="bus_master" >bus mastering</capability>
      <capability id="cap_list" >PCI capabilities listing</capability>
     </capabilities>
      <node id="display" claimed="true" class="display" handle="PCI:0000:06:00.0">
       <description>VGA compatible controller</description>
       <product>NV44 [GeForce 6200 TurboCache(TM)]</product>
       <vendor>NVIDIA Corporation</vendor>
       <physid>0</physid>
       <businfo>pci@0000:06:00.0</businfo>
       <version>a1</version>
       <width units="bits">64</width>
       <clock units="Hz">33000000</clock>
       <configuration>
        <setting id="driver" value="nouveau" />
        <setting id="latency" value="0" />
        <setting id="module" value="drm" />
       </configuration>
       <capabilities>
        <capability id="pm" >Power Management</capability>
        <capability id="msi" >Message Signalled Interrupts</capability>
        <capability id="pciexpress" >PCI Express</capability>
        <capability id="vga_controller" />
        <capability id="bus_master" >bus mastering</capability>
        <capability id="cap_list" >PCI capabilities listing</capability>
       </capabilities>
      </node>
    </node>
    <node id="pci:4" claimed="true" class="bridge" handle="PCIBUS:0000:00">
     <description>Host bridge</description>
     <product>K8 [Athlon64/Opteron] HyperTransport Technology Configuration</product>
     <vendor>Advanced Micro Devices [AMD]</vendor>
     <physid>104</physid>
     <businfo>pci@0000:00:18.0</businfo>
     <version>00</version>
     <width units="bits">32</width>
     <clock units="Hz">33000000</clock>
    </node>
    <node id="pci:5" claimed="true" class="bridge" handle="PCIBUS:0000:00">
     <description>Host bridge</description>
     <product>K8 [Athlon64/Opteron] Address Map</product>
     <vendor>Advanced Micro Devices [AMD]</vendor>
     <physid>105</physid>
     <businfo>pci@0000:00:18.1</businfo>
     <version>00</version>
     <width units="bits">32</width>
     <clock units="Hz">33000000</clock>
    </node>
    <node id="pci:6" claimed="true" class="bridge" handle="PCIBUS:0000:00">
     <description>Host bridge</description>
     <product>K8 [Athlon64/Opteron] DRAM Controller</product>
     <vendor>Advanced Micro Devices [AMD]</vendor>
     <physid>106</physid>
     <businfo>pci@0000:00:18.2</businfo>
     <version>00</version>
     <width units="bits">32</width>
     <clock units="Hz">33000000</clock>
    </node>
    <node id="pci:7" claimed="true" class="bridge" handle="PCIBUS:0000:00">
     <description>Host bridge</description>
     <product>K8 [Athlon64/Opteron] Miscellaneous Control</product>
     <vendor>Advanced Micro Devices [AMD]</vendor>
     <physid>107</physid>
     <businfo>pci@0000:00:18.3</businfo>
     <version>00</version>
     <width units="bits">32</width>
     <clock units="Hz">33000000</clock>
     <configuration>
      <setting id="driver" value="k8temp" />
      <setting id="module" value="k8temp" />
     </configuration>
    </node>
    <node id="pci:8" claimed="true" class="bridge" handle="PCIBUS:0000:00">
     <description>Host bridge</description>
     <product>K8 [Athlon64/Opteron] HyperTransport Technology Configuration</product>
     <vendor>Advanced Micro Devices [AMD]</vendor>
     <physid>108</physid>
     <businfo>pci@0000:00:19.0</businfo>
     <version>00</version>
     <width units="bits">32</width>
     <clock units="Hz">33000000</clock>
    </node>
    <node id="pci:9" claimed="true" class="bridge" handle="PCIBUS:0000:00">
     <description>Host bridge</description>
     <product>K8 [Athlon64/Opteron] Address Map</product>
     <vendor>Advanced Micro Devices [AMD]</vendor>
     <physid>109</physid>
     <businfo>pci@0000:00:19.1</businfo>
     <version>00</version>
     <width units="bits">32</width>
     <clock units="Hz">33000000</clock>
    </node>
    <node id="pci:10" claimed="true" class="bridge" handle="PCIBUS:0000:00">
     <description>Host bridge</description>
     <product>K8 [Athlon64/Opteron] DRAM Controller</product>
     <vendor>Advanced Micro Devices [AMD]</vendor>
     <physid>10a</physid>
     <businfo>pci@0000:00:19.2</businfo>
     <version>00</version>
     <width units="bits">32</width>
     <clock units="Hz">33000000</clock>
    </node>
    <node id="pci:11" claimed="true" class="bridge" handle="PCIBUS:0000:00">
     <description>Host bridge</description>
     <product>K8 [Athlon64/Opteron] Miscellaneous Control</product>
     <vendor>Advanced Micro Devices [AMD]</vendor>
     <physid>10b</physid>
     <businfo>pci@0000:00:19.3</businfo>
     <version>00</version>
     <width units="bits">32</width>
     <clock units="Hz">33000000</clock>
     <configuration>
      <setting id="driver" value="k8temp" />
      <setting id="module" value="k8temp" />
     </configuration>
    </node>
    <node id="memory:2" class="memory" handle="PCI:0000:80:00.0">
     <description>RAM memory</description>
     <product>MCP55 Memory Controller</product>
     <vendor>NVIDIA Corporation</vendor>
     <physid>0</physid>
     <businfo>pci@0000:80:00.0</businfo>
     <version>a2</version>
     <width units="bits">32</width>
     <clock units="Hz">66000000</clock>
     <configuration>
      <setting id="latency" value="0" />
     </configuration>
     <capabilities>
      <capability id="ht" >HyperTransport</capability>
      <capability id="bus_master" >bus mastering</capability>
      <capability id="cap_list" >PCI capabilities listing</capability>
     </capabilities>
    </node>
    <node id="memory:3" class="memory" handle="PCI:0000:80:01.0">
     <description>RAM memory</description>
     <product>MCP55 LPC Bridge</product>
     <vendor>NVIDIA Corporation</vendor>
     <physid>d</physid>
     <businfo>pci@0000:80:01.0</businfo>
     <version>a3</version>
     <width units="bits">32</width>
     <clock units="Hz">66000000</clock>
     <configuration>
      <setting id="latency" value="0" />
     </configuration>
     <capabilities>
      <capability id="bus_master" >bus mastering</capability>
     </capabilities>
    </node>
    <node id="serial:1" claimed="true" class="bus" handle="PCI:0000:80:01.1">
     <description>SMBus</description>
     <product>MCP55 SMBus</product>
     <vendor>NVIDIA Corporation</vendor>
     <physid>e</physid>
     <businfo>pci@0000:80:01.1</businfo>
     <version>a3</version>
     <width units="bits">32</width>
     <clock units="Hz">66000000</clock>
     <configuration>
      <setting id="driver" value="nForce2_smbus" />
      <setting id="latency" value="0" />
      <setting id="module" value="i2c_nforce2" />
     </configuration>
     <capabilities>
      <capability id="pm" >Power Management</capability>
      <capability id="cap_list" >PCI capabilities listing</capability>
     </capabilities>
    </node>
    <node id="pci:12" claimed="true" class="bridge" handle="PCIBUS:0000:81">
     <description>PCI bridge</description>
     <product>MCP55 PCI Express bridge</product>
     <vendor>NVIDIA Corporation</vendor>
     <physid>10c</physid>
     <businfo>pci@0000:80:0a.0</businfo>
     <version>a3</version>
     <width units="bits">32</width>
     <clock units="Hz">33000000</clock>
     <configuration>
      <setting id="driver" value="pcieport" />
     </configuration>
     <capabilities>
      <capability id="pci" />
      <capability id="pm" >Power Management</capability>
      <capability id="msi" >Message Signalled Interrupts</capability>
      <capability id="ht" >HyperTransport</capability>
      <capability id="pciexpress" >PCI Express</capability>
      <capability id="normal_decode" />
      <capability id="bus_master" >bus mastering</capability>
      <capability id="cap_list" >PCI capabilities listing</capability>
     </capabilities>
    </node>
    <node id="pci:13" claimed="true" class="bridge" handle="PCIBUS:0000:82">
     <description>PCI bridge</description>
     <product>MCP55 PCI Express bridge</product>
     <vendor>NVIDIA Corporation</vendor>
     <physid>10d</physid>
     <businfo>pci@0000:80:0d.0</businfo>
     <version>a3</version>
     <width units="bits">32</width>
     <clock units="Hz">33000000</clock>
     <configuration>
      <setting id="driver" value="pcieport" />
     </configuration>
     <capabilities>
      <capability id="pci" />
      <capability id="pm" >Power Management</capability>
      <capability id="msi" >Message Signalled Interrupts</capability>
      <capability id="ht" >HyperTransport</capability>
      <capability id="pciexpress" >PCI Express</capability>
      <capability id="normal_decode" />
      <capability id="bus_master" >bus mastering</capability>
      <capability id="cap_list" >PCI capabilities listing</capability>
     </capabilities>
    </node>
    <node id="pci:14" claimed="true" class="bridge" handle="PCIBUS:0000:83">
     <description>PCI bridge</description>
     <product>MCP55 PCI Express bridge</product>
     <vendor>NVIDIA Corporation</vendor>
     <physid>f</physid>
     <businfo>pci@0000:80:0f.0</businfo>
     <version>a3</version>
     <width units="bits">32</width>
     <clock units="Hz">33000000</clock>
     <configuration>
      <setting id="driver" value="pcieport" />
     </configuration>
     <capabilities>
      <capability id="pci" />
      <capability id="pm" >Power Management</capability>
      <capability id="msi" >Message Signalled Interrupts</capability>
      <capability id="ht" >HyperTransport</capability>
      <capability id="pciexpress" >PCI Express</capability>
      <capability id="normal_decode" />
      <capability id="bus_master" >bus mastering</capability>
      <capability id="cap_list" >PCI capabilities listing</capability>
     </capabilities>
    </node>
    <node id="scsi:0" claimed="true" class="storage" handle="">
     <physid>10</physid>
     <logicalname>scsi0</logicalname>
     <capabilities>
      <capability id="emulated" >Emulated device</capability>
     </capabilities>
      <node id="disk" claimed="true" class="disk" handle="GUID:385de559-9cd9-44f2-9390-e0ca3b712cbc">
       <description>SCSI Disk</description>
       <product>Maxtor 6V250F0</product>
       <vendor>ATA</vendor>
       <physid>0.0.0</physid>
       <businfo>scsi@0:0.0.0</businfo>
       <logicalname>/dev/sda</logicalname>
       <dev>8d:0d</dev>
       <version>VA11</version>
       <serial>V508WXGG</serial>
       <size units="bytes">250059350016</size>
       <configuration>
        <setting id="ansiversion" value="5" />
        <setting id="guid" value="385de559-9cd9-44f2-9390-e0ca3b712cbc" />
       </configuration>
       <capabilities>
        <capability id="gpt-1.00" >GUID Partition Table version 1.00</capability>
        <capability id="partitioned" >Partitioned disk</capability>
        <capability id="partitioned:gpt" >GUID partition table</capability>
       </capabilities>
        <node id="volume:0" claimed="true" class="volume" handle="GUID:33eae56e-54bf-4e76-b2e3-4bb7a907de49">
         <description>System partition</description>
         <physid>1</physid>
         <businfo>scsi@0:0.0.0,1</businfo>
         <logicalname>/dev/sda1</logicalname>
         <dev>8d:1d</dev>
         <serial>33eae56e-54bf-4e76-b2e3-4bb7a907de49</serial>
         <capacity>209714688</capacity>
         <configuration>
          <setting id="name" value="primary" />
         </configuration>
         <capabilities>
          <capability id="boot" >Contains boot code</capability>
         </capabilities>
        </node>
        <node id="volume:1" claimed="true" class="volume" handle="GUID:4d102ad6-2863-4b59-acd4-7e41d3cfa02a">
         <description>Linux Swap partition</description>
         <physid>2</physid>
         <businfo>scsi@0:0.0.0,2</businfo>
         <logicalname>/dev/sda2</logicalname>
         <dev>8d:2d</dev>
         <serial>4d102ad6-2863-4b59-acd4-7e41d3cfa02a</serial>
         <capacity>2096102912</capacity>
         <configuration>
          <setting id="name" value="primary" />
         </configuration>
         <capabilities>
          <capability id="nofs" >No filesystem</capability>
         </capabilities>
        </node>
        <node id="volume:2" claimed="true" class="volume" handle="GUID:df99fc83-8733-4de4-8e48-d1de4420f310">
         <description>Data partition</description>
         <physid>3</physid>
         <businfo>scsi@0:0.0.0,3</businfo>
         <logicalname>/dev/sda3</logicalname>
         <dev>8d:3d</dev>
         <serial>df99fc83-8733-4de4-8e48-d1de4420f310</serial>
         <capacity>1048064</capacity>
         <configuration>
          <setting id="name" value="primary" />
         </configuration>
        </node>
        <node id="volume:3" claimed="true" class="volume" handle="GUID:900204aa-0aa6-4e44-868e-0090ff1165d5">
         <description>Data partition</description>
         <physid>4</physid>
         <businfo>scsi@0:0.0.0,4</businfo>
         <logicalname>/dev/sda4</logicalname>
         <dev>8d:4d</dev>
         <serial>900204aa-0aa6-4e44-868e-0090ff1165d5</serial>
         <capacity>1048064</capacity>
         <configuration>
          <setting id="name" value="primary" />
         </configuration>
        </node>
        <node id="volume:4" claimed="true" class="volume" handle="GUID:118b3902-3dbb-4e0e-9a85-9260b9fa2069">
         <description>Data partition</description>
         <physid>5</physid>
         <businfo>scsi@0:0.0.0,5</businfo>
         <logicalname>/dev/sda5</logicalname>
         <dev>8d:5d</dev>
         <serial>118b3902-3dbb-4e0e-9a85-9260b9fa2069</serial>
         <capacity>31457278976</capacity>
         <configuration>
          <setting id="name" value="primary" />
         </configuration>
        </node>
        <node id="volume:5" claimed="true" class="volume" handle="GUID:b60bb9e4-7328-4c82-8e75-04aed7f3c028">
         <description>Data partition</description>
         <physid>6</physid>
         <businfo>scsi@0:0.0.0,6</businfo>
         <logicalname>/dev/sda6</logicalname>
         <dev>8d:6d</dev>
         <serial>b60bb9e4-7328-4c82-8e75-04aed7f3c028</serial>
         <capacity>31457278976</capacity>
         <configuration>
          <setting id="name" value="primary" />
         </configuration>
        </node>
        <node id="volume:6" claimed="true" class="volume" handle="GUID:1f21e405-8a01-46d0-9225-a29be309f9bf">
         <description>Data partition</description>
         <physid>7</physid>
         <businfo>scsi@0:0.0.0,7</businfo>
         <logicalname>/dev/sda7</logicalname>
         <dev>8d:7d</dev>
         <serial>1f21e405-8a01-46d0-9225-a29be309f9bf</serial>
         <capacity>31457278976</capacity>
         <configuration>
          <setting id="name" value="primary" />
         </configuration>
        </node>
        <node id="volume:7" claimed="true" class="volume" handle="GUID:10437947-5844-40f7-9812-9db028004393">
         <description>Data partition</description>
         <physid>8</physid>
         <businfo>scsi@0:0.0.0,8</businfo>
         <logicalname>/dev/sda8</logicalname>
         <dev>8d:8d</dev>
         <serial>10437947-5844-40f7-9812-9db028004393</serial>
         <capacity>31457278976</capacity>
         <configuration>
          <setting id="name" value="primary" />
         </configuration>
        </node>
        <node id="volume:8" claimed="true" class="volume" handle="GUID:c5f60d30-38eb-478a-add2-34ca3f324622">
         <description>Data partition</description>
         <physid>9</physid>
         <businfo>scsi@0:0.0.0,9</businfo>
         <logicalname>/dev/sda9</logicalname>
         <dev>8d:9d</dev>
         <serial>c5f60d30-38eb-478a-add2-34ca3f324622</serial>
         <capacity>121921076736</capacity>
         <configuration>
          <setting id="name" value="primary" />
         </configuration>
        </node>
      </node>
    </node>
    <node id="scsi:1" claimed="true" class="storage" handle="">
     <physid>11</physid>
     <logicalname>scsi6</logicalname>
     <capabilities>
      <capability id="emulated" >Emulated device</capability>
     </capabilities>
      <node id="cdrom" claimed="true" class="disk" handle="SCSI:06:00:00:00">
       <description>DVD writer</description>
       <product>DVDRW SHW-160P6S</product>
       <vendor>LITE-ON</vendor>
       <physid>0.0.0</physid>
       <businfo>scsi@6:0.0.0</businfo>
       <logicalname>/dev/cdrom</logicalname>
       <logicalname>/dev/dvd</logicalname>
       <logicalname>/dev/sr0</logicalname>
       <dev>11d:0d</dev>
       <version>PS0B</version>
       <configuration>
        <setting id="ansiversion" value="5" />
        <setting id="status" value="nodisc" />
       </configuration>
       <capabilities>
        <capability id="removable" >support is removable</capability>
        <capability id="audio" >Audio CD playback</capability>
        <capability id="cd-r" >CD-R burning</capability>
        <capability id="cd-rw" >CD-RW burning</capability>
        <capability id="dvd" >DVD playback</capability>
        <capability id="dvd-r" >DVD-R burning</capability>
       </capabilities>
      </node>
    </node>
  </node>
</node>
'''
