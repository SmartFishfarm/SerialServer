import serial
import serial.rs485 as rs485

from DBUtils.PooledDB import PooledDB
import pymysql
from datetime import datetime

import sys

num = sys.argv[1]
port = '/dev/ttyUSB'+num
vals = [0x02, 0x44, 0x41, 0x54, 0x41, 0x03]

pool = PooledDB(creator = pymysql, read_default_file='./mysql.cnf')

def dbinput(do, ph, temp):
  conn = pool.connection()
  try:

        with conn.cursor() as cursor:
          sql = "SELECT id FROM appdb.analyzer WHERE company_id = 3 AND num = %s;"
          cursor.execute(sql, (int(num)+1))
          for id in cursor.fetchone():
            analyzer_id = id

        with conn.cursor() as cursor:
          timestamp = datetime.now().strftime('%s')
          sql = "UPDATE appdb.realtime SET timestamp = %s, state = %s, value = %s, ph = %s, temp = %s WHERE analyzer_id = %s;";
          cursor.execute(sql, (timestamp, '00', do, ph, temp, analyzer_id))
          conn.commit()

  finally:
    cursor.close()
    conn.close()


try:
    ser = rs485.RS485(port, baudrate=9600, timeout=2, write_timeout=2)
    ser.rs485_mode = rs485.RS485Settings(delay_before_tx=2, delay_before_rx=2)

    if(ser.isOpen() == False):
      ser.open()

    ser.write(bytearray(vals))
    data = ser.readline()

    try:
      pos1 = data.index(str.encode('+'))
    except ValueError as err:
      pos1 = 10000

    try:
      pos2 = data.index(str.encode('-'))
    except ValueError as err:
     pos2 = 10000

    if ( pos1 < pos2 ):
      pos = pos1
    elif ( pos2 < pos1 ):
      pos = pos2
    else:
      pos = 0

    data = data[pos:]
    
    ph = str(float(data[11:21]))
    do = str(float(data[33:43]))
    temp = str(float(data[56:65]))

    dbinput(do, ph, temp)
    print(data)
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    ser.close()

except OSError as err:
        print(err)


