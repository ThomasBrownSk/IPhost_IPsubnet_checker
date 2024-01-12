import PySimpleGUI as sg
import ipaddress
import pandas as pd
import re

def validate_query(user_input):
    pattern_ip_dirty = r'[0-9]+(?:\.[0-9]+){3}'
    pattern_subnet_dirty =r'[0-9]+(?:\.[0-9]+){3}/(?:[12]?[0-9]|3[012])' 
    temp_list = []
    items = user_input.split()
    
    for item in items:
        if(re.findall(pattern_subnet_dirty, item)):
            w = ""
            item = w.join(re.findall(pattern_subnet_dirty, item))
            temp_list.append(item)
        
        elif(re.findall(pattern_ip_dirty, item)):
            w = ""
            item = w.join(re.findall(pattern_ip_dirty, item))
            temp_list.append(item)
        else: 
            temp_list.append(item) 
    
    return temp_list

def check_host_subnet(inputIP, df):
    output_df = pd.DataFrame(columns=['INPUT', 'IP', 'SITE_ID', 'REGION', 'BEHIND_FW', 'DESCRIPTION'])

    for row in df.itertuples():
        if ipaddress.ip_network(inputIP).subnet_of(ipaddress.ip_network(row.IP)):
            output = df.loc[df.index == row.Index]
            output_df = pd.concat([output_df, output], axis=0, ignore_index=True)

    if output_df.empty:
        #edf = edf.assign(INPUT=[inputIP])  #use in case that DESCRIPTION file is not needed
        description = ['HOST/SUBNET NOT FOUND']
        output_df = output_df.assign(DESCRIPTION=description)

    output_df = output_df.assign(INPUT=inputIP)
    return output_df

def not_found_table(data):
    if not data:
        pass
    else:
        print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        for i in data:
            print(f'{i} \t is not IPv4 host neither IPv4 network ')
        print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ \n')

sg.theme('DarkBlue3')   # Add a touch of color
# All the stuff inside your window.
tab_layout1 = [  [sg.Text('Input: ')],
            [sg.Multiline(size=(70, 5), enter_submits=True, key='-QUERY-', do_not_clear=False),
             sg.Button('SEND', bind_return_key=True), 
             sg.Button('CLEAR'),
             sg.Button('EXIT')],
            [sg.Text('Output: ')],
            [sg.Output(size=(110, 20), font=('Helvetica 10'),  key='-OUTPUT-')] ]

tab_layout2 = [[sg.Text('Log output')],
            [sg.Multiline(size=(110, 20), enter_submits=True, key='-LOG-', do_not_clear=False)]]

layout = [[sg.TabGroup([[sg.Tab('Validation tool', tab_layout1), sg.Tab('Log', tab_layout2)]])]]

# Create the Window
window = sg.Window('Validation tool v 1.0.01', layout)
try:
    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'EXIT'): # if user closes window or clicks EXIT
            break
        if event == 'CLEAR':
            window['-OUTPUT-'].update('')
        if event == 'SEND':
            query = values['-QUERY-'].rstrip()
        
            # TAB: Validation tool
            validated_query = validate_query(query)
            df = pd.read_csv('data.csv')
            out_df = pd.DataFrame()
            not_found_list = []

            for item in validated_query:
                try:
                    net = ipaddress.IPv4Network(item)
                    output = check_host_subnet(item, df)
                    out_df = pd.concat([out_df, output], axis=0, ignore_index=True)
                except ValueError as e:
                    not_found_list.append(item)

            if out_df.empty:
                pass
            else:
                window['-LOG-'].update(out_df)
                print(f'{out_df}\n')

            not_found_table(not_found_list)
            # TAB: Log
            
    window.close()

except Exception as ex_err:
    sg.popup_error_with_traceback(f'An error happened.  Here is the info: {str(ex_err)}')
