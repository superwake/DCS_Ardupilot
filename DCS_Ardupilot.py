#!/usr/bin/env python3

import socket
import struct


def decode_dcs(dcs_msg_in):
    # Takes a message from DCS (created via the Export.lua) and puts it into a Python dictionary
    # Splitting the incoming message into the data components
    data_in = dcs_msg_in.decode("utf-8").strip().split(', ')

    # Putting the message info into the state dictionary
    dcs_state_out = dict()
    for data in data_in:
        tmp = data.split('=')
        try:  # Checking if the value is a float
            tmp[1] = float(tmp[1])
        except:
            pass
        dcs_state_out[tmp[0]] = tmp[1]

    return dcs_state_out


def encode_mp(state_in, mp_subjects_in):

    msg_out = [68, 65, 84, 65, 0]

    for subj in mp_subjects_in:
        msg_out_section = [0] * 36
        msg_out_section[0] = subj

        if subj == 1:  # Time
            msg_out_section[12:16] = list(struct.pack('f', state_in['Time']))

        elif subj == 3:  # V_eas
            # Not sure which one DCS outputs - indicated or equivalent. Ardupilot uses EAS
            msg_out_section[8:12] = list(struct.pack('f', state_in['V_ind'] * 1.94384))  # m/s to knots

        elif subj == 4:  # Norml, Axial, Side
            msg_out_section[20:24] = list(struct.pack('f', state_in['Norml']))
            msg_out_section[24:28] = list(struct.pack('f', state_in['Axial']))
            msg_out_section[28:32] = list(struct.pack('f', state_in['Side']))

        elif subj == 8:  # Elev, Ailr, Rudd
            msg_out_section[4:8] = list(struct.pack('f', state_in['Elev']))
            msg_out_section[8:12] = list(struct.pack('f', state_in['Ailr']))
            msg_out_section[12:16] = list(struct.pack('f', state_in['Rudd']))

        elif subj == 16:  # Q, P, R
            msg_out_section[4:8] = list(struct.pack('f', state_in['Q']))
            msg_out_section[8:12] = list(struct.pack('f', state_in['P']))
            msg_out_section[12:16] = list(struct.pack('f', state_in['R']))

        elif subj == 17:  # Pitch, Roll, Hding
            msg_out_section[4:8] = list(struct.pack('f', state_in['Pitch']))
            msg_out_section[8:12] = list(struct.pack('f', state_in['Roll']))
            msg_out_section[12:16] = list(struct.pack('f', state_in['Hding']))

        elif subj == 20:  # Lat, Lon, Alt, RAlt
            msg_out_section[4:8] = list(struct.pack('f', state_in['Lat']))
            msg_out_section[8:12] = list(struct.pack('f', state_in['Lon']))
            msg_out_section[12:16] = list(struct.pack('f', state_in['Alt'] * 3.28084))  # m to ft
            msg_out_section[16:20] = list(struct.pack('f', state_in['RAlt'] * 3.28084))  # m to ft

        elif subj == 21:  # Pos_E, Pos_U, Pos_S, Vel_E, Vel_U, Vel_S
            msg_out_section[4:8] = list(struct.pack('f', state_in['Pos_E']))
            msg_out_section[8:12] = list(struct.pack('f', state_in['Pos_U']))
            msg_out_section[12:16] = list(struct.pack('f', state_in['Pos_S']))
            msg_out_section[16:20] = list(struct.pack('f', state_in['Vel_E']))
            msg_out_section[20:24] = list(struct.pack('f', state_in['Vel_U']))
            msg_out_section[24:28] = list(struct.pack('f', state_in['Vel_S']))

        msg_out.extend(msg_out_section)

    return bytes(msg_out)


# Port information
FROM_DCS_HOST = '127.0.0.1'
FROM_DCS_PORT = 8001
TO_MP_HOST = '127.0.0.1'
TO_MP_PORT = 49001
FROM_MP_HOST = '127.0.0.1'
FROM_MP_PORT = 49000

mp_s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

mp_subjects = [1, 3, 4, 8, 13, 16, 17, 18, 20, 21, 25, 29, 37, 38, 39, 58]

# from_mp_s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# from_mp_s.bind((FROM_MP_HOST, FROM_MP_PORT))

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as dcs_s:
    dcs_s.bind((FROM_DCS_HOST, FROM_DCS_PORT))
    dcs_s.listen()
    conn, addr = dcs_s.accept()
    with conn:
        print('Connected by', addr)
        while True:
            msg = conn.recv(1024)
            if not msg:
                print('Error in TCP data stream from DCS.')
                break

            dcs_state = decode_dcs(msg)
            mp_msg_out = encode_mp(dcs_state, mp_subjects)

            mp_s.sendto(mp_msg_out, (TO_MP_HOST, TO_MP_PORT))
            # print(mp_msg_out)
            # try:
            #     data, address = mp_s.recvfrom(4096)
            #     print(data)
            # except:
            #     pass
