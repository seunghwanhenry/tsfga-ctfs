# CTFS experiment report (full preset)


## E1 Ablation – MRA (mean ± sd over seeds; rank)

| process | ALL | FILTER | GA | TSFGA |
|---|---|---|---|---|
| deposition | 0.6571 ± 0.005 | 0.6466 ± 0.003 | 0.6733 ± 0.007 | 0.6761 ± 0.013 |
| etching | 0.7502 ± 0.003 | 0.7478 ± 0.004 | 0.7556 ± 0.011 | 0.7663 ± 0.008 |
| implantation | 0.6717 ± 0.003 | 0.6690 ± 0.004 | 0.6945 ± 0.011 | 0.7030 ± 0.007 |
| lithography | 0.7090 ± 0.004 | 0.7079 ± 0.004 | 0.7420 ± 0.010 | 0.7394 ± 0.011 |
| metalization | 0.6967 ± 0.005 | 0.6968 ± 0.003 | 0.7234 ± 0.013 | 0.7278 ± 0.010 |
| planarization | 0.6895 ± 0.003 | 0.6829 ± 0.003 | 0.7125 ± 0.013 | 0.7205 ± 0.013 |
| Average | 0.6957 | 0.6918 | 0.7169 | 0.7222 |


## E1 Ablation – PRF

| process | ALL | FILTER | GA | TSFGA |
|---|---|---|---|---|
| deposition | 0.0000 ± 0.000 | 0.2037 ± 0.000 | 0.8333 ± 0.025 | 0.8556 ± 0.023 |
| etching | 0.0000 ± 0.000 | 0.2037 ± 0.000 | 0.8296 ± 0.032 | 0.8796 ± 0.024 |
| implantation | 0.0000 ± 0.000 | 0.2037 ± 0.000 | 0.8222 ± 0.023 | 0.8611 ± 0.018 |
| lithography | 0.0000 ± 0.000 | 0.1852 ± 0.000 | 0.8315 ± 0.035 | 0.8648 ± 0.025 |
| metalization | 0.0000 ± 0.000 | 0.2037 ± 0.000 | 0.8278 ± 0.038 | 0.8667 ± 0.023 |
| planarization | 0.0000 ± 0.000 | 0.2037 ± 0.000 | 0.8315 ± 0.016 | 0.8778 ± 0.029 |
| Average | 0.0000 | 0.2006 | 0.8293 | 0.8676 |


## E2 Stability – mean pairwise Jaccard across seeds

| process | ALL | BGWO | BPSO | Boruta | DDA | FILTER | GA | LASSO | MI | NSGA2 | PFI-SBS | RFE | TSFGA | mRMR |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deposition | 1.0000 | 1.0000 | 0.5017 | 0.9102 | 0.6052 | 1.0000 | 0.2001 | 1.0000 | 0.9778 | 1.0000 | 0.6972 | 0.9156 | 0.3040 | 0.8116 |
| etching | 1.0000 | 0.9200 | 0.3809 | 0.8889 | 0.6579 | 1.0000 | 0.1483 | 1.0000 | 0.9267 | 1.0000 | 0.6726 | 0.8413 | 0.2610 | 0.9143 |
| implantation | 1.0000 | 0.8133 | 0.4488 | 0.8990 | 0.5161 | 1.0000 | 0.1645 | 1.0000 | 0.6464 | 1.0000 | 0.7747 | 0.8877 | 0.2908 | 0.8616 |
| lithography | 1.0000 | 1.0000 | 0.3419 | 0.9387 | 0.6232 | 1.0000 | 0.2048 | 1.0000 | 0.9537 | 1.0000 | 0.8894 | 0.6670 | 0.3202 | 0.8085 |
| metalization | 1.0000 | 0.8300 | 0.4392 | 0.8915 | 0.5798 | 1.0000 | 0.1568 | 1.0000 | 0.9156 | 1.0000 | 0.8053 | 0.8344 | 0.2801 | 0.9080 |
| planarization | 1.0000 | 0.8933 | 0.4744 | 0.8641 | 0.6452 | 1.0000 | 0.1677 | 1.0000 | 0.9791 | 1.0000 | 0.8560 | 0.8638 | 0.3854 | 1.0000 |
| Average | 1.0000 | 0.9094 | 0.4311 | 0.8987 | 0.6046 | 1.0000 | 0.1737 | 1.0000 | 0.8999 | 1.0000 | 0.7825 | 0.8350 | 0.3069 | 0.8840 |


## E3 Wilcoxon signed-rank vs TSFGA (all processes)

