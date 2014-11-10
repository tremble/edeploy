import re
import compare_sets
import utils
import numpy
from pandas import *
import perf_cpu_tables


def search_item(systems, unique_id, item, regexp, exclude_list=[], include_list=[]):
    sets = {}
    for system in systems:
        sets[system[unique_id]] = set()
        current_set = sets[system[unique_id]]
        for stuff in system[item]:
            m = re.match(regexp, stuff[1])
            if m:
                # If we have an include_list, only those shall be used
                # So everything is exclude by default
                if len(include_list) > 0:
                    shall_be_excluded = True
                else:
                    shall_be_excluded = False

                for include in include_list:
                    if include in stuff[2]:
                        # If something is part of the include list
                        # It is no more excluded
                        shall_be_excluded = False

                for exclude in exclude_list:
                    if exclude in stuff[2]:
                        shall_be_excluded = True
                if shall_be_excluded is False:
                    current_set.add(stuff)
    return sets


def physical_disks(global_params, systems, unique_id):
    sets = search_item(systems, unique_id, "disk", "(\d+)I:(\d+):(\d+)", ['current_temperature_(c)', 'maximum_temperature_(c)', 'serial_number'])
    groups = compare_sets.compare(sets)
    compare_sets.print_groups(global_params, groups, "Physical Disks (HP Controllers)")
    return groups


def logical_disks(global_params, systems, unique_id):
    sets = search_item(systems, unique_id, "disk", "[a-z]d(\S+)", ['simultaneous', 'standalone', 'id'])
    groups = compare_sets.compare(sets)
    compare_sets.print_groups(global_params, groups, "Logical Disks")
    return groups


def compute_deviance_percentage(item, df):
    # If we have a single item
    # checking the variance is useless
    if df[item].count() == 1:
        return 0
    return (df[item].std() / df[item].mean() * 100)


def print_detail(detail_options, details, df, matched_category):
    if ((utils.print_level & utils.Levels.DETAIL) != utils.Levels.DETAIL):
        return
    if len(df.loc[details]) > 0:
        print
        print "%-34s: %-8s: %s" % (matched_category[0], utils.Levels.message[utils.print_level], detail_options['item'])
        print df.loc[details]


def prepare_detail(detail_options, group_number, category, item, details, matched_category_to_save):
    if ((utils.print_level & utils.Levels.DETAIL) != utils.Levels.DETAIL):
        return

    matched_group = ''
    matched_category = ''
    matched_item = ''

    if (detail_options['group'] == str(group_number)):
            matched_group = str(group_number)
    elif (re.search(detail_options['group'], str(group_number)) is not None):
            matched_group = re.search(detail_options['group'], str(group_number)).group()

    if (detail_options['category'] in category):
        matched_category = category
    elif (re.search(detail_options['category'], category) is not None):
        matched_category = re.search(detail_options['category'], category).group()

    if (detail_options['item'] in item):
        matched_item = item
    elif (re.search(detail_options['item'], item) is not None):
        matched_item = re.search(detail_options['item'], item).group()

    if (len(matched_group) > 0) and (len(matched_category) > 0) and (len(matched_item) > 0):
        details.append(matched_item)
        if matched_category not in matched_category_to_save:
            matched_category_to_save.append(matched_category)
        return matched_category
    return ""


def network_perf(systems, unique_id, group_number, detail_options, rampup_value=0, current_dir=""):
    have_net_data = False
    sets = search_item(systems, unique_id, "network", "(.*)", [], [])
    modes = ['bandwidth', 'requests_per_sec']
    for mode in modes:
        results = {}
        for system in sets:
            net = []
            series = []
            for perf in sets[system]:
                if (perf[1] == mode):
                    if not perf[1] in net:
                        net.append(perf[1])
                    series.append(float(perf[3]))
            results[system] = Series(series, index=net)

        df = DataFrame(results)
        details = []
        matched_category = []
        for net in df.transpose().columns:
            if have_net_data is False:
                print
                print "Group %d : Checking network disks perf" % group_number
                have_net_data = True
            consistent = []
            curious = []
            unstable = []
            # How much the variance could be far from the average (in %)
            tolerance_max = 15
            tolerance_min = 2

            print_perf(tolerance_min, tolerance_max, df.transpose()[net], df, mode, net, consistent, curious, unstable, rampup_value, current_dir)
            if mode == 'bandwidth':
                unit = "MB/sec"
            else:
                unit = "RRQ/sec"
            prepare_detail(detail_options, group_number, mode, net, details, matched_category)
            print_summary("%-30s %s" % (mode, net), consistent, "consistent", unit, df)
            print_summary("%-30s %s" % (mode, net), curious, "curious", unit, df)
            print_summary("%-30s %s" % (mode, net), unstable, "unstable", unit, df)

        print_detail(detail_options, details, df, matched_category)


