from datetime import datetime
import socket
import sys
import time

HOST = "127.0.0.1"  # standard loopback interface address (localhost)
PORT = 4444  # port to listen on (non-privileged ports are > 1023)

data = b''
decoded_data = ''

def decode_temp_humi_bytes(raw):
    return (raw[0] << 8) + raw[1], (raw[3] << 8) + raw[4]

def parse_bytes(bytes_in):
    top_bytes = bytes_in[0:6]
    bot_bytes = bytes_in[6:-1]

    top_data_raw = decode_temp_humi_bytes(top_bytes)
    bot_data_raw = decode_temp_humi_bytes(bot_bytes)

    top_data =  -45 + (175 * (top_data_raw[0] / 65535)) , 100 * (top_data_raw[1] / 65535)
    bot_data =  -45 + (175 * (bot_data_raw[0] / 65535)) , 100 * (bot_data_raw[1] / 65535)

    return (top_data, bot_data)

#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# open datafile
with open('chamber_data.csv', 'a') as f:
    # init TCP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        HOST = socket.gethostname() # assign self ip as host ip
        print('HOST: ', HOST)
        #s.settimeout(60)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        s.bind((HOST, PORT))
        s.listen() # listen for connections

        # infinite loop here
        while True:
            # reset timeout
            s.settimeout(None)

            # wait for connection requests and accept
            try: 
                conn, addr = s.accept()
            except socket.timeout:
                "Server froze... trying to accept again"
                conn, addr = s.accept()
 
            # with new connection
            with conn:
                # print connector ip
                print(f"Connected by {addr}")

                # loop to read in all data
                while True:
                    s.settimeout(10) # 10 seconds to read all data

                    try:
                        new_data = conn.recv(1024)
                        if sys.getsizeof(data) == sys.getsizeof(data + new_data):
                            s.settimeout(None) # reset timeout
                            break
                        data += new_data
                        conn.sendall(new_data)
                    except:
                        pass
                
                # parse data with custom function
                try:
                    parsed_data = parse_bytes(data)
                    csv_data = f"{datetime.now()},{parsed_data[0][0]},{parsed_data[0][1]},{parsed_data[1][0]},{parsed_data[1][1]}\n"

                    # write data to file
                    f.write(csv_data)
                    f.flush() # flush buffer bc file is kept open

                    # print confirmation
                    print(f"Received data: {datetime.now().strftime('%H:%M:%S')}: T_top = {round(parsed_data[0][0], 2)} C, H_top = {round(parsed_data[0][1], 2)} %")
                    print(f"\t\t\t T_bot = {round(parsed_data[1][0], 2)} C, H_bot = {round(parsed_data[1][1], 2)} %\n")
                    data = b'' # clear data
                except IndexError:
                    pass