| reference   | method   |   n |   mean_diff |   median_diff |    W |   p_value |   wins |   ties |   losses | significant   | better    | metric   | process       |
|:------------|:---------|----:|------------:|--------------:|-----:|----------:|-------:|-------:|---------:|:--------------|:----------|:---------|:--------------|
| TSFGA       | ALL      |  90 |      0.0265 |        0.0247 |   78 |    0      |     83 |      0 |        7 | True          | reference | MRA      | ALL_PROCESSES |
| TSFGA       | BGWO     |  90 |     -0.0189 |       -0.0189 |   37 |    0      |      1 |      0 |       89 | True          | BGWO      | MRA      | ALL_PROCESSES |
| TSFGA       | BPSO     |  90 |     -0.0101 |       -0.0099 |  136 |    0      |      6 |      0 |       84 | True          | BPSO      | MRA      | ALL_PROCESSES |
| TSFGA       | Boruta   |  90 |     -0.0007 |        0.001  | 1976 |    0.7736 |     46 |      0 |       44 | False         | Boruta    | MRA      | ALL_PROCESSES |
| TSFGA       | DDA      |  90 |     -0.0144 |       -0.0134 |  455 |    0      |     14 |      0 |       76 | True          | DDA       | MRA      | ALL_PROCESSES |
| TSFGA       | FILTER   |  90 |      0.0303 |        0.029  |   16 |    0      |     86 |      0 |        4 | True          | reference | MRA      | ALL_PROCESSES |
| TSFGA       | GA       |  90 |      0.0053 |        0.0063 | 1169 |    0.0004 |     65 |      0 |       25 | True          | reference | MRA      | ALL_PROCESSES |
| TSFGA       | LASSO    |  90 |      0.0241 |        0.0226 |  230 |    0      |     79 |      0 |       11 | True          | reference | MRA      | ALL_PROCESSES |
| TSFGA       | MI       |  90 |     -0.0079 |       -0.0073 |  990 |    0      |     27 |      0 |       63 | True          | MI        | MRA      | ALL_PROCESSES |
| TSFGA       | NSGA2    |  90 |      0.023  |        0.0203 |  323 |    0      |     75 |      0 |       15 | True          | reference | MRA      | ALL_PROCESSES |
| TSFGA       | PFI-SBS  |  90 |     -0.0163 |       -0.0165 |  144 |    0      |      6 |      0 |       84 | True          | PFI-SBS   | MRA      | ALL_PROCESSES |
| TSFGA       | RFE      |  90 |     -0.0145 |       -0.0146 |  239 |    0      |     11 |      0 |       79 | True          | RFE       | MRA      | ALL_PROCESSES |
| TSFGA       | mRMR     |  90 |     -0.0045 |       -0.0035 | 1395 |    0.0087 |     32 |      0 |       58 | True          | mRMR      | MRA      | ALL_PROCESSES |
| TSFGA       | ALL      |  15 |      0.019  |        0.0141 |    7 |    0.0012 |     14 |      0 |        1 | True          | reference | MRA      | deposition    |
| TSFGA       | BGWO     |  15 |     -0.0231 |       -0.0232 |    0 |    0.0001 |      0 |      0 |       15 | True          | BGWO      | MRA      | deposition    |
| TSFGA       | BPSO     |  15 |     -0.0166 |       -0.0155 |    0 |    0.0001 |      0 |      0 |       15 | True          | BPSO      | MRA      | deposition    |
| TSFGA       | Boruta   |  15 |     -0.0037 |       -0.0005 |   42 |    0.3303 |      7 |      0 |        8 | False         | Boruta    | MRA      | deposition    |
| TSFGA       | DDA      |  15 |     -0.0237 |       -0.0238 |    0 |    0.0001 |      0 |      0 |       15 | True          | DDA       | MRA      | deposition    |
| TSFGA       | FILTER   |  15 |      0.0295 |        0.0344 |    1 |    0.0001 |     14 |      0 |        1 | True          | reference | MRA      | deposition    |
| TSFGA       | GA       |  15 |      0.0028 |        0.0046 |   47 |    0.4887 |      9 |      0 |        6 | False         | reference | MRA      | deposition    |
| TSFGA       | LASSO    |  15 |      0.0196 |        0.0251 |   25 |    0.0479 |     10 |      0 |        5 | True          | reference | MRA      | deposition    |
| TSFGA       | MI       |  15 |     -0.0183 |       -0.0208 |    2 |    0.0002 |      1 |      0 |       14 | True          | MI        | MRA      | deposition    |
| TSFGA       | NSGA2    |  15 |      0.0356 |        0.0299 |    6 |    0.0009 |     13 |      0 |        2 | True          | reference | MRA      | deposition    |
| TSFGA       | PFI-SBS  |  15 |     -0.0224 |       -0.0248 |    0 |    0.0001 |      0 |      0 |       15 | True          | PFI-SBS   | MRA      | deposition    |
| TSFGA       | RFE      |  15 |     -0.0203 |       -0.0208 |    1 |    0.0001 |      1 |      0 |       14 | True          | RFE       | MRA      | deposition    |
| TSFGA       | mRMR     |  15 |     -0.0109 |       -0.0111 |    2 |    0.0002 |      1 |      0 |       14 | True          | mRMR      | MRA      | deposition    |
| TSFGA       | ALL      |  15 |      0.0161 |        0.0128 |   10 |    0.0026 |     12 |      0 |        3 | True          | reference | MRA      | etching       |
| TSFGA       | BGWO     |  15 |     -0.0229 |       -0.0234 |    0 |    0.0001 |      0 |      0 |       15 | True          | BGWO      | MRA      | etching       |
| TSFGA       | BPSO     |  15 |     -0.0117 |       -0.0111 |    0 |    0.0001 |      0 |      0 |       15 | True          | BPSO      | MRA      | etching       |
| TSFGA       | Boruta   |  15 |     -0.005  |       -0.0002 |   48 |    0.5245 |      7 |      0 |        8 | False         | Boruta    | MRA      | etching       |
| TSFGA       | DDA      |  15 |     -0.0209 |       -0.0188 |    2 |    0.0002 |      1 |      0 |       14 | True          | DDA       | MRA      | etching       |
| TSFGA       | FILTER   |  15 |      0.0185 |        0.0172 |    2 |    0.0002 |     14 |      0 |        1 | True          | reference | MRA      | etching       |
| TSFGA       | GA       |  15 |      0.0107 |        0.009  |   12 |    0.0043 |     12 |      0 |        3 | True          | reference | MRA      | etching       |
| TSFGA       | LASSO    |  15 |      0.0162 |        0.0148 |    6 |    0.0009 |     12 |      0 |        3 | True          | reference | MRA      | etching       |
| TSFGA       | MI       |  15 |     -0.0125 |       -0.0138 |   14 |    0.0067 |      2 |      0 |       13 | True          | MI        | MRA      | etching       |
| TSFGA       | NSGA2    |  15 |      0.0117 |        0.0106 |   10 |    0.0026 |     12 |      0 |        3 | True          | reference | MRA      | etching       |
| TSFGA       | PFI-SBS  |  15 |     -0.0183 |       -0.018  |    0 |    0.0001 |      0 |      0 |       15 | True          | PFI-SBS   | MRA      | etching       |
| TSFGA       | RFE      |  15 |     -0.0151 |       -0.017  |    5 |    0.0006 |      1 |      0 |       14 | True          | RFE       | MRA      | etching       |
| TSFGA       | mRMR     |  15 |      0.0046 |        0.0001 |   46 |    0.4543 |      8 |      0 |        7 | False         | reference | MRA      | etching       |
| TSFGA       | ALL      |  15 |      0.0313 |        0.0342 |    2 |    0.0002 |     14 |      0 |        1 | True          | reference | MRA      | implantation  |
| TSFGA       | BGWO     |  15 |     -0.0151 |       -0.0151 |    8 |    0.0015 |      1 |      0 |       14 | True          | BGWO      | MRA      | implantation  |
| TSFGA       | BPSO     |  15 |     -0.0049 |       -0.0059 |   25 |    0.0479 |      3 |      0 |       12 | True          | BPSO      | MRA      | implantation  |
| TSFGA       | Boruta   |  15 |      0.0101 |        0.007  |   21 |    0.0256 |     11 |      0 |        4 | True          | reference | MRA      | implantation  |
| TSFGA       | DDA      |  15 |     -0.0012 |       -0.0011 |   52 |    0.6788 |      6 |      0 |        9 | False         | DDA       | MRA      | implantation  |
| TSFGA       | FILTER   |  15 |      0.034  |        0.033  |    1 |    0.0001 |     14 |      0 |        1 | True          | reference | MRA      | implantation  |
| TSFGA       | GA       |  15 |      0.0085 |        0.0099 |   21 |    0.0256 |     13 |      0 |        2 | True          | reference | MRA      | implantation  |
| TSFGA       | LASSO    |  15 |      0.025  |        0.0251 |    2 |    0.0002 |     14 |      0 |        1 | True          | reference | MRA      | implantation  |
| TSFGA       | MI       |  15 |      0.0038 |        0.005  |   35 |    0.1688 |      9 |      0 |        6 | False         | reference | MRA      | implantation  |
| TSFGA       | NSGA2    |  15 |      0.0128 |        0.0156 |   25 |    0.0479 |     12 |      0 |        3 | True          | reference | MRA      | implantation  |
| TSFGA       | PFI-SBS  |  15 |     -0.0109 |       -0.0081 |   17 |    0.0125 |      3 |      0 |       12 | True          | PFI-SBS   | MRA      | implantation  |
| TSFGA       | RFE      |  15 |     -0.0081 |       -0.0053 |   22 |    0.0302 |      4 |      0 |       11 | True          | RFE       | MRA      | implantation  |
| TSFGA       | mRMR     |  15 |     -0.0043 |       -0.0025 |   40 |    0.2769 |      5 |      0 |       10 | False         | mRMR      | MRA      | implantation  |
| TSFGA       | ALL      |  15 |      0.0304 |        0.0337 |    2 |    0.0002 |     14 |      0 |        1 | True          | reference | MRA      | lithography   |
| TSFGA       | BGWO     |  15 |     -0.0208 |       -0.0212 |    0 |    0.0001 |      0 |      0 |       15 | True          | BGWO      | MRA      | lithography   |
| TSFGA       | BPSO     |  15 |     -0.0088 |       -0.0081 |    0 |    0.0001 |      0 |      0 |       15 | True          | BPSO      | MRA      | lithography   |
| TSFGA       | Boruta   |  15 |     -0.0069 |       -0.003  |   41 |    0.3028 |      5 |      0 |       10 | False         | Boruta    | MRA      | lithography   |
| TSFGA       | DDA      |  15 |     -0.0172 |       -0.0143 |    7 |    0.0012 |      2 |      0 |       13 | True          | DDA       | MRA      | lithography   |
| TSFGA       | FILTER   |  15 |      0.0315 |        0.0346 |    1 |    0.0001 |     14 |      0 |        1 | True          | reference | MRA      | lithography   |
| TSFGA       | GA       |  15 |     -0.0027 |        0.0039 |   53 |    0.7197 |     10 |      0 |        5 | False         | GA        | MRA      | lithography   |
| TSFGA       | LASSO    |  15 |      0.0234 |        0.022  |    3 |    0.0003 |     14 |      0 |        1 | True          | reference | MRA      | lithography   |
| TSFGA       | MI       |  15 |     -0.0134 |       -0.0123 |   16 |    0.0103 |      4 |      0 |       11 | True          | MI        | MRA      | lithography   |
| TSFGA       | NSGA2    |  15 |      0.037  |        0.0304 |    0 |    0.0001 |     15 |      0 |        0 | True          | reference | MRA      | lithography   |
| TSFGA       | PFI-SBS  |  15 |     -0.02   |       -0.0198 |    0 |    0.0001 |      0 |      0 |       15 | True          | PFI-SBS   | MRA      | lithography   |
| TSFGA       | RFE      |  15 |     -0.0201 |       -0.0192 |    0 |    0.0001 |      0 |      0 |       15 | True          | RFE       | MRA      | lithography   |
| TSFGA       | mRMR     |  15 |     -0.0172 |       -0.0063 |   14 |    0.0067 |      3 |      0 |       12 | True          | mRMR      | MRA      | lithography   |
| TSFGA       | ALL      |  15 |      0.0311 |        0.0267 |    1 |    0.0001 |     14 |      0 |        1 | True          | reference | MRA      | metalization  |
| TSFGA       | BGWO     |  15 |     -0.0139 |       -0.0109 |    0 |    0.0001 |      0 |      0 |       15 | True          | BGWO      | MRA      | metalization  |
| TSFGA       | BPSO     |  15 |     -0.0097 |       -0.0099 |    5 |    0.0006 |      2 |      0 |       13 | True          | BPSO      | MRA      | metalization  |
| TSFGA       | Boruta   |  15 |     -0.0039 |       -0.0106 |   42 |    0.3303 |      7 |      0 |        8 | False         | Boruta    | MRA      | metalization  |
| TSFGA       | DDA      |  15 |     -0.0165 |       -0.0114 |   18 |    0.0151 |      3 |      0 |       12 | True          | DDA       | MRA      | metalization  |
| TSFGA       | FILTER   |  15 |      0.031  |        0.0238 |    0 |    0.0001 |     15 |      0 |        0 | True          | reference | MRA      | metalization  |
| TSFGA       | GA       |  15 |      0.0044 |        0.003  |   42 |    0.3303 |     10 |      0 |        5 | False         | reference | MRA      | metalization  |
| TSFGA       | LASSO    |  15 |      0.0301 |        0.0236 |    0 |    0.0001 |     15 |      0 |        0 | True          | reference | MRA      | metalization  |
| TSFGA       | MI       |  15 |     -0.0048 |       -0.0093 |   38 |    0.2293 |      7 |      0 |        8 | False         | MI        | MRA      | metalization  |
| TSFGA       | NSGA2    |  15 |      0.0084 |        0.0021 |   35 |    0.1688 |      8 |      0 |        7 | False         | reference | MRA      | metalization  |
| TSFGA       | PFI-SBS  |  15 |     -0.0127 |       -0.0125 |   18 |    0.0151 |      3 |      0 |       12 | True          | PFI-SBS   | MRA      | metalization  |
| TSFGA       | RFE      |  15 |     -0.0116 |       -0.0147 |   21 |    0.0256 |      4 |      0 |       11 | True          | RFE       | MRA      | metalization  |
| TSFGA       | mRMR     |  15 |     -0.0048 |       -0.0057 |   30 |    0.0946 |      4 |      0 |       11 | False         | mRMR      | MRA      | metalization  |
| TSFGA       | ALL      |  15 |      0.031  |        0.0231 |    0 |    0.0001 |     15 |      0 |        0 | True          | reference | MRA      | planarization |
| TSFGA       | BGWO     |  15 |     -0.0174 |       -0.0144 |    0 |    0.0001 |      0 |      0 |       15 | True          | BGWO      | MRA      | planarization |
| TSFGA       | BPSO     |  15 |     -0.0088 |       -0.0071 |    1 |    0.0001 |      1 |      0 |       14 | True          | BPSO      | MRA      | planarization |
| TSFGA       | Boruta   |  15 |      0.0051 |        0.0034 |   41 |    0.3028 |      9 |      0 |        6 | False         | reference | MRA      | planarization |
| TSFGA       | DDA      |  15 |     -0.0069 |       -0.0065 |   22 |    0.0302 |      2 |      0 |       13 | True          | DDA       | MRA      | planarization |
| TSFGA       | FILTER   |  15 |      0.0376 |        0.0323 |    0 |    0.0001 |     15 |      0 |        0 | True          | reference | MRA      | planarization |
| TSFGA       | GA       |  15 |      0.008  |        0.0065 |   28 |    0.073  |     11 |      0 |        4 | False         | reference | MRA      | planarization |
| TSFGA       | LASSO    |  15 |      0.0305 |        0.0262 |    6 |    0.0009 |     14 |      0 |        1 | True          | reference | MRA      | planarization |
| TSFGA       | MI       |  15 |     -0.0019 |       -0.0049 |   32 |    0.1205 |      4 |      0 |       11 | False         | MI        | MRA      | planarization |
| TSFGA       | NSGA2    |  15 |      0.0322 |        0.0292 |    0 |    0.0001 |     15 |      0 |        0 | True          | reference | MRA      | planarization |
| TSFGA       | PFI-SBS  |  15 |     -0.0133 |       -0.0124 |    0 |    0.0001 |      0 |      0 |       15 | True          | PFI-SBS   | MRA      | planarization |
| TSFGA       | RFE      |  15 |     -0.0116 |       -0.01   |    3 |    0.0003 |      1 |      0 |       14 | True          | RFE       | MRA      | planarization |
| TSFGA       | mRMR     |  15 |      0.0055 |        0.005  |   22 |    0.0302 |     11 |      0 |        4 | True          | reference | MRA      | planarization |
| TSFGA       | ALL      |  90 |     -0.5415 |       -0.5092 |   82 |    0      |     83 |      0 |        7 | True          | reference | MAE      | ALL_PROCESSES |
| TSFGA       | BGWO     |  90 |      0.356  |        0.3188 |   72 |    0      |      1 |      0 |       89 | True          | BGWO      | MAE      | ALL_PROCESSES |
| TSFGA       | BPSO     |  90 |      0.1925 |        0.1719 |  191 |    0      |      6 |      0 |       84 | True          | BPSO      | MAE      | ALL_PROCESSES |
| TSFGA       | Boruta   |  90 |      0.0012 |       -0.0154 | 2032 |    0.9503 |     46 |      0 |       44 | False         | Boruta    | MAE      | ALL_PROCESSES |
| TSFGA       | DDA      |  90 |      0.2662 |        0.24   |  563 |    0      |     14 |      0 |       76 | True          | DDA       | MAE      | ALL_PROCESSES |
| TSFGA       | FILTER   |  90 |     -0.6276 |       -0.5825 |   15 |    0      |     86 |      0 |        4 | True          | reference | MAE      | ALL_PROCESSES |
| TSFGA       | GA       |  90 |     -0.1134 |       -0.0938 | 1199 |    0.0006 |     65 |      0 |       25 | True          | reference | MAE      | ALL_PROCESSES |
| TSFGA       | LASSO    |  90 |     -0.5013 |       -0.4327 |  241 |    0      |     79 |      0 |       11 | True          | reference | MAE      | ALL_PROCESSES |
| TSFGA       | MI       |  90 |      0.1307 |        0.1289 | 1113 |    0.0002 |     27 |      0 |       63 | True          | MI        | MAE      | ALL_PROCESSES |
| TSFGA       | NSGA2    |  90 |     -0.4361 |       -0.3745 |  393 |    0      |     75 |      0 |       15 | True          | reference | MAE      | ALL_PROCESSES |
| TSFGA       | PFI-SBS  |  90 |      0.3087 |        0.2619 |  188 |    0      |      6 |      0 |       84 | True          | PFI-SBS   | MAE      | ALL_PROCESSES |
| TSFGA       | RFE      |  90 |      0.2708 |        0.2519 |  280 |    0      |     11 |      0 |       79 | True          | RFE       | MAE      | ALL_PROCESSES |
| TSFGA       | mRMR     |  90 |      0.0915 |        0.066  | 1323 |    0.0036 |     32 |      0 |       58 | True          | mRMR      | MAE      | ALL_PROCESSES |
| TSFGA       | ALL      |  15 |     -0.3977 |       -0.3079 |    7 |    0.0012 |     14 |      0 |        1 | True          | reference | MAE      | deposition    |
| TSFGA       | BGWO     |  15 |      0.4849 |        0.4952 |    0 |    0.0001 |      0 |      0 |       15 | True          | BGWO      | MAE      | deposition    |
| TSFGA       | BPSO     |  15 |      0.3499 |        0.3428 |    0 |    0.0001 |      0 |      0 |       15 | True          | BPSO      | MAE      | deposition    |
| TSFGA       | Boruta   |  15 |      0.0758 |        0.0075 |   45 |    0.4212 |      7 |      0 |        8 | False         | Boruta    | MAE      | deposition    |
| TSFGA       | DDA      |  15 |      0.5073 |        0.4396 |    0 |    0.0001 |      0 |      0 |       15 | True          | DDA       | MAE      | deposition    |
| TSFGA       | FILTER   |  15 |     -0.6216 |       -0.7493 |    1 |    0.0001 |     14 |      0 |        1 | True          | reference | MAE      | deposition    |
| TSFGA       | GA       |  15 |     -0.0901 |       -0.096  |   50 |    0.5995 |      9 |      0 |        6 | False         | reference | MAE      | deposition    |
| TSFGA       | LASSO    |  15 |     -0.4396 |       -0.5121 |   23 |    0.0353 |     10 |      0 |        5 | True          | reference | MAE      | deposition    |
| TSFGA       | MI       |  15 |      0.3833 |        0.3944 |    2 |    0.0002 |      1 |      0 |       14 | True          | MI        | MAE      | deposition    |
| TSFGA       | NSGA2    |  15 |     -0.7653 |       -0.785  |    6 |    0.0009 |     13 |      0 |        2 | True          | reference | MAE      | deposition    |
| TSFGA       | PFI-SBS  |  15 |      0.4668 |        0.5098 |    0 |    0.0001 |      0 |      0 |       15 | True          | PFI-SBS   | MAE      | deposition    |
| TSFGA       | RFE      |  15 |      0.4196 |        0.4675 |    1 |    0.0001 |      1 |      0 |       14 | True          | RFE       | MAE      | deposition    |
| TSFGA       | mRMR     |  15 |      0.2223 |        0.231  |    2 |    0.0002 |      1 |      0 |       14 | True          | mRMR      | MAE      | deposition    |
| TSFGA       | ALL      |  15 |     -0.194  |       -0.1675 |   10 |    0.0026 |     12 |      0 |        3 | True          | reference | MAE      | etching       |
| TSFGA       | BGWO     |  15 |      0.2577 |        0.2533 |    0 |    0.0001 |      0 |      0 |       15 | True          | BGWO      | MAE      | etching       |
| TSFGA       | BPSO     |  15 |      0.1301 |        0.1098 |    0 |    0.0001 |      0 |      0 |       15 | True          | BPSO      | MAE      | etching       |
| TSFGA       | Boruta   |  15 |      0.0439 |        0.0023 |   47 |    0.4887 |      7 |      0 |        8 | False         | Boruta    | MAE      | etching       |
| TSFGA       | DDA      |  15 |      0.2268 |        0.247  |    2 |    0.0002 |      1 |      0 |       14 | True          | DDA       | MAE      | etching       |
| TSFGA       | FILTER   |  15 |     -0.2168 |       -0.1588 |    3 |    0.0003 |     14 |      0 |        1 | True          | reference | MAE      | etching       |
| TSFGA       | GA       |  15 |     -0.1226 |       -0.1056 |    9 |    0.002  |     12 |      0 |        3 | True          | reference | MAE      | etching       |
| TSFGA       | LASSO    |  15 |     -0.1938 |       -0.1932 |    8 |    0.0015 |     12 |      0 |        3 | True          | reference | MAE      | etching       |
| TSFGA       | MI       |  15 |      0.1314 |        0.141  |   12 |    0.0043 |      2 |      0 |       13 | True          | MI        | MAE      | etching       |
| TSFGA       | NSGA2    |  15 |     -0.1277 |       -0.1162 |   10 |    0.0026 |     12 |      0 |        3 | True          | reference | MAE      | etching       |
| TSFGA       | PFI-SBS  |  15 |      0.2046 |        0.2016 |    0 |    0.0001 |      0 |      0 |       15 | True          | PFI-SBS   | MAE      | etching       |
| TSFGA       | RFE      |  15 |      0.1607 |        0.1569 |    5 |    0.0006 |      1 |      0 |       14 | True          | RFE       | MAE      | etching       |
| TSFGA       | mRMR     |  15 |     -0.0455 |       -0.0013 |   49 |    0.5614 |      8 |      0 |        7 | False         | reference | MAE      | etching       |
| TSFGA       | ALL      |  15 |     -0.7866 |       -0.9356 |    2 |    0.0002 |     14 |      0 |        1 | True          | reference | MAE      | implantation  |
| TSFGA       | BGWO     |  15 |      0.3791 |        0.4482 |   11 |    0.0034 |      1 |      0 |       14 | True          | BGWO      | MAE      | implantation  |
| TSFGA       | BPSO     |  15 |      0.1242 |        0.1528 |   24 |    0.0413 |      3 |      0 |       12 | True          | BPSO      | MAE      | implantation  |
| TSFGA       | Boruta   |  15 |     -0.2529 |       -0.1742 |   21 |    0.0256 |     11 |      0 |        4 | True          | reference | MAE      | implantation  |
| TSFGA       | DDA      |  15 |      0.0307 |        0.0356 |   55 |    0.804  |      6 |      0 |        9 | False         | DDA       | MAE      | implantation  |
| TSFGA       | FILTER   |  15 |     -0.8661 |       -0.9714 |    1 |    0.0001 |     14 |      0 |        1 | True          | reference | MAE      | implantation  |
| TSFGA       | GA       |  15 |     -0.2212 |       -0.3154 |   19 |    0.0181 |     13 |      0 |        2 | True          | reference | MAE      | implantation  |
| TSFGA       | LASSO    |  15 |     -0.6208 |       -0.669  |    2 |    0.0002 |     14 |      0 |        1 | True          | reference | MAE      | implantation  |
| TSFGA       | MI       |  15 |     -0.0939 |       -0.1236 |   36 |    0.1876 |      9 |      0 |        6 | False         | reference | MAE      | implantation  |
| TSFGA       | NSGA2    |  15 |     -0.3557 |       -0.3895 |   26 |    0.0554 |     12 |      0 |        3 | False         | reference | MAE      | implantation  |
| TSFGA       | PFI-SBS  |  15 |      0.2779 |        0.23   |   17 |    0.0125 |      3 |      0 |       12 | True          | PFI-SBS   | MAE      | implantation  |
| TSFGA       | RFE      |  15 |      0.205  |        0.1829 |   22 |    0.0302 |      4 |      0 |       11 | True          | RFE       | MAE      | implantation  |
| TSFGA       | mRMR     |  15 |      0.117  |        0.0846 |   37 |    0.2078 |      5 |      0 |       10 | False         | mRMR      | MAE      | implantation  |
| TSFGA       | ALL      |  15 |     -0.4377 |       -0.5111 |    2 |    0.0002 |     14 |      0 |        1 | True          | reference | MAE      | lithography   |
| TSFGA       | BGWO     |  15 |      0.2961 |        0.3026 |    0 |    0.0001 |      0 |      0 |       15 | True          | BGWO      | MAE      | lithography   |
| TSFGA       | BPSO     |  15 |      0.1259 |        0.1131 |    0 |    0.0001 |      0 |      0 |       15 | True          | BPSO      | MAE      | lithography   |
| TSFGA       | Boruta   |  15 |      0.0966 |        0.0409 |   38 |    0.2293 |      5 |      0 |       10 | False         | Boruta    | MAE      | lithography   |
| TSFGA       | DDA      |  15 |      0.2333 |        0.2151 |    8 |    0.0015 |      2 |      0 |       13 | True          | DDA       | MAE      | lithography   |
| TSFGA       | FILTER   |  15 |     -0.4569 |       -0.4802 |    1 |    0.0001 |     14 |      0 |        1 | True          | reference | MAE      | lithography   |
| TSFGA       | GA       |  15 |      0.0215 |       -0.059  |   53 |    0.7197 |     10 |      0 |        5 | False         | GA        | MAE      | lithography   |
| TSFGA       | LASSO    |  15 |     -0.3354 |       -0.3289 |    3 |    0.0003 |     14 |      0 |        1 | True          | reference | MAE      | lithography   |
| TSFGA       | MI       |  15 |      0.1769 |        0.2059 |   17 |    0.0125 |      4 |      0 |       11 | True          | MI        | MAE      | lithography   |
| TSFGA       | NSGA2    |  15 |     -0.5427 |       -0.3965 |    0 |    0.0001 |     15 |      0 |        0 | True          | reference | MAE      | lithography   |
| TSFGA       | PFI-SBS  |  15 |      0.2819 |        0.2789 |    0 |    0.0001 |      0 |      0 |       15 | True          | PFI-SBS   | MAE      | lithography   |
| TSFGA       | RFE      |  15 |      0.2778 |        0.303  |    0 |    0.0001 |      0 |      0 |       15 | True          | RFE       | MAE      | lithography   |
| TSFGA       | mRMR     |  15 |      0.2254 |        0.1046 |   14 |    0.0067 |      3 |      0 |       12 | True          | mRMR      | MAE      | lithography   |
| TSFGA       | ALL      |  15 |     -0.8359 |       -0.8439 |    1 |    0.0001 |     14 |      0 |        1 | True          | reference | MAE      | metalization  |
| TSFGA       | BGWO     |  15 |      0.3728 |        0.3288 |    0 |    0.0001 |      0 |      0 |       15 | True          | BGWO      | MAE      | metalization  |
| TSFGA       | BPSO     |  15 |      0.2516 |        0.2953 |    5 |    0.0006 |      2 |      0 |       13 | True          | BPSO      | MAE      | metalization  |
| TSFGA       | Boruta   |  15 |      0.1101 |        0.282  |   44 |    0.3894 |      7 |      0 |        8 | False         | Boruta    | MAE      | metalization  |
| TSFGA       | DDA      |  15 |      0.4559 |        0.3605 |   19 |    0.0181 |      3 |      0 |       12 | True          | DDA       | MAE      | metalization  |
| TSFGA       | FILTER   |  15 |     -0.8528 |       -0.7156 |    0 |    0.0001 |     15 |      0 |        0 | True          | reference | MAE      | metalization  |
| TSFGA       | GA       |  15 |     -0.1065 |       -0.0662 |   43 |    0.3591 |     10 |      0 |        5 | False         | reference | MAE      | metalization  |
| TSFGA       | LASSO    |  15 |     -0.8142 |       -0.6376 |    0 |    0.0001 |     15 |      0 |        0 | True          | reference | MAE      | metalization  |
| TSFGA       | MI       |  15 |      0.1297 |        0.3302 |   40 |    0.2769 |      7 |      0 |        8 | False         | MI        | MAE      | metalization  |
| TSFGA       | NSGA2    |  15 |     -0.2085 |       -0.0676 |   36 |    0.1876 |      8 |      0 |        7 | False         | reference | MAE      | metalization  |
| TSFGA       | PFI-SBS  |  15 |      0.3518 |        0.4077 |   15 |    0.0084 |      3 |      0 |       12 | True          | PFI-SBS   | MAE      | metalization  |
| TSFGA       | RFE      |  15 |      0.3216 |        0.3562 |   21 |    0.0256 |      4 |      0 |       11 | True          | RFE       | MAE      | metalization  |
| TSFGA       | mRMR     |  15 |      0.1417 |        0.173  |   28 |    0.073  |      4 |      0 |       11 | False         | mRMR      | MAE      | metalization  |
| TSFGA       | ALL      |  15 |     -0.5969 |       -0.49   |    0 |    0.0001 |     15 |      0 |        0 | True          | reference | MAE      | planarization |
| TSFGA       | BGWO     |  15 |      0.3452 |        0.28   |    0 |    0.0001 |      0 |      0 |       15 | True          | BGWO      | MAE      | planarization |
| TSFGA       | BPSO     |  15 |      0.1733 |        0.1334 |    1 |    0.0001 |      1 |      0 |       14 | True          | BPSO      | MAE      | planarization |
| TSFGA       | Boruta   |  15 |     -0.0661 |       -0.0527 |   43 |    0.3591 |      9 |      0 |        6 | False         | reference | MAE      | planarization |
| TSFGA       | DDA      |  15 |      0.1434 |        0.1138 |   21 |    0.0256 |      2 |      0 |       13 | True          | DDA       | MAE      | planarization |
| TSFGA       | FILTER   |  15 |     -0.7512 |       -0.6424 |    0 |    0.0001 |     15 |      0 |        0 | True          | reference | MAE      | planarization |
| TSFGA       | GA       |  15 |     -0.1614 |       -0.111  |   33 |    0.1354 |     11 |      0 |        4 | False         | reference | MAE      | planarization |
| TSFGA       | LASSO    |  15 |     -0.6042 |       -0.4738 |    7 |    0.0012 |     14 |      0 |        1 | True          | reference | MAE      | planarization |
| TSFGA       | MI       |  15 |      0.0571 |        0.0911 |   32 |    0.1205 |      4 |      0 |       11 | False         | MI        | MAE      | planarization |
| TSFGA       | NSGA2    |  15 |     -0.6164 |       -0.4994 |    0 |    0.0001 |     15 |      0 |        0 | True          | reference | MAE      | planarization |
| TSFGA       | PFI-SBS  |  15 |      0.2692 |        0.1935 |    0 |    0.0001 |      0 |      0 |       15 | True          | PFI-SBS   | MAE      | planarization |
| TSFGA       | RFE      |  15 |      0.2404 |        0.1874 |    3 |    0.0003 |      1 |      0 |       14 | True          | RFE       | MAE      | planarization |
| TSFGA       | mRMR     |  15 |     -0.1117 |       -0.0936 |   21 |    0.0256 |     11 |      0 |        4 | True          | reference | MAE      | planarization |
| TSFGA       | ALL      |  90 |     -0.7319 |       -0.6217 |  310 |    0      |     76 |      0 |       14 | True          | reference | RMSE     | ALL_PROCESSES |
| TSFGA       | BGWO     |  90 |      0.4826 |        0.4667 |  126 |    0      |      6 |      0 |       84 | True          | BGWO      | RMSE     | ALL_PROCESSES |
| TSFGA       | BPSO     |  90 |      0.2587 |        0.2308 |  353 |    0      |     11 |      0 |       79 | True          | BPSO      | RMSE     | ALL_PROCESSES |
| TSFGA       | Boruta   |  90 |     -0.0261 |       -0.0183 | 1919 |    0.6051 |     46 |      0 |       44 | False         | reference | RMSE     | ALL_PROCESSES |
| TSFGA       | DDA      |  90 |      0.3068 |        0.3074 |  891 |    0      |     27 |      0 |       63 | True          | DDA       | RMSE     | ALL_PROCESSES |
| TSFGA       | FILTER   |  90 |     -0.8296 |       -0.7251 |  165 |    0      |     81 |      0 |        9 | True          | reference | RMSE     | ALL_PROCESSES |
| TSFGA       | GA       |  90 |     -0.1709 |       -0.2082 | 1334 |    0.0041 |     59 |      0 |       31 | True          | reference | RMSE     | ALL_PROCESSES |
| TSFGA       | LASSO    |  90 |     -0.6376 |       -0.5657 |  621 |    0      |     75 |      0 |       15 | True          | reference | RMSE     | ALL_PROCESSES |
| TSFGA       | MI       |  90 |      0.1555 |        0.0647 | 1458 |    0.0177 |     38 |      0 |       52 | True          | MI        | RMSE     | ALL_PROCESSES |
| TSFGA       | NSGA2    |  90 |     -0.5452 |       -0.3544 |  832 |    0      |     65 |      0 |       25 | True          | reference | RMSE     | ALL_PROCESSES |
| TSFGA       | PFI-SBS  |  90 |      0.3933 |        0.3427 |  587 |    0      |     17 |      0 |       73 | True          | PFI-SBS   | RMSE     | ALL_PROCESSES |
| TSFGA       | RFE      |  90 |      0.345  |        0.3196 |  779 |    0      |     21 |      0 |       69 | True          | RFE       | RMSE     | ALL_PROCESSES |
| TSFGA       | mRMR     |  90 |      0.036  |        0.0455 | 1891 |    0.5289 |     40 |      0 |       50 | False         | mRMR      | RMSE     | ALL_PROCESSES |
| TSFGA       | ALL      |  15 |     -0.4623 |       -0.3597 |   22 |    0.0302 |     11 |      0 |        4 | True          | reference | RMSE     | deposition    |
| TSFGA       | BGWO     |  15 |      0.678  |        0.6274 |    0 |    0.0001 |      0 |      0 |       15 | True          | BGWO      | RMSE     | deposition    |
| TSFGA       | BPSO     |  15 |      0.5148 |        0.4455 |    0 |    0.0001 |      0 |      0 |       15 | True          | BPSO      | RMSE     | deposition    |
| TSFGA       | Boruta   |  15 |      0.1099 |        0.0939 |   43 |    0.3591 |      5 |      0 |       10 | False         | Boruta    | RMSE     | deposition    |
| TSFGA       | DDA      |  15 |      0.7333 |        0.7254 |    1 |    0.0001 |      1 |      0 |       14 | True          | DDA       | RMSE     | deposition    |
| TSFGA       | FILTER   |  15 |     -0.726  |       -0.7105 |   13 |    0.0054 |     12 |      0 |        3 | True          | reference | RMSE     | deposition    |
| TSFGA       | GA       |  15 |      0.0997 |       -0.0161 |   58 |    0.9341 |      9 |      0 |        6 | False         | GA        | RMSE     | deposition    |
| TSFGA       | LASSO    |  15 |     -0.1778 |       -1.0943 |   49 |    0.5614 |      9 |      0 |        6 | False         | reference | RMSE     | deposition    |
| TSFGA       | MI       |  15 |      0.5442 |        0.5864 |   13 |    0.0054 |      4 |      0 |       11 | True          | MI        | RMSE     | deposition    |
| TSFGA       | NSGA2    |  15 |     -1.4181 |       -1.1399 |    8 |    0.0015 |     13 |      0 |        2 | True          | reference | RMSE     | deposition    |
| TSFGA       | PFI-SBS  |  15 |      0.6951 |        0.7016 |    2 |    0.0002 |      1 |      0 |       14 | True          | PFI-SBS   | RMSE     | deposition    |
| TSFGA       | RFE      |  15 |      0.5914 |        0.518  |    4 |    0.0004 |      1 |      0 |       14 | True          | RFE       | RMSE     | deposition    |
| TSFGA       | mRMR     |  15 |      0.362  |        0.336  |   14 |    0.0067 |      3 |      0 |       12 | True          | mRMR      | RMSE     | deposition    |
| TSFGA       | ALL      |  15 |     -0.3672 |       -0.4496 |   13 |    0.0054 |     12 |      0 |        3 | True          | reference | RMSE     | etching       |
| TSFGA       | BGWO     |  15 |      0.3437 |        0.309  |    0 |    0.0001 |      0 |      0 |       15 | True          | BGWO      | RMSE     | etching       |
| TSFGA       | BPSO     |  15 |      0.1618 |        0.1318 |    1 |    0.0001 |      1 |      0 |       14 | True          | BPSO      | RMSE     | etching       |
| TSFGA       | Boruta   |  15 |     -0.071  |       -0.0949 |   46 |    0.4543 |     10 |      0 |        5 | False         | reference | RMSE     | etching       |
| TSFGA       | DDA      |  15 |      0.2173 |        0.2827 |   16 |    0.0103 |      4 |      0 |       11 | True          | DDA       | RMSE     | etching       |
| TSFGA       | FILTER   |  15 |     -0.3367 |       -0.2962 |    5 |    0.0006 |     13 |      0 |        2 | True          | reference | RMSE     | etching       |
| TSFGA       | GA       |  15 |     -0.3842 |       -0.2834 |   10 |    0.0026 |     12 |      0 |        3 | True          | reference | RMSE     | etching       |
| TSFGA       | LASSO    |  15 |     -0.3788 |       -0.3692 |   11 |    0.0034 |     12 |      0 |        3 | True          | reference | RMSE     | etching       |
| TSFGA       | MI       |  15 |      0.0708 |        0.0242 |   49 |    0.5614 |      6 |      0 |        9 | False         | MI        | RMSE     | etching       |
| TSFGA       | NSGA2    |  15 |     -0.1021 |       -0.0546 |   36 |    0.1876 |      8 |      0 |        7 | False         | reference | RMSE     | etching       |
| TSFGA       | PFI-SBS  |  15 |      0.167  |        0.195  |   21 |    0.0256 |      3 |      0 |       12 | True          | PFI-SBS   | RMSE     | etching       |
| TSFGA       | RFE      |  15 |      0.067  |        0.1987 |   49 |    0.5614 |      7 |      0 |        8 | False         | RFE       | RMSE     | etching       |
| TSFGA       | mRMR     |  15 |     -0.3491 |       -0.2957 |   19 |    0.0181 |     11 |      0 |        4 | True          | reference | RMSE     | etching       |
| TSFGA       | ALL      |  15 |     -0.9693 |       -0.9412 |    5 |    0.0006 |     13 |      0 |        2 | True          | reference | RMSE     | implantation  |
| TSFGA       | BGWO     |  15 |      0.572  |        0.7219 |   14 |    0.0067 |      2 |      0 |       13 | True          | BGWO      | RMSE     | implantation  |
| TSFGA       | BPSO     |  15 |      0.2577 |        0.3019 |   18 |    0.0151 |      3 |      0 |       12 | True          | BPSO      | RMSE     | implantation  |
| TSFGA       | Boruta   |  15 |     -0.1424 |       -0.2906 |   45 |    0.4212 |      8 |      0 |        7 | False         | reference | RMSE     | implantation  |
| TSFGA       | DDA      |  15 |      0.103  |       -0.1159 |   58 |    0.9341 |      8 |      0 |        7 | False         | DDA       | RMSE     | implantation  |
| TSFGA       | FILTER   |  15 |     -1.194  |       -1.2085 |    3 |    0.0003 |     14 |      0 |        1 | True          | reference | RMSE     | implantation  |
| TSFGA       | GA       |  15 |     -0.2198 |       -0.3809 |   35 |    0.1688 |      9 |      0 |        6 | False         | reference | RMSE     | implantation  |
| TSFGA       | LASSO    |  15 |     -0.7452 |       -0.6046 |   12 |    0.0043 |     13 |      0 |        2 | True          | reference | RMSE     | implantation  |
| TSFGA       | MI       |  15 |      0.0644 |       -0.0452 |   57 |    0.8904 |      8 |      0 |        7 | False         | MI        | RMSE     | implantation  |
| TSFGA       | NSGA2    |  15 |     -0.3615 |       -0.2018 |   41 |    0.3028 |      9 |      0 |        6 | False         | reference | RMSE     | implantation  |
| TSFGA       | PFI-SBS  |  15 |      0.5084 |        0.5974 |   19 |    0.0181 |      4 |      0 |       11 | True          | PFI-SBS   | RMSE     | implantation  |
| TSFGA       | RFE      |  15 |      0.4962 |        0.5945 |   19 |    0.0181 |      4 |      0 |       11 | True          | RFE       | RMSE     | implantation  |
| TSFGA       | mRMR     |  15 |      0.2656 |        0.3287 |   33 |    0.1354 |      4 |      0 |       11 | False         | mRMR      | RMSE     | implantation  |
| TSFGA       | ALL      |  15 |     -0.6061 |       -0.6413 |    4 |    0.0004 |     14 |      0 |        1 | True          | reference | RMSE     | lithography   |
| TSFGA       | BGWO     |  15 |      0.4065 |        0.4903 |    0 |    0.0001 |      0 |      0 |       15 | True          | BGWO      | RMSE     | lithography   |
| TSFGA       | BPSO     |  15 |      0.148  |        0.1322 |    6 |    0.0009 |      1 |      0 |       14 | True          | BPSO      | RMSE     | lithography   |
| TSFGA       | Boruta   |  15 |      0.088  |        0.0758 |   48 |    0.5245 |      7 |      0 |        8 | False         | Boruta    | RMSE     | lithography   |
| TSFGA       | DDA      |  15 |      0.3321 |        0.2906 |   12 |    0.0043 |      4 |      0 |       11 | True          | DDA       | RMSE     | lithography   |
| TSFGA       | FILTER   |  15 |     -0.6203 |       -0.6068 |    5 |    0.0006 |     13 |      0 |        2 | True          | reference | RMSE     | lithography   |
| TSFGA       | GA       |  15 |     -0.0027 |       -0.0525 |   47 |    0.4887 |     10 |      0 |        5 | False         | reference | RMSE     | lithography   |
| TSFGA       | LASSO    |  15 |     -0.4477 |       -0.3951 |    8 |    0.0015 |     14 |      0 |        1 | True          | reference | RMSE     | lithography   |
| TSFGA       | MI       |  15 |      0.2146 |        0.2276 |   23 |    0.0353 |      5 |      0 |       10 | True          | MI        | RMSE     | lithography   |
| TSFGA       | NSGA2    |  15 |     -0.6441 |       -0.4239 |    2 |    0.0002 |     14 |      0 |        1 | True          | reference | RMSE     | lithography   |
| TSFGA       | PFI-SBS  |  15 |      0.3403 |        0.3382 |    0 |    0.0001 |      0 |      0 |       15 | True          | PFI-SBS   | RMSE     | lithography   |
| TSFGA       | RFE      |  15 |      0.3496 |        0.3693 |    2 |    0.0002 |      1 |      0 |       14 | True          | RFE       | RMSE     | lithography   |
| TSFGA       | mRMR     |  15 |      0.1642 |        0.0388 |   60 |    1      |      7 |      0 |        8 | False         | mRMR      | RMSE     | lithography   |
| TSFGA       | ALL      |  15 |     -1.2461 |       -1.0523 |    1 |    0.0001 |     14 |      0 |        1 | True          | reference | RMSE     | metalization  |
| TSFGA       | BGWO     |  15 |      0.5146 |        0.4766 |    3 |    0.0003 |      2 |      0 |       13 | True          | BGWO      | RMSE     | metalization  |
| TSFGA       | BPSO     |  15 |      0.2567 |        0.3552 |   23 |    0.0353 |      4 |      0 |       11 | True          | BPSO      | RMSE     | metalization  |
| TSFGA       | Boruta   |  15 |     -0.0177 |       -0.0937 |   55 |    0.804  |      8 |      0 |        7 | False         | reference | RMSE     | metalization  |
| TSFGA       | DDA      |  15 |      0.3925 |        0.5201 |   32 |    0.1205 |      5 |      0 |       10 | False         | DDA       | RMSE     | metalization  |
| TSFGA       | FILTER   |  15 |     -1.1949 |       -1.0541 |    0 |    0.0001 |     15 |      0 |        0 | True          | reference | RMSE     | metalization  |
| TSFGA       | GA       |  15 |     -0.2777 |       -0.1434 |   37 |    0.2078 |      8 |      0 |        7 | False         | reference | RMSE     | metalization  |
| TSFGA       | LASSO    |  15 |     -1.2418 |       -0.8469 |    0 |    0.0001 |     15 |      0 |        0 | True          | reference | RMSE     | metalization  |
| TSFGA       | MI       |  15 |      0.0346 |       -0.0651 |   55 |    0.804  |      8 |      0 |        7 | False         | MI        | RMSE     | metalization  |
| TSFGA       | NSGA2    |  15 |     -0.1853 |       -0.1499 |   44 |    0.3894 |      9 |      0 |        6 | False         | reference | RMSE     | metalization  |
| TSFGA       | PFI-SBS  |  15 |      0.3104 |        0.3458 |   27 |    0.0637 |      5 |      0 |       10 | False         | PFI-SBS   | RMSE     | metalization  |
| TSFGA       | RFE      |  15 |      0.2861 |        0.2789 |   32 |    0.1205 |      5 |      0 |       10 | False         | RFE       | RMSE     | metalization  |
| TSFGA       | mRMR     |  15 |      0.0471 |        0.0522 |   45 |    0.4212 |      5 |      0 |       10 | False         | mRMR      | RMSE     | metalization  |
| TSFGA       | ALL      |  15 |     -0.7404 |       -0.6118 |   18 |    0.0151 |     12 |      0 |        3 | True          | reference | RMSE     | planarization |
| TSFGA       | BGWO     |  15 |      0.3809 |        0.2685 |    7 |    0.0012 |      2 |      0 |       13 | True          | BGWO      | RMSE     | planarization |
| TSFGA       | BPSO     |  15 |      0.2134 |        0.1913 |   11 |    0.0034 |      2 |      0 |       13 | True          | BPSO      | RMSE     | planarization |
| TSFGA       | Boruta   |  15 |     -0.1233 |       -0.3561 |   47 |    0.4887 |      8 |      0 |        7 | False         | reference | RMSE     | planarization |
| TSFGA       | DDA      |  15 |      0.0628 |        0.1634 |   40 |    0.2769 |      5 |      0 |       10 | False         | DDA       | RMSE     | planarization |
| TSFGA       | FILTER   |  15 |     -0.9057 |       -0.8137 |    4 |    0.0004 |     14 |      0 |        1 | True          | reference | RMSE     | planarization |
| TSFGA       | GA       |  15 |     -0.2408 |       -0.2942 |   34 |    0.1514 |     11 |      0 |        4 | False         | reference | RMSE     | planarization |
| TSFGA       | LASSO    |  15 |     -0.8346 |       -0.8916 |   17 |    0.0125 |     12 |      0 |        3 | True          | reference | RMSE     | planarization |
| TSFGA       | MI       |  15 |      0.0048 |        0.0526 |   60 |    1      |      7 |      0 |        8 | False         | MI        | RMSE     | planarization |
| TSFGA       | NSGA2    |  15 |     -0.5603 |       -0.4836 |   20 |    0.0215 |     12 |      0 |        3 | True          | reference | RMSE     | planarization |
| TSFGA       | PFI-SBS  |  15 |      0.3386 |        0.2642 |   26 |    0.0554 |      4 |      0 |       11 | False         | PFI-SBS   | RMSE     | planarization |
| TSFGA       | RFE      |  15 |      0.2798 |        0.2031 |   32 |    0.1205 |      3 |      0 |       12 | False         | RFE       | RMSE     | planarization |
| TSFGA       | mRMR     |  15 |     -0.274  |       -0.1386 |   27 |    0.0637 |     10 |      0 |        5 | False         | reference | RMSE     | planarization |