def logical_disks_perf(systems, unique_id, group_number, detail_options, rampup_value=0, current_dir=""):
    have_disk_data = False
    sets = search_item(systems, unique_id, "disk", "[a-z]d(\S+)", [], ['simultaneous', 'standalone'])
    modes = []

    # Searching for modes ran in this benchmark
    for system in sets:
        for perf in sets[system]:
            if perf[2] not in modes:
                modes.append(perf[2])

    if len(modes) == 0:
        return

    for mode in modes:
        results = {}
        for system in sets:
            disks = []
            series = []
            for perf in sets[system]:
                if (perf[2] == mode):
                    if not perf[1] in disks:
                        disks.append(perf[1])
                    series.append(int(perf[3]))
            results[system] = Series(series, index=disks)

        df = DataFrame(results)
        details = []
        matched_category = []
        for disk in df.transpose().columns:
            if have_disk_data is False:
                print
                print "Group %d : Checking logical disks perf" % group_number
                have_disk_data = True
            consistent = []
            curious = []
            unstable = []
            # How much the variance could be far from the average (in %)
            tolerance_max = 10
            tolerance_min = 2
            # In random mode, the variance could be higher as
            # we cannot insure the distribution pattern was similar
            if "rand" in mode:
                tolerance_min = 5
                tolerance_max = 15

            print_perf(tolerance_min, tolerance_max, df.transpose()[disk], df, mode, disk, consistent, curious, unstable, rampup_value, current_dir)

            prepare_detail(detail_options, group_number, mode, disk, details, matched_category)
            print_summary("%-30s %s" % (mode, disk), consistent, "consistent", "IOps", df)
            print_summary("%-30s %s" % (mode, disk), curious, "curious", "IOps", df)
            print_summary("%-30s %s" % (mode, disk), unstable, "unstable", "IOps", df)

        print_detail(detail_options, details, df, matched_category)


def hpa(global_params, systems, unique_id):
    sets = search_item(systems, unique_id, "hpa", "(.*)", ['cache_serial_number', 'serial_number'])
    groups = compare_sets.compare(sets)
    compare_sets.print_groups(global_params, groups, "HPA Controller")
    return groups


def systems(global_params, systems, unique_id):
    sets = search_item(systems, unique_id, "system", "(.*)", ['serial', 'uuid'])
    groups = compare_sets.compare(sets)
    compare_sets.print_groups(global_params, groups, "System")
    return groups


def firmware(global_params, systems, unique_id):
    sets = search_item(systems, unique_id, "firmware", "(.*)")
    groups = compare_sets.compare(sets)
    compare_sets.print_groups(global_params, groups, "Firmware")
    return groups


def memory_timing(global_params, systems, unique_id):
    sets = search_item(systems, unique_id, "memory", "DDR(.*)")
    groups = compare_sets.compare(sets)
    compare_sets.print_groups(global_params, groups, "Memory Timing(RAM)")
    return groups


def memory_banks(global_params, systems, unique_id):
    sets = search_item(systems, unique_id, "memory", "bank(.*)", ['serial'])
    groups = compare_sets.compare(sets)
    compare_sets.print_groups(global_params, groups, "Memory Banks(RAM)")
    return groups


def network_interfaces(global_params, systems, unique_id):
    sets = search_item(systems, unique_id, "network", "(.*)", ['serial', 'ipv4'])
    groups = compare_sets.compare(sets)
    compare_sets.print_groups(global_params, groups, "Network Interfaces")
    return groups


