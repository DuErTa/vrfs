
import string
import sys
import re
import pdfkit

INSTANCE_TYPE_RE = "(set routing\-instances\s)(.*)(\sinstance-type )([^\s].*)$"
GROUPS_INSTANCE_TYPE_RE = "(set groups\s)(.*)(\srouting-\instances\s)(.*)(\sinstance-type )([^\s].*)$"
APPLY_GROUPS_RE = "(set apply-groups\s)(.*)$"

LOGICAL_SYSTEMS_INSTANCE_TYPE_RE = "(set logical-systems\s)(.*)(\srouting-\instances\s)(.*)(\sinstance-type )([^\s].*)$"

#set logical-systems r1-ran-agg-lab routing-instances oam vrf-target target:8000:8000
LOGICAL_SYSTEMS_VRF_TARGET_RE_RAW = "(set logical-systems\s)(.*)(\srouting-instances\s)(.*)(\svrf-target{0}target:)(.*)$"

# Add this ...
LOGICAL_SYSTEMS_VRF_EXPORT_IMPORT_RE_RAW = "(set logical-systems\s)(.*)(\srouting-instances\s)(.*)(\svrf-{0} target:)(.*)$"

LOGICAL_SYSTEM_TARGETS_RE_LIST = [LOGICAL_SYSTEMS_VRF_TARGET_RE_RAW, LOGICAL_SYSTEMS_VRF_EXPORT_IMPORT_RE_RAW]


IMPORT_EXPORT_RE_RAW = "(set routing-instances {0} vrf-{1} )(.*)$"
# Add this ...
VRF_TARGET_EXPORT_AND_IMPORT_RE_RAW = "(set routing-instances\s)(.*)(\svrf-target{0}target:)(.*)$"



POLICY_STATEMENT_EXPORT_ADD_RAW_RE = "(set policy-options policy-statement )({0})( then community add target:)(.*)$"
POLICY_STATEMENT_EXPORT_ACTION_RAW_RE = "(set policy-options policy-statement )({0})( then )(accept|reject)$"


POLICY_STATEMENT_IMPORT_FROM_COMMUNITY_RAW_RE = "(set policy-options policy-statement )({0})( term )(.*)( from community target:)(.*)$"
POLICY_STATEMENT_IMPORT_ACTION_RAW_RE = "(set policy-options policy-statement )({0})( term )(.*)( then )(accept|reject)$"
POLICY_STATEMENT_IMPORT_OTHER_RAW_RE = "(set policy-options policy-statement )({0})( term )(other)( then )(accept|reject)$"

#set groups 10htest policy-options community VPN-Y members target:8866:1240
GROUPS_COMMUNITY_TARGETS_RE_RAW = "(set groups\s)(.*)(\spolicy-options community\s)(.*)(\smembers target:)(.*)$"

#set groups 10htest routing-instances VPN-Y vrf-target import target:8866:1240
GROUPS_VRF_TARGET_IMPORT_OR_EXPORT_RE_RAW = "(set groups\s)(.*)(\srouting-instances\s)(.*)(\svrf-target {0} target:)(.*)$"
#set groups 10htest routing-instances VPN-Y vrf-target target:1234:5577
GROUPS_VRF_TARGET_EXPORT_AND_IMPORT_RE_RAW = "(set groups\s)(.*)(\srouting-instances\s)(.*)(\svrf-target target:)(.*)$"

#TBD: set groups 10htest routing-instances VPN-Y vrf-export VPN-Y-Export
GROUPS_VRF_EXPORT_OR_IMPORT_RE_RAW = "(set groups\s)(.*)(\srouting-instances\s)(.*)(\svrf-{0}\S)(.*)$"

AUTO_EXPORT_RE_RAW = "(set routing-instances\s)(.*)(\srouting-options auto-export)$"



#set groups 10htest policy-options policy-statement VPN-Y-Export term Export-Static from protocol static
#set groups 10htest policy-options policy-statement VPN-Y-Export term Export-Static from route-filter 0.0.0.0/0 exact
#set groups 10htest policy-options policy-statement VPN-Y-Export term Export-Static then community add VPN-Y
#set groups 10htest policy-options policy-statement VPN-Y-Export term Export-Static then accept
#set groups 10htest routing-instances VPN-Y vrf-export VPN-Y-Export

#set groups 10H-test policy-options community VPN-Y members target:8866:1240
#set groups 10H-test routing-instances VPN-Y vrf-target import target:8866:1240
#set groups 10H-test routing-instances VPN-Y vrf-target export target:8866:1240

#set groups 10htest policy-options policy-statement VPN-Y-Export term Export-Static then community add VPN-Y
#set groups 10htest policy-options policy-statement VPN-Y-Export term Export-Static then accept

#set groups 10htest policy-options community VPN-Y members target:8866:1240
#set groups 10htest routing-instances VPN-Y vrf-export VPN-Y-Export
#set groups 10htest routing-instances VPN-Y vrf-target import target:8866:1240


# include all groups...
# ignore groups
# ignore specific groups
# include all targets
# ignore specific targets
# replace caller method if else with a static array

exports_imports_names_list = ["export", "import"]
exports_imports_extended_list = [" export ", " import ", " "]
OTHER_TARGET = "other"
POLICY_STATEMENTS_STR = "policy_statements"
DISPLAY_NAME = "display_name"
CONF = "conf"
IS_RECEIVER = "IS_RECEIVER"
SELF_DEFINED = "SELF_DEFINED"
APPLIED_BY_GROUP = "APPLIED_BY_GROUP"
CAN_AUTO_EXPORT = "CAN_AUTO_EXPORT"
IS_LOGICAL_SYSTEMS_DEVICE = "LOGICAL-SYSTEMS"
IGNORE_THIS_VRF = "IGNORE_THIS_VRF"
DEVICE_NAME = "DEVICE_NAME"
DEFAULT_DEVICE_NAME = "DEFAULT_DEVICE_NAME"
CONF_GROUPS = "CONF_GROUPS"
APPLIED = "APPLIED"
PARTIAL_LEAK = "PartialLeak"
LEAK = "Leak"

SEPARATION_LINE = 60*"="
SUB_SEPARATION_LINE = 60*"_"

SAFETY = "safety"
SAFE_STR = "safe"
FILE_NAME_STR = "file_name"
UNTRUSTED_STR = "untrusted"
DEFINED_IN_GROUPS = "DEFINED_IN_GROUPS"

