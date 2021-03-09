利用SuSE10.0做路由器，单网卡配置nat
作者：mishuang 2006/08/23 09:20
    由于我们实验室本科生来作毕业设计,ip地址不够用，我的SuSE就暂时做了router。

    eth0原来的配置如下：

    IP: 211.71.6.144

    MASK: 255.255.255.192

    ROUTER: 211.71.6.190

    DNS: 202.112.128.73

    第一步：

    为了使用nat必须给eth0再配置另外一个ip，192.168.3.1/255.255.255.0

    在suse10下，使用命令yast2 lan来添加另外一个ip

    也可以用下面的命令添加一个临时IP

    # ifconfig eth0:0 192.168.3.254

    不过用下面的命令重启网络服务之后，这个临时IP就没有了

    # /etc/init.d/network restart

    在/etc/dhcpd.conf文件中添加如下配置(不配置DHCP也是可以的)：

    subnet 192.168.3.0 netmask 255.255.255.0 {

     range 192.168.3.2 192.168.3.253;

     option routers 192.168.3.254;

     option domain-name "vrlab.buaa.edu.cn";

     option domain-name-servers 202.112.128.73;

    }

    然后启动dhcp服务

    chkconfig dhcpd on

    /etc/init.d/dhcpd start

    第二步：

    然后编写脚本/etc/init.d/nat，内容如下：

    #!/bin/bash

    IPTABLES='/usr/sbin/iptables'
    EXTERNAL='eth0'
    EXTERNIP='211.71.6.144'
    INTERNAL='eth0'
    INTERNIP='192.168.3.0/24'

    ifconfig eth0:0 192.168.3.254

    start(){

     $IPTABLES -P INPUT ACCEPT
     $IPTABLES -P OUTPUT ACCEPT
     $IPTABLES -P FORWARD ACCEPT

     # reset the nat talbe
     $IPTABLES -t nat -P PREROUTING ACCEPT
     $IPTABLES -t nat -P POSTROUTING ACCEPT
     $IPTABLES -t nat -P OUTPUT ACCEPT

     # flush the ipchains and nat table
     $IPTABLES -F
     $IPTABLES -F -t nat

     # delete non-default rules of ipchains and nat table

     # only the flushed user-defined chains can be deleted

     $IPTABLES -X
     $IPTABLES -t nat -X

     #reset zero

     #$IPTABLES -Z -t nat

     $IPTABLES -Z

     $IPTABLES -t nat -Z

     # 在这里添加自己的规则

     $IPTABLES -N priv

     # $IPTABLES -A priv -s 219.224.167.181 -j DROP

     # reset the three default ipchains

     $IPTABLES -A INPUT -j priv

     $IPTABLES -A OUTPUT -j priv

     $IPTABLES -A FORWARD -j priv

     #load necessary modules

     echo "Starting modprobe necessary modules for iptables"

    

     modprobe ip_tables 1> /dev/null

     # modprobe ip_nat_ftp 2> /dev/null

     # modprobe ip_nat_irc 2> /dev/null

     # modprobe ip_conntrack 2> /dev/null

     # modprobe ip_conntrack_ftp 2> /dev/null

     # modprobe ip_conntrack_irc 2> /dev/null

     # enable ICMP packet (ping) 默认是打开的

     # $IPTABLES -A INPUT -p all -j ACCEPT

     # $IPTABLES -A INPUT -p udp -j DROP

     # $IPTABLES -A INPUT -p tcp -j DROP

     # $IPTABLES -A INPUT -p icmp -j DROP

    

     # enable communication inside local domain

     $IPTABLES -A INPUT -i $INTERNAL -s $INTERNIP -j ACCEPT

     $IPTABLES -A OUTPUT -o $INTERNAL -d $INTERNIP -j ACCEPT

    

     # enable ip masquerade

     echo "1" >/proc/sys/net/ipv4/ip_forward

     # 出网后路由处理

     $IPTABLES -t nat -A POSTROUTING -o $EXTERNAL -s $INTERNIP -j MASQUERADE

     # $IPTABLES -t nat -A POSTROUTING -s $IPDOMAIN -j SNAT --to $OUTIP

     # 入网预路由处理

     # $IPTABLES -t nat -A PREROUTING -d $EXTERNIP -p tcp --dport 21 -j DNAT --to $FTPIP

     # $IPTABLES -t nat -A PREROUTING -d $EXTERNIP -p tcp --dport 79 -j DNAT --to $WEBIP

    }

    

    stop(){

     echo "Stopping firewall"

     $IPTABLES -P INPUT DROP

     $IPTABLES -P OUTPUT DROP

     $IPTABLES -P FORWARD DROP

     echo "0" >/proc/sys/net/ipv4/ip_forward

    }

    

    restart(){

     stop

     start

    }

    # see how we were called

    case $1 in

    start)

     start

     ;;

    stop)

     stop

     ;;

    restart)

     restart

     ;;

    *)

     echo $"Usage:$0 { start | stop | restart }"

     exit 1

    esac

    最后使用如下命令启动nat

    chkconfig nat on

    /etc/init.d/nat start

    在同一个局域网中的主机通过运行dhcp客户端就可以得到192.168.3.*的内网IP地址。额外的好处是vmware虚拟的所有操作系统只要设置为bridged，通过dhcp客户端也可以得到一个IP地址。