def cpu(global_params, systems, unique_id):
    sets = search_item(systems, unique_id, "cpu", "(.*)", ['bogomips', 'loops_per_sec', 'bandwidth', 'cache_size', '/temperature'])
    groups = compare_sets.compare(sets)
    compare_sets.print_groups(global_params, groups, "Processors")
    return groups


def print_perf(tolerance_min, tolerance_max, item, df, mode, title, consistent=None, curious=None, unstable=None, rampup_value=0, current_dir=""):
    # Tolerance_min represents the min where variance shall be considered (in %)
    # Tolerance_max represents the maximum that variance represent regarding the average (in %)

    variance_group = item.std()
    mean_group = item.mean()
    sum_group = item.sum()
    min_group = mean_group - 2*variance_group
    max_group = mean_group + 2*variance_group

    utils.do_print(mode, utils.Levels.INFO, "%-12s : Group performance : min=%8.2f, mean=%8.2f, max=%8.2f, stddev=%8.2f", title, item.min(), mean_group, item.max(), variance_group)

    variance_tolerance = compute_deviance_percentage(title, df.transpose())

    if (rampup_value > 0) and (current_dir):
        utils.write_gnuplot_file(current_dir+"/deviance.plot", rampup_value, variance_group)
        utils.write_gnuplot_file(current_dir+"/deviance_percentage.plot", rampup_value, variance_tolerance)
        utils.write_gnuplot_file(current_dir+"/mean.plot", rampup_value, mean_group)
        utils.write_gnuplot_file(current_dir+"/sum.plot", rampup_value, sum_group)

    if (variance_tolerance > tolerance_max):
        utils.do_print(mode, utils.Levels.ERROR, "%-12s : Group's variance is too important : %7.2f%% of %7.2f whereas limit is set to %3.2f%%", title, variance_tolerance, mean_group, tolerance_max)
        utils.do_print(mode, utils.Levels.ERROR, "%-12s : Group performance : UNSTABLE", title)
        for host in df.columns:
            if host not in curious:
                unstable.append(host)
    else:
        curious_performance = False
        for host in df.columns:
            if (("loops_per_sec") in mode) or ("bogomips" in mode):
                mean_host = df[host][title].mean()
            else:
                mean_host = df[host].mean()
            # If the variance is very low, don't try to find the black sheep
            if (variance_tolerance > tolerance_min):
                if (mean_host > max_group):
                    curious_performance = True
                    utils.do_print(mode, utils.Levels.WARNING, "%-12s : %s : Curious overperformance  %7.2f : min_allow_group = %.2f, mean_group = %.2f max_allow_group = %.2f", title, host, mean_host, min_group, mean_group, max_group)
                    if host not in curious:
                        curious.append(host)
                        if host in consistent:
                            consistent.remove(host)
                elif (mean_host < min_group):
                    curious_performance = True
                    utils.do_print(mode, utils.Levels.WARNING, "%-12s : %s : Curious underperformance %7.2f : min_allow_group = %.2f, mean_group = %.2f max_allow_group = %.2f", title, host, mean_host, min_group, mean_group, max_group)
                    if host not in curious:
                        curious.append(host)
                        if host in consistent:
                            consistent.remove(host)
                else:
                    if (host not in consistent) and (host not in curious):
                        consistent.append(host)
            else:
                if (host not in consistent) and (host not in curious):
                    consistent.append(host)

        unit = " "
        if "Effi." in title:
            unit = "%"
        if curious_performance is False:
            utils.do_print(mode, utils.Levels.INFO, "%-12s : Group performance = %7.2f %s : CONSISTENT", title, mean_group, unit)
        else:
            utils.do_print(mode, utils.Levels.WARNING, "%-12s : Group performance = %7.2f %s : SUSPICIOUS", title, mean_group, unit)