## E3 Friedman test (MRA)

chi2 = 745.926, p = 5.19e-151, Iman–Davenport p = 1.11e-16, Nemenyi CD = 2.091 (k=14, N=90)

| method   |   avg_rank |
|:---------|-----------:|
| BGWO     |      3.089 |
| PFI-SBS  |      3.433 |
| RFE      |      3.956 |
| DDA      |      3.967 |
| BPSO     |      5.5   |
| MI       |      5.967 |
| mRMR     |      6.967 |
| Boruta   |      7.711 |
| TSFGA    |      8.1   |
| GA       |      9.322 |
| NSGA2    |     10.856 |
| LASSO    |     11.556 |
| ALL      |     12.111 |
| FILTER   |     12.467 |


## E4 Sensitivity (average over processes and seeds)

| param         |   value |    MRA |    PRF |   n_selected |    CFS |
|:--------------|--------:|-------:|-------:|-------------:|-------:|
| ga.pc         |    0.3  | 0.7283 | 0.8745 |       6.7778 | 0.5933 |
| ga.pc         |    0.5  | 0.7229 | 0.8652 |       7.2778 | 0.5533 |
| ga.pc         |    0.8  | 0.7251 | 0.8416 |       8.5556 | 0.5385 |
| ga.pm         |    0.05 | 0.7371 | 0.8951 |       5.6667 | 0.6552 |
| ga.pm         |    0.1  | 0.7229 | 0.8652 |       7.2778 | 0.5533 |
| ga.pm         |    0.2  | 0.7188 | 0.8158 |       9.9444 | 0.5006 |
| ga.pop_size   |   40    | 0.7269 | 0.8652 |       7.2778 | 0.5829 |
| ga.pop_size   |   80    | 0.7229 | 0.8652 |       7.2778 | 0.5533 |
| ga.pop_size   |  120    | 0.7287 | 0.8652 |       7.2778 | 0.578  |
| lambda        |    0.5  | 0.7129 | 0.9095 |       4.8889 | 0.6001 |
| lambda        |    1    | 0.7144 | 0.8868 |       6.1111 | 0.5659 |
| lambda        |    2    | 0.7229 | 0.8652 |       7.2778 | 0.5533 |
| lambda        |    5    | 0.7312 | 0.8488 |       8.1667 | 0.5693 |
| lambda        |   10    | 0.7312 | 0.823  |       9.5556 | 0.5555 |
| pcc_threshold |    0.7  | 0.7263 | 0.8735 |       6.8333 | 0.5813 |
| pcc_threshold |    0.8  | 0.7229 | 0.8652 |       7.2778 | 0.5533 |
| pcc_threshold |    0.9  | 0.7199 | 0.8601 |       7.5556 | 0.5254 |
| pcc_threshold |    1    | 0.7152 | 0.8323 |       9.0556 | 0.5409 |