html_rows = []
output_lines = []
senders = {}
receivers = {}
vrfs_safety = {
    "Voice": {
        SAFETY: {
            SAFE_STR: False
        }
    },
    "isravpntst_Sharon": {
        SAFETY: {
            SAFE_STR: True
        }
    },
    "internet": {
        SAFETY: {
            SAFE_STR: True
        }
    },
    "DDOS_PARTNER": {
        SAFETY: {
            SAFE_STR: False
        }
    },
    "extranet": {
        SAFETY: {
            SAFE_STR: True
        }
    },
    "gx": {
        SAFETY: {
            SAFE_STR: True
        }
    },
    "gi_temp": {
        SAFETY: {
            SAFE_STR: True
        }
    },
    "mcdonalds-01-vlan100": {
        SAFETY: {
            SAFE_STR: True
        }
    },
    "ydtk": {
        SAFETY: {
            SAFE_STR: True
        }
    },
    "boxit": {
        SAFETY: {
            SAFE_STR: False
        }
    }
}

all_vrfs_are_required = True
include_partial_vrf_names = True
required_vrf_names = ["ip2", "ip1", "extranet", "data", "Voice", "internet"]
required_vrf_names = ["extranet", "boxit"]

# This is for partial search
required_vrf_names_str = str.join(",", required_vrf_names)

vrfs = {}
vrfs_unique_names = {}
conf_groups_list = {}
exports_list = {}
imports_list = {}
logical_system_devices_list = {}

ERROR_LEVEL = "ERROR_LEVEL"
DEBUG = "DEBUG"
INFO = "INFO"

SYSTEM_OUTPUT_LEVEL = INFO


def output_text(msg, required_output_level=DEBUG):
    if required_output_level == ERROR_LEVEL or SYSTEM_OUTPUT_LEVEL == DEBUG:
        print msg
        output_lines.append(msg)
    elif required_output_level == INFO:
        print msg
        output_lines.append(msg)


def end_of_vrf():
    inside_vrf = False
    current_vrf_name = None


def file_reader(file_name):
    #print "Reading {0}...".format(file_name)
    with open("{}".format(file_name)) as f:
        all_lines = f.read().splitlines()
    #print "End of reading {0}".format(file_name)
    return all_lines


def init_current_vrf_safety(vrf_display_name, vrf_unique_name):

    if vrf_unique_name not in vrfs_safety:
        vrfs_safety[vrf_unique_name] = {}
        vrfs_safety[vrf_unique_name][SAFETY] = {}
        if vrf_display_name not in vrfs_safety:
            vrfs_safety[vrf_display_name] = {}
            vrfs_safety[vrf_display_name][SAFETY] = {}
            vrfs_safety[vrf_display_name][SAFETY][SAFE_STR] = False
        vrfs_safety[vrf_unique_name][SAFETY][SAFE_STR] = vrfs_safety[vrf_display_name][SAFETY][SAFE_STR]
        vrfs[vrf_unique_name][SAFETY] = {}

    vrfs[vrf_unique_name][SAFETY][SAFE_STR] = vrfs_safety[vrf_unique_name][SAFETY][SAFE_STR]


def init_vrf(vrf_display_name, file_name, is_receiver, vrf_used_but_defined=False):

    vrf_unique_name = "{0}#{1}".format(file_name, vrf_display_name)

    if vrf_used_but_defined:
        output_text("XXXX VRF {0} is used but it's undefined !!! - Missing definition in {1}: ".
                    format(vrf_display_name, file_name), ERROR_LEVEL)

    if vrf_unique_name not in vrfs:
        vrfs[vrf_unique_name] = {}
        vrfs[vrf_unique_name][DISPLAY_NAME] = vrf_display_name
        vrfs[vrf_unique_name][DEVICE_NAME] = DEFAULT_DEVICE_NAME

        vrfs_unique_names[vrf_display_name] = vrf_unique_name

        vrfs[vrf_unique_name]["imports"] = {}
        vrfs[vrf_unique_name]["exports"] = {}
        vrfs[vrf_unique_name]["targets"] = {
            "imports": {},
            "exports": {}
        }

        vrfs[vrf_unique_name][CONF_GROUPS] = {}

        vrfs[vrf_unique_name][CONF] = {
            FILE_NAME_STR: file_name,
            SELF_DEFINED: True,
            APPLIED_BY_GROUP: False,
            # xxx take care of it: It's in the end of this file
            CAN_AUTO_EXPORT: False,
            IS_LOGICAL_SYSTEMS_DEVICE: False,
            IS_RECEIVER: is_receiver,
            IGNORE_THIS_VRF: vrf_used_but_defined
        }

        init_current_vrf_safety(vrf_display_name, vrf_unique_name)
    return vrf_unique_name


#TBD
def take_care_of_exports():
    # TBD for regular
    # TBD for logical-systems vrf-export export_name/id
    return True

#TBD
def take_care_of_imports():
    # TBD for regular
    # TBD for logical-systems vrf-import import_name/id
    return True


#TBD and take care of exports and imports
def find_group_community_members_targets(curr_line, file_name, is_receiver):


    # Look for
    # #set groups 10H-test policy-options community VPN-Y members target:8866:1240
    # The above is the same as
    # set policy-options policy-statement extranet-out3 then community add target:2424:3535
    # set policy-options policy-statement extranet-out3 then accept
    # set groups 10H-test routing-instances VPN-Y vrf-target import target:8866:1240
    # need to add accept by default in these cases
    # grep " VPN-Y " sender_26_06_2017.txt
    #grep -n "10htest" sender_26_06_2017.txt | grep -E " VPN-Y-Export |VPN-Y"
    #65:set groups 10htest policy-options policy-statement VPN-Y-Export term Export-Static from protocol static
    #66:set groups 10htest policy-options policy-statement VPN-Y-Export term Export-Static from route-filter 0.0.0.0/0 exact
    #67:set groups 10htest policy-options policy-statement VPN-Y-Export term Export-Static then community add VPN-Y
    #68:set groups 10htest policy-options policy-statement VPN-Y-Export term Export-Static then accept
    #69:set groups 10htest policy-options community VPN-Y members target:8866:1240
    #70:set groups 10htest routing-instances VPN-Y instance-type vrf
    #71:set groups 10htest routing-instances VPN-Y interface lo0.111
    #72:set groups 10htest routing-instances VPN-Y route-distinguisher 212.39.94.47:117
    #73:set groups 10htest routing-instances VPN-Y vrf-export VPN-Y-Export
    #74:set groups 10htest routing-instances VPN-Y vrf-target import target:8866:1240
    #75:set groups 10htest routing-instances VPN-Y vrf-table-label

    #set groups 10htest policy-options community VPN-Y members target:8866:1240
    found_group_targets = False
    curr_line_match = re.search(GROUPS_COMMUNITY_TARGETS_RE_RAW, curr_line)
    if curr_line_match:
        current_group_name = curr_line_match.group(2)
        community_name = curr_line_match.group(4)
        targets_names_str = curr_line_match.group(6)
        current_targets_names = str.split(targets_names_str, " ")
        for current_target_name in current_targets_names:
            output_text("{0}(group)->{1}(community)->{2}(target)".
                        format(current_group_name, community_name,
                               current_target_name))

        return True
    return False