def print_summary(mode, array, array_name, unit, df, item_value=None):
    if (utils.print_level & utils.Levels.SUMMARY) and (len(array) > 0):
        result = []
        before = ""
        after = ""
        RED = "\033[1;31m"
        ORANGE = "\033[1;33m"
        WHITE = "\033[1;m"
        GREEN = "\033[1;32m"

        for host in array:
            result.append(df[host].sum())
        if "unstable" in array_name:
            before = RED
            after = WHITE
        if "curious" in array_name:
            before = ORANGE
            after = WHITE

        mean = numpy.mean(result)
        perf_status = ""
        if array_name == "consistent":
            if item_value is not None:
                if mode == "loops_per_sec" or mode == "bogomips":
                    min_cpu_perf = perf_cpu_tables.get_cpu_min_perf(mode, item_value)
                    if min_cpu_perf == 0:
                        perf_status = ": " + ORANGE + "NO PERF ENTRY IN DB" + WHITE + " for " + item_value
                    elif (mean >= min_cpu_perf):
                        perf_status = ": " + GREEN + "PERF OK" + WHITE
                    else:
                        perf_status = ": " + RED + "PERF FAIL" + WHITE + " as min perf should have been : " + str(min_cpu_perf)
        utils.do_print(mode, utils.Levels.SUMMARY, "%3d %s%-10s%s hosts with %8.2f %-4s as average value and %8.2f standard deviation %s", len(array), before, array_name, after, mean, unit, numpy.std(result), perf_status)


def cpu_perf(systems, unique_id, group_number, detail_options, rampup_value=0, current_dir=""):
    have_cpu_data = False
    host_cpu_list = search_item(systems, unique_id, "cpu", "(.*)", [], ['product'])
    host_cpu_number = search_item(systems, unique_id, "cpu", "(.*logical.*)", [], ['number'])
    core_counts = 1
    for host in host_cpu_number:
        for item in host_cpu_number[host]:
            core_counts = item[3]
            break

    cpu_type = ''
    for host in host_cpu_list:
        for item in host_cpu_list[host]:
            cpu_type = item[3]
            break

    modes = ['bogomips', 'loops_per_sec']
    sets = search_item(systems, unique_id, "cpu", "(.*)", [], modes)
    global_perf = dict()
    for mode in modes:
        results = {}
        for system in sets:
            cpu = []
            series = []
            found_data = False
            for perf in sets[system]:
                if (perf[2] == mode):
                    # We shall split individual cpu benchmarking from the global one
                    if ("_" in perf[1]):
                        if (not perf[1] in cpu):
                            cpu.append(perf[1])
                        series.append(float(perf[3]))
                        found_data = True
                    elif "loops_per_sec" in mode:
                        global_perf[system] = float(perf[3])
                        found_data = True

            if found_data is True:
                # If no series are populated, it means that a single "All CPU" run was done
                # If so, let's create a single run value
                if not series:
                    series.append(global_perf[system])
                    cpu.append("logical")

                results[system] = Series(series, index=cpu)

        # No need to continue if no CPU data in this benchmark
        if not results:
            continue

        df = DataFrame(results)
        consistent = []
        curious = []
        unstable = []
        details = []
        matched_category = []

        for cpu in df.transpose().columns:
            if have_cpu_data is False:
                print
                print "Group %d : Checking CPU perf" % group_number
                have_cpu_data = True
            print_perf(2, 7, df.transpose()[cpu], df, mode, cpu, consistent, curious, unstable, rampup_value, current_dir)
            prepare_detail(detail_options, group_number, mode, cpu, details, matched_category)

        print_detail(detail_options, details, df, matched_category)

        print_summary(mode, consistent, "consistent", "", df, cpu_type)
        print_summary(mode, curious, "curious", "", df)
        print_summary(mode, unstable, "unstable", "", df)

        if mode == "loops_per_sec":
            efficiency = {}
            mode_text = 'CPU Effi.'
            consistent = []
            curious = []
            unstable = []
            details = []
            matched_category = []

            for system in sets:
                host_efficiency_full_load = []
                host_perf = df[system].sum() * (int(core_counts) / df[system].count())
                host_efficiency_full_load.append(global_perf[system] / host_perf * 100)
                efficiency[system] = Series(host_efficiency_full_load, index=[mode_text])

            cpu_eff = DataFrame(efficiency)
            print_perf(1, 2, cpu_eff.transpose()[mode_text], cpu_eff, mode, mode_text, consistent, curious, unstable)
            prepare_detail(detail_options, group_number, mode, mode_text, details, matched_category)

            print_detail(detail_options, details, cpu_eff, matched_category)
            print_summary("CPU Efficiency", consistent, "consistent", '%', cpu_eff)
            print_summary("CPU Efficiency", curious, "curious", '%', cpu_eff)
            print_summary("CPU Efficiency", unstable, "unstable", '%', cpu_eff)