## E6 Baselines – MRA

| process | ALL | BGWO | BPSO | Boruta | DDA | FILTER | GA | LASSO | MI | NSGA2 | PFI-SBS | RFE | TSFGA | mRMR |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deposition | 0.6571 ± 0.005 (11) | 0.6992 ± 0.003 (2) | 0.6928 ± 0.007 (6) | 0.6798 ± 0.006 (8) | 0.6999 ± 0.004 (1) | 0.6466 ± 0.003 (13) | 0.6733 ± 0.007 (10) | 0.6565 ± 0.004 (12) | 0.6945 ± 0.003 (5) | 0.6405 ± 0.004 (14) | 0.6985 ± 0.003 (3) | 0.6964 ± 0.003 (4) | 0.6761 ± 0.013 (9) | 0.6871 ± 0.003 (7) |
| etching | 0.7502 ± 0.003 (12) | 0.7892 ± 0.002 (1) | 0.7780 ± 0.008 (6) | 0.7712 ± 0.004 (7) | 0.7872 ± 0.002 (2) | 0.7478 ± 0.004 (14) | 0.7556 ± 0.011 (10) | 0.7501 ± 0.005 (13) | 0.7788 ± 0.002 (5) | 0.7546 ± 0.001 (11) | 0.7846 ± 0.003 (3) | 0.7814 ± 0.002 (4) | 0.7663 ± 0.008 (8) | 0.7617 ± 0.003 (9) |
| implantation | 0.6717 ± 0.003 (13) | 0.7181 ± 0.004 (1) | 0.7078 ± 0.009 (4) | 0.6929 ± 0.003 (10) | 0.7042 ± 0.008 (6) | 0.6690 ± 0.004 (14) | 0.6945 ± 0.011 (9) | 0.6780 ± 0.002 (12) | 0.6992 ± 0.006 (8) | 0.6902 ± 0.003 (11) | 0.7139 ± 0.003 (2) | 0.7111 ± 0.003 (3) | 0.7030 ± 0.007 (7) | 0.7073 ± 0.005 (5) |
| lithography | 0.7090 ± 0.004 (12) | 0.7602 ± 0.003 (1) | 0.7482 ± 0.005 (7) | 0.7462 ± 0.002 (8) | 0.7566 ± 0.004 (4) | 0.7079 ± 0.004 (13) | 0.7420 ± 0.010 (9) | 0.7160 ± 0.003 (11) | 0.7528 ± 0.003 (6) | 0.7024 ± 0.002 (14) | 0.7594 ± 0.002 (3) | 0.7595 ± 0.003 (2) | 0.7394 ± 0.011 (10) | 0.7565 ± 0.003 (5) |
| metalization | 0.6967 ± 0.005 (14) | 0.7418 ± 0.005 (2) | 0.7375 ± 0.008 (5) | 0.7317 ± 0.003 (8) | 0.7443 ± 0.003 (1) | 0.6968 ± 0.003 (13) | 0.7234 ± 0.013 (10) | 0.6978 ± 0.003 (12) | 0.7326 ± 0.003 (7) | 0.7194 ± 0.002 (11) | 0.7405 ± 0.003 (3) | 0.7395 ± 0.002 (4) | 0.7278 ± 0.010 (9) | 0.7327 ± 0.003 (6) |
| planarization | 0.6895 ± 0.003 (12) | 0.7379 ± 0.004 (1) | 0.7293 ± 0.009 (4) | 0.7154 ± 0.003 (8) | 0.7274 ± 0.004 (5) | 0.6829 ± 0.003 (14) | 0.7125 ± 0.013 (10) | 0.6900 ± 0.003 (11) | 0.7224 ± 0.004 (6) | 0.6883 ± 0.002 (13) | 0.7338 ± 0.004 (2) | 0.7321 ± 0.004 (3) | 0.7205 ± 0.013 (7) | 0.7150 ± 0.003 (9) |
| Average | 0.6957 | 0.7411 | 0.7323 | 0.7229 | 0.7366 | 0.6918 | 0.7169 | 0.6981 | 0.7300 | 0.6992 | 0.7385 | 0.7367 | 0.7222 | 0.7267 |
| rank sum | 74 | 8 | 32 | 49 | 19 | 81 | 58 | 71 | 37 | 74 | 16 | 20 | 50 | 41 |


