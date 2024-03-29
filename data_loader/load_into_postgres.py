import click
import psycopg2 as pg
import threading
from udpRead import UdpReader
import threading

def start_loading(dbname, password, user, ecu_ip, db_host):
    udpReader = UdpReader(ecu_ip)
    conn = pg.connect(f'dbname={dbname}  user={user} password={password} host={db_host} port=5432')

    while True:
        try:
            data = udpReader.getData(f"sAll;tc;pt;")
            if (data is not None):
                data = str(data, encoding='utf-8')
                sAll, tc, pt,  *extra = data.split(';')
                print(sAll)
                tc = [float(t) for t in tc.split(',') if t != '']
                sAll = [int(s) for s in sAll.split(',') if s != '']
                pt = [float(p) for p in pt.split(',') if p != '']

                print("PT: ", pt)
        except KeyboardInterrupt as k:
            conn.close()
            exit(0)
        except Exception as e:
            click.secho(f"fucked {e}", fg='red')
        with conn.cursor() as cur:
            cur.execute("INSERT INTO solenoids (he, lng, lox, pv1, pv2, mvas) VALUES (%s, %s, %s, %s, %s, %s);", 
                    (sAll[0], sAll[1], sAll[2], sAll[3], sAll[4], sAll[5]))
            cur.execute("INSERT INTO pt (pt1, pt2, pt3, pt4) VALUES (%s, %s, %s, %s);", (pt[1], pt[2], pt[3], pt[4]))
            cur.execute("INSERT INTO tc (tc1, tc2, tc3, tc4) VALUES (%s, %s, %s, %s);", (tc[0], tc[1], tc[2], tc[3]))
        conn.commit()

def gse_start_loading(dbname, password, user, ecu_ip, db_host):
    udpReader = UdpReader(ecu_ip)
    conn = pg.connect(f'dbname={dbname}  user={user} password={password} host={db_host} port=5432')

    while True:
        try:
            data = udpReader.getData(f"sAll;tc;pt;")
            if (data is not None):
                data = str(data, encoding='utf-8')
                sAll, tc, pt,  *extra = data.split(';')
                print(sAll)
                pt = [float(p) for p in pt.split(',') if p != '']
                extra = float(extra[0])

                print("PT: ", pt)
            else:
                print("No GSE found")
                return
        except KeyboardInterrupt as k:
            conn.close()
            exit(0)
        except Exception as e:
            click.secho(f"fucked {e}", fg='red')
        with conn.cursor() as cur:
            cur.execute("INSERT INTO gse_pt (pt1, pt2, pt3, pt4) VALUES (%s, %s, %s, %s);", (pt[3], pt[4], extra, pt[0]))
        conn.commit()

if __name__ == '__main__':
        start_loading('postgres', 'postgres', 'postgres', '192.168.0.6', 'postgres')


