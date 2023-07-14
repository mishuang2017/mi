set -x

link=enp4s0f0
tc qdisc del dev $link root handle 1: htb
read
tc qdisc add dev $link root handle 1: htb default 6
read
tc class add dev $link parent 1: classid 1:1 htb rate 2mbit ceil 2mbit
read
# Creating leaf class 1:5 (prio represents priority, and 0 means high priority)

tc class add dev $link parent 1:1 classid 1:5 htb rate 1mbit ceil 1.5mbit
read
tc filter add dev $link protocol ip parent 1:0 prio 0 u32 match ip src 1.1.1.1/32 flowid 1:5
read
tc filter add dev $link protocol ip parent 1:0 prio 0 u32 match ip sport 22 0xffff flowid 1:5
read
# Creating leaf class 1:6 (It is set as default in root qdisc, so we are not setting any rules)

tc class add dev $link parent 1:1 classid 1:6 htb rate 0.5mbit ceil 1.5mbit
read
# Creating leaf class 1:7 (use /32 for specific IP, /24 for that series. Priority low - prio 5. You can get the IP address using "iptraf" tool)

tc class add dev $link parent 1:1 classid 1:7 htb rate 0.2mbit ceil 1mbit
read
tc filter add dev $link protocol ip parent 1:0 prio 5 u32 match ip src 1.1.1.2/32 flowid 1:7
read
# Optionally we can also add discipline with leaf (for an example we are adding SFQ with leaf class 1:5)

# tc qdisc add dev $link parent 1:5 handle 20: sfq perturb 10
set +x