## E6 Baselines – PRF

| process | ALL | BGWO | BPSO | Boruta | DDA | FILTER | GA | LASSO | MI | NSGA2 | PFI-SBS | RFE | TSFGA | mRMR |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deposition | 0.0000 ± 0.000 (14) | 0.9259 ± 0.000 (2) | 0.8963 ± 0.022 (3) | 0.7259 ± 0.008 (10) | 0.8019 ± 0.030 (7) | 0.2037 ± 0.000 (13) | 0.8333 ± 0.025 (5) | 0.2407 ± 0.000 (12) | 0.7074 ± 0.008 (11) | 0.9630 ± 0.000 (1) | 0.7704 ± 0.060 (9) | 0.8222 ± 0.018 (6) | 0.8556 ± 0.023 (4) | 0.7759 ± 0.046 (8) |
| etching | 0.0000 ± 0.000 (14) | 0.9259 ± 0.000 (2) | 0.8963 ± 0.016 (4) | 0.6944 ± 0.016 (11) | 0.8111 ± 0.034 (8) | 0.2037 ± 0.000 (12) | 0.8296 ± 0.032 (6) | 0.1111 ± 0.000 (13) | 0.7648 ± 0.015 (10) | 0.9630 ± 0.000 (1) | 0.8204 ± 0.059 (7) | 0.8056 ± 0.025 (9) | 0.8796 ± 0.024 (5) | 0.9204 ± 0.018 (3) |
| implantation | 0.0000 ± 0.000 (14) | 0.9259 ± 0.000 (2) | 0.9019 ± 0.023 (3) | 0.7037 ± 0.012 (11) | 0.7833 ± 0.035 (9) | 0.2037 ± 0.000 (12) | 0.8222 ± 0.023 (7) | 0.2037 ± 0.000 (12) | 0.7519 ± 0.093 (10) | 0.9630 ± 0.000 (1) | 0.8444 ± 0.032 (6) | 0.8537 ± 0.011 (5) | 0.8611 ± 0.018 (4) | 0.7907 ± 0.032 (8) |
| lithography | 0.0000 ± 0.000 (14) | 0.9259 ± 0.000 (2) | 0.8796 ± 0.010 (4) | 0.6778 ± 0.013 (11) | 0.7907 ± 0.030 (9) | 0.1852 ± 0.000 (13) | 0.8315 ± 0.035 (8) | 0.2963 ± 0.000 (12) | 0.7444 ± 0.012 (10) | 0.9630 ± 0.000 (1) | 0.8519 ± 0.021 (7) | 0.8667 ± 0.015 (5) | 0.8648 ± 0.025 (6) | 0.9111 ± 0.024 (3) |
| metalization | 0.0000 ± 0.000 (14) | 0.9315 ± 0.009 (2) | 0.8926 ± 0.017 (3) | 0.7407 ± 0.009 (11) | 0.8426 ± 0.028 (5) | 0.2037 ± 0.000 (12) | 0.8278 ± 0.038 (6) | 0.1667 ± 0.000 (13) | 0.7704 ± 0.018 (10) | 0.9630 ± 0.000 (1) | 0.8241 ± 0.020 (7) | 0.8167 ± 0.020 (8) | 0.8667 ± 0.023 (4) | 0.8019 ± 0.029 (9) |
| planarization | 0.0000 ± 0.000 (14) | 0.9148 ± 0.010 (2) | 0.8778 ± 0.016 (4) | 0.7074 ± 0.019 (10) | 0.7870 ± 0.028 (8) | 0.2037 ± 0.000 (13) | 0.8315 ± 0.016 (5) | 0.4259 ± 0.000 (12) | 0.7000 ± 0.008 (11) | 0.9630 ± 0.000 (1) | 0.8037 ± 0.023 (7) | 0.8167 ± 0.022 (6) | 0.8778 ± 0.029 (3) | 0.7593 ± 0.000 (9) |
| Average | 0.0000 | 0.9250 | 0.8907 | 0.7083 | 0.8028 | 0.2006 | 0.8293 | 0.2407 | 0.7398 | 0.9630 | 0.8191 | 0.8302 | 0.8676 | 0.8265 |
| rank sum | 84 | 12 | 21 | 64 | 46 | 75 | 37 | 74 | 62 | 6 | 43 | 39 | 26 | 40 |


## E6 Baselines – CFS

