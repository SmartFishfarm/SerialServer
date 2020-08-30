import serial
import time
from DBUtils.PooledDB import PooledDB
import pymysql
from datetime import datetime
import sys

Zigbee_id = ['F6DD']
Node_id = ['0495']

i=0

num = sys.argv[1]
zigbee = serial.Serial(port='/dev/ttyUSB'+num,baudrate=9600)
pool = PooledDB(creator = pymysql, read_default_file='./mysql.cnf')
conn = pool.connection()

try:
    with conn.cursor() as curs: 
        timestamp = datetime.now().strftime('%s')
        for node_id in Node_id:
            zigbee.write(bytes('AT+UNICAST='+ node_id +',\\02DATA\\03 \n', 'ascii'));
            time.sleep(.1)
            data = zigbee.read(300)
            print(data)

            pos = data.index(str.encode('OK'))
            data = data[pos:]
            id = str(data[17:21])
            ph = str(float(data[65:70]))
            do = str(float(data[87:92]))
            temp = str(float(data[109:116])) 
            zigbee.flushInput()
            zigbee.flushOutput()

            curscommand = "SELECT id FROM appdb.analyzer WHERE company_id = 3 AND num = %s;"
            curs.execute(curscommand, (int(num)+1))
            result = curs.fetchone()
            id =str(result[0])
            curscommand="UPDATE appdb.realtime SET timestamp = %s, state = %s, value = %s, ph = %s, temp = %s WHERE analyzer_id = %s;";
            curs.execute(curscommand, (timestamp, '00', do, ph, temp, id))
            conn.commit()
            i = i + 1


finally:
    zigbee.close()
    conn.close()
    curs.close()