def add_logical_device(vrf_unique_name, logical_system_device, file_name):
    vrfs[vrf_unique_name][CONF][IS_LOGICAL_SYSTEMS_DEVICE] = True
    device_unique_name = "{0}#{1}".format(file_name, logical_system_device)
    vrfs[vrf_unique_name][DEVICE_NAME] = device_unique_name
    if device_unique_name not in logical_system_devices_list:
        logical_system_devices_list[device_unique_name] = [vrf_unique_name]
    else:
        logical_system_devices_list[device_unique_name].append(vrf_unique_name)
    output_text("{1}(logical_system device)-> {0}(vrf)".
                format(vrf_unique_name, logical_system_device))


def add_group(current_vrf_unique_name, conf_groups_list_str, file_name):
    current_groups = str.split(conf_groups_list_str, " ")
    vrfs[current_vrf_unique_name][CONF][SELF_DEFINED] = False
    for current_group in current_groups:
        unique_base_conf_group = "{0}#{1}".format(file_name, current_group)
        vrfs[current_vrf_unique_name][CONF_GROUPS][unique_base_conf_group] = {
            APPLIED: False,
            "members": {},
            "exports": {},
            "imports": {},
            "targets": {
                "imports": {},
                "exports": {}
            }
        }

        output_text("group {2} :vrf name is {0} ({1})".format(vrfs[current_vrf_unique_name][DISPLAY_NAME],
                                                              current_vrf_unique_name, unique_base_conf_group))

        if unique_base_conf_group not in conf_groups_list:
            conf_groups_list[unique_base_conf_group] = \
                {
                    "vrfs": [current_vrf_unique_name],
                    APPLIED: False
                }
        else:
            conf_groups_list[unique_base_conf_group]["vrfs"].append(current_vrf_unique_name)


def found_an_applied_group(curr_line, file_name, is_receiver):

    found_applied_group = False
    curr_line_match = re.search(APPLY_GROUPS_RE, curr_line)
    if curr_line_match:
        if curr_line_match.lastindex == 2:
            found_applied_group = True
            current_groups_names_str = curr_line_match.group(2)
            current_groups_names = str.split(current_groups_names_str, " ")
            for base_applied_group_name in current_groups_names:
                applied_group_name = "{0}#{1}".format(file_name, base_applied_group_name)
                if applied_group_name in conf_groups_list:
                    curr_group = conf_groups_list[applied_group_name]
                    curr_group[APPLIED] = True
                    for unique_vrf_name in conf_groups_list[applied_group_name]["vrfs"]:
                        vrfs[unique_vrf_name][CONF_GROUPS][applied_group_name][APPLIED] = True
                        group_vrf = vrfs[unique_vrf_name][CONF_GROUPS][applied_group_name]
                        for export_or_import_str in exports_imports_names_list:
                            exports_or_imports_str = "{0}s".format(export_or_import_str)
                            for vrf_export_or_import_name, current_targets in group_vrf[exports_or_imports_str].iteritems():
                                if len(current_targets) > 0:
                                    for curr_target, curr_action in current_targets.iteritems():
                                        output_text("{0}(vrf)->{1}->{2}->targets->{3}:{4}".
                                                    format(unique_vrf_name, exports_or_imports_str,
                                                           vrf_export_or_import_name, curr_target,
                                                           curr_action))
                                        vrfs[unique_vrf_name][exports_or_imports_str][curr_target] = curr_action
                            for curr_target, curr_action in group_vrf["targets"][exports_or_imports_str].iteritems():
                                output_text("{0}(vrf)->targets->{1}-> {2}:{3}".
                                            format(unique_vrf_name, exports_or_imports_str,
                                                   curr_target, curr_action))
                                vrfs[unique_vrf_name]["targets"][exports_or_imports_str][curr_target] = curr_action
                        output_text("{0}(group) is applied in {1}(vrf)".format(applied_group_name, unique_vrf_name))
                    vrfs[unique_vrf_name][CONF][APPLIED_BY_GROUP] = True
                else:
                    output_text("Error!!! :Group {0} is applied but is undefined in '{1}'".
                                format(base_applied_group_name, file_name), ERROR_LEVEL)
                output_text(SUB_SEPARATION_LINE, INFO)

    return found_applied_group


def found_auto_export(curr_line, file_name, is_receiver):
    curr_line_match = re.search(AUTO_EXPORT_RE_RAW, curr_line)
    if curr_line_match:
        if curr_line_match.lastindex == 3:
            curr_vrf_base_name = curr_line_match.group(2)
            if is_vrf_required(curr_vrf_base_name):
                vrf_unique_name = "{0}#{1}".format(file_name, curr_vrf_base_name)
                vrfs[vrf_unique_name][CONF][CAN_AUTO_EXPORT] = True
    return False


def is_vrf_required(current_vrf_name):
    return all_vrfs_are_required or current_vrf_name in required_vrf_names or \
            (include_partial_vrf_names and current_vrf_name in required_vrf_names_str)


