#!/usr/bin/env python
# License: Apache version 2
# (c) 2017 MyungJoo Ham <myungjoo.ham@samsung.com>
#
# Building Block Rule Checker
#
# This does not check all rules of "RULES".
# The level of subblocks is limited to 3.


from __future__ import print_function
import re
import os
import sys
import collections

verbose = 0


def print_v(*args):
    global verbose
    if verbose:
        print(*args)

Block = collections.namedtuple(
    'Block', 'name level parent children description files')
blocks = {}
referedblock = []


def report(file, lc, code):
    print(file + ":Line " + str(lc) + " |" + code)
    return 0


def ruleCheckInterBlock():
    global blocks
    global referedblock

    error = 0
    warning = 0
    root_suggested = {}
    file = "packaging/building-blocks.spec"

    try:
        f = open(file)
    except:
        error += 1
        print("ERROR: cannot find packaging/building-blocks.spec")
        return (1, 0)
    for line in f:
        if re.search(r'^\s*Suggests:\s*%{name}-root-[a-zA-Z0-9_]', line):
            n = re.sub(r'^\s*Suggests:\s*%{name}-root-', r'', line)
            n = re.sub(r'\s*', r'', n)
            n = re.sub(r'\n', r'', n)
            root_suggested[n] = 1
    f.close()

    for n in blocks:
        # Orphan check
        if blocks[n].level == 0:
            if n not in root_suggested:
                error += 1
                print(
                    "ERROR: Orphaned root block. Add Suggests: %{name}-root-" + n + " at building-blocks.spec or in its categories.")
        else:  # subX
            p = blocks[n].parent
            if p not in blocks:
                error += 1
                print("ERROR: Orphaned sub block. The block " +
                      n + " requires a parent block " + p + ".")
            else:
                found = 0
                # check if p has n as its child
                for c in blocks[p].children:
                    if c == n:
                        found = 1
                        break
                if found == 0:
                    error += 1
                    print("ERROR: Orphaned sub block. The block " + n +
                          " is not registered at the parent block " + p + " although " + p + " exists.")
        # TODO: Add more rules here?

    # Check if Required/Suggested blocks exist in this repo
    for refered in referedblock:
        if refered not in blocks:
            error += 1
            print("ERROR: A nonexisting block '" + refered + "' is refered.")

    return (error, warning)


