#!/usr/bin/awk -f
# echo -e 'a\tb\t15\na\tb\t3\na\tc\t10' | ./23-prune.awk
BEGIN {
    FS  = "\t";
    OFS = "\t";
}
$3 >= T {
    if (E == "count") {
        print $1, $2, $3;
        print $2, $1, $3;
    } else if (E == "log") {
        weight = log($3);
        print $1, $2, weight;
        print $2, $1, weight;
    } else {
        print "Unknown weighting parameter set, exiting." > "/dev/stderr";
        exit 1;
    }
}
