#!/usr/bin/python
# -*- coding: utf-8
import MySQLdb
from subprocess import Popen, PIPE
import subprocess
import httplib, urllib
import json
from termcolor import colored
import string, os, sys, re
try:
    import configparser
except:
    from six.moves import configparser

conf_file = "/etc/asterisk/extconfig.conf"
rtm_str = "sippeers => odbc,asterisk,SIP"
sip_conf = "/etc/asterisk/sip.conf"
tmp_secret_file = "/tmp/tmp_secret_file"
parse_sipconf = "cat " + sip_conf + " | sed  '/^;--/,/^--;/d' > " + tmp_secret_file

def main():
    while True:
        try:
            sip = raw_input("SIP: ")
            int(sip)
        except SyntaxError:
            print(colored('It`s not a number! Try again, please!', 'red'))
        except ValueError:
            print(colored('It`s not a number! Try again, please!', 'red'))
        except KeyboardInterrupt:
            sys.exit(0)
        else:
            try:
                if parse_file(conf_file) == 1:
                   stat_secret = sipconf_peers(sip)
                   rtm_secret = rtm_peers(sip)
                   if str(stat_secret) == str('0'):
                        print(colored("Realtime technology, this peer is only in DB", 'green') + '\n'
                        + "(rtm) " +  rtm_secret)
                   elif str(rtm_secret) == str('None'):
                        print(colored("Realtime technology, but no such peer in DB", 'yellow') + '\n'
                        + "(static) " + stat_secret)
                   elif str(rtm_secret) == str(stat_secret):
                        print(colored("Realtime technology, same passwords are using", 'green') + '\n'
                        + "(rtm) " +  rtm_secret)
                   elif str(rtm_secret) == str('None') and str(stat_secret) == str('0'):
                        print(colored('No such peer! Try again, please!', 'red'))
                   else:
                        print(colored("Realtime technology, different passwords are using", 'yellow') + '\n'
                        + "(rtm) " + rtm_secret + '\n'
                        + "(static) " + stat_secret)
                        choose(sip, stat_secret)
                else:
                   stat_secret = sipconf_peers(sip)
                   rtm_secret = rtm_peers(sip)
                   if str(rtm_secret) == str('None'):
                       print(colored("Static technology, but this peer is only in /etc/asterisk/sip.conf", 'green') + '\n'
                       + "(stat) " + stat_secret)
                   elif str(stat_secret) == str('0'):
                       print(colored("Static technology, but no such peer in /etc/asterisk/sip.conf", 'yellow') + '\n'
                       + "(rtm) " + rtm_secret)
                   elif str(stat_secret) == str(rtm_secret):
                       print(colored("Static technology, same passwords are using", 'green') + '\n'
                       + "(static) " + stat_secret)
                   elif str(rtm_secret) == str('None') and str(stat_secret) == str('0') or str(stat_secret) == str('0'):
                       print(colored('No such peer! Try again, please!', 'red'))
                   else:
                       print(colored("Static technology, different passwords are using", 'yellow') + '\n'
                       + "(rtm)" + rtm_secret + '\n'
                       + "(static) " + stat_secret)
                       choose(sip, stat_secret)
            except ValueError:
                print(colored('No such peer in DB! Try again, please!', 'red'))

def parse_file(conf_file):
    with open(conf_file, 'r') as tmp_file:
        for line in tmp_file:
            line.strip()
            if line.startswith('sippeers'):
                conf_flag = 1
                break
            else:
                conf_flag = 0
    return conf_flag


def rtm_peers(sip):
    try:
        db = MySQLdb.connect(host="localhost", user="root", passwd="gjhjctyjr26", db="asterisk")
        cursor = db.cursor()
        sql = "SELECT secret FROM SIP WHERE sip_name LIKE '%" + str(sip) + "%'"
        cursor.execute(sql)
        rows_count = cursor.execute(sql)
        if rows_count > 0:
            data = cursor.fetchall()
            for rec in data:
                secret = rec
        else:
            return str('None')
    except MySQLdb.Error, e:
        print(colored("Error %d: %s" % (e.args[0], e.args[1]), 'red'))
    finally:
        if db:
            db.close()
    return str(secret).strip('\'(,)\'')

def update_rtm_secret(sip, secret):
    try:
        db = MySQLdb.connect(host="localhost", user="root", passwd="gjhjctyjr26", db="asterisk")
        cursor = db.cursor()
        sql = "UPDATE SIP set secret=\"" + secret + "\" where sip_name=\"SIP/" + sip + "\""
        cursor.execute(sql)
        db.commit()
    except _mysql.Error, e:
        print(colored("Error %d: %s" % (e.args[0], e.args[1]), 'red'))
    finally:
        if db:
            db.close()

def choose(sip, secret):
    try:
        choose = raw_input("Do you want to duplicate secret from SIP.CONF to DB?(y/n) ")
        if str(choose).lower() == 'y':
            update_rtm_secret(sip, secret)
    except  KeyboardInterrupt:
        sys.exit(0)

def conffile(conffile):
    fts = Popen(conffile, shell=True, stdout=PIPE, stderr=PIPE)

def sipconf_peers(sip):
    try:
        config = configparser.ConfigParser()
        conffile(parse_sipconf)
        config.read(tmp_secret_file)
        secret = config.get(str(sip), "secret")
    except configparser.NoSectionError:
        print(colored("No such section [" + str(sip) + "] in /etc/asterisk/sip.conf", 'red'))
        secret = 0
    except configparser.ParsingError:
        secret = 0
    return str(secret)

if __name__ == "__main__":
    main()