def validate_vrf(curr_line, curr_raw_re, file_name, last_re_index, group_re_index, is_receiver):
    curr_line_match = re.search(curr_raw_re, curr_line)
    if curr_line_match:
        if curr_line_match.lastindex == last_re_index:
            if curr_line_match.group(last_re_index) == "vrf":
                current_vrf_name = curr_line_match.group(group_re_index)
                if is_vrf_required(current_vrf_name):
                    vrf_unique_name = init_vrf(current_vrf_name, file_name, is_receiver)
                    output_text(SUB_SEPARATION_LINE)
                    output_text(SUB_SEPARATION_LINE)
                    if curr_raw_re == GROUPS_INSTANCE_TYPE_RE:
                        logical_system_device = None
                        base_conf_group = curr_line_match.group(2)
                        add_group(vrf_unique_name, base_conf_group, file_name)
                    elif curr_raw_re == INSTANCE_TYPE_RE:
                        base_conf_group = logical_system_device = None
                        output_text("vrf name is {0} ({1})".
                                    format(current_vrf_name, vrfs_unique_names[current_vrf_name]))
                    else:
                        logical_system_device = curr_line_match.group(2)
                        base_conf_group = None
                        add_logical_device(vrf_unique_name, logical_system_device, file_name)
                    return True, base_conf_group, logical_system_device
    return False, None, None


def found_vrf(curr_line, file_name, is_receiver):
    vrf_found, found_group_name, logical_system = validate_vrf(curr_line, INSTANCE_TYPE_RE, file_name, 4, 2, is_receiver)
    if vrf_found:
        return True

    vrf_found, found_group_name , logical_system = validate_vrf(curr_line, GROUPS_INSTANCE_TYPE_RE, file_name, 6, 4, is_receiver)
    if vrf_found:
        return True

    vrf_found, found_group_name, logical_system = validate_vrf(curr_line, LOGICAL_SYSTEMS_INSTANCE_TYPE_RE, file_name, 6, 4, is_receiver)
    return vrf_found


def found_import_or_export(curr_line, current_vrf_name, import_or_export):
    current_vrf = vrfs[current_vrf_name]
    current_vrf_display_name = current_vrf[DISPLAY_NAME]
    curr_re = IMPORT_EXPORT_RE_RAW.format(current_vrf_display_name, import_or_export)
    curr_line_match = re.search(curr_re, curr_line)
    if curr_line_match:
        if curr_line_match.lastindex == 2:
            curr_vrf_export_or_import_name = curr_line_match.group(2)
            output_text("{0}(vrf) {1} is {2}".
                        format(current_vrf_display_name, import_or_export, curr_vrf_export_or_import_name))
            curr_exports_or_imports = vrfs[current_vrf_name]["{0}s".format(import_or_export)]
            curr_target_or_policy_statements = "targets" if import_or_export == "export" else POLICY_STATEMENTS_STR
            curr_exports_or_imports[curr_vrf_export_or_import_name] = {}
            curr_exports_or_imports[curr_vrf_export_or_import_name][curr_target_or_policy_statements] = {}
            if import_or_export == "import":
                curr_exports_or_imports[curr_vrf_export_or_import_name][curr_target_or_policy_statements][OTHER_TARGET] = None
        return True
    return False


def look_for_group_targets_by_re(curr_line_match, curr_line, import_or_export_str,
                                 file_name, is_receiver, is_target=True):
    if curr_line_match:
        if curr_line_match.lastindex == 6:
            curr_group_name = curr_line_match.group(2)
            curr_vrf_name = curr_line_match.group(4)
            if not is_vrf_required(curr_vrf_name):
                return True

            curr_target_or_export_import_name = curr_line_match.group(6)
            if is_target:
                output_text("{0}(group)->{2}(vrf)->{3}->{1}(target)".
                        format(curr_group_name, curr_target_or_export_import_name,
                               curr_vrf_name, import_or_export_str))
            else:
                output_text("{0}(group)->{2}(vrf)->{3}->{1}".
                            format(curr_group_name, curr_target_or_export_import_name,
                                   curr_vrf_name, import_or_export_str))

            curr_unique_group_name = "{0}#{1}".format(file_name, curr_group_name)
            curr_unique_vrf_name = "{0}#{1}".format(file_name, curr_vrf_name)
            curr_group = vrfs[curr_unique_vrf_name][CONF_GROUPS][curr_unique_group_name]
            if import_or_export_str == "":
                if is_target:
                    curr_group["targets"]["exports"][curr_target_or_export_import_name] = "accept"
                    curr_group["targets"]["imports"][curr_target_or_export_import_name] = "accept"
            else:
                if is_target:
                    curr_group["targets"]["{}s".format(import_or_export_str)][curr_target_or_export_import_name] = "accept"
                else:
                    curr_group["{0}s".format(import_or_export_str)][curr_target_or_export_import_name] = {}
            return True
    return False


def look_for_group_targets(curr_line, file_name, is_receiver):

    for import_or_export_str in exports_imports_names_list:
        curr_line_match = re.search(GROUPS_VRF_TARGET_IMPORT_OR_EXPORT_RE_RAW.
                                    format(import_or_export_str), curr_line)
        if look_for_group_targets_by_re(curr_line_match, curr_line, import_or_export_str, file_name, is_receiver):
            return True
        else:
            curr_line_match = re.search(GROUPS_VRF_EXPORT_OR_IMPORT_RE_RAW.
                                        format(import_or_export_str), curr_line)
            if look_for_group_targets_by_re(curr_line_match, curr_line, import_or_export_str,
                                            file_name, is_receiver, False):
                return True

    curr_line_match = re.search(GROUPS_VRF_TARGET_EXPORT_AND_IMPORT_RE_RAW, curr_line)
    return look_for_group_targets_by_re(curr_line_match, curr_line, "", file_name, is_receiver)


def look_for_vrf_targets(curr_line, file_name, is_receiver):
    #set routing-instances yyy vrf-target import/export target:65535:2071
    #set routing-instances xxx vrf-target target:12400:1026
    for import_or_export_str in exports_imports_extended_list:
        curr_line_match = re.search(VRF_TARGET_EXPORT_AND_IMPORT_RE_RAW.
                                    format(import_or_export_str), curr_line)
        if curr_line_match:
            if curr_line_match.lastindex == 4:
                curr_vrf_name = curr_line_match.group(2)
                if not is_vrf_required(curr_vrf_name):
                    return True
                curr_unique_vrf_name = "{0}#{1}".format(file_name, curr_vrf_name)
                curr_target_name = curr_line_match.group(4)
                if curr_unique_vrf_name not in vrfs:
                    init_vrf(curr_vrf_name, file_name, is_receiver, True)

                curr_vrf_targets = vrfs[curr_unique_vrf_name]["targets"]
                if import_or_export_str == " ":
                    for curr_import_or_export_str in exports_imports_names_list:
                        output_text("{0}(vrf)->{2}->{1}(target)".
                                    format(curr_vrf_name, curr_target_name,
                                           curr_import_or_export_str.strip()))
                        curr_vrf_targets["{0}s".
                            format(curr_import_or_export_str.strip())][curr_target_name] = "accept"
                else:
                    output_text("{0}(vrf)->{2}->{1}(target)".
                                format(curr_vrf_name, curr_target_name,
                                       import_or_export_str.strip()))
                    curr_vrf_targets["{0}s".
                        format(import_or_export_str.strip())][curr_target_name] = "accept"
                return True
    return False


