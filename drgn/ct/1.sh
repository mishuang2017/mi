#!/bin/bash

uplink=$1
file=/tmp/$$.txt

sudo ./esw_chains_priv.py $uplink > $file
sudo ./mlx5_tc_ct_priv.py $uplink >> $file
echo "=== post_action ===" >> $file
cd ..
sudo ./post_action.py $uplink >> $file
echo "=== indir_table ===" >> $file
sudo ./indir_table.py $uplink >> $file

vi $file
