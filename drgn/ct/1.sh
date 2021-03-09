#!/bin/bash

file=/tmp/1.txt

sudo ./esw_chains_priv.py > $file
sudo ./mlx5_tc_ct_priv.py >> $file

vi $file
