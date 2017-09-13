#!/usr/bin/awk -f
BEGIN {
    FS  = "\t";
    OFS = "\t";
    # the C parameter might be passed as ./aggregate.awk -v C=0.000001
}
NR==1 {
    for (i=1; i<=NF; i++) ix[$i] = i;
}
NR > 1 && $ix["coverage"] >= C {
    p_score     += $ix["pscore"];
    p_scoresq   += $ix["pscore"] ^ 2;

    h_score     += $ix["hscore"];
    h_scoresq   += $ix["hscore"] ^ 2;

    hp_score    += $ix["hpscore"];
    hp_scoresq  += $ix["hpscore"] ^ 2;

    hpc_score   += $ix["hpcscore"];
    hpc_scoresq += $ix["hpcscore"] ^ 2;

    N++;
}
END {
    printf "C ≥ %f\n", C;
    printf "N = %d\n", N;
    printf "p-score   = %f ± %f\n", p_score   / N, sqrt(p_scoresq   / N - (p_score     / N) ^ 2);
    printf "h-score   = %f ± %f\n", h_score   / N, sqrt(h_scoresq   / N - (h_score     / N) ^ 2);
    printf "hp-score  = %f ± %f\n", hp_score  / N,  sqrt(hp_scoresq / N - (hp_scoresq  / N) ^ 2);
    printf "hpc-score = %f ± %f\n", hpc_score / N, sqrt(hpc_scoresq / N - (hpc_scoresq / N) ^ 2);
}