def memory_perf(systems, unique_id, group_number, detail_options, rampup_value=0, current_dir=""):
    have_memory_data = False
    modes = ['1K', '4K', '1M', '16M', '128M', '256M', '1G', '2G']
    sets = search_item(systems, unique_id, "cpu", "(.*)", [], modes)
    for mode in modes:
        real_mode = "Memory benchmark %s" % mode
        results = {}
        threaded_perf = dict()
        forked_perf = dict()
        for system in sets:
            memory = []
            series = []
            found_data = ""
            threaded_perf[system] = 0
            forked_perf[system] = 0
            for perf in sets[system]:
                if (mode in perf[2]):
                    # We shall split individual cpu benchmarking from the global one
                    if ("logical_" in perf[1]) and (("bandwidth_%s" % mode) in perf[2]):
                        if (not perf[1] in memory):
                            memory.append(perf[1])
                        series.append(float(perf[3]))
                    elif ("threaded_bandwidth_%s" % mode) in perf[2]:
                        threaded_perf[system] = float(perf[3])
                        found_data = float(perf[3])
                    elif ("forked_bandwidth_%s" % mode) in perf[2]:
                        forked_perf[system] = float(perf[3])
                        found_data = float(perf[3])

            if found_data:
                # If no series are populated, it means that a single "All CPU" run was done
                # If so, let's create a single run value
                if not series:
                    series.append(found_data)
                    memory.append("logical")

            results[system] = Series(series, index=memory)

        # No need to continue if no Memory data in this benchmark
        if not results:
            continue

        consistent = []
        curious = []
        unstable = []
        details = []
        matched_category = ''

        df = DataFrame(results)
        for memory in df.transpose().columns:
            if have_memory_data is False:
                print
                print "Group %d : Checking Memory perf" % group_number
                have_memory_data = True

            print_perf(1, 7, df.transpose()[memory], df, real_mode, memory, consistent, curious, unstable, rampup_value, current_dir)
            matched_category = []
            prepare_detail(detail_options, group_number, mode, memory, details, matched_category)

        print_detail(detail_options, details, df, matched_category)
        print_summary(mode, consistent, "consistent", "MB/s", df)
        print_summary(mode, curious, "curious", "MB/s", df)
        print_summary(mode, unstable, "unstable", "MB/s", df)

        for bench_type in ["threaded", "forked"]:
            efficiency = {}
            have_forked_or_threaded = False
            if ("threaded" in bench_type):
                mode_text = "Thread effi."
            else:
                mode_text = "Forked Effi."
            for system in sets:
                host_efficiency_full_load = []
                host_perf = df[system].sum()
                if (host_perf > 0) and (threaded_perf[system] > 0) and (forked_perf[system] > 0):
                    have_forked_or_threaded = True
                    if ("threaded" in bench_type):
                        host_efficiency_full_load.append(threaded_perf[system] / host_perf * 100)
                    else:
                        host_efficiency_full_load.append(forked_perf[system] / host_perf * 100)

                    efficiency[system] = Series(host_efficiency_full_load, index=[mode_text])

            details = []
            memory_eff = DataFrame(efficiency)
            if have_forked_or_threaded is True:
                consistent = []
                curious = []
                unstable = []

                for memory in memory_eff.transpose().columns:
                    print_perf(2, 10, memory_eff.transpose()[memory], memory_eff, real_mode, memory, consistent, curious, unstable)
                    matched_category = []
                    prepare_detail(detail_options, group_number, mode, memory, details, matched_category)

                # Let's pad if its a thread or forked effi in addition of the block size
                if matched_category:
                    matched_category[0] += " " + mode_text

                print_detail(detail_options, details, memory_eff, matched_category)
                print_summary(mode + " " + mode_text, consistent, "consistent", "%", memory_eff)
                print_summary(mode + " " + mode_text, curious, "curious", "%", memory_eff)
                print_summary(mode + " " + mode_text, unstable, "unstable", "%", memory_eff)
            else:
                utils.do_print(real_mode, utils.Levels.WARNING, "%-12s : Benchmark not run on this group", mode_text)
