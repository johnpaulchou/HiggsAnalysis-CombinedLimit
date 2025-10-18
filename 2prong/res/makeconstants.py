#!/bin/env python3

import files
import argparse

if __name__ == "__main__":
    # setup and use the parser
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--sigtype",help="signal type that we're using",choices=files.sigtypes, default=files.sigtypes[0])
    parser.add_argument("--region",help="region that we're working in",choices=files.regions, default=files.regions[0])
    args=parser.parse_args()

    TOTAL_BINS = files.get_num_m2pbins(args.region, args.sigtype)

    string0 = ""
    params = ['p3', 'p4', 'p5', 'p6']
    bins = []
    for n in range(0, TOTAL_BINS):
        bins.append("bin"+str(n))
    for param in params:
        for binn in bins:
            for loc in ['barrel', 'endcap']:
                string0 += param + '_' + binn + loc + ','
    string0 = string0[:-1]

    string1 = ""
    params = ['p1', 'p2', 'p5', 'p6']
    bins = []
    for n in range(0, TOTAL_BINS):
        bins.append("bin"+str(n))
    for param in params:
        for binn in bins:
            for loc in ['barrel', 'endcap']:
                string1 += param + '_' + binn + loc + ','
    string1 = string1[:-1]

    string2 = ""
    params = ['p1', 'p2', 'p3', 'p4']
    bins = []
    for n in range(0, TOTAL_BINS):
        bins.append("bin"+str(n))
    for param in params:
        for binn in bins:
            for loc in ['barrel', 'endcap']:
                string2 += param + '_' + binn + loc + ','
    string2 = string2[:-1]


    fixstring0 = ""
    for n in range(0, TOTAL_BINS):
        for loc in ['barrel', 'endcap']:
            fixstring0 += 'pdfindex_bin' + str(n) + loc + '=0,'
    fixstring0 = fixstring0[:-1]

    fixstring1 = ""
    for n in range(0, TOTAL_BINS):
        for loc in ['barrel', 'endcap']:
            fixstring1 += 'pdfindex_bin' + str(n) + loc + '=1,'
    fixstring1 = fixstring1[:-1]

    fixstring2 = ""
    for n in range(0, TOTAL_BINS):
        for loc in ['barrel', 'endcap']:
            fixstring2 += 'pdfindex_bin' + str(n) + loc + '=2,'
    fixstring2 = fixstring2[:-1]

    liststring = ""
    for n in range(0, TOTAL_BINS):
        for loc in ['barrel', 'endcap']:
            liststring += 'pdfindex_bin' + str(n) + loc + ','
    liststring = liststring[:-1]

    with open("constants.sh", "w") as f:
        f.write('fix0="{}"\n\n'.format(fixstring0))
        f.write('fix1="{}"\n\n'.format(fixstring1))
        f.write('fix2="{}"\n\n'.format(fixstring2))

        f.write('list_params="{}"\n\n'.format(liststring))

        f.write('freezeparams0="{}"\n\n'.format(string0))
        f.write('freezeparams1="{}"\n\n'.format(string1))
        f.write('freezeparams2="{}"\n\n'.format(string2))