def look_for_logical_vrf_targets(curr_line, file_name):
    #set logical-systems r1-ran-agg-lab routing-instances oam vrf-target import/export target:8000:8000
    #set logical-systems r1-ran-agg-lab routing-instances oam vrf-target target:2321:8776
    # (set logical-systems\s)(.*)(\srouting-instances\s)(.*)(\svrf-target{0}target:)(.*)$
    # (set logical-systems\s)(.*)(\srouting-instances\s)(.*)(\svrf-{0} target:)(.*)$
    for curr_raw_re in LOGICAL_SYSTEM_TARGETS_RE_LIST:
        for import_or_export_str in exports_imports_extended_list:
            if import_or_export_str == " " and curr_raw_re == LOGICAL_SYSTEMS_VRF_EXPORT_IMPORT_RE_RAW:
                break

            curr_line_match = re.search(curr_raw_re.format(import_or_export_str), curr_line)
            if curr_line_match:
                if curr_line_match.lastindex == 6:
                    # curr_device_name = curr_line_match.group(2)
                    curr_vrf_name = curr_line_match.group(4)
                    curr_unique_vrf_name = "{0}#{1}".format(file_name, curr_vrf_name)
                    curr_target_name = curr_line_match.group(6)
                    curr_vrf_targets = vrfs[curr_unique_vrf_name]["targets"]
                    if import_or_export_str == " ":
                        for curr_import_or_export_str in exports_imports_names_list:
                            output_text("{0}(vrf)->{2}->{1}(target)".
                                        format(curr_vrf_name, curr_target_name,
                                               curr_import_or_export_str.strip()))
                            curr_vrf_targets["{0}s".
                                format(curr_import_or_export_str.strip())][curr_target_name] = "accept"
                    else:
                        output_text("{0}(vrf)->{2}->{1}(target)".
                                    format(curr_vrf_name, curr_target_name,import_or_export_str.strip()))
                        curr_vrf_targets["{0}s".
                            format(import_or_export_str.strip())][curr_target_name] = "accept"
                    return True
    return False


def get_export_or_import_settings(caller_method, import_or_export):

    if "look_for_community" == caller_method:
        if import_or_export == "export":
            curr_raw_re = POLICY_STATEMENT_EXPORT_ADD_RAW_RE
            matching_index = 4
        else:
            curr_raw_re = POLICY_STATEMENT_IMPORT_FROM_COMMUNITY_RAW_RE
            matching_index = 6
    elif "look_for_statement_action" == caller_method:
        if import_or_export == "export":
            curr_raw_re = POLICY_STATEMENT_EXPORT_ACTION_RAW_RE
            matching_index = 4
        else:
            curr_raw_re = POLICY_STATEMENT_IMPORT_ACTION_RAW_RE
            matching_index = 6

    return curr_raw_re, matching_index


def look_for_community(curr_line, current_vrf_name, import_or_export):
    curr_target_or_policy_statements = "targets" if import_or_export == "export" else POLICY_STATEMENTS_STR
    curr_exports_or_imports = vrfs[current_vrf_name]["{0}s".format(import_or_export)]
    curr_raw_re, matching_index = get_export_or_import_settings(sys._getframe().f_code.co_name, import_or_export)

    for curr_export_or_import_name in curr_exports_or_imports.keys():
        curr_re = curr_raw_re.format(curr_export_or_import_name)
        curr_line_match = re.search(curr_re, curr_line)
        if curr_line_match:
            if curr_line_match.lastindex == matching_index:
                curr_target_name = curr_line_match.group(matching_index)
                output_text(SUB_SEPARATION_LINE)
                output_text("{0}(vrf)-> {2}({1})-> community target is: {3}".
                            format(current_vrf_name, import_or_export,
                                   curr_export_or_import_name, curr_target_name))
                curr_exports_or_imports = vrfs[current_vrf_name]["{0}s".format(import_or_export)]
                curr_export_or_import = curr_exports_or_imports[curr_export_or_import_name]
                curr_export_or_import[curr_target_or_policy_statements][curr_target_name] = None
                return True, curr_target_name

    return False, None


def look_for_statement_action(curr_line, current_vrf_name, import_or_export, curr_target_name):
    curr_target_or_policy_statements = "targets" if import_or_export == "export" else POLICY_STATEMENTS_STR
    curr_exports_or_imports = vrfs[current_vrf_name]["{0}s".format(import_or_export)]
    curr_raw_re, matching_index = get_export_or_import_settings(sys._getframe().f_code.co_name, import_or_export)
    for curr_export_or_import_name in curr_exports_or_imports.keys():
        curr_re = curr_raw_re.format(curr_export_or_import_name)
        curr_line_match = re.search(curr_re, curr_line)
        if curr_line_match:
            if curr_line_match.lastindex == matching_index:
                curr_vrf_target_action = curr_line_match.group(matching_index)
                curr_exports_or_imports = vrfs[current_vrf_name]["{0}s".format(import_or_export)]
                curr_export_or_import = curr_exports_or_imports[curr_export_or_import_name]
                if import_or_export == "import" and curr_line_match.group(4) == OTHER_TARGET:
                    output_text("{0}(vrf)-> {2}({1})-> {3}(target) action is:{4}".
                                format(current_vrf_name, import_or_export,
                                       curr_export_or_import_name, OTHER_TARGET,
                                       curr_vrf_target_action))
                    curr_export_or_import[curr_target_or_policy_statements][OTHER_TARGET] = curr_vrf_target_action
                else:
                    output_text("{0}(vrf)-> {2}({1})-> {3}(target) action is:{4}".
                                format(current_vrf_name, import_or_export, curr_export_or_import_name,
                                       curr_target_name, curr_vrf_target_action))
                    curr_export_or_import[curr_target_or_policy_statements][curr_target_name] = curr_vrf_target_action
                return True
    return False


