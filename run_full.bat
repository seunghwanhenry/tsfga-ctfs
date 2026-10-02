@echo off
REM Double-click alternative to the notebook (Windows). Edit WORKERS / SEEDS if needed.
cd /d %~dp0
set WORKERS=16
set SEEDS=0,1,2,3,4
python -u run_experiments.py --preset full --exp all --out results/full --set workers=%WORKERS% seeds=%SEEDS% sensitivity.seeds=0,1 >> results_full.log 2>&1
