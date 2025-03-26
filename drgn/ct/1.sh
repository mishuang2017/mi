#!/bin/bash

file=/tmp/$$.txt

sudo ./esw_chains_priv.py > $file
sudo ./mlx5_tc_ct_priv.py >> $file
echo "=== post_action ===" >> $file
cd ..
sudo ./post_action.py >> $file
echo "=== indir_table ===" >> $file
sudo ./indir_table.py >> $file

vi $file