| process | ALL | BGWO | BPSO | Boruta | DDA | FILTER | GA | LASSO | MI | NSGA2 | PFI-SBS | RFE | TSFGA | mRMR |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deposition | 0.4628 ± 0.000 (12) | 0.7407 ± 0.000 (2) | 0.6422 ± 0.045 (4) | 0.5715 ± 0.004 (9) | 0.6198 ± 0.041 (7) | 0.3200 ± 0.000 (14) | 0.5317 ± 0.038 (11) | 0.4522 ± 0.000 (13) | 0.5991 ± 0.002 (8) | 0.7721 ± 0.000 (1) | 0.6481 ± 0.027 (3) | 0.6283 ± 0.010 (6) | 0.5535 ± 0.034 (10) | 0.6410 ± 0.059 (5) |
| etching | 0.4546 ± 0.000 (12) | 0.7174 ± 0.008 (3) | 0.6079 ± 0.038 (7) | 0.5575 ± 0.004 (9) | 0.7249 ± 0.033 (2) | 0.3255 ± 0.000 (14) | 0.5349 ± 0.032 (11) | 0.4497 ± 0.000 (13) | 0.5853 ± 0.004 (8) | 0.7744 ± 0.000 (1) | 0.6653 ± 0.052 (6) | 0.6824 ± 0.052 (5) | 0.5416 ± 0.042 (10) | 0.6877 ± 0.024 (4) |
| implantation | 0.4791 ± 0.000 (13) | 0.7366 ± 0.006 (2) | 0.6563 ± 0.052 (6) | 0.6030 ± 0.003 (8) | 0.6741 ± 0.056 (4) | 0.3258 ± 0.000 (14) | 0.5493 ± 0.046 (11) | 0.4895 ± 0.000 (12) | 0.5942 ± 0.026 (9) | 0.8135 ± 0.000 (1) | 0.6759 ± 0.042 (3) | 0.6400 ± 0.010 (7) | 0.5551 ± 0.040 (10) | 0.6618 ± 0.059 (5) |
| lithography | 0.4820 ± 0.000 (12) | 0.7380 ± 0.000 (3) | 0.5856 ± 0.059 (10) | 0.6001 ± 0.005 (8) | 0.6857 ± 0.023 (6) | 0.3586 ± 0.000 (14) | 0.5888 ± 0.064 (9) | 0.4422 ± 0.000 (13) | 0.6018 ± 0.005 (7) | 0.7772 ± 0.000 (1) | 0.7492 ± 0.039 (2) | 0.7078 ± 0.043 (5) | 0.5404 ± 0.030 (11) | 0.7112 ± 0.032 (4) |
| metalization | 0.4992 ± 0.000 (12) | 0.7492 ± 0.016 (2) | 0.6366 ± 0.036 (7) | 0.6226 ± 0.004 (8) | 0.6593 ± 0.103 (5) | 0.3313 ± 0.000 (14) | 0.5689 ± 0.049 (10) | 0.3998 ± 0.000 (13) | 0.6205 ± 0.004 (9) | 0.7922 ± 0.000 (1) | 0.6716 ± 0.033 (4) | 0.6498 ± 0.010 (6) | 0.5438 ± 0.041 (11) | 0.7264 ± 0.034 (3) |
| planarization | 0.4887 ± 0.000 (12) | 0.7577 ± 0.011 (2) | 0.6362 ± 0.037 (7) | 0.6081 ± 0.007 (10) | 0.7338 ± 0.043 (3) | 0.3536 ± 0.000 (14) | 0.5511 ± 0.052 (11) | 0.4464 ± 0.000 (13) | 0.6293 ± 0.001 (8) | 0.7878 ± 0.000 (1) | 0.6943 ± 0.042 (5) | 0.6963 ± 0.038 (4) | 0.6226 ± 0.072 (9) | 0.6929 ± 0.000 (6) |
| Average | 0.4777 | 0.7399 | 0.6275 | 0.5938 | 0.6829 | 0.3358 | 0.5541 | 0.4466 | 0.6050 | 0.7862 | 0.6841 | 0.6674 | 0.5595 | 0.6868 |
| rank sum | 73 | 14 | 41 | 52 | 27 | 84 | 63 | 77 | 49 | 6 | 23 | 33 | 61 | 27 |


## E5 Baselines – wall-clock time (s)

| process | ALL | BGWO | BPSO | Boruta | DDA | FILTER | GA | LASSO | MI | NSGA2 | PFI-SBS | RFE | TSFGA | mRMR |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deposition | 0.8817 ± 0.072 | 465.3 ± 26.511 | 6487.5 ± 80.144 | 15.4733 ± 4.395 | 18.7193 ± 0.944 | 1.3837 ± 0.137 | 5646.6 ± 1790.529 | 0.9113 ± 0.071 | 31.5595 ± 0.495 | 1726.7 ± 125.756 | 38.5858 ± 0.589 | 120.4 ± 1.111 | 5005.8 ± 1668.650 | 31.3680 ± 0.660 |
| etching | 0.8567 ± 0.110 | 450.1 ± 37.192 | 6488.5 ± 66.979 | 17.3554 ± 2.993 | 18.4965 ± 1.278 | 1.5915 ± 0.164 | 5317.9 ± 1772.222 | 0.9453 ± 0.092 | 32.1694 ± 0.987 | 1672.4 ± 107.635 | 38.9485 ± 0.412 | 120.3 ± 3.625 | 3840.3 ± 855.848 | 31.2881 ± 0.965 |
| implantation | 0.8996 ± 0.066 | 477.6 ± 24.082 | 6447.8 ± 58.452 | 18.2531 ± 4.355 | 19.0623 ± 1.326 | 1.3641 ± 0.122 | 5147.9 ± 1318.511 | 0.9514 ± 0.102 | 32.0752 ± 0.568 | 1695.8 ± 109.086 | 38.5118 ± 0.986 | 119.1 ± 3.921 | 4407.1 ± 1229.691 | 31.9086 ± 1.202 |
| lithography | 0.8478 ± 0.095 | 539.5 ± 21.978 | 6548.0 ± 80.551 | 11.4823 ± 6.147 | 18.9393 ± 1.045 | 1.3895 ± 0.129 | 5951.2 ± 1806.944 | 0.9433 ± 0.081 | 24.8193 ± 4.839 | 1594.4 ± 71.775 | 39.0018 ± 0.987 | 112.6 ± 1.979 | 4010.0 ± 1220.214 | 21.5563 ± 1.770 |
| metalization | 0.9285 ± 0.078 | 462.0 ± 17.380 | 6547.5 ± 60.172 | 12.7496 ± 5.080 | 17.3875 ± 0.761 | 1.2736 ± 0.086 | 4941.4 ± 1234.079 | 0.9036 ± 0.066 | 31.6837 ± 0.606 | 1724.6 ± 143.843 | 39.9641 ± 0.504 | 120.5 ± 1.015 | 4259.6 ± 1814.034 | 31.6580 ± 0.532 |
| planarization | 0.8559 ± 0.103 | 482.7 ± 23.835 | 5911.0 ± 181.700 | 16.8009 ± 4.606 | 19.6419 ± 1.080 | 1.5223 ± 0.100 | 5559.0 ± 1115.736 | 0.9421 ± 0.100 | 32.1343 ± 0.743 | 1594.0 ± 109.322 | 38.7372 ± 1.052 | 114.8 ± 1.216 | 4472.9 ± 1802.809 | 30.9514 ± 0.486 |
| Average | 0.8784 | 479.5 | 6405.0 | 15.3524 | 18.7078 | 1.4208 | 5427.3 | 0.9328 | 30.7402 | 1668.0 | 38.9582 | 118.0 | 4332.6 | 29.7884 |


## E5 Baselines – MAE

| process | ALL | BGWO | BPSO | Boruta | DDA | FILTER | GA | LASSO | MI | NSGA2 | PFI-SBS | RFE | TSFGA | mRMR |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deposition | 7.3528 ± 0.104 (11) | 6.4701 ± 0.061 (2) | 6.6051 ± 0.143 (6) | 6.8793 ± 0.122 (8) | 6.4478 ± 0.076 (1) | 7.5767 ± 0.058 (13) | 7.0452 ± 0.153 (10) | 7.3947 ± 0.082 (12) | 6.5718 ± 0.068 (5) | 7.7204 ± 0.088 (14) | 6.4883 ± 0.067 (3) | 6.5355 ± 0.069 (4) | 6.9551 ± 0.290 (9) | 6.7327 ± 0.055 (7) |
| etching | 2.8669 ± 0.040 (13) | 2.4152 ± 0.023 (1) | 2.5428 ± 0.089 (6) | 2.6290 ± 0.052 (7) | 2.4461 ± 0.026 (2) | 2.8897 ± 0.050 (14) | 2.7955 ± 0.119 (10) | 2.8667 ± 0.052 (12) | 2.5415 ± 0.026 (5) | 2.8006 ± 0.016 (11) | 2.4684 ± 0.028 (3) | 2.5123 ± 0.027 (4) | 2.6730 ± 0.089 (8) | 2.7185 ± 0.033 (9) |
| implantation | 8.7074 ± 0.088 (13) | 7.5417 ± 0.111 (1) | 7.7966 ± 0.237 (4) | 8.1736 ± 0.088 (10) | 7.8901 ± 0.200 (6) | 8.7869 ± 0.109 (14) | 8.1420 ± 0.305 (9) | 8.5416 ± 0.070 (12) | 8.0146 ± 0.142 (8) | 8.2765 ± 0.086 (11) | 7.6428 ± 0.071 (2) | 7.7158 ± 0.064 (3) | 7.9208 ± 0.186 (7) | 7.8037 ± 0.140 (5) |
| lithography | 4.1229 ± 0.048 (12) | 3.3892 ± 0.046 (1) | 3.5594 ± 0.071 (7) | 3.5887 ± 0.035 (8) | 3.4519 ± 0.058 (4) | 4.1422 ± 0.063 (13) | 3.6638 ± 0.147 (9) | 4.0207 ± 0.037 (11) | 3.5084 ± 0.047 (6) | 4.2280 ± 0.030 (14) | 3.4033 ± 0.030 (2) | 3.4074 ± 0.042 (3) | 3.6853 ± 0.165 (10) | 3.4599 ± 0.045 (5) |
| metalization | 8.2031 ± 0.119 (13) | 6.9944 ± 0.139 (2) | 7.1157 ± 0.241 (5) | 7.2571 ± 0.087 (8) | 6.9113 ± 0.086 (1) | 8.2201 ± 0.075 (14) | 7.4738 ± 0.328 (10) | 8.1814 ± 0.094 (12) | 7.2376 ± 0.074 (7) | 7.5758 ± 0.044 (11) | 7.0155 ± 0.077 (3) | 7.0456 ± 0.057 (4) | 7.3672 ± 0.259 (9) | 7.2255 ± 0.081 (6) |
| planarization | 6.2070 ± 0.053 (11) | 5.2650 ± 0.066 (1) | 5.4369 ± 0.180 (4) | 5.6763 ± 0.063 (8) | 5.4668 ± 0.082 (5) | 6.3614 ± 0.066 (14) | 5.7715 ± 0.244 (10) | 6.2143 ± 0.066 (12) | 5.5531 ± 0.080 (6) | 6.2266 ± 0.043 (13) | 5.3410 ± 0.079 (2) | 5.3697 ± 0.076 (3) | 5.6102 ± 0.248 (7) | 5.7219 ± 0.067 (9) |
| Average | 6.2434 | 5.3459 | 5.5094 | 5.7007 | 5.4357 | 6.3295 | 5.8153 | 6.2032 | 5.5712 | 6.1380 | 5.3932 | 5.4311 | 5.7019 | 5.6104 |
| rank sum | 73 | 8 | 32 | 49 | 19 | 82 | 58 | 71 | 37 | 74 | 15 | 21 | 50 | 41 |


## E5 Baselines – R2

| process | ALL | BGWO | BPSO | Boruta | DDA | FILTER | GA | LASSO | MI | NSGA2 | PFI-SBS | RFE | TSFGA | mRMR |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deposition | 0.6568 ± 0.010 (12) | 0.7109 ± 0.010 (3) | 0.7029 ± 0.012 (6) | 0.6852 ± 0.010 (9) | 0.7128 ± 0.011 (2) | 0.6427 ± 0.009 (13) | 0.6855 ± 0.011 (8) | 0.6690 ± 0.008 (11) | 0.7055 ± 0.009 (5) | 0.6007 ± 0.012 (14) | 0.7133 ± 0.008 (1) | 0.7085 ± 0.009 (4) | 0.6779 ± 0.021 (10) | 0.6974 ± 0.009 (7) |
| etching | 0.7408 ± 0.009 (11) | 0.8068 ± 0.003 (1) | 0.7898 ± 0.011 (4) | 0.7719 ± 0.007 (8) | 0.7987 ± 0.007 (2) | 0.7421 ± 0.009 (10) | 0.7323 ± 0.029 (13) | 0.7391 ± 0.010 (12) | 0.7861 ± 0.006 (5) | 0.7596 ± 0.004 (9) | 0.7924 ± 0.005 (3) | 0.7852 ± 0.006 (6) | 0.7733 ± 0.014 (7) | 0.7295 ± 0.006 (14) |
| implantation | 0.6850 ± 0.005 (13) | 0.7508 ± 0.009 (1) | 0.7378 ± 0.015 (5) | 0.7208 ± 0.007 (9) | 0.7314 ± 0.015 (6) | 0.6781 ± 0.008 (14) | 0.7178 ± 0.021 (11) | 0.6938 ± 0.004 (12) | 0.7298 ± 0.010 (7) | 0.7189 ± 0.007 (10) | 0.7477 ± 0.005 (2) | 0.7468 ± 0.006 (3) | 0.7282 ± 0.012 (8) | 0.7381 ± 0.010 (4) |
| lithography | 0.6140 ± 0.008 (12) | 0.7132 ± 0.006 (1) | 0.6894 ± 0.013 (7) | 0.6816 ± 0.006 (8) | 0.7078 ± 0.009 (3) | 0.6123 ± 0.009 (13) | 0.6742 ± 0.024 (10) | 0.6306 ± 0.003 (11) | 0.6969 ± 0.007 (5) | 0.6101 ± 0.005 (14) | 0.7078 ± 0.005 (4) | 0.7091 ± 0.006 (2) | 0.6742 ± 0.019 (9) | 0.6940 ± 0.009 (6) |
| metalization | 0.7018 ± 0.007 (14) | 0.7705 ± 0.008 (1) | 0.7619 ± 0.013 (3) | 0.7492 ± 0.007 (9) | 0.7625 ± 0.007 (2) | 0.7081 ± 0.005 (12) | 0.7363 ± 0.023 (11) | 0.7033 ± 0.008 (13) | 0.7508 ± 0.007 (7) | 0.7428 ± 0.005 (10) | 0.7602 ± 0.005 (4) | 0.7601 ± 0.005 (5) | 0.7510 ± 0.013 (6) | 0.7503 ± 0.006 (8) |
| planarization | 0.6073 ± 0.005 (13) | 0.6923 ± 0.009 (1) | 0.6816 ± 0.014 (4) | 0.6496 ± 0.005 (9) | 0.6683 ± 0.010 (5) | 0.6024 ± 0.010 (14) | 0.6532 ± 0.019 (8) | 0.6126 ± 0.006 (12) | 0.6604 ± 0.009 (7) | 0.6241 ± 0.009 (11) | 0.6862 ± 0.008 (2) | 0.6822 ± 0.007 (3) | 0.6663 ± 0.018 (6) | 0.6485 ± 0.007 (10) |
| Average | 0.6676 | 0.7408 | 0.7272 | 0.7097 | 0.7303 | 0.6643 | 0.6999 | 0.6747 | 0.7216 | 0.6760 | 0.7346 | 0.7320 | 0.7118 | 0.7096 |
| rank sum | 75 | 8 | 29 | 52 | 20 | 76 | 61 | 71 | 36 | 68 | 16 | 23 | 46 | 49 |