def parse_conf(file_name, is_receiver):
    conf_lines = file_reader(file_name)
    total_lines = len(conf_lines)
    current_line_number = 0
    print "Parsing {0} lines of {1}...".format(total_lines, file_name)
    prev_target_name = None
    for curr_line in conf_lines:
        current_line_number += 1
        if not found_vrf(curr_line, file_name, is_receiver):
            found_a_match = False
            vrf_names = [current_vrf_name for current_vrf_name in vrfs.keys()
                          if vrfs[current_vrf_name][CONF][FILE_NAME_STR] == file_name]
            for current_vrf_name in vrf_names:
                if not found_a_match:
                    for import_or_export_str in exports_imports_names_list:
                        if found_import_or_export(curr_line, current_vrf_name, import_or_export_str):
                            found_a_match = True
                            break
                    if not found_a_match and prev_target_name is None:
                        for import_or_export_str in exports_imports_names_list:
                            found_a_match, prev_target_name = \
                                look_for_community(curr_line, current_vrf_name, import_or_export_str)
                            if found_a_match:
                                break
                    if not found_a_match:
                        #print "200 {0}".format(curr_line)
                        #print "210 {0}".format(prev_target_name)
                        for import_or_export_str in exports_imports_names_list:
                            curr_exports_or_imports_list = vrfs[current_vrf_name]["{0}s".format(import_or_export_str)]
                            #print len(curr_exports_or_imports_list)
                            curr_target_or_policy_statements_str = "targets" \
                                if import_or_export_str == "export" else POLICY_STATEMENTS_STR
                            for curr_export_or_import_name, curr_export_or_import in \
                                    curr_exports_or_imports_list.iteritems():
                                curr_target_or_policy_statements = \
                                    curr_export_or_import[curr_target_or_policy_statements_str]
                                for curr_target_or_policy_name in curr_target_or_policy_statements:
                                    if curr_target_or_policy_name != OTHER_TARGET:
                                        if prev_target_name is not None \
                                                and prev_target_name != curr_target_or_policy_name:
                                            curr_target_or_policy_name = prev_target_name

                                        if look_for_statement_action(curr_line, current_vrf_name,
                                                                     import_or_export_str, curr_target_or_policy_name):
                                            found_a_match = True
                                            prev_target_name = None
                                            break
            if not found_a_match:
                found_a_match = found_an_applied_group(curr_line, file_name, is_receiver)
            if not found_a_match:
                found_a_match = find_group_community_members_targets(curr_line, file_name, is_receiver)
            if not found_a_match:
                found_a_match = look_for_group_targets(curr_line, file_name, is_receiver)
            if not found_a_match:
                found_a_match = look_for_vrf_targets(curr_line, file_name, is_receiver)
            if not found_a_match:
                found_a_match = found_auto_export(curr_line, file_name, is_receiver)

    print "Parsed {0}".format(file_name)
    print "{0}".format(SEPARATION_LINE)


def get_target_parts(target):
    target_parts = target.split(":")
    return target_parts[0], target_parts[1]


def targets_match(export_target, import_target):
    if export_target == import_target:
        return True, False

    export_target_p1, export_target_p2 = get_target_parts(export_target)
    import_target_p1, import_target_p2 = get_target_parts(import_target)
    if export_target_p1 == import_target_p1:
        if "*" == export_target_p2 or "*" == import_target_p2:
            return True, True
    elif export_target_p2 == import_target_p2:
        if "*" == export_target_p1 or "*" == import_target_p1:
            return True, True

    if "*" == export_target_p1 and "*" == import_target_p2:
        return True, True

    if "*" == export_target_p2 and "*" == import_target_p1:
        return True, True

    return False, False


def set_export_target_verdict(curr_importing_vrf_name, curr_import_or_target_name, import_policy_statement_name,
                              import_target_action_value, curr_exporting_vrf_name, curr_export_target_name,
                              curr_export_target_action, curr_export_name=None):

    import_target_name = curr_import_or_target_name if import_policy_statement_name is None else import_policy_statement_name

    target_are_matched, partial_match = targets_match(curr_export_target_name, import_target_name)
    if target_are_matched:
        # filter by "accept"
        if curr_export_target_action == "accept":
            export_safe = vrfs_safety[curr_exporting_vrf_name][SAFETY][SAFE_STR]
            export_safe_str = SAFE_STR if export_safe else UNTRUSTED_STR
            import_safe = vrfs_safety[curr_importing_vrf_name][SAFETY][SAFE_STR]
            import_safe_str = SAFE_STR if import_safe else UNTRUSTED_STR

            if export_safe_str == UNTRUSTED_STR or import_safe_str == UNTRUSTED_STR:
                curr_log_level = ERROR_LEVEL
                output_text("  XXXX - The following is a leak !!!!:  - XXXX", curr_log_level)
                is_leak = True
            else:
                curr_log_level = SYSTEM_OUTPUT_LEVEL
                output_text("  The following is a valid traffic route", curr_log_level)
                is_leak = False

            curr_html_row = []

            curr_html_row.append(curr_exporting_vrf_name)
            curr_html_row.append(curr_export_target_name)

            curr_html_row.append(curr_importing_vrf_name)

            if is_leak:
                leak_or_valid_str = LEAK
                if partial_match:
                    leak_or_valid_class = PARTIAL_LEAK
                else:
                    leak_or_valid_class = LEAK
            else:
                leak_or_valid_str = "Valid"
                leak_or_valid_class = "Valid"


            curr_html_row.append(import_target_name)

            curr_html_row.append(
                    {
                      "type": leak_or_valid_str,
                      "class": leak_or_valid_class
                    }
            )

            if curr_export_name is None:
                output_text("  {0} ({3} vrf-export-> {1}(target)->{2}". \
                    format(curr_exporting_vrf_name, curr_export_target_name, curr_export_target_action,
                           export_safe_str), curr_log_level)

            else:
                output_text("  {0} ({3} vrf)-> {4}(export)-> {1}(target)->{2}".format(curr_exporting_vrf_name,
                    curr_export_target_name, curr_export_target_action,
                    export_safe_str, curr_export_name), curr_log_level)

            if import_policy_statement_name is None:
                output_text("  {0} ({3} vrf)-target (import)-> {1}(target)->{2}". \
                        format(curr_importing_vrf_name, import_target_name, import_target_action_value,
                               import_safe_str), curr_log_level)

            else:
                output_text("  {0} ({3} vrf)-> {4}(import)-> {1}(target)->{2}". \
                            format(curr_importing_vrf_name, import_target_name, import_target_action_value,
                                   import_safe_str, curr_import_or_target_name), curr_log_level)
            html_rows.append(curr_html_row)
            output_text(SUB_SEPARATION_LINE, curr_log_level)


