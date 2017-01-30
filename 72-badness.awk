#!/usr/bin/awk -f
BEGIN {
    FS  = "\t";
    OFS = "\t";
}
NR==1 {
    $4 = $4 OFS "badness";
    print $0;
}
NR > 1 {
    badness = 0.0;
    if (($2 > 0) || ($4 > 0)) badness = 2 * $2 * $4 / ($2 + $4);
    $4 = $4 OFS badness;
    print $0 | "sort -t \"\t\" -k5n -k4n -k2n -k9nr -k1n";
}