## E6 Baselines – # feature pairs with |r|>0.8

| process | ALL | BGWO | BPSO | Boruta | DDA | FILTER | GA | LASSO | MI | NSGA2 | PFI-SBS | RFE | TSFGA | mRMR |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deposition | 18.0000 ± 0.000 | 0.0000 ± 0.000 | 0.0000 ± 0.000 | 15.0000 ± 0.000 | 4.4000 ± 1.838 | 0.0000 ± 0.000 | 1.4000 ± 1.430 | 11.0000 ± 0.000 | 15.0000 ± 0.000 | 0.0000 ± 0.000 | 9.3000 ± 3.889 | 6.1000 ± 0.316 | 0.0000 ± 0.000 | 5.4000 ± 1.265 |
| etching | 19.0000 ± 0.000 | 0.0000 ± 0.000 | 0.0000 ± 0.000 | 16.2000 ± 0.422 | 3.2000 ± 1.814 | 0.0000 ± 0.000 | 0.7000 ± 0.949 | 11.0000 ± 0.000 | 13.0000 ± 0.000 | 0.0000 ± 0.000 | 5.3000 ± 2.406 | 6.0000 ± 1.944 | 0.0000 ± 0.000 | 0.1000 ± 0.316 |
| implantation | 18.0000 ± 0.000 | 0.0000 ± 0.000 | 0.0000 ± 0.000 | 15.0000 ± 0.000 | 5.6000 ± 2.547 | 0.0000 ± 0.000 | 1.2000 ± 1.033 | 11.0000 ± 0.000 | 11.4000 ± 3.471 | 0.0000 ± 0.000 | 4.5000 ± 1.780 | 5.6000 ± 0.843 | 0.0000 ± 0.000 | 5.3000 ± 1.418 |
| lithography | 18.0000 ± 0.000 | 0.0000 ± 0.000 | 0.0000 ± 0.000 | 15.0000 ± 0.000 | 5.8000 ± 1.687 | 0.0000 ± 0.000 | 0.9000 ± 1.197 | 4.0000 ± 0.000 | 12.0000 ± 0.000 | 0.0000 ± 0.000 | 4.2000 ± 0.632 | 3.4000 ± 0.516 | 0.0000 ± 0.000 | 0.5000 ± 0.850 |
| metalization | 19.0000 ± 0.000 | 0.0000 ± 0.000 | 0.0000 ± 0.000 | 16.0000 ± 0.000 | 2.2000 ± 0.919 | 0.0000 ± 0.000 | 0.7000 ± 0.949 | 3.0000 ± 0.000 | 14.8000 ± 1.317 | 0.0000 ± 0.000 | 6.5000 ± 1.509 | 7.1000 ± 1.370 | 0.0000 ± 0.000 | 4.5000 ± 1.581 |
| planarization | 19.0000 ± 0.000 | 0.0000 ± 0.000 | 0.0000 ± 0.000 | 16.0000 ± 0.000 | 5.3000 ± 2.312 | 0.0000 ± 0.000 | 0.5000 ± 0.972 | 4.0000 ± 0.000 | 16.0000 ± 0.000 | 0.0000 ± 0.000 | 6.9000 ± 1.197 | 6.3000 ± 1.059 | 0.0000 ± 0.000 | 4.0000 ± 0.000 |
| Average | 18.5000 | 0.0000 | 0.0000 | 15.5333 | 4.4167 | 0.0000 | 0.9000 | 7.3333 | 13.7000 | 0.0000 | 6.1167 | 5.7500 | 0.0000 | 3.3000 |


## E7 Temporal vs random split – MRA

| split_mode   | process       |    ALL |    DDA |   FILTER |     MI |   NSGA2 |   PFI-SBS |   TSFGA |   mRMR |   gain_TSFGA_vs_ALL |
|:-------------|:--------------|-------:|-------:|---------:|-------:|--------:|----------:|--------:|-------:|--------------------:|
| random       | deposition    | 0.6594 | 0.6994 |   0.6472 | 0.6951 |  0.6433 |    0.6995 |  0.6836 | 0.688  |              0.0242 |
| random       | etching       | 0.75   | 0.7864 |   0.7472 | 0.7784 |  0.7548 |    0.7845 |  0.7636 | 0.7607 |              0.0136 |
| random       | implantation  | 0.6711 | 0.7026 |   0.6695 | 0.6978 |  0.6891 |    0.7138 |  0.705  | 0.7046 |              0.0339 |
| random       | lithography   | 0.711  | 0.758  |   0.7094 | 0.7551 |  0.7038 |    0.7606 |  0.7432 | 0.7578 |              0.0322 |
| random       | metalization  | 0.6976 | 0.7452 |   0.6969 | 0.7338 |  0.7197 |    0.7424 |  0.7295 | 0.734  |              0.0319 |
| random       | planarization | 0.6893 | 0.7254 |   0.6837 | 0.7209 |  0.687  |    0.7322 |  0.7184 | 0.7151 |              0.029  |
| temporal     | deposition    | 0.6448 | 0.6848 |   0.6408 | 0.684  |  0.6553 |    0.6883 |  0.6825 | 0.6801 |              0.0377 |
| temporal     | etching       | 0.7437 | 0.7782 |   0.7447 | 0.7713 |  0.7513 |    0.7797 |  0.7627 | 0.7669 |              0.0189 |
| temporal     | implantation  | 0.6804 | 0.7304 |   0.6825 | 0.7118 |  0.7002 |    0.7266 |  0.7177 | 0.7133 |              0.0373 |
| temporal     | lithography   | 0.7238 | 0.7563 |   0.7206 | 0.7501 |  0.7037 |    0.7529 |  0.738  | 0.7475 |              0.0142 |
| temporal     | metalization  | 0.7098 | 0.7464 |   0.7038 | 0.746  |  0.7006 |    0.7488 |  0.7109 | 0.7473 |              0.0011 |
| temporal     | planarization | 0.6989 | 0.7422 |   0.6975 | 0.7366 |  0.6913 |    0.7424 |  0.723  | 0.729  |              0.0242 |


## E7 TSFGA selection overlap (random vs temporal)

| process       |   seed |   jaccard_random_vs_temporal |
|:--------------|-------:|-----------------------------:|
| lithography   |      0 |                       0.2308 |
| lithography   |      1 |                       0.3077 |
| lithography   |      2 |                       0.2308 |
| lithography   |      3 |                       0.4    |
| lithography   |      4 |                       0.2143 |
| implantation  |      0 |                       0.5    |
| implantation  |      1 |                       0.3636 |
| implantation  |      2 |                       0.2727 |
| implantation  |      3 |                       0.2727 |
| implantation  |      4 |                       0.3333 |
| etching       |      0 |                       0.0833 |
| etching       |      1 |                       0.0769 |
| etching       |      2 |                       0.0909 |
| etching       |      3 |                       0.2727 |
| etching       |      4 |                       0.1    |
| metalization  |      0 |                       0.0909 |
| metalization  |      1 |                       0.1818 |
| metalization  |      2 |                       0.125  |
| metalization  |      3 |                       0.0714 |
| metalization  |      4 |                       0.0909 |
| deposition    |      0 |                       0.4167 |
| deposition    |      1 |                       0.2727 |
| deposition    |      2 |                       0.3    |
| deposition    |      3 |                       0.2143 |
| deposition    |      4 |                       0.3636 |
| planarization |      0 |                       0.3333 |
| planarization |      1 |                       0.2308 |
| planarization |      2 |                       0.375  |
| planarization |      3 |                       0.3333 |
| planarization |      4 |                       0.25   |


## E8 Transfer of TSFGA subset to other regressors – MRA

| process       | regressor   |    ALL |   TSFGA(majority) |   TSFGA(seed0) |   gain_majority |
|:--------------|:------------|-------:|------------------:|---------------:|----------------:|
| deposition    | dt          | 0.5667 |            0.6112 |         0.6019 |          0.0445 |
| deposition    | lgbm        | 0.6522 |            0.6461 |         0.6643 |         -0.0061 |
| deposition    | mlp         | 0.5555 |            0.6412 |         0.6465 |          0.0857 |
| deposition    | rf          | 0.6597 |            0.6943 |         0.6885 |          0.0346 |
| deposition    | svr         | 0.5848 |            0.6934 |         0.6465 |          0.1086 |
| etching       | dt          | 0.6867 |            0.7219 |         0.7071 |          0.0353 |
| etching       | lgbm        | 0.7581 |            0.7417 |         0.7284 |         -0.0164 |
| etching       | mlp         | 0.687  |            0.7399 |         0.6996 |          0.0529 |
| etching       | rf          | 0.7494 |            0.7551 |         0.7547 |          0.0057 |
| etching       | svr         | 0.693  |            0.7744 |         0.7057 |          0.0814 |
| implantation  | dt          | 0.6032 |            0.654  |         0.6403 |          0.0507 |
| implantation  | lgbm        | 0.6971 |            0.7015 |         0.7009 |          0.0044 |
| implantation  | mlp         | 0.6019 |            0.6886 |         0.5924 |          0.0867 |
| implantation  | rf          | 0.6692 |            0.7169 |         0.7068 |          0.0476 |
| implantation  | svr         | 0.5763 |            0.704  |         0.6326 |          0.1277 |
| lithography   | dt          | 0.6339 |            0.7139 |         0.6886 |          0.08   |
| lithography   | lgbm        | 0.7259 |            0.7441 |         0.7231 |          0.0182 |
| lithography   | mlp         | 0.686  |            0.743  |         0.7026 |          0.057  |
| lithography   | rf          | 0.7086 |            0.7618 |         0.7418 |          0.0533 |
| lithography   | svr         | 0.7071 |            0.7867 |         0.7441 |          0.0796 |
| metalization  | dt          | 0.6222 |            0.6881 |         0.6888 |          0.0659 |
| metalization  | lgbm        | 0.707  |            0.6863 |         0.7083 |         -0.0207 |
| metalization  | mlp         | 0.6167 |            0.6848 |         0.6605 |          0.0681 |
| metalization  | rf          | 0.702  |            0.7419 |         0.7485 |          0.0398 |
| metalization  | svr         | 0.596  |            0.7069 |         0.7056 |          0.1109 |
| planarization | dt          | 0.6133 |            0.6711 |         0.665  |          0.0578 |
| planarization | lgbm        | 0.7077 |            0.7216 |         0.7174 |          0.0139 |
| planarization | mlp         | 0.6919 |            0.7169 |         0.7041 |          0.025  |
| planarization | rf          | 0.6882 |            0.7382 |         0.7291 |          0.05   |
| planarization | svr         | 0.68   |            0.7563 |         0.7251 |          0.0763 |


## E8 Wilcoxon (majority subset vs ALL per regressor)

| reference       | method       |   n |   mean_diff |   median_diff |    W |   p_value |   wins |   ties |   losses | significant   | better       | regressor   |
|:----------------|:-------------|----:|------------:|--------------:|-----:|----------:|-------:|-------:|---------:|:--------------|:-------------|:------------|
| TSFGA(majority) | ALL          |  90 |      0.0385 |        0.0359 |  152 |    0      |     80 |      0 |       10 | True          | reference    | rf          |
| TSFGA(majority) | TSFGA(seed0) |  90 |      0.0065 |        0.0074 | 1110 |    0.0002 |     60 |      0 |       30 | True          | reference    | rf          |
| TSFGA(majority) | ALL          |  90 |     -0.0011 |       -0.001  | 1970 |    0.7552 |     43 |      0 |       47 | False         | ALL          | lgbm        |
| TSFGA(majority) | TSFGA(seed0) |  90 |     -0.0002 |        0.0012 | 2030 |    0.9439 |     49 |      0 |       41 | False         | TSFGA(seed0) | lgbm        |
| TSFGA(majority) | ALL          |  90 |      0.0626 |        0.0616 |  366 |    0      |     74 |      0 |       16 | True          | reference    | mlp         |
| TSFGA(majority) | TSFGA(seed0) |  90 |      0.0348 |        0.0361 | 1087 |    0.0001 |     59 |      0 |       31 | True          | reference    | mlp         |
| TSFGA(majority) | ALL          |  90 |      0.0974 |        0.0871 |    0 |    0      |     90 |      0 |        0 | True          | reference    | svr         |
| TSFGA(majority) | TSFGA(seed0) |  90 |      0.0437 |        0.0439 |   86 |    0      |     84 |      0 |        6 | True          | reference    | svr         |
| TSFGA(majority) | ALL          |  90 |      0.0557 |        0.0459 |  137 |    0      |     82 |      0 |        8 | True          | reference    | dt          |
| TSFGA(majority) | TSFGA(seed0) |  90 |      0.0114 |        0.0052 |  918 |    0.0001 |     55 |      6 |       29 | True          | reference    | dt          |


## E9 Second dataset – MRA