def set_policy_statement_verdict(curr_export_targets, import_policy_statement_or_target_name, curr_exporting_vrf_name,
                                 curr_importing_vrf_name, import_target_action_value, curr_export_name,
                                 curr_import_name):

    for curr_export_target_name, curr_export_target_action in curr_export_targets.iteritems():
        set_export_target_verdict(curr_importing_vrf_name, curr_import_name, import_policy_statement_or_target_name,
                                  import_target_action_value, curr_exporting_vrf_name, curr_export_target_name,
                                  curr_export_target_action, curr_export_name)


def set_targets_exports_verdict(curr_target_exports, import_policy_statement_or_target_name, curr_exporting_vrf_name, curr_importing_vrf_name,
                                import_target_action_value, curr_import_or_target_name):

    for curr_export_target_name, curr_export_target_action in curr_target_exports.iteritems():
        set_export_target_verdict(curr_importing_vrf_name, curr_import_or_target_name, import_policy_statement_or_target_name,
                                  import_target_action_value, curr_exporting_vrf_name, curr_export_target_name,
                                  curr_export_target_action)


def compare_exports(curr_importing_vrf_name, import_policy_statement_name, curr_import_or_action_name,
        curr_import_or_target_name):
    for curr_exporting_vrf_name, curr_exporting_vrf in vrfs.iteritems():
        if curr_importing_vrf_name != curr_exporting_vrf_name:
            curr_conf = curr_exporting_vrf[CONF]
            if not curr_conf[IGNORE_THIS_VRF]:
                if not curr_conf[IS_RECEIVER]:
                    curr_vrf_exports = curr_exporting_vrf["exports"]
                    if len(curr_vrf_exports) > 0:
                        for curr_export_name, curr_export in curr_vrf_exports.iteritems():
                            if "targets" in curr_export:
                                curr_export_targets = curr_export["targets"]
                                set_policy_statement_verdict(curr_export_targets,
                                                             import_policy_statement_name, curr_exporting_vrf_name,
                                                             curr_importing_vrf_name, curr_import_or_action_name,
                                                             curr_export_name, curr_import_or_target_name)

                    curr_vrf_targets_exports = curr_exporting_vrf["targets"]["exports"]
                    if len(curr_vrf_targets_exports) > 0:
                        set_targets_exports_verdict(curr_vrf_targets_exports, import_policy_statement_name,
                                                    curr_exporting_vrf_name, curr_importing_vrf_name,
                                                    curr_import_or_action_name, curr_import_or_target_name)


def check_vrf_imports(curr_importing_vrf_name, curr_vrf_imports):
    if len(curr_vrf_imports) > 0:
        for curr_import_or_target_name, curr_import_or_action_name in curr_vrf_imports.iteritems():
            if POLICY_STATEMENTS_STR in curr_import_or_action_name:
                curr_policy_statements = curr_import_or_action_name[POLICY_STATEMENTS_STR]
                for import_policy_statement_name, import_action_value in curr_policy_statements.iteritems():
                    if import_action_value == "accept":
                        compare_exports(curr_importing_vrf_name, import_policy_statement_name, import_action_value,
                                        curr_import_or_target_name)

            else:
                import_policy_statement_name = None
                if curr_import_or_action_name == "accept":
                    compare_exports(curr_importing_vrf_name, import_policy_statement_name, curr_import_or_action_name,
                                    curr_import_or_target_name)


def check_imports(curr_vrf_name, curr_vrf):
    check_vrf_imports(curr_vrf_name, curr_vrf["imports"])
    check_vrf_imports(curr_vrf_name, curr_vrf["targets"]["imports"])


# Needed ?
def check_targets_imports_orig(curr_importing_vrf_name, curr_vrf):
    curr_vrf_targets_imports = curr_vrf["targets"]["imports"]
    if len(curr_vrf_targets_imports) > 0:
        for curr_target_name, curr_action in curr_vrf_targets_imports.iteritems():
            if curr_action == "accept":
                compare_exports(curr_importing_vrf_name, None, curr_action, curr_target_name)

    # XXX TBD Add here current_receiver


def generate_report():
    print "Leaks detection ..."
    # xxx filter out all the ones which have no imports
    for curr_vrf_name, curr_vrf in vrfs.iteritems():
        # iterate only over :
        #  1. Active vrfs (SELF_DEFINED equals True)
        #  2. vrfs defined by at least one applied group (APPLIED_BY_GROUP equals True)

        curr_conf = vrfs[curr_vrf_name][CONF]
        if not curr_conf[IGNORE_THIS_VRF]:
            vrf_is_receiver = curr_conf[IS_RECEIVER]
            if vrf_is_receiver:
                check_imports(curr_vrf_name, curr_vrf)
                #check_targets_imports(curr_vrf_name, curr_vrf)



def look_for_non_applied_groups():
    #output_text("In {0}".format(sys._getframe().f_code.co_name), INFO)

    for current_group_name in conf_groups_list:
        applied = conf_groups_list[current_group_name][APPLIED]
        if not applied:
            for unique_vrf_name in conf_groups_list[current_group_name]["vrfs"]:
                output_text("{0}(group)->{1}(vrf)->is defined but {0} is not applied".
                        format(current_group_name, unique_vrf_name))
    output_text(SEPARATION_LINE, INFO)


def create_pdf():
    pdfkit.from_string(string.join(output_lines, "<br />"), 'out.pdf')