def ruleCheckInc(file):
    global blocks
    global referedblock

    print_v("Checking " + file)

    error = 0
    warning = 0
    lc = 0

    files = 0  # Start checking if %files section have files (error if exists)
    lastpkg = ''
    descpkg = ''
    uipkg_checking = 0  # 1 if we are in a context of uipkg (after %package, before %description/%files/...)
    description = 0  # 1 if it is next line of description

    try:
        f = open("packaging/" + file, 'r')
    except:
        warning += 1
        print("WARNING: cannot find packaging/" + file)
        return (0, 1)
    for line in f:
        lc += 1

        # RULE 5.7
        if description == 1:
            description = 0
            if re.search(r'^__KS_URL__', line):
                if not re.search(r'Preset_boards-', descpkg) and not re.search(r'Preset_sd-', descpkg):
                    error += 1
                    print("ERROR: Rule 5.7.1. The package: " + descpkg)
                    report(file, lc, line)
                    continue
        if re.search(r'^\s*%description', line):
            description = 1

        if (files == 1):
            if re.search(r'^\s*(%package)|(%build)|(%description)|(%prep)|(%clean)|(%install)|(%post)|(%pre)', line):
                files = 0
                uipkg_checking = 0
            else:
                if re.search(r'^\s*[^#\s]+', line) and \
                   not re.search(r'^\s*(%include)|(%endif)|(%ifarch)|(%list_require)', line):
                    error += 1
                    print(
                        "ERROR: RULE 5.3 a block must not have a file included (%files section must be empty)")
                    report(file, lc, line)
                    continue

        if re.search(r'^\s*((Suggests)|(Requires))', line, re.IGNORECASE):
            # RULE 5.5
            if uipkg_checking == 1:
                error += 1
                print(
                    "ERROR: RULE 5.5 a UI block cannot have relation with others.")
                report(file, lc, line)
                continue

            if not re.search(r'^\s*((Suggests)|(Requires)):', line):
                error += 1
                print(
                    "ERROR: Use case sensitive put : directly after the keyword")
                report(file, lc, line)
                continue

            if len(lastpkg) < 1:
                error += 1
                print(
                    "ERROR: You should add Suggests:/Requires: after %package before other sections")
                report(file, lc, line)
                continue
            else:
                # If it's just a package, skip checking.
                cname = re.sub(
                    r'^\s*((Suggests)|(Requires)):\s*%{name}-', r'', line)
                if cname == line:
                    continue
                c = re.sub(
                    r'^\s*((Suggests)|(Requires)):\s*%{name}-sub[123]-', r'', line)
                c = re.sub(r'\s*', r'', c)
                c = re.sub(r'\n', r'', c)

                # RULE 5.4
                #if n[:6] != "Preset" and n[:7] != "feature":
                #    level = blocks[n].level
                #    clevel = 0
                #    if cname[:4] == 'root':
                #        clevel = 0
                #    elif cname[:4] == 'sub1':
                #        clevel = 1
                #    elif cname[:4] == 'sub2':
                #        clevel = 2
                #    elif cname[:4] == 'sub3':
                #        clevel = 3
                #    if (clevel - 1) != level:
                #        error += 1
                #        print(
                #            "ERROR: RULE 5.4. Non Preset/feature block cannot have non-direct child block as its dependents (Requires/Suggests). Level Mismatch")
                #        report(file, lc, line)
                #        continue
                #    if c[:len(n)] != n:
                #        error += 1
                #        print(
                #            "ERROR: RULE 5.4. Non Preset/feature block cannot have non-direct child block as its dependents (Requires/Suggests). Child from another hierarchy.")
                #        report(file, lc, line)
                #        continue

                referedblock.append(cname[5:].strip())

                cs = blocks[n].children
                cs.append(c)
                blocks[n]._replace(children=cs)
                print_v("Children added to " + n + " of " + c)

        # RULE 5.1
        if re.search(r'^\s*BuildRequires', line, re.IGNORECASE):
            error += 1
            print("ERROR: RULE 5.1 .inc file cannot have BuildRequires tags")
            report(file, lc, line)
            continue

        # Prevent: https://github.com/rpm-software-management/rpm/issues/158
        if re.search(r'^#.*[^%]%[^%]', line) and not re.search('^#!', line):
            error += 1
            print(
                "ERROR: unless it is shebang, you must not have rpm macro in a # comment. They are expanded and multiline macro will do unexpected effects.")
            report(file, lc, line)
            continue

        # RULE 5.2
        if re.search(r'^\s*Recommends', line, re.IGNORECASE) or	\
            re.search(r'^\s*Provides', line, re.IGNORECASE) or	\
            re.search(r'^\s*Enhances', line, re.IGNORECASE) or	\
                re.search(r'^\s*Supplements', line, re.IGNORECASE):
            error += 1
            print(
                "ERROR: RULE 5.2 .inc file cannot have unsupported relations")
            report(file, lc, line)
            continue

        # RULE 1-1
        if re.search(r'^\s*%package\s*-n', line, re.IGNORECASE):
            error += 1
            print(
                "ERROR: RULE 1.1 to ensure 1.1, do not use -n option in package name")
            report(file, lc, line)
            continue

        # Implicit / General Rule
        if re.search(r'^\s*%package\s', line, re.IGNORECASE) and	\
                not re.search(r'^\s*%package\s', line):
            error += 1
            print(
                'ERROR: (General) Please use %package, not ' + re.search('^%package'))
            report(file, lc, line)
            continue

        # RULE 1-3 / 1-4
        if re.search(r'^\s*%package', line) and	\
                not re.search(r'^\s*%package\s*((root)|(sub1)|(sub2))-', line):

            if re.search(r'^\s*%package\s*sub3-', line):
                warning += 1
                print(
                    "WARNING: RULE 1-3-A. Try not to use sub3 level subblocks")
                report(file, lc, fline)
            else:
                error += 1
                print(
                    "ERROR: RULE 1.3 the send prefix should be root, sub1, sub2, or sub3.")
                report(file, lc, line)
                continue
            if re.search(r'^.*__UI__..$', line):
                uipkg_checking = 1

        # RULE 1-9 for root block (1-5)
        if re.search(r'^\s*%package\s*root', line) and	\
                not re.search(r'^\s*%package\s*root-[a-zA-Z0-9_]+\s*$', line):
            error += 1
            print("ERROR: RULE 1.9 not met with root (RULE 1.5)")
            report(file, lc, line)
            continue

        # RULE 1-9 for sub1 block (1-6)
        if re.search(r'^\s*%package\s*sub1', line) and	\
                not re.search(r'^\s*%package\s*sub1-[a-zA-Z0-9_]+-[a-zA-Z0-9_]+\s*$', line):
            error += 1
            print("ERROR: RULE 1.9 not met with sub1 (RULE 1.6)")
            report(file, lc, line)
            continue

        # RULE 1-9 for sub2 block (1-7)
        if re.search(r'^\s*%package\s*sub2', line) and	\
                not re.search(r'^\s*%package\s*sub2-[a-zA-Z0-9_]+-[a-zA-Z0-9_]+-[a-zA-Z0-9_]+\s*$', line):
            error += 1
            print("ERROR: RULE 1.9 not met with sub2 (RULE 1.7)")
            report(file, lc, line)
            continue

        # RULE 1-9 for sub3 block (1-7)
        if re.search(r'^\s*%package\s*sub3', line) and	\
                not re.search(r'^\s*%package\s*sub3-[a-zA-Z0-9_]+-[a-zA-Z0-9_]+-[a-zA-Z0-9_]+-[a-zA-Z0-9_]+\s*$', line):
            error += 1
            print("ERROR: RULE 1.9 not met with sub3 (RULE 1.7)")
            report(file, lc, line)
            continue

        # Adding a new package. Register to the data structure for
        # context-aware check
        if re.search(r'^\s*%package\s*((root)|(sub1)|(sub2)|(sub3))-', line):
            # remove tag & prefixes
            n = re.sub(
                r'^\s*%package\s*((root)|(sub1)|(sub2)|(sub3))-', r'', line)
            # remove tailing whitespaces
            n = re.sub(r'\s*', r'', n)
            # remove trailing \n
            n = re.sub(r'\n', r'', n)

            if len(n) > 0:
                l = 0
                p = ''

                if re.search(r'^\s*%package\s*root-', line):
                    l = 0
                    p = ''
                elif re.search(r'^\s*%package\s*sub1-', line):
                    l = 1
                    p = re.sub(r'^([a-zA-Z0-9_]+)-.*', r'\1', n)
                elif re.search(r'^\s*%package\s*sub2-', line):
                    l = 2
                    p = re.sub(r'^([a-zA-Z0-9_]+-[a-zA-Z0-9_]+)-.*', r'\1', n)
                elif re.search(r'^\s*%package\s*sub3-', line):
                    l = 3
                    p = re.sub(
                        r'^([a-zA-Z0-9_]+-[a-zA-Z0-9_]+-[a-zA-Z0-9_]+)-.*', r'\1', n)
                p = re.sub(r'\n', r'', p)  # remove trailing \n

                print_v(
                    "Block: " + n + ", level = " + str(l) + ", parent = [" + p + "]")
                lastpkg = n

                newBlock = Block(
                    name=n, level=l, parent=p, children=[], description=0, files=0)
                blocks[n] = newBlock
            else:
                error += 1
                print("ERROR: Package name too short")
                report(file, lc, line)
                continue

        # Check for %description entry
        if re.search(r'^\s*%description\s+', line):
            descpkg = lastpkg
            lastpkg = ''

            # remove tag
            n = re.sub(r'^\s*%description\s+', r'', line)
            # prefixes
            n = re.sub(r'^((root)|(sub1)|(sub2))-', r'', n)
            # remove trailing whitespaces / \n
            n = re.sub(r'\s*', r'', n)
            n = re.sub(r'\n', r'', n)

            if n in blocks:
                if blocks[n].description == 1:
                    error += 1
                    print("ERROR: (General) duplicated %description")
                    report(file, lc, line)
                    continue
                else:
                    blocks[n]._replace(description=1)
            else:
                error += 1
                print(
                    "ERROR: (General) %description appears before %package or in another file")
                report(file, lc, line)
                continue

        # Check for %files entry
        if re.search(r'^\s*%files\s+', line):
            files = 1
            lastpkg = ''

            # remove tag
            n = re.sub(r'^\s*%files\s+', r'', line)
            # prefixes
            n = re.sub(r'^((root)|(sub1)|(sub2)|(sub3))-', r'', n)
            # remove trailing whitespaces / \n
            n = re.sub(r'\s*', r'', n)
            n = re.sub(r'\n', r'', n)

            if n in blocks:
                if blocks[n].files == 1:
                    error += 1
                    print("ERROR: (General) duplicated %files")
                    report(file, lc, line)
                    continue
                else:
                    blocks[n]._replace(files=1)
            else:
                error += 1
                print(
                    "ERROR: (General) %files appears before %package or in another file")
                report(file, lc, line)
                continue

        # Check for not allowed sections
        if re.search(r'^\s*(%post(?!trans))|(%pre)|(%build)|(%clean)|(%install)', line):
            error += 1
            print(
                "ERROR: It is not allowed to add such sections in each domain.")
            report(file, lc, line)
            continue

    f.close()

    return (error, warning)


def main():
    global blocks, verbose

    if len(sys.argv) > 1:
        count = 0
        for option in sys.argv:
            count += 1
            if (count == 1):
                continue
            if option == '-v':
                verbose = 1

    dirs = os.listdir("packaging/")
    error = 0
    warning = 0

    # iterate in the list of ./packaging/
    for file in dirs:
        if re.search(r'\.inc', file):
            result = ruleCheckInc(file)
            error += result[0]
            warning += result[1]
        elif re.search(r'^\..*\.sw.', file):
            # skip if it is vi swap file
            print_v(
                "There is a garbage in packaging. But let's skip (next version should check git status")
        elif not file == 'building-blocks.spec':
            print(
                "ERROR: Please do not put garbage files in packaging/ directory: " + file)
            error += 1

    result = ruleCheckInterBlock()
    error += result[0]
    warning += result[1]

    print('Error: ' + str(error))
    print('Warning: ' + str(warning))

    return error

retval = main()
sys.exit(retval)