| process | ALL | DDA | FILTER | GA | MI | NSGA2 | PFI-SBS | TSFGA | mRMR |
|---|---|---|---|---|---|---|---|---|---|
| deposition | 0.6170 ± 0.006 (8) | 0.6531 ± 0.006 (3) | 0.6140 ± 0.004 (9) | 0.6548 ± 0.009 (2) | 0.6473 ± 0.004 (4) | 0.6442 ± 0.002 (6) | 0.6570 ± 0.003 (1) | 0.6466 ± 0.013 (5) | 0.6306 ± 0.007 (7) |
| etching | 0.6500 ± 0.005 (9) | 0.6914 ± 0.003 (1) | 0.6537 ± 0.006 (8) | 0.6760 ± 0.006 (7) | 0.6837 ± 0.005 (5) | 0.6852 ± 0.003 (3) | 0.6908 ± 0.004 (2) | 0.6845 ± 0.007 (4) | 0.6779 ± 0.002 (6) |
| implantation | 0.5946 ± 0.006 (8) | 0.6355 ± 0.006 (3) | 0.5909 ± 0.007 (9) | 0.6253 ± 0.021 (5) | 0.6249 ± 0.014 (6) | 0.6228 ± 0.003 (7) | 0.6472 ± 0.007 (1) | 0.6321 ± 0.017 (4) | 0.6356 ± 0.003 (2) |
| lithography | 0.6366 ± 0.005 (8) | 0.6756 ± 0.004 (2) | 0.6182 ± 0.006 (9) | 0.6640 ± 0.012 (4) | 0.6720 ± 0.004 (3) | 0.6376 ± 0.003 (7) | 0.6792 ± 0.005 (1) | 0.6529 ± 0.008 (6) | 0.6530 ± 0.001 (5) |
| metalization | 0.5766 ± 0.006 (8) | 0.6349 ± 0.009 (1) | 0.5676 ± 0.007 (9) | 0.5997 ± 0.017 (6) | 0.6203 ± 0.006 (3) | 0.5936 ± 0.002 (7) | 0.6346 ± 0.006 (2) | 0.6113 ± 0.014 (4) | 0.6014 ± 0.005 (5) |
| planarization | 0.6326 ± 0.005 (8) | 0.6728 ± 0.005 (2) | 0.6305 ± 0.003 (9) | 0.6517 ± 0.016 (6) | 0.6715 ± 0.004 (3) | 0.6543 ± 0.003 (5) | 0.6743 ± 0.005 (1) | 0.6628 ± 0.007 (4) | 0.6424 ± 0.003 (7) |
| Average | 0.6179 | 0.6606 | 0.6125 | 0.6453 | 0.6533 | 0.6396 | 0.6639 | 0.6484 | 0.6402 |
| rank sum | 49 | 12 | 53 | 30 | 24 | 35 | 8 | 27 | 32 |


## E9 Second dataset – PRF

| process | ALL | DDA | FILTER | GA | MI | NSGA2 | PFI-SBS | TSFGA | mRMR |
|---|---|---|---|---|---|---|---|---|---|
| deposition | 0.0000 ± 0.000 (9) | 0.7407 ± 0.039 (5) | 0.2037 ± 0.000 (8) | 0.8444 ± 0.038 (3) | 0.7000 ± 0.030 (6) | 0.9630 ± 0.000 (1) | 0.7778 ± 0.043 (4) | 0.8481 ± 0.027 (2) | 0.5741 ± 0.101 (7) |
| etching | 0.0000 ± 0.000 (9) | 0.8037 ± 0.021 (6) | 0.1852 ± 0.000 (8) | 0.8222 ± 0.028 (5) | 0.7593 ± 0.000 (7) | 0.9630 ± 0.000 (1) | 0.8889 ± 0.029 (3) | 0.8630 ± 0.017 (4) | 0.9444 ± 0.000 (2) |
| implantation | 0.0000 ± 0.000 (9) | 0.8259 ± 0.028 (5) | 0.2037 ± 0.000 (8) | 0.8111 ± 0.020 (6) | 0.8000 ± 0.085 (7) | 0.9630 ± 0.000 (1) | 0.8407 ± 0.053 (4) | 0.8704 ± 0.013 (2) | 0.8630 ± 0.031 (3) |
| lithography | 0.0000 ± 0.000 (9) | 0.8333 ± 0.013 (3) | 0.2037 ± 0.000 (8) | 0.8296 ± 0.030 (4) | 0.7704 ± 0.017 (6) | 0.9630 ± 0.000 (1) | 0.8000 ± 0.020 (5) | 0.8667 ± 0.027 (2) | 0.6963 ± 0.140 (7) |
| metalization | 0.0000 ± 0.000 (9) | 0.8185 ± 0.036 (4) | 0.1852 ± 0.000 (8) | 0.8000 ± 0.024 (5) | 0.7370 ± 0.024 (7) | 0.9630 ± 0.000 (1) | 0.9037 ± 0.008 (2) | 0.8407 ± 0.021 (3) | 0.7481 ± 0.077 (6) |
| planarization | 0.0000 ± 0.000 (9) | 0.7519 ± 0.021 (7) | 0.2037 ± 0.000 (8) | 0.8333 ± 0.035 (4) | 0.7593 ± 0.013 (6) | 0.9630 ± 0.000 (1) | 0.8185 ± 0.055 (5) | 0.8852 ± 0.030 (3) | 0.9259 ± 0.000 (2) |
| Average | 0.0000 | 0.7957 | 0.1975 | 0.8235 | 0.7543 | 0.9630 | 0.8383 | 0.8623 | 0.7920 |
| rank sum | 54 | 30 | 48 | 27 | 39 | 6 | 23 | 16 | 27 |


## E10 Ground-truth recovery by method (synthetic only)

| method   |   precision |   recall |     f1 |   n_redundant_kept |
|:---------|------------:|---------:|-------:|-------------------:|
| DDA      |      0.8591 |   0.5424 | 0.6614 |             2.8833 |
| Boruta   |      0.8234 |   0.4985 | 0.6157 |             4.0333 |
| PFI-SBS  |      0.8661 |   0.4364 | 0.5748 |             2.4333 |
| MI       |      0.835  |   0.45   | 0.5744 |             3.5    |
| RFE      |      0.8647 |   0.4061 | 0.5499 |             2.3    |
| BGWO     |      0.9833 |   0.3621 | 0.5284 |             0      |
| GA       |      0.61   |   0.4606 | 0.5205 |             0.6667 |
| BPSO     |      0.7146 |   0.3788 | 0.4914 |             0      |
| mRMR     |      0.6502 |   0.3924 | 0.4771 |             1.55   |
| TSFGA    |      0.5944 |   0.3773 | 0.4572 |             0.0333 |
| LASSO    |      0.2982 |   0.9545 | 0.453  |             3.5    |
| ALL      |      0.2558 |   1      | 0.4074 |             5      |
| FILTER   |      0.2558 |   1      | 0.4074 |             0.1667 |
| NSGA2    |      1      |   0.1818 | 0.3077 |             0      |


## E10 Category share of TSFGA-selected features

| process       |   lot |   machine |   workshop |
|:--------------|------:|----------:|-----------:|
| deposition    |     0 |         3 |          1 |
| etching       |     0 |         2 |          0 |
| implantation  |     0 |         2 |          2 |
| lithography   |     1 |         2 |          1 |
| metalization  |     0 |         3 |          0 |
| planarization |     1 |         3 |          0 |


## Figures

- E10_interpret\fig_E10_importance_deposition.png
- E10_interpret\fig_E10_importance_etching.png
- E10_interpret\fig_E10_importance_implantation.png
- E10_interpret\fig_E10_importance_lithography.png
- E10_interpret\fig_E10_importance_metalization.png
- E10_interpret\fig_E10_importance_planarization.png
- E10_interpret\fig_E10_selection_frequency.png
- E3_stats\fig_E3_cd_diagram_MRA.png
- E3_stats\fig_E3_cd_diagram_ablation.png
- E4_sensitivity\fig_E4_ga_pc.png
- E4_sensitivity\fig_E4_ga_pm.png
- E4_sensitivity\fig_E4_ga_pop_size.png
- E4_sensitivity\fig_E4_lambda.png
- E4_sensitivity\fig_E4_pcc_threshold.png
- E7_temporal\fig_E7_temporal_vs_random.png
- E7_temporal\split_random\fig_E1_violin_before_after.png
- E7_temporal\split_random\fig_E2_convergence.png
- E7_temporal\split_random\fig_E2_selection_frequency_TSFGA.png
- E7_temporal\split_random\fig_E6_corr_deposition.png
- E7_temporal\split_random\fig_E6_corr_etching.png
- E7_temporal\split_random\fig_E6_corr_implantation.png
- E7_temporal\split_random\fig_E6_corr_lithography.png
- E7_temporal\split_random\fig_E6_corr_metalization.png
- E7_temporal\split_random\fig_E6_corr_planarization.png
- E7_temporal\split_random\fig_E6_mra_vs_size_deposition.png
- E7_temporal\split_random\fig_E6_mra_vs_size_etching.png
- E7_temporal\split_random\fig_E6_mra_vs_size_implantation.png
- E7_temporal\split_random\fig_E6_mra_vs_size_lithography.png
- E7_temporal\split_random\fig_E6_mra_vs_size_metalization.png
- E7_temporal\split_random\fig_E6_mra_vs_size_planarization.png
- E7_temporal\split_random\fig_E6_pareto_deposition.png
- E7_temporal\split_random\fig_E6_pareto_etching.png
- E7_temporal\split_random\fig_E6_pareto_implantation.png
- E7_temporal\split_random\fig_E6_pareto_lithography.png
- E7_temporal\split_random\fig_E6_pareto_metalization.png
- E7_temporal\split_random\fig_E6_pareto_planarization.png
- E7_temporal\split_temporal\fig_E1_violin_before_after.png
- E7_temporal\split_temporal\fig_E2_convergence.png
- E7_temporal\split_temporal\fig_E2_selection_frequency_TSFGA.png
- E7_temporal\split_temporal\fig_E6_corr_deposition.png
- E7_temporal\split_temporal\fig_E6_corr_etching.png
- E7_temporal\split_temporal\fig_E6_corr_implantation.png
- E7_temporal\split_temporal\fig_E6_corr_lithography.png
- E7_temporal\split_temporal\fig_E6_corr_metalization.png
- E7_temporal\split_temporal\fig_E6_corr_planarization.png
- E7_temporal\split_temporal\fig_E6_mra_vs_size_deposition.png
- E7_temporal\split_temporal\fig_E6_mra_vs_size_etching.png
- E7_temporal\split_temporal\fig_E6_mra_vs_size_implantation.png
- E7_temporal\split_temporal\fig_E6_mra_vs_size_lithography.png
- E7_temporal\split_temporal\fig_E6_mra_vs_size_metalization.png
- E7_temporal\split_temporal\fig_E6_mra_vs_size_planarization.png
- E7_temporal\split_temporal\fig_E6_pareto_deposition.png
- E7_temporal\split_temporal\fig_E6_pareto_etching.png
- E7_temporal\split_temporal\fig_E6_pareto_implantation.png
- E7_temporal\split_temporal\fig_E6_pareto_lithography.png
- E7_temporal\split_temporal\fig_E6_pareto_metalization.png
- E7_temporal\split_temporal\fig_E6_pareto_planarization.png
- E8_transfer\fig_E8_transfer.png
- E9_dataset2\fig_E1_violin_before_after.png
- E9_dataset2\fig_E2_convergence.png
- E9_dataset2\fig_E2_selection_frequency_TSFGA.png
- E9_dataset2\fig_E6_corr_deposition.png
- E9_dataset2\fig_E6_corr_etching.png
- E9_dataset2\fig_E6_corr_implantation.png
- E9_dataset2\fig_E6_corr_lithography.png
- E9_dataset2\fig_E6_corr_metalization.png
- E9_dataset2\fig_E6_corr_planarization.png
- E9_dataset2\fig_E6_mra_vs_size_deposition.png
- E9_dataset2\fig_E6_mra_vs_size_etching.png
- E9_dataset2\fig_E6_mra_vs_size_implantation.png
- E9_dataset2\fig_E6_mra_vs_size_lithography.png
- E9_dataset2\fig_E6_mra_vs_size_metalization.png
- E9_dataset2\fig_E6_mra_vs_size_planarization.png
- E9_dataset2\fig_E6_pareto_deposition.png
- E9_dataset2\fig_E6_pareto_etching.png
- E9_dataset2\fig_E6_pareto_implantation.png
- E9_dataset2\fig_E6_pareto_lithography.png
- E9_dataset2\fig_E6_pareto_metalization.png
- E9_dataset2\fig_E6_pareto_planarization.png
- main\fig_E1_violin_before_after.png
- main\fig_E2_convergence.png
- main\fig_E2_selection_frequency_TSFGA.png
- main\fig_E6_corr_deposition.png
- main\fig_E6_corr_etching.png
- main\fig_E6_corr_implantation.png
- main\fig_E6_corr_lithography.png
- main\fig_E6_corr_metalization.png
- main\fig_E6_corr_planarization.png
- main\fig_E6_mra_vs_size_deposition.png
- main\fig_E6_mra_vs_size_etching.png
- main\fig_E6_mra_vs_size_implantation.png
- main\fig_E6_mra_vs_size_lithography.png
- main\fig_E6_mra_vs_size_metalization.png
- main\fig_E6_mra_vs_size_planarization.png
- main\fig_E6_pareto_deposition.png
- main\fig_E6_pareto_etching.png
- main\fig_E6_pareto_implantation.png
- main\fig_E6_pareto_lithography.png
- main\fig_E6_pareto_metalization.png
- main\fig_E6_pareto_planarization.png