def create_html():
    css_link = "<link rel=\"stylesheet\" type=\"text/css\" href=\"css/main.css\">"
    scripts = "<script src=\"scripts/utils.js\"></script>"
    header = '<!doctyle html><html><head><title>My Title</title>{0}</head>{1}<body>'.format(css_link, scripts)
    body = '<table><tr><th>Exporting VRF</th><th>Exporting Target</th><th>Importing VRF</th><th>Importing Target</th><th>Verdict</th><th>info</th></tr>'
    footer = '</table></body></html>'



    with open('output.html', 'w') as output:
        output.write(header)
        output.write(body)

        for idx, curr_html_row in enumerate(html_rows):
            curr_row_id = "row{0}".format(idx)
            output.write('<tr id="{0}">'.format(curr_row_id))

            leak_or_valid_str = curr_html_row[4]["type"]
            leak_or_valid_class = curr_html_row[4]["class"]
            exporting_vrf_target_class = ""
            importing_vrf_target_class = ""

            export_vrf_unique_name = curr_html_row[0]
            export_vrf_base_source = export_vrf_unique_name.split("#")[0]
            export_vrf_base_unique_name = export_vrf_unique_name.split("#")[1]
            export_vrf_display_name = vrfs[export_vrf_unique_name][DISPLAY_NAME]
            export_safe = vrfs_safety[export_vrf_display_name][SAFETY][SAFE_STR]
            if export_safe:
                export_safe_str, export_safe_class = SAFE_STR, "Valid"
            else:
                export_safe_str, export_safe_class = UNTRUSTED_STR, "Leak"

            export_safety_span = "<span class=\"{0}\">({1})</span>".format(export_safe_class, export_safe_str)
            output.write('<td title=\"{2}\">{0}{1}</td>'
                         .format(export_vrf_base_unique_name, export_safety_span, export_vrf_unique_name))
            export_vrf_exports = len(vrfs[export_vrf_unique_name]["exports"])
            export_vrf_export_targets = len(vrfs[export_vrf_unique_name]["targets"]["exports"])

            curr_exporting_target = curr_html_row[1]
            if "*" in curr_exporting_target:
                if leak_or_valid_class == PARTIAL_LEAK:
                    exporting_vrf_target_class = " class=\"{0}\" ".format(PARTIAL_LEAK)

            output.write('<td{1}>{0}</td>'.format(curr_exporting_target,  exporting_vrf_target_class))

            import_vrf_unique_name = curr_html_row[2]
            import_vrf_base_source = import_vrf_unique_name.split("#")[0]
            import_vrf_base_unique_name = export_vrf_unique_name.split("#")[1]
            import_vrf_display_name = vrfs[import_vrf_unique_name][DISPLAY_NAME]
            import_safe = vrfs_safety[import_vrf_display_name][SAFETY][SAFE_STR]
            if import_safe:
                import_safe_str, import_safe_class = SAFE_STR, "Valid"
            else:
                import_safe_str, import_safe_class = UNTRUSTED_STR, "Leak"

            import_safety_span = "<span class=\"{0}\">({1})</span>".format(import_safe_class, import_safe_str)
            output.write('<td title=\"{2}\">{0}{1}</td>'.
                         format(import_vrf_base_unique_name, import_safety_span, import_vrf_unique_name))

            curr_importing_target = curr_html_row[3]
            if "*" in curr_importing_target:
                if leak_or_valid_class == PARTIAL_LEAK:
                    importing_vrf_target_class = " class=\"{0}\" ".format(PARTIAL_LEAK)
            output.write('<td{1}>{0}</td>'.format(curr_importing_target,  importing_vrf_target_class))

            output.write("<td><span class=\"{0}\">{1}</span></td>".format(leak_or_valid_class, leak_or_valid_str))

            import_vrf_imports = len(vrfs[import_vrf_unique_name]["imports"])
            import_vrf_import_targets = len(vrfs[import_vrf_unique_name]["targets"]["imports"])

            extra_info = "<ul>"
            extra_info = "<li> {0}(vrf) has {1} exports and {2} target exports </li>".\
                format(export_vrf_unique_name, export_vrf_exports, export_vrf_export_targets)
            extra_info += "<li> {0}(vrf) has {1} imports and {2} target imports </li>".\
                format(import_vrf_unique_name, import_vrf_imports, import_vrf_import_targets)
            extra_info += '<li> <button onclick="alert(\'Exporting target ({0}) is now disabled\');">Disable export target ({0})</button> | <button onclick="alert(\'Importing target ({1}) is now disabled\');">Disable import target ({1})</button></li>'.format(curr_exporting_target, curr_importing_target)
            extra_info += "</ul>"

            curr_row_info_id = "{0}_info".format(curr_row_id)
            curr_row_button_id = "btn_{0}".format(curr_row_info_id)


            output.write('<td><button id="{0}" onclick="toggle_class(\'{1}\',\'hidden_table_row\',\'displayed_table_row\');toggle_innerhtml(\'{0}\',\'{2}\',\'{3}\');">'
             '{2}</button></td>'.format(curr_row_button_id, curr_row_info_id, "More info", "Hide info&nbsp;"))
            output.write('</tr>')

            output.write('<tr id="{0}" class="hidden_table_row"><td colspan="6">{1}</td></tr>'.format(curr_row_info_id, extra_info))
        output.write(footer)


def main(args):

    x = 2

    if x == 1:
        parse_conf("sender_26_06_2017.txt", False)
        parse_conf("receiver_26_06_2017.txt", True)
    else:
        parse_conf("sender", False)
        parse_conf("receiver", True)
    look_for_non_applied_groups()
    generate_report()
    #create_pdf()
    create_html()


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))


#set routing-instances dp instance-type vrf
#set routing-instances dp route-distinguisher 65535:34532
    # import and export is ""
#set routing-instances dp vrf-target target:65535:34600
#set routing-instances dp vrf-table-label
    # this device can be a sender and a receiver in the same device
#set routing-instances dp routing-options auto-export


# 12_PE is s device
# set logical-systems 012_PE routing-instances TEST_VRF instance-type vrf

#x:012_PE vrf:aaa
#x:012_PE vrf:bbb  auto_export only beteen two vrfs in the same device
#x:root  vrf:bbb

# two vrfs in the same device:
#x:012_PE vrf:aaa
#x:root  vrf:bbb


# the following means both export and import. Right ?
#set routing-instances dp vrf-target target:65535:34600


#The following means that vrf XXX has both export and import of target 111:222.  - Right ?
#set routing-instances XXX vrf-target target:111:222

# Add this ... vrf-export
#set groups 10htest routing-instances VPN-Y vrf-export VPN-Y-Export